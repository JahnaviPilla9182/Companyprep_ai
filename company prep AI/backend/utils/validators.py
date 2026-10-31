"""
backend/utils/validators.py
Input validation helpers for CompanyPrep AI.
Includes strong password policy, email validation, HTML sanitization,
rate limiting via session state, and all form-level validators.
"""
import re
import html
import streamlit as st
from typing import Tuple

KNOWN_COMPANIES = [
    "Infosys", "TCS", "Cognizant", "Wipro", "HCL", "Accenture",
    "Capgemini", "Tech Mahindra", "IBM", "Amazon", "Google", "Microsoft",
    "Flipkart", "Zomato", "Swiggy", "Zoho", "Freshworks", "Tata Elxsi",
    "Mindtree", "Mphasis", "Hexaware", "LTIMindtree", "Oracle", "SAP",
    "Generic Software Developer",
]

KNOWN_ROLES = [
    "Software Engineer", "System Engineer", "Junior Software Engineer",
    "Associate Software Engineer", "Software Developer", "Full Stack Developer",
    "Backend Developer", "Frontend Developer", "Data Analyst",
    "Data Engineer", "Machine Learning Engineer", "DevOps Engineer",
    "QA Engineer", "Test Engineer", "Business Analyst", "Entry Level Developer",
    "Trainee Engineer", "Graduate Engineer Trainee",
]

EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]
LANGUAGES = ["Python", "Java", "C++", "C", "JavaScript", "Go", "C#", "Kotlin"]

# Password strength requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Special characters for password strength
SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;':\",./<>?`~\\")


# ---------------------------------------------------------------------------
# Authentication Validators
# ---------------------------------------------------------------------------

def validate_password_strength(password: str) -> Tuple[bool, str, int]:
    """
    Validate password strength.
    Returns (is_valid, message, score 0-4).
    Score: 0=Very Weak, 1=Weak, 2=Fair, 3=Strong, 4=Very Strong
    """
    if not password:
        return False, "Password is required.", 0

    score = 0
    issues = []

    if len(password) < PASSWORD_MIN_LENGTH:
        issues.append(f"at least {PASSWORD_MIN_LENGTH} characters")
    else:
        score += 1

    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"Password must not exceed {PASSWORD_MAX_LENGTH} characters.", 0

    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(any(c in SPECIAL_CHARS for c in password))

    if not has_upper:
        issues.append("one uppercase letter (A-Z)")
    else:
        score += 1

    if not has_lower:
        issues.append("one lowercase letter (a-z)")
    else:
        score += 1

    if not has_digit:
        issues.append("one digit (0-9)")
    else:
        score += 1

    if not has_special:
        issues.append("one special character (!@#$%^&*...)")
    else:
        score += 1

    # Bonus for length
    if len(password) >= 12:
        score = min(score + 1, 4)

    if issues:
        return False, f"Password must contain: {', '.join(issues)}.", score

    return True, "Password meets all requirements.", score


def get_password_strength_label(score: int) -> Tuple[str, str]:
    """Return (label, color) for a given password score 0-4."""
    labels = {
        0: ("Very Weak", "#EF4444"),
        1: ("Weak", "#F97316"),
        2: ("Fair", "#EAB308"),
        3: ("Strong", "#22C55E"),
        4: ("Very Strong", "#10B981"),
    }
    return labels.get(score, ("Very Weak", "#EF4444"))


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format."""
    if not email or not email.strip():
        return True, ""  # Email is optional

    email = email.strip()
    if len(email) > 254:
        return False, "Email address is too long (max 254 characters)."

    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Please enter a valid email address (e.g., user@example.com)."

    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format."""
    u = (username or "").strip()
    if not u:
        return False, "Username is required."
    if len(u) < 3:
        return False, "Username must be at least 3 characters long."
    if len(u) > 30:
        return False, "Username must not exceed 30 characters."
    if not re.match(r"^[a-zA-Z0-9_.\-]+$", u):
        return False, "Username may only contain letters, numbers, underscores ( _ ), dots ( . ), and dashes ( - )."
    if u.startswith((".", "-", "_")) or u.endswith((".", "-", "_")):
        return False, "Username cannot start or end with special characters."
    return True, ""


def validate_display_name(name: str) -> Tuple[bool, str]:
    """Validate display/full name."""
    n = (name or "").strip()
    if not n:
        return True, ""  # Display name is optional
    if len(n) < 1:
        return False, "Display name must be at least 1 character."
    if len(n) > 60:
        return False, "Display name must not exceed 60 characters."
    # Block HTML tags
    if re.search(r"<[^>]+>", n):
        return False, "Display name must not contain HTML tags."
    return True, ""


def validate_confirm_password(password: str, confirm: str) -> Tuple[bool, str]:
    """Validate that password and confirmation match."""
    if not confirm:
        return False, "Please confirm your password."
    if password != confirm:
        return False, "Passwords do not match. Please re-enter your password."
    return True, ""


def validate_registration(
    username: str,
    password: str,
    confirm_password: str,
    email: str = "",
    display_name: str = "",
) -> Tuple[bool, list]:
    """
    Full registration validation.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []

    ok, msg = validate_username(username)
    if not ok:
        errors.append(msg)

    ok, msg, _ = validate_password_strength(password)
    if not ok:
        errors.append(msg)

    ok, msg = validate_confirm_password(password, confirm_password)
    if not ok:
        errors.append(msg)

    ok, msg = validate_email(email)
    if not ok:
        errors.append(msg)

    ok, msg = validate_display_name(display_name)
    if not ok:
        errors.append(msg)

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Input Sanitization
# ---------------------------------------------------------------------------

def sanitize_html(text: str, max_len: int = 5000) -> str:
    """Escape HTML tags and truncate arbitrary user text input."""
    if not text:
        return ""
    # Escape HTML special characters to prevent XSS
    safe = html.escape(text.strip())
    return safe[:max_len]


def sanitize_text(text: str, max_len: int = 5000) -> str:
    """Strip and truncate arbitrary user text input (legacy alias)."""
    return sanitize_html(text, max_len)


def strip_html_tags(text: str) -> str:
    """Remove all HTML tags from a string."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


