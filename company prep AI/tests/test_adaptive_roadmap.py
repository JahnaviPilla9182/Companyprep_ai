"""
tests/test_adaptive_roadmap.py
Tests for adaptive roadmap functionality.
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


from backend.core.roadmap_generator import generate_roadmap, adapt_roadmap


@pytest.fixture
def base_roadmap():
    return generate_roadmap(
        company="TCS", job_role="Software Engineer",
        skills=["Python"], experience_level="Beginner",
        weekly_hours=10, duration_weeks=6,
    )


class TestAdaptiveRoadmap:
    def test_adapt_updates_weekly_hours(self, base_roadmap):
        new_rm, changes = adapt_roadmap(
            existing_roadmap=base_roadmap,
            completed_keys=set(),
            new_weekly_hours=20,
            new_duration_weeks=6,
            new_experience_level="Beginner",
            new_skills=["Python"],
        )
        assert new_rm["weekly_hours"] == 20

    def test_adapt_updates_duration(self, base_roadmap):
        new_rm, changes = adapt_roadmap(
            existing_roadmap=base_roadmap,
            completed_keys=set(),
            new_weekly_hours=10,
            new_duration_weeks=4,
            new_experience_level="Beginner",
            new_skills=["Python"],
        )
        assert new_rm["duration_weeks"] == 4
        assert len(new_rm["weeks"]) == 4

    def test_adapt_updates_experience(self, base_roadmap):
        new_rm, changes = adapt_roadmap(
            existing_roadmap=base_roadmap,
            completed_keys=set(),
            new_weekly_hours=10,
            new_duration_weeks=6,
            new_experience_level="Advanced",
            new_skills=["Python"],
        )
        assert new_rm["experience_level"] == "Advanced"
        assert any("experience" in c.lower() or "level" in c.lower() for c in changes)

    def test_adapt_preserves_completed_tasks(self, base_roadmap):
        completed = {"topic_1_Programming Fundamentals", "task_1_0"}
        new_rm, changes = adapt_roadmap(
            existing_roadmap=base_roadmap,
            completed_keys=completed,
            new_weekly_hours=10,
            new_duration_weeks=6,
            new_experience_level="Beginner",
            new_skills=["Python"],
        )
        changes_text = " ".join(changes).lower()
        assert "preserved" in changes_text or "completed" in changes_text

    def test_adapt_returns_valid_roadmap_structure(self, base_roadmap):
        new_rm, changes = adapt_roadmap(
            existing_roadmap=base_roadmap,
            completed_keys=set(),
            new_weekly_hours=15,
            new_duration_weeks=6,
            new_experience_level="Intermediate",
            new_skills=["Python", "Java"],
        )
        assert "weeks" in new_rm
        assert "company" in new_rm
        assert "disclaimer" in new_rm
        for week in new_rm["weeks"]:
            assert "week_number" in week
            assert "topics" in week

    def test_changes_list_not_empty_when_settings_changed(self, base_roadmap):
        new_rm, changes = adapt_roadmap(
            existing_roadmap=base_roadmap,
            completed_keys=set(),
            new_weekly_hours=15,
            new_duration_weeks=4,
            new_experience_level="Advanced",
            new_skills=["Python"],
        )
        assert len(changes) >= 2
