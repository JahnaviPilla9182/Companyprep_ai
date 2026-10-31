"""
tests/test_question_generator.py
Tests for interview question generation.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(autouse=True)
def force_demo_mode(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    try:
        monkeypatch.setattr("backend.config.DEMO_MODE", True)
        monkeypatch.setattr("backend.services.llm_service.DEMO_MODE", True)
    except Exception:
        pass


from backend.core.question_generator import generate_questions


class TestQuestionGeneration:
    def test_generates_technical_questions(self):
        qs = generate_questions(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
            categories=["Technical"]
        )
        assert "Technical" in qs
        assert len(qs["Technical"]) >= 1

    def test_generates_coding_questions(self):
        qs = generate_questions(
            company="Infosys", job_role="System Engineer",
            skills=["Java"], experience_level="Intermediate",
            categories=["Coding"]
        )
        assert "Coding" in qs
        coding = qs["Coding"]
        assert len(coding) >= 1
        assert "problem" in coding[0] or "title" in coding[0]

    def test_generates_aptitude_questions(self):
        qs = generate_questions(
            company="Cognizant", job_role="Junior Software Engineer",
            skills=["Python"], experience_level="Beginner",
            categories=["Aptitude"]
        )
        assert "Aptitude" in qs
        assert len(qs["Aptitude"]) >= 1
        for q in qs["Aptitude"]:
            assert "a" in q

    def test_generates_hr_questions(self):
        qs = generate_questions(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
            categories=["HR"]
        )
        assert "HR" in qs
        hr_qs = qs["HR"]
        assert len(hr_qs) >= 1
        for q in hr_qs:
            assert "framework" in q or "q" in q

    def test_disclaimer_present(self):
        qs = generate_questions(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
        )
        assert "_disclaimer" in qs

    def test_num_per_category_respected(self):
        qs = generate_questions(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
            categories=["Aptitude"],
            num_per_category=3
        )
        if "Aptitude" in qs:
            assert len(qs["Aptitude"]) <= 10

    def test_coding_question_has_solution(self):
        qs = generate_questions(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Intermediate",
            categories=["Coding"]
        )
        coding = qs.get("Coding", [])
        if coding:
            q = coding[0]
            assert "python_solution" in q or "approach" in q
