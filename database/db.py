import os
import sqlite3
import hashlib
import secrets

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "school.db")

def get_connection(db_path=None):
    """Establish and return a connection to the SQLite database with Foreign Keys enabled."""
    target_path = db_path if db_path is not None else DB_PATH
    conn = sqlite3.connect(target_path, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password, salt=None):
    """Hash a password using PBKDF2 with SHA-256 and a random cryptographic salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${key.hex()}"

def verify_password(stored_hash, password):
    """Verify password against stored hash, supporting both PBKDF2 and legacy SHA-256."""
    if not stored_hash or not password:
        return False
    if "$" in stored_hash:
        salt, hash_val = stored_hash.split("$", 1)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(key.hex(), hash_val)
    else:
        # Legacy plain SHA-256 fallback
        legacy_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return secrets.compare_digest(legacy_hash, stored_hash)

def init_db():
    """Initialize database and seed the default admin account if empty."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birth_date TEXT,
        gender TEXT,
        class_name TEXT,
        address TEXT,
        parent_name TEXT,
        photo_path TEXT,
        absence_count INTEGER DEFAULT 0
    );
    """)

    # 2. Employees Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        role TEXT NOT NULL,
        hire_date TEXT,
        salary REAL,
        specialty TEXT,
        phone TEXT
    );
    """)

    # 3. Attendance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        attendance_date TEXT NOT NULL,
        status TEXT NOT NULL, -- 'Present' or 'Absent'
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        UNIQUE(student_id, attendance_date)
    );
    """)

    # 4. Admin Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)

    # 5. Classes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)

    # Seed Admin User if not exists
    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        hashed = hash_password("admin")
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", hashed))
        conn.commit()

    # Seed Mock Classes if table is empty
    cursor.execute("SELECT COUNT(*) FROM classes")
    if cursor.fetchone()[0] == 0:
        default_classes = [
            ("1 AS - Science 1",),
            ("1 AS - Science 2",),
            ("1 AS - Lettres 1",),
            ("2 AS - Math",),
            ("2 AS - Sc. Expérim",),
            ("3 AS - Math",),
            ("3 AS - Sc. Expérim",),
            ("3 AS - Ph. Philo",)
        ]
        cursor.executemany("INSERT INTO classes (name) VALUES (?)", default_classes)
        conn.commit()

    # Seed Mock Students if table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        mock_students = [
            ("Amine", "Belkacem", "12/03/2009", "Male", "1 AS - Science 1", "Cité les Mandariniers, Oran", "Moustafa Belkacem", "", 0),
            ("Sarah", "Dahmani", "24/07/2009", "Female", "1 AS - Science 1", "Rue Larbi Ben M'hidi, Oran", "Kader Dahmani", "", 0),
            ("Yacine", "Berrabah", "05/11/2008", "Male", "3 AS - Math", "Cité 1500 Logements, Bir El Djir", "Omar Berrabah", "", 0),
            ("Ines", "Mansouri", "18/01/2009", "Female", "3 AS - Sc. Expérim", "Bvd Front de Mer, Oran", "Fouad Mansouri", "", 0),
            ("Mohamed", "Ziane", "30/09/2008", "Male", "2 AS - Math", "Cité USTO, Oran", "Rachid Ziane", "", 0)
        ]
        cursor.executemany("""
            INSERT INTO students (first_name, last_name, birth_date, gender, class_name, address, parent_name, photo_path, absence_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, mock_students)
        conn.commit()

    # Seed Mock Employees if table is empty
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        mock_employees = [
            ("EMP001", "Kamel", "Benali", "Enseignant", "05/09/2018", 68000.00, "Mathématiques", "0550123456"),
            ("EMP002", "Leila", "Messaoudi", "Enseignant", "10/09/2020", 65000.00, "Langue Française", "0661987654"),
            ("EMP003", "Rachid", "Hammadi", "Directeur", "01/09/2015", 85000.00, "Administration", "0770112233"),
            ("EMP004", "Meriem", "Kacemi", "Enseignant", "12/09/2021", 62000.00, "Langue Anglaise", "0555443322")
        ]
        cursor.executemany("""
            INSERT INTO employees (employee_id, first_name, last_name, role, hire_date, salary, specialty, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, mock_employees)
        conn.commit()

    # Fast lookup indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_id, attendance_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_employees_role ON employees(role);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_employees_employee_id ON employees(employee_id);")

    conn.commit()
    conn.close()

# =====================================================================
# Student Repository Methods
# =====================================================================

def add_student(first_name, last_name, birth_date, gender, class_name, address, parent_name, photo_path=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (first_name, last_name, birth_date, gender, class_name, address, parent_name, photo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, birth_date, gender, class_name, address, parent_name, photo_path))
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return student_id

def update_student(id, first_name, last_name, birth_date, gender, class_name, address, parent_name, photo_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    if photo_path is not None:
        cursor.execute("""
            UPDATE students 
            SET first_name=?, last_name=?, birth_date=?, gender=?, class_name=?, address=?, parent_name=?, photo_path=?
            WHERE id=?
        """, (first_name, last_name, birth_date, gender, class_name, address, parent_name, photo_path, id))
    else:
        cursor.execute("""
            UPDATE students 
            SET first_name=?, last_name=?, birth_date=?, gender=?, class_name=?, address=?, parent_name=?
            WHERE id=?
        """, (first_name, last_name, birth_date, gender, class_name, address, parent_name, id))
    conn.commit()
    conn.close()

def delete_student(id):
    conn = get_connection()
    cursor = conn.cursor()
    # Delete student (foreign key delete cascade handles attendance)
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def get_students(search_query="", class_filter="", gender_filter=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM students WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (first_name LIKE ? OR last_name LIKE ? OR parent_name LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])
        
    if class_filter:
        query += " AND class_name = ?"
        params.append(class_filter)
        
    if gender_filter:
        query += " AND gender = ?"
        params.append(gender_filter)
        
    query += " ORDER BY last_name ASC, first_name ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_student_by_id(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# =====================================================================
# Employee Repository Methods
# =====================================================================

def add_employee(employee_id, first_name, last_name, role, hire_date, salary, specialty, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (employee_id, first_name, last_name, role, hire_date, salary, specialty, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (employee_id, first_name, last_name, role, hire_date, salary, specialty, phone))
    emp_db_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return emp_db_id

def update_employee(id, employee_id, first_name, last_name, role, hire_date, salary, specialty, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees 
        SET employee_id=?, first_name=?, last_name=?, role=?, hire_date=?, salary=?, specialty=?, phone=?
        WHERE id=?
    """, (employee_id, first_name, last_name, role, hire_date, salary, specialty, phone, id))
    conn.commit()
    conn.close()

