"""
tests/conftest.py
Shared fixtures for CompanyPrep AI test suite.
"""
import sys
import os
import sqlite3
import tempfile
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Monkeypatch DEMO_MODE to True for all tests
os.environ.setdefault("AI_PROVIDER", "gemini")
os.environ.setdefault("GEMINI_API_KEY", "")  # Ensure demo mode


@pytest.fixture
def sample_onboarding_data():
    return {
        "company": "Infosys",
        "job_role": "System Engineer",
        "skills": ["Python", "SQL", "OOP"],
        "experience_level": "Beginner",
        "weekly_hours": 10,
        "duration_weeks": 8,
    }


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Create a fresh temporary SQLite database for tests."""
    db_file = str(tmp_path / "test_companyprep.db")
    monkeypatch.setattr("database.db_manager.DB_PATH", db_file)
    from database import db_manager
    db_manager.DB_PATH = db_file
    import importlib
    importlib.reload(db_manager)
    db_manager.init_db()
    return db_file


@pytest.fixture
def mock_demo_mode(monkeypatch):
    """Force demo mode (no AI calls)."""
    monkeypatch.setattr("backend.config.DEMO_MODE", True)
    monkeypatch.setattr("backend.services.llm_service.DEMO_MODE", True)
    return True
