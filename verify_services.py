import os
import sys

# Add workspace folder to Python path dynamically
workspace_dir = os.path.dirname(os.path.abspath(__file__))
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

import database.db as db
import services.excel_service as excel_service
import services.pdf_service as pdf_service

def verify():
    print("--- 1. Initializing Database ---")
    db.init_db()
    print("Database Initialized successfully.")
    
    print("\n--- 2. Checking Seed Data ---")
    students = db.get_students()
    employees = db.get_employees()
    print(f"Total Enrolled Students: {len(students)}")
    print(f"Total Enrolled Staff: {len(employees)}")
    assert len(students) > 0, "No students seeded!"
    assert len(employees) > 0, "No employees seeded!"
    
    print("\n--- 3. Testing Attendance System ---")
    today = "26/05/2026"
    yesterday = "25/05/2026"
    
    # Use an isolated test student to avoid mutating existing records
    test_sid = db.add_student("TestRunner", "Verification", "01/01/2010", "Male", "1 AS - Science 1", "Temp Address", "Temp Parent", "")
    try:
        print(f"Marking test student (ID {test_sid}) absent for {today} and {yesterday}...")
        db.save_attendance(test_sid, today, "Absent")
        db.save_attendance(test_sid, yesterday, "Absent")
        
        s_updated = db.get_student_by_id(test_sid)
        print(f"Absence count after marking: {s_updated['absence_count']}")
        assert s_updated['absence_count'] == 2, "Absence count recalculation sync mismatch!"
        
        # Mark present for today
        print("Toggling today's attendance to Present...")
        db.save_attendance(test_sid, today, "Present")
        s_updated = db.get_student_by_id(test_sid)
        print(f"Absence count after toggling to Present: {s_updated['absence_count']}")
        assert s_updated['absence_count'] == 1, "Absence count recalculation toggle mismatch!"
    finally:
        db.delete_student(test_sid)
        print("Cleaned up temporary verification student record.")
    
    sid = students[0]['id']
    
    print("\n--- 4. Testing Excel Export Service ---")
    excel_stud = excel_service.export_students_to_excel(lang="fr")
    excel_emp = excel_service.export_employees_to_excel(lang="en")
    excel_att = excel_service.export_attendance_to_excel(lang="fr")
    
    print(f"Excel Students exported to: {excel_stud}")
    print(f"Excel Employees exported to: {excel_emp}")
    print(f"Excel Attendance exported to: {excel_att}")
    
    assert os.path.exists(excel_stud), "Excel Students file not found!"
    assert os.path.exists(excel_emp), "Excel Employees file not found!"
    assert os.path.exists(excel_att), "Excel Attendance file not found!"
    
    print("\n--- 5. Testing PDF Report Generation Service ---")
    pdf_stud_list = pdf_service.generate_student_list_pdf(class_filter=None, lang="fr")
    pdf_emp_list = pdf_service.generate_employee_list_pdf(lang="en")
    pdf_att_report = pdf_service.generate_attendance_report_pdf(class_name="1 AS - Science 1", lang="fr")
    pdf_stud_sheet = pdf_service.generate_student_info_sheet_pdf(student_id=sid, lang="fr")
    pdf_emp_sheet = pdf_service.generate_employee_info_sheet_pdf(employee_db_id=employees[0]['id'], lang="en")
    pdf_cert = pdf_service.generate_work_certificate_pdf(employee_db_id=employees[0]['id'])
    
    print(f"PDF Student List: {pdf_stud_list}")
    print(f"PDF Employee List: {pdf_emp_list}")
    print(f"PDF Attendance Report: {pdf_att_report}")
    print(f"PDF Student Sheet: {pdf_stud_sheet}")
    print(f"PDF Employee Sheet: {pdf_emp_sheet}")
    print(f"PDF Work Certificate: {pdf_cert}")
    
    assert os.path.exists(pdf_stud_list), "PDF Student List file not found!"
    assert os.path.exists(pdf_emp_list), "PDF Employee List file not found!"
    assert os.path.exists(pdf_att_report), "PDF Attendance Report file not found!"
    assert os.path.exists(pdf_stud_sheet), "PDF Student Sheet file not found!"
    assert os.path.exists(pdf_emp_sheet), "PDF Employee Sheet file not found!"
    assert os.path.exists(pdf_cert), "PDF Work Certificate file not found!"
    
    print("\n==========================================")
    print("ALL SERVICES INTEGRATION CHECKS SUCCESSFUL!")
    print("==========================================")

if __name__ == "__main__":
    verify()