def delete_employee(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def get_employees(search_query="", role_filter="", specialty_filter=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM employees WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (first_name LIKE ? OR last_name LIKE ? OR employee_id LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term])
        
    if role_filter:
        query += " AND role = ?"
        params.append(role_filter)
        
    if specialty_filter:
        query += " AND specialty = ?"
        params.append(specialty_filter)
        
    query += " ORDER BY last_name ASC, first_name ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_employee_by_id(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_employee_by_employee_id(employee_id):
    """Retrieve employee by public employee ID string (e.g. EMP001)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def is_employee_id_exists(employee_id, exclude_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if exclude_id:
        cursor.execute("SELECT COUNT(*) FROM employees WHERE employee_id = ? AND id != ?", (employee_id, exclude_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM employees WHERE employee_id = ?", (employee_id,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists

# =====================================================================
# Attendance Repository Methods
# =====================================================================

def recalculate_student_absences(student_id):
    """Helper method to count a student's total absences and update their record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND status = 'Absent'", (student_id,))
    count = cursor.fetchone()[0]
    cursor.execute("UPDATE students SET absence_count = ? WHERE id = ?", (count, student_id))
    conn.commit()
    conn.close()

def save_attendance(student_id, attendance_date, status):
    """Insert or replace attendance status for a student on a specific date and recalculate total absences."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (student_id, attendance_date, status)
        VALUES (?, ?, ?)
        ON CONFLICT(student_id, attendance_date) DO UPDATE SET status=excluded.status
    """, (student_id, attendance_date, status))
    conn.commit()
    conn.close()
    
    # Update cumulative student count
    recalculate_student_absences(student_id)

def save_attendance_batch(records):
    """
    Atomically insert/update multiple attendance records in a single transaction
    and recalculate absence counts for all affected students.
    records: list of tuples (student_id, attendance_date, status)
    """
    if not records:
        return
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany("""
            INSERT INTO attendance (student_id, attendance_date, status)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, attendance_date) DO UPDATE SET status=excluded.status
        """, records)
        
        affected_students = list({r[0] for r in records})
        for sid in affected_students:
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND status = 'Absent'", (sid,))
            count = cursor.fetchone()[0]
            cursor.execute("UPDATE students SET absence_count = ? WHERE id = ?", (count, sid))
        conn.commit()
        return len(records)
    finally:
        conn.close()

