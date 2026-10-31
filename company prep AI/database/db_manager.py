"""
database/db_manager.py
Manages SQLite database connections, initialization, and all CRUD operations
for CompanyPrep AI. Uses parameterized queries for SQL injection safety.

Security features:
  - PBKDF2-HMAC-SHA256 (100k rounds) password hashing
  - Account lockout: 5 failed attempts → 15-minute lock
  - Session token expiry: 7 days rolling
  - Strong password policy enforced at DB layer
"""
import sqlite3
import json
import os
import hashlib
import secrets
import re
import uuid
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timezone, timedelta


DB_PATH = Path(__file__).parent / "companyprep.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory set to sqlite3.Row."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db() -> None:
    """Initialize the database by executing schema.sql and running safe migrations."""
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = get_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()

        # Migrate existing users table if columns are missing
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(users);")
        existing_cols = {row["name"] for row in cur.fetchall()}

        migrations = [
            ("username", "TEXT"),
            ("password_hash", "TEXT"),
            ("salt", "TEXT"),
            ("email", "TEXT DEFAULT ''"),
            ("role", "TEXT DEFAULT 'USER'"),
            ("session_token", "TEXT"),
            ("last_active_roadmap_id", "INTEGER"),
            ("last_login", "TIMESTAMP"),
            # Security columns
            ("failed_login_attempts", "INTEGER DEFAULT 0"),
            ("locked_until", "TIMESTAMP"),
            ("session_expires_at", "TIMESTAMP"),
        ]
        for col_name, col_type in migrations:
            if col_name not in existing_cols:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")

        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username);")
        conn.commit()

        # Seed default admin and student accounts if absent
        admin_check = conn.execute("SELECT user_id FROM users WHERE LOWER(username) = 'admin'").fetchone()
        if not admin_check:
            a_id = str(uuid.uuid4())
            a_hash, a_salt = hash_password("Admin@2026!")
            a_tok = secrets.token_urlsafe(32)
            conn.execute(
                """INSERT INTO users (user_id, username, password_hash, salt, display_name, email, role, session_token, failed_login_attempts)
                   VALUES (?, 'admin', ?, ?, 'System Admin', 'admin@companyprep.ai', 'ADMIN', ?, 0)""",
                (a_id, a_hash, a_salt, a_tok)
            )
            conn.commit()

        student_check = conn.execute("SELECT user_id FROM users WHERE LOWER(username) = 'student'").fetchone()
        if not student_check:
            s_id = str(uuid.uuid4())
            s_hash, s_salt = hash_password("CompanyPrep@2026!")
            s_tok = secrets.token_urlsafe(32)
            conn.execute(
                """INSERT INTO users (user_id, username, password_hash, salt, display_name, email, role, session_token, failed_login_attempts)
                   VALUES (?, 'student', ?, ?, 'Demo Student', 'student@gmrit.edu.in', 'USER', ?, 0)""",
                (s_id, s_hash, s_salt, s_tok)
            )
            conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Authentication & User helpers
# ---------------------------------------------------------------------------

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password using salted PBKDF2-HMAC-SHA256 (100k rounds)."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return key.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify a plaintext password against the stored PBKDF2 hash and salt."""
    if not password or not password_hash or not salt:
        return False
    calculated_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(calculated_hash, password_hash)


# ---------------------------------------------------------------------------
# Security constants
# ---------------------------------------------------------------------------
MAX_FAILED_ATTEMPTS = 5          # Lock after this many failures
LOCKOUT_MINUTES = 15             # Lock duration in minutes
SESSION_EXPIRY_DAYS = 7          # Session token lifetime

# Password complexity requirements (mirrors validators.py)
_SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;':\",./<>?`~\\")


def _check_password_policy(password: str) -> tuple[bool, str]:
    """Enforce strong password policy at the DB layer."""
    if not password:
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 128:
        return False, "Password must not exceed 128 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit (0-9)."
    if not any(c in _SPECIAL_CHARS for c in password):
        return False, "Password must contain at least one special character (!@#$%^&* etc.)."
    return True, ""


def register_user(
    username: str,
    password: str,
    display_name: str = "",
    email: str = "",
    role: str = "USER",
) -> tuple[bool, str, Optional[dict]]:
    """Register a new user with strong password policy and salted PBKDF2 hashing."""
    u = (username or "").strip().lower()
    if not u:
        return False, "Username is required.", None
    if len(u) < 3 or len(u) > 30 or not re.match(r"^[a-zA-Z0-9_.-]+$", u):
        return False, "Username must be 3-30 characters (letters, numbers, underscores, dots, or dashes).", None

    # Enforce strong password
    ok, pwd_msg = _check_password_policy(password)
    if not ok:
        return False, pwd_msg, None

    # Email format check (optional field)
    email_clean = (email or "").strip()
    if email_clean:
        email_pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email_clean):
            return False, "Please enter a valid email address (e.g., user@example.com).", None
        if len(email_clean) > 254:
            return False, "Email address is too long.", None

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT user_id FROM users WHERE LOWER(username) = ?", (u,)
        ).fetchone()
        if existing:
            return False, f"Username '{u}' is already taken. Please choose another username.", None

        user_id = str(uuid.uuid4())
        disp_name = (display_name or "").strip() or u.capitalize()
        pwd_hash, salt = hash_password(password)
        session_token = secrets.token_urlsafe(32)
        session_expires_at = (datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
        user_role = (role or "USER").strip().upper()

        conn.execute(
            """INSERT INTO users
               (user_id, username, password_hash, salt, display_name, email, role,
                session_token, session_expires_at, last_login,
                failed_login_attempts)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 0)""",
            (user_id, u, pwd_hash, salt, disp_name, email_clean, user_role, session_token, session_expires_at),
        )
        conn.commit()
        user_data = get_user(user_id)
        return True, "Account created successfully!", user_data
    finally:
        conn.close()


def authenticate_user(
    username: str,
    password: str,
) -> tuple[bool, str, Optional[dict]]:
    """
    Authenticate a user by username & password.
    Enforces account lockout: 5 failed attempts → locked for 15 minutes.
    Refreshes session token on success with 7-day expiry.
    """
    u = (username or "").strip().lower()
    if not u or not password:
        return False, "Please enter both username and password.", None

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = ?", (u,)
        ).fetchone()
        if not row:
            # Generic message to prevent username enumeration
            return False, "Invalid username or password.", None

        user_data = dict(row)

        # ── Check account lockout ──────────────────────────────────────────
        locked_until = user_data.get("locked_until")
        if locked_until:
            try:
                lock_dt = datetime.fromisoformat(locked_until)
                if lock_dt.tzinfo is None:
                    lock_dt = lock_dt.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                if now < lock_dt:
                    remaining = int((lock_dt - now).total_seconds() / 60) + 1
                    return False, (
                        f"🔒 Account temporarily locked due to too many failed attempts. "
                        f"Please try again in {remaining} minute(s)."
                    ), None
            except (ValueError, TypeError):
                pass  # Ignore malformed date, proceed

        stored_hash = user_data.get("password_hash")
        salt = user_data.get("salt")
        if not stored_hash or not salt:
            return False, "This account does not have a password configured (guest account).", None

        # ── Verify password ────────────────────────────────────────────────
        if not verify_password(password, stored_hash, salt):
            # Increment failed attempt counter
            new_attempts = (user_data.get("failed_login_attempts") or 0) + 1
            lock_time = None
            if new_attempts >= MAX_FAILED_ATTEMPTS:
                lock_time = (datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()

            conn.execute(
                """UPDATE users SET failed_login_attempts = ?, locked_until = ?
                   WHERE user_id = ?""",
                (new_attempts, lock_time, user_data["user_id"]),
            )
            conn.commit()

            remaining_attempts = max(0, MAX_FAILED_ATTEMPTS - new_attempts)
            if lock_time:
                return False, (
                    f"🔒 Account locked for {LOCKOUT_MINUTES} minutes after {MAX_FAILED_ATTEMPTS} "
                    f"failed attempts. Please try again later."
                ), None
            elif remaining_attempts <= 2:
                return False, (
                    f"Invalid username or password. "
                    f"⚠️ Warning: {remaining_attempts} attempt(s) remaining before account lockout."
                ), None
            else:
                return False, "Invalid username or password.", None

        # ── Successful login — reset counters, issue new session token ─────
        session_token = secrets.token_urlsafe(32)
        session_expires_at = (datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
        conn.execute(
            """UPDATE users SET
                 session_token = ?,
                 session_expires_at = ?,
                 last_login = CURRENT_TIMESTAMP,
                 failed_login_attempts = 0,
                 locked_until = NULL
               WHERE user_id = ?""",
            (session_token, session_expires_at, user_data["user_id"]),
        )
        conn.commit()
        user_data["session_token"] = session_token
        user_data["session_expires_at"] = session_expires_at
        user_data["last_login"] = datetime.now(timezone.utc).isoformat()
        user_data["failed_login_attempts"] = 0
        return True, "Login successful!", user_data
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[dict]:
    """Fetch a user record by username."""
    u = (username or "").strip().lower()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = ?", (u,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_session_token(token: str) -> Optional[dict]:
    """Fetch a user record by their persistent session token, checking expiry."""
    if not token or not token.strip():
        return None
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE session_token = ? AND session_token IS NOT NULL",
            (token.strip(),),
        ).fetchone()
        if not row:
            return None
        user_data = dict(row)
        # Check session expiry
        expires_at = user_data.get("session_expires_at")
        if expires_at:
            try:
                exp_dt = datetime.fromisoformat(expires_at)
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > exp_dt:
                    # Session expired — clear the token
                    conn.execute(
                        "UPDATE users SET session_token = NULL, session_expires_at = NULL WHERE user_id = ?",
                        (user_data["user_id"],),
                    )
                    conn.commit()
                    return None
            except (ValueError, TypeError):
                pass  # Ignore malformed date
        return user_data
    finally:
        conn.close()


def get_account_security_info(user_id: str) -> dict:
    """
    Return security-relevant info for a user account:
    last login time, failed attempts, lockout status, session expiry.
    """
    user = get_user(user_id)
    if not user:
        return {}
    now = datetime.now(timezone.utc)

    # Determine lockout status
    locked = False
    lock_remaining_min = 0
    locked_until = user.get("locked_until")
    if locked_until:
        try:
            lock_dt = datetime.fromisoformat(locked_until)
            if lock_dt.tzinfo is None:
                lock_dt = lock_dt.replace(tzinfo=timezone.utc)
            if now < lock_dt:
                locked = True
                lock_remaining_min = int((lock_dt - now).total_seconds() / 60) + 1
        except (ValueError, TypeError):
            pass

    # Session expiry
    session_valid = False
    session_expires_str = ""
    expires_at = user.get("session_expires_at")
    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(expires_at)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if now < exp_dt:
                session_valid = True
                session_expires_str = exp_dt.strftime("%d %b %Y, %H:%M UTC")
        except (ValueError, TypeError):
            pass

    last_login = user.get("last_login", "Never")

    return {
        "failed_login_attempts": user.get("failed_login_attempts") or 0,
        "is_locked": locked,
        "lock_remaining_minutes": lock_remaining_min,
        "max_attempts": MAX_FAILED_ATTEMPTS,
        "lockout_minutes": LOCKOUT_MINUTES,
        "session_valid": session_valid,
        "session_expires_at": session_expires_str,
        "session_expiry_days": SESSION_EXPIRY_DAYS,
        "last_login": last_login,
    }


def set_user_session_token(user_id: str, token: Optional[str]) -> None:
    """Set or clear a user's session token."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET session_token = ? WHERE user_id = ?",
            (token, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_user_active_roadmap(user_id: str, roadmap_id: int) -> None:
    """Record the most recently active roadmap for a user."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET last_active_roadmap_id = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (roadmap_id, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def reassign_roadmap_user(roadmap_id: int, new_user_id: str) -> None:
    """Reassign an existing roadmap to a new user account (e.g. converting guest to registered)."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE roadmaps SET user_id = ?, updated_at = CURRENT_TIMESTAMP WHERE roadmap_id = ?",
            (new_user_id, roadmap_id),
        )
        conn.execute(
            "UPDATE users SET last_active_roadmap_id = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (roadmap_id, new_user_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_resume_checkpoint(user_id: str) -> Optional[dict]:
    """
    Find the user's active roadmap, calculate completion statistics,
    and pinpoint the exact week and task where they left off.
    """
    user = get_user(user_id)
    if not user:
        return None

    roadmap_id = user.get("last_active_roadmap_id")
    roadmap = None
    if roadmap_id:
        roadmap = get_roadmap(roadmap_id)

    # Fallback to the latest roadmap if active one not found
    if not roadmap:
        user_roadmaps = get_user_roadmaps(user_id)
        if not user_roadmaps:
            return None
        roadmap_id = user_roadmaps[0]["roadmap_id"]
        roadmap = get_roadmap(roadmap_id)
        if roadmap:
            update_user_active_roadmap(user_id, roadmap_id)

    if not roadmap:
        return None

    weeks = get_roadmap_weeks(roadmap_id)
    summary = get_progress_summary(roadmap_id)
    completed_keys = get_completed_keys(roadmap_id)

    # Find the first incomplete task/topic and its week
    resume_week = 1
    next_task_label = "Complete initial orientation"
    next_task_type = "topic"
    found_pending = False

    for w in weeks:
        wn = w.get("week_number", 1)
        # 1. Check core topics
        for t in w.get("topics", []):
            key = f"topic_{wn}_{t}"
            if key not in completed_keys:
                resume_week = wn
                next_task_label = f"Study Topic: {t}"
                next_task_type = "topic"
                found_pending = True
                break
        if found_pending:
            break

        # 2. Check daily tasks
        for i, task in enumerate(w.get("daily_tasks", [])):
            key = f"task_{wn}_{i}"
            if key not in completed_keys:
                resume_week = wn
                next_task_label = f"Task: {task}"
                next_task_type = "task"
                found_pending = True
                break
        if found_pending:
            break

        # 3. Check coding exercises
        for i, ex in enumerate(w.get("coding_exercises", [])):
            key = f"exercise_{wn}_{i}"
            if key not in completed_keys:
                resume_week = wn
                next_task_label = f"Coding Problem: {ex}"
                next_task_type = "exercise"
                found_pending = True
                break
        if found_pending:
            break

    if not found_pending and weeks:
        resume_week = weeks[-1].get("week_number", 1)
        next_task_label = "All current milestones completed! Review & practice mock interviews."
        next_task_type = "completed"

    # Fetch the most recently completed item
    last_completed_item = None
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT item_label, item_type, week_number, completed_at
               FROM progress WHERE roadmap_id = ? AND is_completed = 1
               ORDER BY completed_at DESC LIMIT 1""",
            (roadmap_id,),
        ).fetchone()
        if row:
            last_completed_item = dict(row)
    finally:
        conn.close()

    return {
        "roadmap_id": roadmap_id,
        "company": roadmap.get("company", "Target Company"),
        "job_role": roadmap.get("job_role", "Software Engineer"),
        "duration_weeks": roadmap.get("duration_weeks", len(weeks)),
        "weekly_hours": roadmap.get("weekly_hours", 0),
        "experience_level": roadmap.get("experience_level", "Beginner"),
        "preferred_language": roadmap.get("preferred_language", "Python"),
        "summary": summary,
        "resume_week": resume_week,
        "next_task": next_task_label,
        "next_task_type": next_task_type,
        "last_completed_item": last_completed_item,
        "total_weeks": len(weeks),
        "weeks": weeks,
        "roadmap_data": roadmap,
    }


def upsert_user(user_id: str, display_name: str = "Student") -> None:
    """Insert or update a user record."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO users (user_id, display_name)
               VALUES (?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                 display_name = excluded.display_name,
                 updated_at = CURRENT_TIMESTAMP""",
            (user_id, display_name),
        )
        conn.commit()
    finally:
        conn.close()


def get_user(user_id: str) -> Optional[dict]:
    """Fetch a user record by user_id."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Roadmap helpers
# ---------------------------------------------------------------------------

def save_roadmap(
    user_id: str,
    company: str,
    job_role: str,
    experience_level: str,
    weekly_hours: float,
    duration_weeks: int,
    skills: list,
    preferred_language: str,
    job_description: str,
    interview_date: str,
    ai_provider: str,
) -> int:
    """Insert a new roadmap and return its roadmap_id."""
    upsert_user(user_id)
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO roadmaps
               (user_id, company, job_role, experience_level, weekly_hours,
                duration_weeks, skills, preferred_language, job_description,
                interview_date, ai_provider)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id, company, job_role, experience_level, weekly_hours,
                duration_weeks, json.dumps(skills), preferred_language,
                job_description, interview_date, ai_provider,
            ),
        )
        conn.commit()
        roadmap_id = cur.lastrowid
        conn.execute(
            "UPDATE users SET last_active_roadmap_id = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (roadmap_id, user_id),
        )
        conn.commit()
        return roadmap_id
    finally:
        conn.close()


def update_roadmap_settings(roadmap_id: int, weekly_hours: float,
                             duration_weeks: int, experience_level: str,
                             skills: list) -> None:
    """Update modifiable roadmap settings (adaptive roadmap)."""
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE roadmaps SET
               weekly_hours = ?, duration_weeks = ?,
               experience_level = ?, skills = ?, updated_at = CURRENT_TIMESTAMP
               WHERE roadmap_id = ?""",
            (weekly_hours, duration_weeks, experience_level,
             json.dumps(skills), roadmap_id),
        )
        conn.commit()
    finally:
        conn.close()


def save_roadmap_weeks(roadmap_id: int, weeks: list[dict]) -> None:
    """Replace all week rows for a roadmap (used during generation/adaptation)."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM roadmap_weeks WHERE roadmap_id = ?", (roadmap_id,))
        conn.executemany(
            """INSERT INTO roadmap_weeks (roadmap_id, week_number, week_data)
               VALUES (?, ?, ?)""",
            [(roadmap_id, w["week_number"], json.dumps(w)) for w in weeks],
        )
        conn.commit()
    finally:
        conn.close()


def get_roadmap(roadmap_id: int) -> Optional[dict]:
    """Fetch roadmap metadata by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM roadmaps WHERE roadmap_id = ?", (roadmap_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["skills"] = json.loads(d["skills"])
        return d
    finally:
        conn.close()


def get_roadmap_weeks(roadmap_id: int) -> list[dict]:
    """Fetch all week records for a roadmap, parsed from JSON."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT week_data FROM roadmap_weeks WHERE roadmap_id = ? ORDER BY week_number",
            (roadmap_id,),
        ).fetchall()
        return [json.loads(r["week_data"]) for r in rows]
    finally:
        conn.close()


def get_user_roadmaps(user_id: str) -> list[dict]:
    """Fetch all roadmaps for a user (metadata only)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT roadmap_id, company, job_role, experience_level,
                      weekly_hours, duration_weeks, ai_provider, created_at
               FROM roadmaps WHERE user_id = ? ORDER BY created_at DESC""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_roadmap(roadmap_id: int) -> None:
    """Delete a roadmap and all its data (cascade)."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM roadmaps WHERE roadmap_id = ?", (roadmap_id,))
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Progress helpers
# ---------------------------------------------------------------------------

def upsert_progress_item(
    roadmap_id: int,
    week_number: int,
    item_type: str,
    item_key: str,
    item_label: str,
    is_completed: bool,
    notes: str = "",
) -> None:
    """Insert or update a single progress item."""
    conn = get_connection()
    completed_at = datetime.now(timezone.utc).isoformat() if is_completed else None
    try:
        conn.execute(
            """INSERT INTO progress
               (roadmap_id, week_number, item_type, item_key, item_label,
                is_completed, completed_at, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(roadmap_id, week_number, item_type, item_key) DO UPDATE SET
                 is_completed = excluded.is_completed,
                 completed_at = excluded.completed_at,
                 item_label = excluded.item_label,
                 notes = excluded.notes""",
            (roadmap_id, week_number, item_type, item_key, item_label,
             int(is_completed), completed_at, notes),
        )
        conn.commit()
    finally:
        conn.close()


def get_progress(roadmap_id: int) -> list[dict]:
    """Fetch all progress items for a roadmap."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM progress WHERE roadmap_id = ? ORDER BY week_number, item_type",
            (roadmap_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_progress_summary(roadmap_id: int) -> dict:
    """Compute overall completion statistics for a roadmap."""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT
               COUNT(*) as total,
               SUM(is_completed) as completed
               FROM progress WHERE roadmap_id = ?""",
            (roadmap_id,),
        ).fetchone()
        total = row["total"] or 0
        completed = row["completed"] or 0
        pct = round((completed / total * 100), 1) if total > 0 else 0.0

        by_type = conn.execute(
            """SELECT item_type,
               COUNT(*) as total,
               SUM(is_completed) as completed
               FROM progress WHERE roadmap_id = ?
               GROUP BY item_type""",
            (roadmap_id,),
        ).fetchall()

        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "percent": pct,
            "by_type": {r["item_type"]: {"total": r["total"], "completed": r["completed"] or 0} for r in by_type},
        }
    finally:
        conn.close()


def get_completed_keys(roadmap_id: int) -> set:
    """Return a set of item_keys that are completed for a roadmap."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT item_key FROM progress WHERE roadmap_id = ? AND is_completed = 1",
            (roadmap_id,),
        ).fetchall()
        return {r["item_key"] for r in rows}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Assessment helpers
# ---------------------------------------------------------------------------

def save_assessment(
    user_id: str,
    roadmap_id: Optional[int],
    company: str,
    job_role: str,
    experience_level: str,
    total_questions: int,
    correct_answers: int,
    score_percent: float,
    time_taken_seconds: int,
    topic_results: list[dict],
) -> int:
    """Save a completed assessment and per-topic results."""
    upsert_user(user_id)
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO assessments
               (user_id, roadmap_id, company, job_role, experience_level,
                total_questions, correct_answers, score_percent, time_taken_seconds)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, roadmap_id, company, job_role, experience_level,
             total_questions, correct_answers, score_percent, time_taken_seconds),
        )
        assessment_id = cur.lastrowid
        conn.executemany(
            """INSERT INTO assessment_results
               (assessment_id, topic, category, total_questions, correct, score_percent)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (assessment_id, r["topic"], r["category"],
                 r["total"], r["correct"], r["score_percent"])
                for r in topic_results
            ],
        )
        conn.commit()
        return assessment_id
    finally:
        conn.close()


def get_user_assessments(user_id: str) -> list[dict]:
    """Fetch all assessment attempts for a user."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT * FROM assessments WHERE user_id = ? ORDER BY attempted_at DESC""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_assessment_results(assessment_id: int) -> list[dict]:
    """Fetch per-topic results for an assessment."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM assessment_results WHERE assessment_id = ?",
            (assessment_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_weak_topics(user_id: str, threshold: float = 50.0) -> list[str]:
    """Return topics where the user's average score is below threshold."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT ar.topic, AVG(ar.score_percent) as avg_score
               FROM assessment_results ar
               JOIN assessments a ON ar.assessment_id = a.assessment_id
               WHERE a.user_id = ?
               GROUP BY ar.topic
               HAVING avg_score < ?
               ORDER BY avg_score ASC""",
            (user_id, threshold),
        ).fetchall()
        return [r["topic"] for r in rows]
    finally:
        conn.close()


def get_all_users() -> list[dict]:
    """Retrieve all registered users with their account metadata for admin overview."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT u.user_id, u.username, u.display_name, u.email, u.role,
                      u.created_at, u.last_login, u.failed_login_attempts,
                      r.company, r.job_role
               FROM users u
               LEFT JOIN roadmaps r ON u.last_active_roadmap_id = r.roadmap_id
               WHERE u.username IS NOT NULL
               ORDER BY u.created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_platform_stats() -> dict:
    """Retrieve platform aggregate statistics for admin dashboard."""
    conn = get_connection()
    try:
        total_users = conn.execute("SELECT COUNT(*) FROM users WHERE username IS NOT NULL").fetchone()[0]
        total_roadmaps = conn.execute("SELECT COUNT(*) FROM roadmaps").fetchone()[0]
        total_assessments = conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
        total_progress = conn.execute("SELECT COUNT(*) FROM progress WHERE is_completed = 1").fetchone()[0]
        return {
            "total_users": total_users,
            "total_roadmaps": total_roadmaps,
            "total_assessments": total_assessments,
            "completed_tasks": total_progress,
        }
    finally:
        conn.close()


def get_all_roadmaps_admin() -> list[dict]:
    """Retrieve all roadmaps across the platform with associated user info."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT r.roadmap_id, r.user_id, r.company, r.job_role, r.experience_level,
                      r.weekly_hours, r.duration_weeks, r.created_at,
                      u.username, u.display_name, u.email
               FROM roadmaps r
               LEFT JOIN users u ON r.user_id = u.user_id
               ORDER BY r.created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_assessments_admin() -> list[dict]:
    """Retrieve all completed assessments with user details for admin review."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT a.assessment_id, a.user_id, a.company, a.job_role, a.total_questions,
                      a.correct_answers, a.score_percent, a.attempted_at,
                      u.username, u.display_name
               FROM assessments a
               LEFT JOIN users u ON a.user_id = u.user_id
               ORDER BY a.attempted_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