# ---------------------------------------------------------------------------
# Rate Limiting (session-state based, per-key)
# ---------------------------------------------------------------------------

def check_rate_limit(key: str, max_attempts: int = 5, window_label: str = "session") -> Tuple[bool, int]:
    """
    Check if the given action key has exceeded max_attempts in the current session.
    Returns (is_allowed, attempts_so_far).
    """
    counter_key = f"_ratelimit_{key}"
    attempts = st.session_state.get(counter_key, 0)
    if attempts >= max_attempts:
        return False, attempts
    return True, attempts


def increment_rate_limit(key: str) -> int:
    """Increment the rate limit counter for a given key."""
    counter_key = f"_ratelimit_{key}"
    current = st.session_state.get(counter_key, 0)
    st.session_state[counter_key] = current + 1
    return current + 1


def reset_rate_limit(key: str) -> None:
    """Reset the rate limit counter for a given key."""
    counter_key = f"_ratelimit_{key}"
    st.session_state[counter_key] = 0


# ---------------------------------------------------------------------------
# Form Validators (Roadmap, JD, Resume)
# ---------------------------------------------------------------------------

def validate_company(company: str) -> Tuple[bool, str]:
    """Validate company name."""
    c = strip_html_tags((company or "").strip())
    if not c:
        return False, "Company name cannot be empty."
    if len(c) < 2:
        return False, "Company name must be at least 2 characters."
    if len(c) > 100:
        return False, "Company name must be under 100 characters."
    if re.search(r"[<>\"'&;]", c):
        return False, "Company name contains invalid characters."
    return True, ""


def validate_role(role: str) -> Tuple[bool, str]:
    """Validate job role."""
    r = strip_html_tags((role or "").strip())
    if not r:
        return False, "Job role cannot be empty."
    if len(r) < 2:
        return False, "Job role must be at least 2 characters."
    if len(r) > 100:
        return False, "Job role must be under 100 characters."
    if re.search(r"[<>\"'&;]", r):
        return False, "Job role contains invalid characters."
    return True, ""


def validate_skills(skills: list) -> Tuple[bool, str]:
    """Validate skill list."""
    if not skills:
        return False, "Please select or enter at least one skill."
    if len(skills) > 30:
        return False, "Please select no more than 30 skills."
    return True, ""


def validate_weekly_hours(hours) -> Tuple[bool, str]:
    """Validate weekly study hours."""
    try:
        h = float(hours)
    except (TypeError, ValueError):
        return False, "Weekly study hours must be a number."
    if h < 1:
        return False, "Weekly study hours must be at least 1."
    if h > 80:
        return False, "Weekly study hours cannot exceed 80 per week."
    return True, ""


def validate_duration(weeks) -> Tuple[bool, str]:
    """Validate preparation duration in weeks."""
    try:
        w = int(weeks)
    except (TypeError, ValueError):
        return False, "Preparation duration must be a whole number of weeks."
    if w < 1:
        return False, "Duration must be at least 1 week."
    if w > 52:
        return False, "Duration cannot exceed 52 weeks (1 year)."
    return True, ""


def validate_experience_level(level: str) -> Tuple[bool, str]:
    """Validate experience level."""
    if level not in EXPERIENCE_LEVELS:
        return False, f"Experience level must be one of: {', '.join(EXPERIENCE_LEVELS)}."
    return True, ""


def validate_onboarding(data: dict) -> Tuple[bool, list]:
    """
    Validate the full onboarding form.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []
    checks = [
        validate_company(data.get("company", "")),
        validate_role(data.get("job_role", "")),
        validate_skills(data.get("skills", [])),
        validate_weekly_hours(data.get("weekly_hours", 0)),
        validate_duration(data.get("duration_weeks", 0)),
        validate_experience_level(data.get("experience_level", "")),
    ]
    for ok, msg in checks:
        if not ok:
            errors.append(msg)
    return len(errors) == 0, errors


def validate_jd_text(jd_text: str) -> Tuple[bool, str]:
    """Validate job description text length."""
    text = (jd_text or "").strip()
    if not text:
        return False, "Job description cannot be empty."
    if len(text) < 50:
        return False, "Job description is too short. Please provide a complete description (minimum 50 characters)."
    if len(text) > 10000:
        return False, f"Job description is too long ({len(text):,} characters). Maximum allowed is 10,000 characters."
    return True, ""


def validate_file_upload(file, allowed_types: list = None, max_mb: float = 5.0) -> Tuple[bool, str]:
    """Validate an uploaded file object from Streamlit."""
    if file is None:
        return False, "No file uploaded."
    if allowed_types and not any(file.name.lower().endswith(ext) for ext in allowed_types):
        return False, f"Unsupported file type. Allowed: {', '.join(allowed_types)}."
    size_mb = len(file.getvalue()) / (1024 * 1024)
    if size_mb > max_mb:
        return False, f"File is {size_mb:.1f} MB. Maximum allowed is {max_mb} MB."
    return True, ""
