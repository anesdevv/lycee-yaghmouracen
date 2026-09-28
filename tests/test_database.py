import hashlib
import database.db as db

def test_admin_auth_and_pbkdf2():
    # Verify default admin seeded by init_db
    assert db.verify_admin("admin", "admin") is True
    assert db.verify_admin("admin", "wrong_password") is False
    assert db.verify_admin("nonexistent", "admin") is False

    # Check that password hash uses PBKDF2 format ($ separated)
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM admin WHERE username = ?", ("admin",))
    stored_hash = cur.fetchone()["password"]
    conn.close()
    assert "$" in stored_hash

    # Test password change
    assert db.change_admin_password("admin", "wrong_password", "new_secret123") is False
    assert db.change_admin_password("admin", "admin", "new_secret123") is True
    assert db.verify_admin("admin", "admin") is False
    assert db.verify_admin("admin", "new_secret123") is True

def test_legacy_sha256_hash_upgrade():
    conn = db.get_connection()
    cur = conn.cursor()
    # Manually insert a legacy sha256 hash without salt
    legacy_hash = hashlib.sha256("legacy_pass".encode("utf-8")).hexdigest()
    cur.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("legacy_user", legacy_hash))
    conn.commit()
    conn.close()

    # Authenticate with legacy password - should succeed and auto-upgrade to PBKDF2
    assert db.verify_admin("legacy_user", "legacy_pass") is True

    # Verify database was updated to salted PBKDF2 format
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM admin WHERE username = ?", ("legacy_user",))
    updated_hash = cur.fetchone()["password"]
    conn.close()
    assert "$" in updated_hash
    # Still authenticates after upgrade
    assert db.verify_admin("legacy_user", "legacy_pass") is True

def test_students_crud():
    # Create student
    student_id = db.add_student(
        first_name="Tarek",
        last_name="Boudiaf",
        birth_date="15/04/2008",
        gender="Male",
        class_name="1 AS - Science 1",
        address="Oran Centre",
        parent_name="Ali Boudiaf",
        photo_path=""
    )
    assert student_id > 0

    # Read student
    student = db.get_student_by_id(student_id)
    assert student is not None
    assert student["first_name"] == "Tarek"
    assert student["last_name"] == "Boudiaf"
    assert student["class_name"] == "1 AS - Science 1"

    # Search students
    results = db.get_students(search_query="Boudiaf")
    assert any(s["id"] == student_id for s in results)

    # Filter by class
    class_results = db.get_students(class_filter="1 AS - Science 1")
    assert any(s["id"] == student_id for s in class_results)

    # Update student
    db.update_student(
        id=student_id,
        first_name="Tarek",
        last_name="Boudiaf-Updated",
        birth_date="15/04/2008",
        gender="Male",
        class_name="2 AS - Math",
        address="Es-Senia, Oran",
        parent_name="Ali Boudiaf",
        photo_path=""
    )
    updated = db.get_student_by_id(student_id)
    assert updated["last_name"] == "Boudiaf-Updated"
    assert updated["class_name"] == "2 AS - Math"

    # Delete student
    db.delete_student(student_id)
    assert db.get_student_by_id(student_id) is None

def test_foreign_key_cascade_attendance():
    # Create student
    student_id = db.add_student(
        first_name="Karim",
        last_name="Zitouni",
        birth_date="01/01/2008",
        gender="Male",
        class_name="1 AS - Science 1",
        address="Oran",
        parent_name="Bachir Zitouni",
        photo_path=""
    )

    # Add attendance records
    db.save_attendance(student_id, "01/10/2026", "Absent")
    db.save_attendance(student_id, "02/10/2026", "Absent")
    st = db.get_student_by_id(student_id)
    assert st["absence_count"] == 2

    # Check rows directly in attendance table
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ?", (student_id,))
    assert cur.fetchone()[0] == 2
    conn.close()

    # Delete student - foreign key cascade should delete attendance rows
    db.delete_student(student_id)

    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ?", (student_id,))
    count_after = cur.fetchone()[0]
    conn.close()
    assert count_after == 0

