"""
backend/core/job_analyzer.py
Analyzes job descriptions to extract skills, requirements, and generate gap analysis.
"""
import re
from typing import Optional

try:
    from backend.services.llm_service import generate_json, generate, DEMO_NOTICE
    from backend.config import DEMO_MODE
except ImportError:
    from services.llm_service import generate_json, generate, DEMO_NOTICE
    from config import DEMO_MODE

# Known technical skills for extraction
KNOWN_SKILLS = [
    "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "Go", "Kotlin", "C#", "Ruby",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQLite", "Redis",
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", "FastAPI",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "CI/CD", "Git",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "scikit-learn",
    "REST API", "GraphQL", "Microservices", "System Design", "Linux", "Shell scripting",
    "Data Structures", "Algorithms", "OOP", "DBMS", "Computer Networks",
    "HTML", "CSS", "Excel", "Tableau", "Power BI", "Agile", "Scrum",
]

EXPERIENCE_PATTERNS = [
    r"(\d+)[\+\-]?\s*(?:to\s*\d+)?\s*years?\s*(?:of\s*)?experience",
    r"experience\s*of\s*(\d+)[\+]?\s*years?",
    r"fresher|fresh\s*graduate|entry.level|0.?1\s*years?",
]


def _extract_skills_regex(text: str) -> list:
    """Extract known skills from text using keyword matching."""
    found = []
    text_lower = text.lower()
    for skill in KNOWN_SKILLS:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


def _extract_experience(text: str) -> str:
    """Extract experience requirements from text."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["fresher", "fresh graduate", "entry level", "entry-level"]):
        return "0-1 years (Fresher/Entry Level)"
    for pat in EXPERIENCE_PATTERNS:
        m = re.search(pat, text_lower)
        if m and m.group(1):
            return f"{m.group(1)}+ years"
    return "Not specified"


def _extract_sections(text: str) -> dict:
    """Split JD into approximate sections."""
    sections = {
        "responsibilities": [],
        "requirements": [],
        "preferred": [],
        "full_text": text,
    }
    lines = text.split("\n")
    current_section = "full"
    for line in lines:
        ll = line.lower().strip()
        if any(w in ll for w in ["responsibilities", "what you will do", "your role", "duties"]):
            current_section = "responsibilities"
        elif any(w in ll for w in ["requirements", "qualifications", "must have", "required skills"]):
            current_section = "requirements"
        elif any(w in ll for w in ["preferred", "nice to have", "good to have", "bonus"]):
            current_section = "preferred"
        elif line.strip().startswith(("•", "-", "*", "✓")) or (line.strip() and current_section != "full"):
            item = line.strip().lstrip("•-*✓ ").strip()
            if item and len(item) > 5:
                sections.get(current_section, sections["requirements"]).append(item)
    return sections


def analyze_job_description(
    jd_text: str,
    user_skills: list,
    company: str = "",
    role: str = "",
) -> dict:
    """
    Analyze a job description and generate a gap analysis.
    Returns structured analysis dict.
    """
    if not jd_text or len(jd_text.strip()) < 20:
        return {"error": "Job description is too short or empty. Please paste a complete JD."}

    sections = _extract_sections(jd_text)
    extracted_skills = _extract_skills_regex(jd_text)
    experience_req = _extract_experience(jd_text)

    # Gap analysis
    user_skills_lower = [s.lower() for s in user_skills]
    matched = []
    missing = []
    for skill in extracted_skills:
        if skill.lower() in user_skills_lower:
            matched.append(skill)
        else:
            missing.append(skill)

    # AI enrichment
    ai_insights = None
    if not DEMO_MODE and len(jd_text) > 50:
        try:
            prompt = f"""Analyze this job description for a {role} position at {company}.
Extract the top 5 most important technical skills and 3 key responsibilities.
JD excerpt (first 1000 chars): {jd_text[:1000]}

Return JSON: {{
  "key_skills": ["skill1", ...],
  "key_responsibilities": ["resp1", ...],
  "experience_level": "Fresher/Junior/Mid/Senior",
  "preparation_tips": ["tip1", "tip2", "tip3"]
}}"""
            ai_result = generate_json(prompt, fallback={})
            if ai_result:
                ai_insights = ai_result
        except Exception:
            pass

    # Build preparation priorities
    priorities = []
    for skill in missing[:5]:
        priorities.append({
            "skill": skill,
            "status": "Missing — needs development",
            "priority": "High",
        })
    for skill in matched[:5]:
        priorities.append({
            "skill": skill,
            "status": "Present in your profile",
            "priority": "Revise & strengthen",
        })

    result = {
        "company": company,
        "role": role,
        "experience_required": experience_req,
        "extracted_skills": extracted_skills,
        "responsibilities": sections["responsibilities"][:10],
        "requirements": sections["requirements"][:10],
        "preferred_skills": sections["preferred"][:5],
        "matched_skills": matched,
        "missing_skills": missing,
        "preparation_priorities": priorities,
        "gap_summary": {
            "total_required": len(extracted_skills),
            "you_have": len(matched),
            "you_need": len(missing),
            "coverage_pct": round(len(matched) / len(extracted_skills) * 100, 1) if extracted_skills else 0,
        },
        "ai_insights": ai_insights,
        "source_note": (
            "Skills extracted using keyword matching from the provided job description. "
            "AI insights (if shown) are generated suggestions, not guaranteed analysis. "
            "Always verify requirements from the official job posting."
        ),
    }

    return result


def read_uploaded_file(uploaded_file) -> tuple[str, str]:
    """
    Read an uploaded Streamlit file object.
    Returns (text_content, error_message).
    Supports .txt and .pdf files.
    """
    if uploaded_file is None:
        return "", "No file provided."

    filename = uploaded_file.name.lower()
    try:
        content = uploaded_file.getvalue()
        if filename.endswith(".txt"):
            return content.decode("utf-8", errors="replace"), ""
        elif filename.endswith(".pdf"):
            try:
                import io
                # Try reading PDF text using simple byte extraction
                pdf_text = content.decode("latin-1", errors="replace")
                # Extract readable text (rough extraction)
                text_parts = re.findall(r"[\x20-\x7E\n\r\t]{20,}", pdf_text)
                extracted = " ".join(text_parts)
                if len(extracted) < 50:
                    return "", "Could not extract text from PDF. Please paste the job description as text instead."
                return extracted[:8000], ""
            except Exception as e:
                return "", f"PDF parsing error: {str(e)}. Please paste the JD as text."
        else:
            return "", "Unsupported file format. Please upload a .txt file or paste text directly."
    except Exception as e:
        return "", f"File reading error: {str(e)}"
