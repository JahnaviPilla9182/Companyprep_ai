"""
tests/test_validators.py
Tests for input validation.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.validators import (
    validate_company, validate_role, validate_skills,
    validate_weekly_hours, validate_duration,
    validate_experience_level, validate_onboarding,
    sanitize_text,
)


class TestCompanyValidation:
    def test_valid_company(self):
        ok, msg = validate_company("Infosys")
        assert ok is True
        assert msg == ""

    def test_empty_company(self):
        ok, msg = validate_company("")
        assert ok is False
        assert "empty" in msg.lower()

    def test_whitespace_only_company(self):
        ok, msg = validate_company("   ")
        assert ok is False

    def test_single_char_company(self):
        ok, msg = validate_company("A")
        assert ok is False

    def test_long_company_name(self):
        ok, msg = validate_company("A" * 101)
        assert ok is False
        assert "100" in msg


class TestRoleValidation:
    def test_valid_role(self):
        ok, msg = validate_role("Software Engineer")
        assert ok is True

    def test_empty_role(self):
        ok, msg = validate_role("")
        assert ok is False

    def test_none_role(self):
        ok, msg = validate_role(None)
        assert ok is False


class TestSkillsValidation:
    def test_valid_skills(self):
        ok, msg = validate_skills(["Python", "Java"])
        assert ok is True

    def test_empty_skills(self):
        ok, msg = validate_skills([])
        assert ok is False

    def test_too_many_skills(self):
        ok, msg = validate_skills([str(i) for i in range(31)])
        assert ok is False


class TestHoursValidation:
    def test_valid_hours(self):
        ok, msg = validate_weekly_hours(10)
        assert ok is True

    def test_zero_hours(self):
        ok, msg = validate_weekly_hours(0)
        assert ok is False

    def test_excessive_hours(self):
        ok, msg = validate_weekly_hours(100)
        assert ok is False

    def test_string_hours(self):
        ok, msg = validate_weekly_hours("abc")
        assert ok is False

    def test_float_hours(self):
        ok, msg = validate_weekly_hours(7.5)
        assert ok is True


class TestDurationValidation:
    def test_valid_duration(self):
        ok, msg = validate_duration(8)
        assert ok is True

    def test_zero_duration(self):
        ok, msg = validate_duration(0)
        assert ok is False

    def test_excessive_duration(self):
        ok, msg = validate_duration(53)
        assert ok is False

    def test_float_duration(self):
        ok, msg = validate_duration(8)
        assert ok is True


class TestOnboardingValidation:
    def test_valid_full_onboarding(self, sample_onboarding_data):
        ok, errors = validate_onboarding(sample_onboarding_data)
        assert ok is True
        assert len(errors) == 0

    def test_missing_company(self, sample_onboarding_data):
        sample_onboarding_data["company"] = ""
        ok, errors = validate_onboarding(sample_onboarding_data)
        assert ok is False
        assert len(errors) >= 1

    def test_missing_skills(self, sample_onboarding_data):
        sample_onboarding_data["skills"] = []
        ok, errors = validate_onboarding(sample_onboarding_data)
        assert ok is False

    def test_invalid_hours(self, sample_onboarding_data):
        sample_onboarding_data["weekly_hours"] = -5
        ok, errors = validate_onboarding(sample_onboarding_data)
        assert ok is False

    def test_invalid_duration(self, sample_onboarding_data):
        sample_onboarding_data["duration_weeks"] = 0
        ok, errors = validate_onboarding(sample_onboarding_data)
        assert ok is False

    def test_invalid_experience(self, sample_onboarding_data):
        sample_onboarding_data["experience_level"] = "Expert"
        ok, errors = validate_onboarding(sample_onboarding_data)
        assert ok is False


class TestSanitizeText:
    def test_strips_whitespace(self):
        assert sanitize_text("  hello  ") == "hello"

    def test_truncates_long_text(self):
        assert len(sanitize_text("a" * 10000, max_len=100)) == 100

    def test_empty_string(self):
        assert sanitize_text("") == ""

    def test_none_input(self):
        assert sanitize_text(None) == ""
