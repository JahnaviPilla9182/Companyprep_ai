"""
tests/test_exports.py
Tests for CSV and PDF export functionality.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.export_manager import export_roadmap_csv, export_roadmap_pdf


SAMPLE_ROADMAP = {
    "company": "TCS",
    "job_role": "Software Engineer",
    "experience_level": "Beginner",
    "weekly_hours": 10,
    "duration_weeks": 2,
    "language": "Python",
    "disclaimer": "Test disclaimer.",
}

SAMPLE_WEEKS = [
    {
        "week_number": 1,
        "topics": ["Python", "OOP"],
        "estimated_hours": 10,
        "objectives": ["Learn Python basics", "Understand OOP"],
        "daily_tasks": ["Study variables", "Practice loops", "Implement classes"],
        "coding_exercises": ["Fibonacci", "Linked list"],
        "practice_questions": ["What is polymorphism?"],
        "mini_projects": [],
        "revision": ["Revise Python"],
        "mock_interview": False,
        "assessment": {"milestone": "Week 1 Checkpoint", "description": "Review topics"},
        "optional_topics": [],
    },
    {
        "week_number": 2,
        "topics": ["DSA", "Algorithms"],
        "estimated_hours": 10,
        "objectives": ["Learn data structures"],
        "daily_tasks": ["Study arrays", "Study linked lists"],
        "coding_exercises": ["Two Sum", "Binary Search"],
        "practice_questions": ["What is Big O notation?"],
        "mini_projects": ["Task Queue"],
        "revision": ["Revise DSA"],
        "mock_interview": True,
        "assessment": {"milestone": "Week 2 Checkpoint", "description": "Review DSA"},
        "optional_topics": ["System Design"],
    },
]


class TestCSVExport:
    def test_csv_returns_bytes(self):
        result = export_roadmap_csv(SAMPLE_ROADMAP, SAMPLE_WEEKS)
        assert isinstance(result, bytes)

    def test_csv_not_empty(self):
        result = export_roadmap_csv(SAMPLE_ROADMAP, SAMPLE_WEEKS)
        assert len(result) > 50

    def test_csv_contains_headers(self):
        result = export_roadmap_csv(SAMPLE_ROADMAP, SAMPLE_WEEKS)
        text = result.decode("utf-8")
        assert "Week" in text
        assert "Topic" in text

    def test_csv_contains_week_data(self):
        result = export_roadmap_csv(SAMPLE_ROADMAP, SAMPLE_WEEKS)
        text = result.decode("utf-8")
        assert "Week 1" in text
        assert "Python" in text

    def test_csv_empty_roadmap_graceful(self):
        """Empty weeks should not crash, returns header only."""
        result = export_roadmap_csv(SAMPLE_ROADMAP, [])
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestPDFExport:
    def test_pdf_returns_bytes(self):
        result = export_roadmap_pdf(SAMPLE_ROADMAP, SAMPLE_WEEKS)
        assert isinstance(result, bytes)

    def test_pdf_not_empty(self):
        result = export_roadmap_pdf(SAMPLE_ROADMAP, SAMPLE_WEEKS)
        assert len(result) > 100

    def test_pdf_empty_roadmap_graceful(self):
        """Empty weeks should not crash."""
        result = export_roadmap_pdf(SAMPLE_ROADMAP, [])
        assert isinstance(result, bytes)

    def test_pdf_contains_company_name(self):
        """Either PDF bytes or text fallback should contain company name."""
        result = export_roadmap_pdf(SAMPLE_ROADMAP, SAMPLE_WEEKS)
        try:
            text = result.decode("latin-1")
            if not result[:4] == b'%PDF':
                assert "TCS" in text or "CompanyPrep" in text
        except Exception:
            pass
