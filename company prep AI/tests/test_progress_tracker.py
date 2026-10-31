"""
tests/test_progress_tracker.py
Tests for progress tracking and SQLite persistence.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def setup_db(tmp_path, monkeypatch):
    """Set up a fresh temp DB and a test roadmap."""
    import database.db_manager as dm
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr(dm, "DB_PATH", db_path)
    dm.init_db()
    dm.upsert_user("test_user", "Test Student")
    rid = dm.save_roadmap(
        user_id="test_user", company="TCS", job_role="Software Engineer",
        experience_level="Beginner", weekly_hours=10, duration_weeks=4,
        skills=["Python"], preferred_language="Python",
        job_description="", interview_date="", ai_provider="demo",
    )
    return rid, dm


class TestProgressCRUD:
    def test_mark_item_completed(self, setup_db):
        rid, dm = setup_db
        dm.upsert_progress_item(
            roadmap_id=rid, week_number=1, item_type="topic",
            item_key="topic_1_Python", item_label="Python",
            is_completed=True
        )
        keys = dm.get_completed_keys(rid)
        assert "topic_1_Python" in keys

    def test_mark_item_uncompleted(self, setup_db):
        rid, dm = setup_db
        dm.upsert_progress_item(
            roadmap_id=rid, week_number=1, item_type="topic",
            item_key="topic_1_DSA", item_label="DSA",
            is_completed=True
        )
        dm.upsert_progress_item(
            roadmap_id=rid, week_number=1, item_type="topic",
            item_key="topic_1_DSA", item_label="DSA",
            is_completed=False
        )
        keys = dm.get_completed_keys(rid)
        assert "topic_1_DSA" not in keys

    def test_progress_summary_empty(self, setup_db):
        rid, dm = setup_db
        summary = dm.get_progress_summary(rid)
        assert summary["total"] == 0
        assert summary["completed"] == 0
        assert summary["percent"] == 0.0

    def test_progress_percentage_calculation(self, setup_db):
        rid, dm = setup_db
        for i in range(4):
            dm.upsert_progress_item(
                roadmap_id=rid, week_number=1, item_type="topic",
                item_key=f"topic_1_item{i}", item_label=f"Item {i}",
                is_completed=(i < 2)  # 2 out of 4 completed
            )
        summary = dm.get_progress_summary(rid)
        assert summary["total"] == 4
        assert summary["completed"] == 2
        assert summary["percent"] == 50.0

    def test_persistence_after_reconnect(self, setup_db):
        """Test that data persists after creating a new DB connection."""
        rid, dm = setup_db
        dm.upsert_progress_item(
            roadmap_id=rid, week_number=1, item_type="topic",
            item_key="topic_1_Persist", item_label="Persist Test",
            is_completed=True
        )
        # New connection (simulating app restart)
        conn2 = dm.get_connection()
        try:
            row = conn2.execute(
                "SELECT is_completed FROM progress WHERE item_key = ?",
                ("topic_1_Persist",)
            ).fetchone()
            assert row is not None
            assert row["is_completed"] == 1
        finally:
            conn2.close()


class TestProgressDataframe:
    def test_build_progress_dataframe_empty(self, setup_db):
        rid, dm = setup_db
        from backend.core.progress_tracker import build_progress_dataframe
        df = build_progress_dataframe(rid)
        assert df.empty or len(df) == 0

    def test_build_progress_dataframe_with_data(self, setup_db):
        rid, dm = setup_db
        for i in range(3):
            dm.upsert_progress_item(
                roadmap_id=rid, week_number=1, item_type="topic",
                item_key=f"topic_1_t{i}", item_label=f"Topic {i}",
                is_completed=(i % 2 == 0)
            )
        from backend.core.progress_tracker import build_progress_dataframe
        df = build_progress_dataframe(rid)
        assert len(df) == 3
        assert "is_completed" in df.columns
