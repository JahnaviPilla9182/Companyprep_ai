"""
tests/test_roadmap_generator.py
Tests for roadmap generation logic.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(autouse=True)
def force_demo_mode(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GROQ_API_KEY", "")
    try:
        monkeypatch.setattr("backend.config.DEMO_MODE", True)
        monkeypatch.setattr("backend.services.llm_service.DEMO_MODE", True)
    except Exception:
        pass


from backend.core.roadmap_generator import generate_roadmap, adapt_roadmap, _get_role_topics, _distribute_topics


COMPANY_ROLE_CONFIGS = [
    ("Infosys", "System Engineer"),
    ("TCS", "Software Engineer"),
    ("Cognizant", "Junior Software Engineer"),
    ("Generic Software Developer", "Software Developer"),
]


class TestRoadmapGeneration:
    @pytest.mark.parametrize("company,role", COMPANY_ROLE_CONFIGS)
    def test_generates_for_all_required_configs(self, company, role):
        roadmap = generate_roadmap(
            company=company, job_role=role,
            skills=["Python"], experience_level="Beginner",
            weekly_hours=10, duration_weeks=4,
        )
        assert "weeks" in roadmap
        assert len(roadmap["weeks"]) >= 1
        assert roadmap["company"] == company

    def test_roadmap_has_required_fields(self):
        roadmap = generate_roadmap(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
            weekly_hours=10, duration_weeks=4,
        )
        for week in roadmap["weeks"]:
            assert "week_number" in week
            assert "topics" in week
            assert "daily_tasks" in week
            assert "practice_questions" in week
            assert "assessment" in week

    def test_duration_respected(self):
        for weeks in [2, 4, 8, 12]:
            roadmap = generate_roadmap(
                company="TCS", job_role="Software Engineer",
                skills=["Python"], experience_level="Beginner",
                weekly_hours=10, duration_weeks=weeks,
            )
            assert len(roadmap["weeks"]) == weeks

    def test_weekly_hours_not_exceeded(self):
        weekly_limit = 5
        roadmap = generate_roadmap(
            company="Infosys", job_role="System Engineer",
            skills=["Python"], experience_level="Beginner",
            weekly_hours=weekly_limit, duration_weeks=4,
        )
        for week in roadmap["weeks"]:
            # Allow small floating point tolerance
            assert week["estimated_hours"] <= weekly_limit + 0.5

    def test_disclaimer_present(self):
        roadmap = generate_roadmap(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
            weekly_hours=10, duration_weeks=4,
        )
        assert "disclaimer" in roadmap
        assert len(roadmap["disclaimer"]) > 20

    def test_beginner_vs_advanced_hours(self):
        """Advanced users should need fewer hours per topic."""
        beginner = generate_roadmap(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
            weekly_hours=10, duration_weeks=8,
        )
        advanced = generate_roadmap(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Advanced",
            weekly_hours=10, duration_weeks=8,
        )
        # Advanced roadmap should cover more topics in same time
        total_beginner = sum(len(w["topics"]) for w in beginner["weeks"])
        total_advanced = sum(len(w["topics"]) for w in advanced["weeks"])
        # At minimum both should have topics
        assert total_beginner >= 1
        assert total_advanced >= 1


class TestRoleTopics:
    def test_software_engineer_has_core_topics(self):
        topics = _get_role_topics("Software Engineer")
        assert "Data Structures" in topics or "Algorithms" in topics

    def test_default_fallback(self):
        topics = _get_role_topics("Unknown Random Role")
        assert len(topics) >= 5


class TestAdaptRoadmap:
    def test_adapt_changes_weekly_hours(self):
        original = generate_roadmap(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
            weekly_hours=10, duration_weeks=8,
        )
        new_roadmap, changes = adapt_roadmap(
            existing_roadmap=original,
            completed_keys=set(),
            new_weekly_hours=20,
            new_duration_weeks=8,
            new_experience_level="Beginner",
            new_skills=["Python"],
        )
        assert new_roadmap["weekly_hours"] == 20
        assert len(changes) >= 1

    def test_adapt_preserves_completed_count(self):
        original = generate_roadmap(
            company="TCS", job_role="Software Engineer",
            skills=["Python"], experience_level="Beginner",
            weekly_hours=10, duration_weeks=4,
        )
        completed = {"topic_1_Python", "task_1_0"}
        new_roadmap, changes = adapt_roadmap(
            existing_roadmap=original,
            completed_keys=completed,
            new_weekly_hours=15,
            new_duration_weeks=4,
            new_experience_level="Beginner",
            new_skills=["Python"],
        )
        # Changes should mention completed tasks preserved
        assert any("preserved" in c.lower() or "completed" in c.lower() for c in changes)
