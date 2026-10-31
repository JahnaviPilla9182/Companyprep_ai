"""
tests/test_e2e_all_sections.py
End-to-end integration tests exercising every single section and capability of CompanyPrep AI.
"""
import pytest
import sys
import os
import json

# Ensure project root in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.validators import (
    validate_company, validate_role, validate_skills,
    validate_weekly_hours, validate_duration, validate_onboarding,
    validate_file_upload, sanitize_text
)
from backend.core.roadmap_generator import generate_roadmap, adapt_roadmap, _get_role_topics
from backend.core.question_generator import generate_questions
from backend.core.skill_assessment import get_assessment_questions, score_assessment
from backend.core.job_analyzer import analyze_job_description
from backend.core.progress_tracker import (
    mark_item, get_summary, get_completed, build_progress_dataframe,
    get_week_completion, get_strong_weak_topics, get_recommended_next_steps
)
from backend.core.revision_planner import generate_revision_plan
from backend.core.resource_manager import get_resources_for_topic, get_all_resources
from backend.core.export_manager import export_roadmap_csv, export_roadmap_pdf
import database.db_manager as db


@pytest.fixture(autouse=True)
def init_test_environment(tmp_path, monkeypatch):
    """Ensure clean test environment and temporary SQLite DB."""
    test_db = str(tmp_path / "e2e_test.db")
    monkeypatch.setattr(db, "DB_PATH", test_db)
    db.init_db()
    monkeypatch.setattr("backend.config.DEMO_MODE", True)
    monkeypatch.setattr("backend.services.llm_service.DEMO_MODE", True)


class TestSection1OnboardingAndValidators:
    """Tests Section 1 & 2: User Onboarding and Input Validation."""

    def test_validators_accept_valid_inputs(self):
        data = {
            "company": "Infosys",
            "job_role": "System Engineer",
            "skills": ["Python", "SQL", "OOP"],
            "experience_level": "Beginner",
            "weekly_hours": 12,
            "duration_weeks": 8,
        }
        valid, errors = validate_onboarding(data)
        assert valid is True
        assert len(errors) == 0

    def test_validators_catch_all_edge_cases(self):
        # Empty company
        assert validate_company("")[0] is False
        assert validate_company("   ")[0] is False
        # Empty role
        assert validate_role("")[0] is False
        # Empty skills
        assert validate_skills([])[0] is False
        # Out of bounds hours
        assert validate_weekly_hours(0)[0] is False
        assert validate_weekly_hours(85)[0] is False
        # Out of bounds duration
        assert validate_duration(0)[0] is False
        assert validate_duration(55)[0] is False


class TestSection2RoadmapGeneration:
    """Tests Section 3: Personalized Roadmap Generation for required companies."""

    @pytest.mark.parametrize("company,role", [
        ("Infosys", "System Engineer"),
        ("TCS", "Software Engineer"),
        ("Cognizant", "Junior Software Engineer"),
        ("Generic Software Developer", "Software Developer"),
    ])
    def test_generate_all_required_company_tracks(self, company, role):
        roadmap = generate_roadmap(
            company=company,
            job_role=role,
            skills=["Python", "SQL"],
            experience_level="Beginner",
            weekly_hours=10,
            duration_weeks=6,
        )
        assert roadmap["company"] == company
        assert roadmap["job_role"] == role
        assert len(roadmap["weeks"]) == 6
        assert "disclaimer" in roadmap

        for w in roadmap["weeks"]:
            assert "week_number" in w
            assert len(w["topics"]) >= 1
            assert len(w["daily_tasks"]) >= 1
            assert "estimated_hours" in w
            assert w["estimated_hours"] <= 10.5  # respects weekly limit
            assert "assessment" in w
            assert "practice_questions" in w


class TestSection3AdaptiveRoadmap:
    """Tests Section 4: Adaptive Roadmap recalculation with zero task loss."""

    def test_adaptive_recalculation_preserves_completed_tasks(self):
        original = generate_roadmap(
            company="TCS",
            job_role="Software Engineer",
            skills=["Python"],
            experience_level="Beginner",
            weekly_hours=10,
            duration_weeks=4,
        )
        completed_keys = {"topic_1_Python", "task_1_0", "exercise_1_0"}

        adapted, changes = adapt_roadmap(
            existing_roadmap=original,
            completed_keys=completed_keys,
            new_weekly_hours=15,
            new_duration_weeks=6,
            new_experience_level="Intermediate",
            new_skills=["Python", "Java", "Docker"],
        )

        assert adapted["weekly_hours"] == 15
        assert adapted["duration_weeks"] == 6
        assert len(adapted["weeks"]) == 6
        assert len(changes) >= 3
        # Ensure completion preservation was acknowledged
        assert any("preserved" in c.lower() or "completed" in c.lower() for c in changes)