def test_attendance_batch_save_and_toggle():
    s1_id = db.add_student("Nadia", "Khelif", "10/05/2008", "Female", "1 AS - Science 1", "Oran", "Parent", "")
    s2_id = db.add_student("Samir", "Hamidi", "12/06/2008", "Male", "1 AS - Science 1", "Oran", "Parent", "")

    # Batch save attendance
    batch = [
        (s1_id, "26/05/2026", "Absent"),
        (s2_id, "26/05/2026", "Present")
    ]
    saved_count = db.save_attendance_batch(batch)
    assert saved_count == 2

    # Check daily attendance map
    daily = db.get_attendance_for_date_and_class("26/05/2026", "1 AS - Science 1")
    daily_map = {row["student_id"]: row["status"] for row in daily}
    assert daily_map[s1_id] == "Absent"
    assert daily_map[s2_id] == "Present"

    # Check absence count
    assert db.get_student_by_id(s1_id)["absence_count"] == 1
    assert db.get_student_by_id(s2_id)["absence_count"] == 0

    # Toggle s1 to Present via batch
    db.save_attendance_batch([(s1_id, "26/05/2026", "Present")])
    daily_updated = db.get_attendance_for_date_and_class("26/05/2026", "1 AS - Science 1")
    daily_updated_map = {row["student_id"]: row["status"] for row in daily_updated}
    assert daily_updated_map[s1_id] == "Present"
    assert db.get_student_by_id(s1_id)["absence_count"] == 0

def test_attendance_date_sorting_and_filtering():
    s_id = db.add_student("Amina", "Saidi", "10/05/2008", "Female", "1 AS - Science 1", "Oran", "Parent", "")

    # Add records spanning across chronological dates (stored as DD/MM/YYYY)
    db.save_attendance(s_id, "05/01/2026", "Absent")
    db.save_attendance(s_id, "20/02/2026", "Absent")
    db.save_attendance(s_id, "10/12/2025", "Absent")

    # Get student attendance history - should be ordered DESC (most recent first)
    history = db.get_attendance_history(class_name="1 AS - Science 1")
    dates = [row["attendance_date"] for row in history if row["student_id"] == s_id]
    assert dates == ["20/02/2026", "05/01/2026", "10/12/2025"]

    # Filter with start_date and end_date in DD/MM/YYYY
    filtered = db.get_attendance_history(
        class_name="1 AS - Science 1",
        date_from="01/01/2026",
        date_to="31/01/2026"
    )
    filtered_dates = [r["attendance_date"] for r in filtered if r["student_id"] == s_id]
    assert filtered_dates == ["05/01/2026"]

def test_employees_crud():
    emp_id = db.add_employee(
        employee_id="EMP-TEST-01",
        first_name="Fatima",
        last_name="Mansour",
        role="Enseignant",
        hire_date="01/09/2020",
        salary=48000.0,
        specialty="Physique",
        phone="0555123456"
    )
    assert emp_id > 0

    # Get by numeric ID
    emp = db.get_employee_by_id(emp_id)
    assert emp is not None
    assert emp["first_name"] == "Fatima"
    assert emp["salary"] == 48000.0

    # Get by employee string code
    emp_by_code = db.get_employee_by_employee_id("EMP-TEST-01")
    assert emp_by_code is not None
    assert emp_by_code["id"] == emp_id

    # Update employee
    db.update_employee(
        id=emp_id,
        employee_id="EMP-TEST-01",
        first_name="Fatima",
        last_name="Mansour-Kaddour",
        role="Enseignant",
        hire_date="01/09/2020",
        salary=52000.0,
        specialty="Physique-Chimie",
        phone="0555987654"
    )
    updated = db.get_employee_by_id(emp_id)
    assert updated["last_name"] == "Mansour-Kaddour"
    assert updated["salary"] == 52000.0
    assert updated["specialty"] == "Physique-Chimie"

    # Delete employee
    db.delete_employee(emp_id)
    assert db.get_employee_by_id(emp_id) is None
    assert db.get_employee_by_employee_id("EMP-TEST-01") is None

def test_classes_crud():
    # Add new class
    class_id = db.add_class("Terminal - Math Technique")
    assert class_id > 0
    assert db.is_class_name_exists("Terminal - Math Technique") is True

    # Associate student with this class
    sid = db.add_student("Zouhir", "Benali", "01/01/2007", "Male", "Terminal - Math Technique", "Oran", "P", "")
    student = db.get_student_by_id(sid)
    assert student["class_name"] == "Terminal - Math Technique"

    # Rename class - student's class name should synchronize
    db.update_class(class_id, "3 AS - Math Technique")
    student_synced = db.get_student_by_id(sid)
    assert student_synced["class_name"] == "3 AS - Math Technique"

    # Delete class - student's class name should be cleared
    db.delete_class(class_id)
    student_cleared = db.get_student_by_id(sid)
    assert student_cleared["class_name"] == ""

def test_dashboard_stats():
    stats = db.get_dashboard_stats()
    assert isinstance(stats, dict)
    assert "students" in stats
    assert "employees" in stats
    assert "classes" in stats
    assert "absences" in stats
