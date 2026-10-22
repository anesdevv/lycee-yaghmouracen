# Lycée Yaghmouracen: High School Management System
*Système de gestion administrative scolaire*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20%28Qt6%29-brightgreen.svg)](https://wiki.qt.io/Qt_for_Python)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-success.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An offline desktop application for administrative management at Lycée Yaghmouracen in Algeria. Built with Python, PySide6 (Qt 6), and SQLite, it runs locally without internet access and provides workflows for managing students, faculty, staff, and attendance.

---

## Features

- Administrative dashboard: summary metrics for enrolled students, active faculty and staff, class sections, cumulative absences, gender ratios, and class distributions
- Student records: registration, profile updates, photo upload, section assignments, contact details, and printable student summary dossiers
- Staff administration: records for teachers, administrative agents, and school monitors with specialty, role, salary, and phone tracking, including work certificates (Attestation de Travail)
- Attendance tracking: daily classroom roll call with batch saving, automatic absence counter synchronization, and date filtering
- PDF reports: class rosters, employee directories, periodic attendance sheets, student cards, and official certificates using ReportLab with Algerian educational header templates
- Excel exports: `.xlsx` exports with formatted headers using Pandas and OpenPyXL for records and ministry submissions
- Authentication and security: PBKDF2 password hashing (100,000 iterations), legacy hash migration, SQLite foreign keys with cascading deletions, and indexed queries
- Bilingual interface: language toggle between French and English

---

## Tech stack and architecture

| Layer | Component | Description |
|---|---|---|
| GUI Framework | [PySide6 (Qt 6)](https://wiki.qt.io/Qt_for_Python) | Desktop interface with dark and light QSS stylesheets |
| Database | [SQLite3](https://www.sqlite.org/) | Embedded relational engine with foreign keys enabled |
| PDF Engine | [ReportLab](https://www.reportlab.com/) | Programmatic document generation and vector layout |
| Spreadsheets | [Pandas](https://pandas.pydata.org/) & [OpenPyXL](https://openpyxl.readthedocs.io/) | Dataframe transformation and `.xlsx` workbooks |
| Image Processing | [Pillow (PIL)](https://python-pillow.org/) | Student photo handling and resizing |
| Testing | [Pytest](https://docs.pytest.org/) | Automated unit and integration test suite |

### Repository structure

```text
├── assets/                     # Application logos, branding, and UI icons
├── database/                   # Database access layer and schema definitions
│   ├── db.py                   # SQLite repository, connection pooling, and migrations
│   └── school.db               # Embedded database pre-seeded with demo records
├── exports/                    # Target directory for generated PDFs and Excel spreadsheets
├── services/                   # Business logic and export generators
│   ├── auth_service.py         # Session management and authentication
│   ├── excel_service.py        # Styled Excel workbook export routines
│   └── pdf_service.py          # ReportLab official document flowables
├── tests/                      # Automated test suite
│   ├── conftest.py             # Isolated in-memory/temp database fixtures
│   ├── test_database.py        # Database CRUD, auth, and query tests
│   └── test_services.py        # Export generation and service verification tests
├── ui/                         # PySide6 graphical user interface modules
│   ├── attendance.py           # Daily roll call and absence logs
│   ├── components.py           # Reusable UI widgets (cards, badges, modals, tables)
│   ├── dashboard.py            # Overview statistics and analytical charts
│   ├── employees.py            # Staff directory and registration modals
│   ├── exports.py              # Export center for document generation
│   ├── main_window.py          # Application frame, navigation sidebar, and header
│   └── students.py             # Student roster, profile editor, and search filters
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore rules for Python, Qt, and local data
├── LICENSE                     # MIT Open Source License
├── main.py                     # Application entry point and splash screen
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Locked project dependencies
└── verify_services.py          # End-to-end integration verification script
```

---

## Prerequisites

- Python: version 3.10 or higher
- Operating System: Windows 10/11, Linux, or macOS

---

## Installation and quick start

### 1. Clone the repository

```bash
git clone https://github.com/anesdevv/lycee-yaghmouracen.git
cd lycee-yaghmouracen
```

### 2. Create and activate a virtual environment

```powershell
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

### 5. Default admin credentials

When launching the application for the first time, log in using the initial administrator account:
- Username: `admin`
- Password: `admin`

The password can be updated directly within the application or via `db.change_admin_password()`.

---

## Running automated tests

Run the test suite to verify database operations, authentication, and document exports:

```bash
# Run all unit and integration tests
pytest -v

# Run the end-to-end verification script
python verify_services.py
```

---

## Configuration

Optional environment configurations can be set via a `.env` file in the root directory (see [`.env.example`](.env.example)):

```ini
APP_ENV=development
APP_LANG=fr
DB_PATH=database/school.db
EXPORTS_DIR=exports
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASS=admin
```

---

## Contributing

Contributions, bug reports, and suggestions are welcome:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m "feat: add new feature"`
4. Run tests: `pytest -v`
5. Push to your branch: `git push origin feature/new-feature`
6. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