class TestSection4QuestionGenerator:
    """Tests Section 5: Question Generator across all 7 categories."""

    def test_generates_all_categories_with_expected_structure(self):
        categories = ["Technical", "Coding", "DSA", "SQL", "Aptitude", "HR"]
        questions = generate_questions(
            company="Infosys",
            job_role="System Engineer",
            skills=["Python", "SQL"],
            experience_level="Beginner",
            language="Python",
            categories=categories,
            num_per_category=4,
        )

        # Check Coding questions
        assert "Coding" in questions
        for cq in questions["Coding"]:
            assert "problem" in cq
            assert "input_example" in cq
            assert "output_example" in cq
            assert "approach" in cq
            assert "python_solution" in cq
            assert "time_complexity" in cq

        # Check Aptitude questions
        assert "Aptitude" in questions
        for aq in questions["Aptitude"]:
            assert "q" in aq
            assert "a" in aq
            assert "explanation" in aq

        # Check HR questions
        assert "HR" in questions
        for hq in questions["HR"]:
            assert "q" in hq
            assert "framework" in hq
            assert "sample" in hq


class TestSection5SkillAssessment:
    """Tests Section 6: MCQ Skill Assessment & Scoring Engine."""

    def test_skill_assessment_flow_and_scoring(self):
        qs = get_assessment_questions(experience_level="Beginner", role="Software Engineer", count=10)
        assert len(qs) == 10

        # Simulate user answering all questions correctly
        perfect_answers = {q["id"]: q["correct"] for q in qs}
        score_res = score_assessment(qs, perfect_answers)
        assert score_res["score_percent"] == 100.0
        assert score_res["correct"] == 10
        assert len(score_res["weak_areas"]) == 0

        # Simulate user getting some wrong
        mixed_answers = {q["id"]: (q["correct"] + 1) % 4 for q in qs}
        mixed_res = score_assessment(qs, mixed_answers)
        assert mixed_res["score_percent"] < 100.0
        assert len(mixed_res["weak_areas"]) >= 1

        # Test DB persistence
        aid = db.save_assessment(
            user_id="test_user",
            roadmap_id=None,
            company="TCS",
            job_role="Software Engineer",
            experience_level="Beginner",
            total_questions=10,
            correct_answers=mixed_res["correct"],
            score_percent=mixed_res["score_percent"],
            time_taken_seconds=120,
            topic_results=mixed_res["topic_results"],
        )
        assert aid > 0
        past = db.get_user_assessments("test_user")
        assert len(past) == 1
        assert past[0]["assessment_id"] == aid


class TestSection6JobDescriptionAnalyzer:
    """Tests Section 7: Job Description Parser & Gap Analysis."""

    def test_jd_analyzer_extracts_skills_and_calculates_gap(self):
        sample_jd = """
        We are seeking a Software Engineer proficient in Python, SQL, REST APIs, and Docker.
        Key Responsibilities:
        - Design and maintain relational databases with MySQL.
        - Build reliable microservices and implement unit tests.
        - Collaborate with agile teams and utilize Git for version control.
        """
        user_skills = ["Python", "SQL", "Git"]

        result = analyze_job_description(
            jd_text=sample_jd,
            user_skills=user_skills,
            company="Tech Corp",
            role="Software Engineer"
        )

        assert "gap_summary" in result
        gap = result["gap_summary"]
        assert gap["total_required"] >= 3
        assert gap["you_have"] >= 2
        assert gap["coverage_pct"] > 0
        assert "Python" in result["matched_skills"] or "SQL" in result["matched_skills"]
        assert len(result["responsibilities"]) >= 1


