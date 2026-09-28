# High School Management System — PRD

## Summary

A Windows desktop application for Algerian high schools built with Python, PySide6, and SQLite.

The system allows a school administrator to manage:
- students
- employees
- student attendance
- printable PDF documents
- Excel exports
- dashboard statistics

The application is designed to be simple, modern, fast, and suitable as a school project while still looking professional.

---

# 1. Goals

## Main Goal

Create a centralized desktop system for managing high school administrative data.

## Project Goals

- Simple and clean UI
- Fast local database
- Easy navigation
- Professional administration workflows
- Offline support
- Exportable reports
- Easy to present during school defense/demo

---

# 2. Technical Stack

| Layer | Technology |
|---|---|
| Language | Python |
| GUI Framework | PySide6 |
| Database | SQLite |
| PDF Export | ReportLab |
| Excel Export | Pandas + OpenPyXL |
| ORM/DB Access | sqlite3 |
| Images | Pillow |

---

# 3. System Architecture

## Application Type

Desktop application for Windows only.

## Architecture Style

Simple modular architecture:

- UI Layer
- Business Logic Layer
- Database Layer

## Folder Structure

```text
project/
│
├── main.py
├── database/
│   ├── db.py
│   └── school.db
│
├── ui/
│   ├── dashboard/
│   ├── students/
│   ├── employees/
│   ├── attendance/
│   └── components/
│
├── services/
│   ├── pdf_service.py
│   ├── excel_service.py
│   └── auth_service.py
│
├── assets/
│   ├── icons/
│   └── images/
│
└── exports/
```

---

# 4. Authentication

## Admin Login

Single admin account only.

## Login Fields

- Username
- Password

## Features

- Simple login window
- Password hidden
- Logout button

---

# 5. Dashboard Module

## Purpose

Provide a quick overview of school data.

## Dashboard Widgets

- High school name (large title)
- Total students
- Total employees
- Total classes
- Current date
- Current time

---

# 6. Student Management Module

## Purpose

Manage all student records.

## Student Fields

| Field | Type |
|---|---|
| ID | Integer |
| First Name | Text |
| Last Name | Text |
| Birth Date | Date |
| Gender | Text |
| Class | Text |
| Address | Text |
| Parent Name | Text |
| Photo | Image (optional) |
| Absence Count | Integer |

## Features

### Add Student
Admin can create a new student record.

### Edit Student
Modify existing student information.

### Delete Student
Remove student from database.

### Search Students
Search by:
- name
- class

### Filter Students
Filter by:
- class
- gender

### Student Table

Display:
- photo
- full name
- class
- absence count

### Student Profile Page

Detailed student information page.

---

# 7. Attendance Module

## Purpose

Track student absences.

## Features

### Mark Attendance

Admin can:
- mark absent
- mark present

### Attendance Fields

| Field | Type |
|---|---|
| Attendance ID | Integer |
| Student ID | Foreign Key |
| Date | Date |
| Status | Present/Absent |

### Attendance Actions

- view attendance history
- filter by class
- filter by date

### Automatic Absence Count

System automatically updates student absence count.

---

# 8. Employee Management Module

## Purpose

Manage school employees and teachers.

## Employee Fields

| Field | Type |
|---|---|
| Employee ID | Text |
| First Name | Text |
| Last Name | Text |
| Role/Job | Text |
| Hire Date | Date |
| Salary | Real |
| Specialty/Subject | Text |
| Phone | Text |

## Features

### Add Employee

Create employee record.

### Edit Employee

Update employee information.

### Delete Employee

Remove employee.

### Search Employees

Search by:
- name
- role
- subject

### Employee Profile

Detailed employee information page.

---

# 9. PDF Export Module

## Purpose

Generate printable documents.

## Supported Documents

### Students
- Student list
- Attendance report
- Student information sheet

### Employees
- Employee information card
- Employee list
- Work certificate

## PDF Features

- School header
- School name
- Date
- Clean table formatting
- Export to local folder

---

# 10. Excel Export Module

## Purpose

Export tables into Excel files.

## Exportable Data

- students
- employees
- attendance

## Features

- One-click export
- XLSX format
- Auto column sizing

---

# 11. Database Design

## Tables

### students

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    birth_date TEXT,
    gender TEXT,
    class_name TEXT,
    address TEXT,
    parent_name TEXT,
    photo_path TEXT,
    absence_count INTEGER DEFAULT 0
);
```

### employees

```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT,
    first_name TEXT,
    last_name TEXT,
    role TEXT,
    hire_date TEXT,
    salary REAL,
    specialty TEXT,
    phone TEXT
);
```

### attendance

```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    attendance_date TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
);
```

### admin

```sql
CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
);
```

---

# 12. UI Design

## Style Direction

Modern administrative interface inspired by:
- Algerian education portals
- blue/white color palette
- sidebar navigation

## Main Layout

### Sidebar
- Dashboard
- Students
- Attendance
- Employees
- Exports
- Logout

### Main Content Area
Dynamic pages/tables/forms.

## Tables

All tables should support:
- search
- sorting
- filtering

---

# 13. Validation Rules

## Students

- required first/last name
- valid class required

## Employees

- unique employee ID
- valid phone number

## Attendance

- prevent duplicate attendance for same date

---

# 14. MVP Priority

## Phase 1
- login
- dashboard
- SQLite connection
- sidebar navigation

## Phase 2
- student CRUD
- employee CRUD

## Phase 3
- attendance system

## Phase 4
- PDF export
- Excel export

## Phase 5
- UI polishing
- icons
- animations

---

# 15. Future Improvements

Not required for MVP.

- multiple admin accounts
- grades management
- parent accounts
- SMS/email notifications
- cloud backup
- timetable management
- biometric attendance
- dark mode

---

# 16. Success Criteria

The project is successful if:
- admin can manage students and employees
- attendance works correctly
- exports generate successfully
- UI feels modern and responsive
- database persists correctly
- app works offline on Windows
