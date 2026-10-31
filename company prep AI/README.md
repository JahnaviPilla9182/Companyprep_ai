# 🎯 CompanyPrep AI — Company-Wise Interview Preparation Roadmap Planner

**Project 08 — GMRIT Grand AI & NLP Student Projects**  
*An intelligent, adaptive, company-specific interview preparation roadmap planner.*

---

## 🌟 Overview

Students and fresh graduates often struggle to prepare for technical placements because they lack a structured roadmap, clarity on company-specific patterns, and targeted practice materials across coding, CS fundamentals, aptitude, and HR rounds.

**CompanyPrep AI** solves this by generating personalized, week-by-week interview preparation plans based on:
- Target Company (e.g., Infosys, TCS, Cognizant, Wipro, Accenture, or any custom firm)
- Target Job Role (e.g., Software Engineer, System Engineer, Junior SE, Data Analyst)
- Current Skill Set & Experience Level (Beginner, Intermediate, Advanced)
- Weekly Study Hours & Target Preparation Duration (weeks)
- Preferred Programming Language (Python, Java, C++, JavaScript)
- Optional Job Description (JD) text/file

> **Important Educational Disclaimer**:  
> CompanyPrep AI is an educational preparation assistant. It does not promise or guarantee job placement, interview selection, salary packages, or official certification outcomes. Company patterns and topics provided are general preparation guidance based on standard industry hiring practices and are not official recruitment disclosures.

---

## 🚀 Key Features

1. **Personalized Week-by-Week Roadmap Planner**
   - Topic distribution calibrated to weekly hours and duration
   - Essential, recommended, and optional topic tagging
   - Suggested daily tasks, coding exercises, practice questions, and milestones
   - Specific out-of-the-box configurations for **Infosys**, **TCS**, **Cognizant**, and **Generic Software Developer**

2. **Adaptive Roadmap Calibration**
   - Change available hours, timeline, or skill level anytime
   - Smart redistribution of pending topics
   - **Zero-loss preservation** of completed tasks and assessment history
   - Change explanation log detailing what shifted and why

3. **Multi-Category AI Interview Question Practice**
   - Curated & AI-generated questions across 7 categories:
     - Technical Fundamentals
     - Programming & Coding (with full code solutions, time/space complexity)
     - Data Structures & Algorithms
     - DBMS & SQL
     - Aptitude & Quantitative Ability (with step-by-step explanations)
     - Logical Reasoning
     - HR & Behavioral Questions (with structured answer frameworks)
   - Unverified questions clearly labeled as *AI-Generated Practice Questions*

4. **Skill Assessment & Gap Calibration**
   - MCQ knowledge checks across Programming, OOP, DSA, DBMS/SQL, and Aptitude
   - Detailed score report, per-category breakdown, and weak-area identification
   - Past assessment attempt history saved in SQLite

5. **Job Description (JD) Analyzer & Gap Analysis**
   - Paste or upload `.txt` job descriptions
   - Extracts required skills, preferred frameworks, and responsibilities
   - Computes a quantitative coverage score (%) and highlights missing skills

6. **Progress Tracking & Analytics Dashboard**
   - Real-time completion percentage and task tracking
   - Pandas-powered aggregation by category and week
   - Visual charts: Item type completion, Week-by-week progress, Strong vs. Weak topics
   - Persistent storage in SQLite that survives app restarts

7. **Targeted Revision Planner**
   - Generates a focused daily revision schedule based on identified weak areas
   - Includes milestone checkpoints and scheduled mock interview reminders

8. **Company Roadmap Comparison**
   - Compare roadmaps for two companies or roles side-by-side
   - Identifies shared core skills vs. company-specific focus areas

9. **Resume & Portfolio Advisor**
   - Role-specific project suggestions, GitHub profile optimization tips, and ATS resume keywords

10. **Study Calendar Export**
    - Instant export of study schedules to **CSV** (for Excel/Google Sheets)
    - Downloadable formatted **PDF** study guide (via `fpdf2` with text fallback)

11. **Graceful Demo Mode (Zero-API Required)**
    - Automatically operates offline in Demo Mode using rich curated banks if no API key is supplied
    - Seamlessly upgrades to live AI with Google Gemini or Groq API keys