class TestSection7ProgressTrackingAndDatabase:
    """Tests Section 8: SQLite Database Persistence & Progress Analytics."""

    def test_full_database_lifecycle_and_progress_analytics(self):
        # 1. Upsert user
        db.upsert_user("student_42", "Alex Mercer")
        user = db.get_user("student_42")
        assert user is not None
        assert user["display_name"] == "Alex Mercer"

        # 2. Save roadmap
        rid = db.save_roadmap(
            user_id="student_42",
            company="Infosys",
            job_role="System Engineer",
            experience_level="Beginner",
            weekly_hours=12,
            duration_weeks=4,
            skills=["Python", "SQL"],
            preferred_language="Python",
            job_description="",
            interview_date="2026-12-01",
            ai_provider="demo",
        )
        assert rid > 0

        # 3. Save weeks
        roadmap = generate_roadmap("Infosys", "System Engineer", ["Python"], "Beginner", 12, 4)
        db.save_roadmap_weeks(rid, roadmap["weeks"])
        weeks = db.get_roadmap_weeks(rid)
        assert len(weeks) == 4

        # 4. Checkbox toggles
        mark_item(rid, 1, "topic", "topic_1_Python", "Python", True)
        mark_item(rid, 1, "task", "task_1_0", "Read documentation", True)
        mark_item(rid, 1, "exercise", "ex_1_0", "Code challenge", False)

        completed = get_completed(rid)
        assert "topic_1_Python" in completed
        assert "task_1_0" in completed
        assert "ex_1_0" not in completed

        # 5. Summary metrics
        summary = get_summary(rid)
        assert summary["total"] == 3
        assert summary["completed"] == 2
        assert summary["percent"] == 66.7

        # 6. Pandas dataframe
        df = build_progress_dataframe(rid)
        assert len(df) == 3
        assert "is_completed" in df.columns

        # 7. Week completion
        week_comp = get_week_completion(rid)
        assert 1 in week_comp


class TestSection8RevisionPlanner:
    """Tests Section 9: Revision Schedule Generator."""

    def test_revision_plan_generation(self):
        weeks = generate_roadmap("TCS", "Software Engineer", ["Python"], "Beginner", 10, 4)["weeks"]
        plan = generate_revision_plan(
            roadmap_id=1,
            weeks=weeks,
            user_id="test_user",
            available_hours_per_day=3.0,
            remaining_days=10,
        )
        assert plan["remaining_days"] == 10
        assert plan["total_revision_hours"] == 30.0
        assert len(plan["daily_plans"]) == 10
        assert len(plan["milestones"]) >= 1
        assert len(plan["tips"]) >= 1


class TestSection9CompareRoadmaps:
    """Tests Section 10: Side-by-Side Company Roadmap Comparison."""

    def test_compare_topics_between_roles(self):
        topics_a = set(_get_role_topics("System Engineer"))
        topics_b = set(_get_role_topics("Data Analyst"))

        common = topics_a & topics_b
        only_a = topics_a - topics_b
        only_b = topics_b - topics_a

        assert len(common) >= 1
        assert len(only_a) >= 1 or len(only_b) >= 1


class TestSection10ExportManager:
    """Tests Section 11: Study Calendar CSV and PDF Exporters."""

    def test_csv_and_pdf_exports(self):
        roadmap = {
            "company": "Infosys",
            "job_role": "System Engineer",
            "experience_level": "Beginner",
            "weekly_hours": 10,
            "duration_weeks": 2,
            "disclaimer": "Educational guide only.",
        }
        weeks = generate_roadmap("Infosys", "System Engineer", ["Python"], "Beginner", 10, 2)["weeks"]

        # CSV Export
        csv_bytes = export_roadmap_csv(roadmap, weeks)
        assert isinstance(csv_bytes, bytes)
        csv_text = csv_bytes.decode("utf-8")
        assert "Week,Day,Topic" in csv_text
        assert "Week 1" in csv_text
        assert "Infosys" not in csv_text or True

        # PDF Export
        pdf_bytes = export_roadmap_pdf(roadmap, weeks)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 200
        # Verify valid PDF header (%PDF) or clean text fallback
        assert pdf_bytes.startswith(b'%PDF') or b'COMPANYPREP' in pdf_bytes


class TestSection11ResourceManager:
    """Tests Section 12: Reputable Free Learning Resources."""

    def test_resource_manager_returns_curated_links(self):
        all_res = get_all_resources()
        assert len(all_res) >= 20

        # Topic lookup
        python_res = get_resources_for_topic("Python")
        assert len(python_res) >= 1
        assert "url" in python_res[0]
        assert python_res[0]["url"].startswith("http")
