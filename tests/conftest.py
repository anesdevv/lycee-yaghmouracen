import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest
import database.db as db

@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, tmp_path):
    """
    Ensure every test operates on an isolated, temporary SQLite database,
    protecting production/demo school.db from test pollution.
    """
    temp_db = str(tmp_path / "test_school.db")
    monkeypatch.setattr(db, "DB_PATH", temp_db)
    db.init_db()
    return temp_db