12. **User Authentication & Task Resume Engine**
    - Secure user registration, login, and session persistence (salted PBKDF2-HMAC-SHA256 password hashing)
    - Automatically restores active company preparation track, checked off milestones, and exact week upon login
    - "Resume Where You Left Off" hero dashboard with one-click direct jump to the active week
    - Multi-track support: save, switch, and maintain multiple preparation roadmaps simultaneously

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Language** | Python 3.11 / 3.12 / 3.13 | Core backend & scripting |
| **Frontend UI** | Streamlit (v1.63+) | Responsive multi-page web application |
| **Storage** | SQLite3 | Persistent database (`companyprep.db`) |
| **Data Analysis** | Pandas | Progress analysis and reporting |
| **Export Engine** | `fpdf2` & CSV | Study guide PDF & calendar spreadsheet export |
| **Generative AI** | Google Gemini / Groq API | AI enrichment & question generation |
| **Configuration** | `python-dotenv` & Streamlit Secrets | Environment variable configuration |
| **Testing** | `pytest` | Comprehensive unit and integration test suite |

---

## 📁 Project Architecture

```
company-prep-ai/
├── app.py                      # Main entry point & home dashboard
├── requirements.txt            # Python dependencies
├── .env.example                # Template for API keys & config
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation
│
├── .streamlit/
│   └── config.toml             # Streamlit dark theme configuration
│
├── database/
│   ├── schema.sql              # SQLite relational schema (6 tables)
│   ├── db_manager.py           # Thread-safe SQLite CRUD operations
│   └── companyprep.db          # Auto-created SQLite database file
│
├── backend/
│   ├── config.py               # Env & secrets loader with demo mode auto-detection
│   ├── services/
│   │   └── llm_service.py      # LLM abstraction (Gemini + Groq + Demo Fallback)
│   ├── core/
│   │   ├── roadmap_generator.py # Week-by-week generation & adaptive planning
│   │   ├── question_generator.py# 7-category question generator
│   │   ├── progress_tracker.py  # Progress calculations & Pandas analytics
│   │   ├── skill_assessment.py  # MCQ assessment engine & scoring
│   │   ├── job_analyzer.py      # JD parser & skill gap analyzer
│   │   ├── revision_planner.py  # Weak-topic focused revision planner
│   │   ├── resource_manager.py  # Curated reputable free resources (26+ links)
│   │   └── export_manager.py    # CSV and PDF study plan generators
│   └── utils/
│       └── validators.py       # Input validation & sanitization
│
├── components/
│   └── ui_helpers.py           # Reusable UI cards, badges, progress bars, disclaimers
│
├── pages/
│   ├── 02_📋_Create_Roadmap.py       # Onboarding form & adaptive settings
│   ├── 03_📅_Weekly_Roadmap.py       # Week-by-week interactive checkboxes & topics
│   ├── 04_❓_Interview_Questions.py  # Multi-category question practice
│   ├── 05_🎯_Skill_Assessment.py     # Skill assessment quiz & history
│   ├── 06_📄_JD_Analyzer.py          # Job description analysis & skill match
│   ├── 07_📊_Progress_Dashboard.py   # Analytics, charts, and next steps
│   ├── 08_🔄_Revision_Planner.py     # Focused revision schedule
│   ├── 09_⚖️_Compare_Roadmaps.py     # Side-by-side company comparison
│   ├── 10_💼_Resume_Advisor.py       # Portfolio & resume recommendations
│   └── 11_📥_Export_Calendar.py      # CSV / PDF calendar export
│
└── tests/
    ├── conftest.py                   # Pytest fixtures & mock environment
    ├── test_validators.py            # Unit tests for input validation
    ├── test_roadmap_generator.py     # Roadmap generation & constraints tests
    ├── test_question_generator.py    # Question generation tests
    ├── test_progress_tracker.py      # SQLite progress & Pandas tests
    ├── test_exports.py               # CSV and PDF export tests
    └── test_adaptive_roadmap.py      # Adaptive recalculation tests
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/company-prep-ai.git
cd company-prep-ai
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure AI Provider
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to add your API key:
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```
*(If no API key is provided, the application runs automatically in full **Demo Mode** with all features operational.)*

### 5. Launch the application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full pytest suite:
```bash
pytest -v
```

All tests execute in isolated demo mode using mock fixtures; no network calls or API keys are required.

---

## ☁️ Deployment to Streamlit Community Cloud

1. Push your repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Click **New app**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. In **Advanced Settings**, add any necessary secrets (e.g., `GEMINI_API_KEY` or `GROQ_API_KEY`).
5. Click **Deploy!**

---

## 🎓 Academic Integrity & Ethics

- **GMRIT Project Code**: Project 08 — CompanyPrep AI
- **Domain**: Artificial Intelligence, Natural Language Processing, Career Technology
- All AI responses provide verified advice and include disclaimers preventing misrepresentation of actual recruitment processes.
