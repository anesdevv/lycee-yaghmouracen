# Lycée Yaghmouracen — High School Management System
*Système de Gestion Administrative Scolaire*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20%28Qt6%29-brightgreen.svg)](https://wiki.qt.io/Qt_for_Python)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-success.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A lightweight, modern, and high-performance desktop application designed for Algerian high school administrative management (*Lycée Yaghmouracen*). Built with **Python**, **PySide6 (Qt 6)**, and **SQLite**, it operates 100% offline, starts instantly, and provides streamlined workflows for managing students, faculty, staff, and attendance records.

---

## Key Features

- **Executive Dashboard**: Real-time KPI summary cards (total enrolled students, active faculty/staff, registered class sections, cumulative absences), gender ratio breakdowns, and class distributions.
- **Student Information Management**: Complete student lifecycle tracking (registration, profile editing, photo upload, section assignments, contact info, and individual student printable summary dossiers).
- **Staff & Faculty Administration**: Manage teachers, administrative agents, and school monitors with specialty, role, salary, and phone tracking. Generates official **Work Certificates** (*Attestation de Travail*).
- **Attendance & Absence System**: Fast, responsive daily classroom attendance switcher with **atomic batch saving**, automated absence counter synchronization, and chronological date filtering.
- **Official PDF Report Engine**: Automated generation of publication-ready, branded PDF reports using ReportLab (class rosters, employee directories, periodic attendance sheets, student cards, and official certificates) with Algerian educational header templates.
- **Excel Data Export**: Instant `.xlsx` exports with formatted header bands and auto-adjusted columns using Pandas and OpenPyXL for external record keeping and ministry submissions.
- **Security & Speed**: Cryptographically secure **PBKDF2 salted password hashing** (100,000 iterations), automatic legacy hash migration, SQLite foreign keys with cascading deletions, and indexed queries for sub-millisecond local execution.
- **Bilingual Interface**: Seamless runtime language switching between **French** (*Français*) and **English**.

---

## Technical Stack & Architecture

| Layer | Component | Description |
|---|---|---|
| **GUI Framework** | [PySide6 (Qt 6)](https://wiki.qt.io/Qt_for_Python) | Modern desktop interface with custom dark/light QSS stylesheets |
| **Persistence** | [SQLite3](https://www.sqlite.org/) | Embedded zero-latency relational engine with enforced foreign keys |
| **PDF Engine** | [ReportLab](https://www.reportlab.com/) | Programmatic document layout and vector typography |
| **Spreadsheets** | [Pandas](https://pandas.pydata.org/) & [OpenPyXL](https://openpyxl.readthedocs.io/) | Dataframe transformation and styled `.xlsx` workbooks |
| **Image Processing**| [Pillow (PIL)](https://python-pillow.org/) | Student identification photo handling and rendering |
| **Testing** | [Pytest](https://docs.pytest.org/) | Automated unit and integration test suite |

### Repository Structure

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

- **Python**: Version `3.10` or higher (tested up to Python `3.14`).
- **Operating System**: Windows 10 / Windows 11 (Cross-platform compatible with Linux / macOS).

---

## Installation & Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/lycee-yaghmouracen.git
cd lycee-yaghmouracen
```

### 2. Create and Activate a Virtual Environment
```powershell
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

### 5. Default Admin Credentials
When launching the application for the first time, log in using the pre-configured administrator account:
- **Username**: `admin`
- **Password**: `admin`

> *Note: The password can be updated at any time directly through the application or using `db.change_admin_password()`.*

---

## Running Automated Tests

Run the test suite to verify database operations, encryption, and document generation:

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

Contributions, feature suggestions, and bug reports are welcome:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m "feat: add new feature"`
4. Run tests: `pytest -v`
5. Push to your branch: `git push origin feature/new-feature`
6. Open a Pull Request.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
