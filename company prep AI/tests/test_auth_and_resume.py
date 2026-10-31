"""
tests/test_auth_and_resume.py
Unit and integration tests for User Authentication and Resume Checkpoint functionality.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import database.db_manager as dm


@pytest.fixture
def auth_db(tmp_path, monkeypatch):
    """Set up an isolated database for auth and resume tests."""
    db_file = str(tmp_path / "auth_test.db")
    monkeypatch.setattr(dm, "DB_PATH", db_file)
    dm.init_db()
    return dm


class TestPasswordHashing:
    def test_hash_and_verify_correct_password(self):
        pwd = "SecretPassword123!"
        hashed, salt = dm.hash_password(pwd)
        assert hashed is not None
        assert salt is not None
        assert dm.verify_password(pwd, hashed, salt) is True

    def test_verify_incorrect_password(self):
        pwd = "CorrectPassword"
        hashed, salt = dm.hash_password(pwd)
        assert dm.verify_password("WrongPassword", hashed, salt) is False

    def test_verify_empty_password(self):
        pwd = "ValidPassword"
        hashed, salt = dm.hash_password(pwd)
        assert dm.verify_password("", hashed, salt) is False
        assert dm.verify_password(pwd, "", salt) is False


class TestUserRegistration:
    def test_register_valid_user(self, auth_db):
        ok, msg, user = auth_db.register_user(
            username="candidate1",
            password="SecurePassword99!",
            display_name="Alex Student",
            email="alex@university.edu"
        )
        assert ok is True
        assert "success" in msg.lower()
        assert user["username"] == "candidate1"
        assert user["display_name"] == "Alex Student"
        assert user["email"] == "alex@university.edu"
        assert user["session_token"] is not None

    def test_register_duplicate_username_fails(self, auth_db):
        auth_db.register_user("unique_dev", "ValidPass123!")
        ok, msg, user = auth_db.register_user("unique_dev", "ValidPass456!")
        assert ok is False
        assert "already taken" in msg.lower()
        assert user is None

    def test_register_short_username_fails(self, auth_db):
        ok, msg, user = auth_db.register_user("ab", "ValidPass123!")
        assert ok is False
        assert "3-30 characters" in msg.lower()

    def test_register_short_password_fails(self, auth_db):
        ok, msg, user = auth_db.register_user("validname", "123")
        assert ok is False
        assert "at least 8 characters" in msg.lower()


class TestUserAuthentication:
    def test_authenticate_success(self, auth_db):
        auth_db.register_user("coder_joe", "Mysecret123!", "Joe Coder")
        ok, msg, user = auth_db.authenticate_user("coder_joe", "Mysecret123!")
        assert ok is True
        assert "successful" in msg.lower()
        assert user["username"] == "coder_joe"
        assert user["session_token"] is not None

    def test_authenticate_case_insensitive_username(self, auth_db):
        auth_db.register_user("PurnaTech", "Pwd12345!", "Purna")
        ok, msg, user = auth_db.authenticate_user("purnatech", "Pwd12345!")
        assert ok is True
        assert user["username"] == "purnatech"

    def test_authenticate_wrong_password_fails(self, auth_db):
        auth_db.register_user("user_a", "Mypassword123!")
        ok, msg, user = auth_db.authenticate_user("user_a", "Wrongpassword123!")
        assert ok is False
        assert "invalid" in msg.lower()
        assert user is None

    def test_authenticate_nonexistent_user_fails(self, auth_db):
        ok, msg, user = auth_db.authenticate_user("ghost_user", "Password123!")
        assert ok is False
        assert "invalid" in msg.lower()

    def test_session_token_retrieval(self, auth_db):
        _, _, reg_user = auth_db.register_user("session_tester", "Mypass123!")
        token = reg_user["session_token"]
        retrieved = auth_db.get_user_by_session_token(token)
        assert retrieved is not None
        assert retrieved["username"] == "session_tester"

    def test_invalid_session_token_returns_none(self, auth_db):
        retrieved = auth_db.get_user_by_session_token("non_existent_token_12345")
        assert retrieved is None


class TestResumeCheckpoint:
    def test_resume_checkpoint_progression(self, auth_db):
        # 1. Register candidate
        _, _, user = auth_db.register_user("resume_hero", "Pass1234!", "Resume Hero")
        uid = user["user_id"]

        # 2. Initially no checkpoint
        cp0 = auth_db.get_user_resume_checkpoint(uid)
        assert cp0 is None

        # 3. Create roadmap
        rid = auth_db.save_roadmap(
            user_id=uid,
            company="Infosys",
            job_role="System Engineer",
            experience_level="Beginner",
            weekly_hours=10,
            duration_weeks=3,
            skills=["Python", "SQL"],
            preferred_language="Python",
            job_description="",
            interview_date="",
            ai_provider="demo"
        )
        weeks = [
            {
                "week_number": 1,
                "topics": ["Python Basics", "Control Structures"],
                "daily_tasks": ["Complete loops practice", "Read syntax guide"],
                "coding_exercises": ["Palindrome check"]
            },
            {
                "week_number": 2,
                "topics": ["OOP Principles"],
                "daily_tasks": ["Implement Class Inheritance"],
                "coding_exercises": ["BankAccount Class"]
            },
            {
                "week_number": 3,
                "topics": ["SQL Queries"],
                "daily_tasks": ["Solve JOIN queries"],
                "coding_exercises": ["Customer Orders Schema"]
            }
        ]
        auth_db.save_roadmap_weeks(rid, weeks)

        # 4. Initial Checkpoint: Should be Week 1 with first topic
        cp1 = auth_db.get_user_resume_checkpoint(uid)
        assert cp1 is not None
        assert cp1["resume_week"] == 1
        assert "Python Basics" in cp1["next_task"]
        assert cp1["summary"]["completed"] == 0

        # 5. Complete first topic: Should point to second topic in Week 1
        auth_db.upsert_progress_item(rid, 1, "topic", "topic_1_Python Basics", "Python Basics", True)
        cp2 = auth_db.get_user_resume_checkpoint(uid)
        assert cp2["resume_week"] == 1
        assert "Control Structures" in cp2["next_task"]
        assert cp2["last_completed_item"]["item_label"] == "Python Basics"

        # 6. Complete remaining Week 1 items: Checkpoint should automatically advance to Week 2!
        auth_db.upsert_progress_item(rid, 1, "topic", "topic_1_Control Structures", "Control Structures", True)
        auth_db.upsert_progress_item(rid, 1, "task", "task_1_0", "Complete loops practice", True)
        auth_db.upsert_progress_item(rid, 1, "task", "task_1_1", "Read syntax guide", True)
        auth_db.upsert_progress_item(rid, 1, "exercise", "exercise_1_0", "Palindrome check", True)

        cp3 = auth_db.get_user_resume_checkpoint(uid)
        assert cp3["resume_week"] == 2
        assert "OOP Principles" in cp3["next_task"]

    def test_guest_roadmap_reassignment(self, auth_db):
        guest_id = "guest_temp_uuid_123"
        auth_db.upsert_user(guest_id, "Guest")
        rid = auth_db.save_roadmap(
            user_id=guest_id,
            company="TCS",
            job_role="Software Engineer",
            experience_level="Beginner",
            weekly_hours=12,
            duration_weeks=2,
            skills=["DSA"],
            preferred_language="Python",
            job_description="",
            interview_date="",
            ai_provider="demo"
        )

        # Candidate now creates an account
        _, _, registered = auth_db.register_user("new_dev", "Password123!")
        new_uid = registered["user_id"]

        # Reassign roadmap to new account
        auth_db.reassign_roadmap_user(rid, new_uid)

        # Check that new account now owns and resumes this roadmap
        cp = auth_db.get_user_resume_checkpoint(new_uid)
        assert cp is not None
        assert cp["roadmap_id"] == rid
        assert cp["company"] == "TCS"