def get_attendance_for_date_and_class(date_str, class_name):
    """Get all students in a class, joined with their attendance status on date_str."""
    conn = get_connection()
    cursor = conn.cursor()
    # Pull all students in this class, and do a LEFT JOIN on attendance records for that day.
    cursor.execute("""
        SELECT s.id as student_id, s.first_name, s.last_name, s.class_name, a.status 
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND a.attendance_date = ?
        WHERE s.class_name = ?
        ORDER BY s.last_name ASC, s.first_name ASC
    """, (date_str, class_name))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def _to_iso_date(d_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD for accurate SQL string comparison."""
    if not d_str:
        return ""
    d_str = d_str.strip()
    if "/" in d_str:
        parts = d_str.split("/")
        if len(parts) == 3:
            return f"{parts[2].zfill(4)}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return d_str

def get_attendance_history(class_name=None, date_from=None, date_to=None):
    """Fetch attendance list history logs, with optional class and date range filters."""
    conn = get_connection()
    cursor = conn.cursor()
    
    date_expr = """CASE 
        WHEN a.attendance_date LIKE '__/__/____' 
        THEN substr(a.attendance_date, 7, 4) || '-' || substr(a.attendance_date, 4, 2) || '-' || substr(a.attendance_date, 1, 2)
        ELSE a.attendance_date 
    END"""
    
    query = f"""
        SELECT a.id, a.attendance_date, a.status, s.id as student_id, s.first_name, s.last_name, s.class_name
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE 1=1
    """
    params = []
    
    if class_name:
        query += " AND s.class_name = ?"
        params.append(class_name)
    if date_from:
        iso_from = _to_iso_date(date_from)
        query += f" AND {date_expr} >= ?"
        params.append(iso_from)
    if date_to:
        iso_to = _to_iso_date(date_to)
        query += f" AND {date_expr} <= ?"
        params.append(iso_to)
        
    query += f" ORDER BY {date_expr} DESC, s.last_name ASC, s.first_name ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# =====================================================================
# Admin & Auth Methods
# =====================================================================

def verify_admin(username, raw_password):
    """Check admin username and password match, auto-upgrading legacy SHA-256 hashes to PBKDF2."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM admin WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
        
    stored_hash = row['password']
    is_valid = verify_password(stored_hash, raw_password)
    
    # Auto-upgrade legacy hash on successful authentication
    if is_valid and "$" not in stored_hash:
        new_hash = hash_password(raw_password)
        cursor.execute("UPDATE admin SET password = ? WHERE id = ?", (new_hash, row['id']))
        conn.commit()
        
    conn.close()
    return is_valid

def change_admin_password(username, old_password, new_password):
    """Safely update admin password after verifying the old password."""
    if not verify_admin(username, old_password):
        return False
    conn = get_connection()
    cursor = conn.cursor()
    new_hash = hash_password(new_password)
    cursor.execute("UPDATE admin SET password = ? WHERE username = ?", (new_hash, username))
    conn.commit()
    conn.close()
    return True

# =====================================================================
# Dashboard statistics
# =====================================================================

def get_dashboard_stats():
    """Retrieve aggregate numbers for the dashboard cards."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    
    # 2. Total Employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]
    
    # 3. Total Classes (count in classes table)
    cursor.execute("SELECT COUNT(*) FROM classes")
    total_classes = cursor.fetchone()[0]
    
    # 4. Cumulative Absences (all absence markers in db)
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE status = 'Absent'")
    total_absences = cursor.fetchone()[0]
    
    conn.close()
    return {
        "students": total_students,
        "employees": total_employees,
        "classes": total_classes,
        "absences": total_absences
    }

# =====================================================================
# Classes Repository Methods
# =====================================================================

def get_classes():
    """Fetch all classes sorted alphabetically."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classes ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_class(name):
    """Insert a new class into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO classes (name) VALUES (?)", (name,))
    class_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return class_id

def update_class(class_id, new_name):
    """Update class name and synchronize all students using the old name."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get the old name first
    cursor.execute("SELECT name FROM classes WHERE id = ?", (class_id,))
    row = cursor.fetchone()
    if row:
        old_name = row['name']
        # Update classes table
        cursor.execute("UPDATE classes SET name = ? WHERE id = ?", (new_name, class_id))
        # Sync students table (to keep string representation in sync)
        cursor.execute("UPDATE students SET class_name = ? WHERE class_name = ?", (new_name, old_name))
        conn.commit()
        
    conn.close()

def delete_class(class_id):
    """Delete a class and clear class field for all affected students."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get class name first
    cursor.execute("SELECT name FROM classes WHERE id = ?", (class_id,))
    row = cursor.fetchone()
    if row:
        class_name = row['name']
        # Delete class
        cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
        # Set students' class field in this class to blank
        cursor.execute("UPDATE students SET class_name = '' WHERE class_name = ?", (class_name,))
        conn.commit()
        
    conn.close()

def is_class_name_exists(name, exclude_id=None):
    """Check if a class name already exists, optionally excluding a specific class ID."""
    conn = get_connection()
    cursor = conn.cursor()
    if exclude_id:
        cursor.execute("SELECT COUNT(*) FROM classes WHERE name = ? AND id != ?", (name, exclude_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM classes WHERE name = ?", (name,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists
