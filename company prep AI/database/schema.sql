-- CompanyPrep AI — SQLite Schema
-- Version: 1.0

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    salt TEXT,
    display_name TEXT DEFAULT 'Student',
    email TEXT DEFAULT '',
    session_token TEXT,
    last_active_roadmap_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roadmaps (
    roadmap_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    company TEXT NOT NULL,
    job_role TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    weekly_hours REAL NOT NULL,
    duration_weeks INTEGER NOT NULL,
    skills TEXT NOT NULL,
    preferred_language TEXT DEFAULT 'Python',
    job_description TEXT DEFAULT '',
    interview_date TEXT DEFAULT '',
    ai_provider TEXT DEFAULT 'demo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS roadmap_weeks (
    week_id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadmap_id INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    week_data TEXT NOT NULL,  -- JSON blob
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadmap_id INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    item_type TEXT NOT NULL,  -- 'topic', 'task', 'exercise', 'question', 'project', 'assessment'
    item_key TEXT NOT NULL,
    item_label TEXT NOT NULL,
    is_completed INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    notes TEXT DEFAULT '',
    FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id) ON DELETE CASCADE,
    UNIQUE(roadmap_id, week_number, item_type, item_key)
);

CREATE TABLE IF NOT EXISTS assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    roadmap_id INTEGER,
    company TEXT NOT NULL,
    job_role TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    score_percent REAL NOT NULL,
    time_taken_seconds INTEGER DEFAULT 0,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id)
);

CREATE TABLE IF NOT EXISTS assessment_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    category TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct INTEGER NOT NULL,
    score_percent REAL NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_roadmaps_user ON roadmaps(user_id);
CREATE INDEX IF NOT EXISTS idx_roadmap_weeks_roadmap ON roadmap_weeks(roadmap_id);
CREATE INDEX IF NOT EXISTS idx_progress_roadmap ON progress(roadmap_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user ON assessments(user_id);
