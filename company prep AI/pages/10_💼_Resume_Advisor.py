"""
pages/10_💼_Resume_Advisor.py
Resume and portfolio recommendations based on target role and job description.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.llm_service import generate, get_provider_info, DEMO_NOTICE
from backend.config import DEMO_MODE
from components.ui_helpers import (
    show_header, show_disclaimer, show_info_card, show_metric_card,
    init_session_auth, render_sidebar_auth, require_auth
)
from backend.utils.validators import KNOWN_ROLES

st.set_page_config(page_title="Resume Advisor — CompanyPrep AI", page_icon="💼", layout="wide")

require_auth()

with st.sidebar:
    render_sidebar_auth()
show_header("Resume & Portfolio Advisor",
            "Tailored portfolio project concepts, GitHub profile optimization strategies, and ATS resume keywords.", "💼")

show_disclaimer(
    "These suggestions represent skill development guidelines and do NOT guarantee ATS clearing or interview shortlisting. "
    "Never fabricate project experience or claim skills you have not actively practiced."
)

roadmap = st.session_state.get("roadmap_data")
if roadmap:
    company = roadmap.get("company", "")
    role = roadmap.get("job_role", "Software Engineer")
    skills = roadmap.get("skills", [])
    language = roadmap.get("language", "Python")
    st.markdown(f"""
    <div style='background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.35);
                border-radius: 12px; padding: 0.8rem 1.2rem; margin-bottom: 1rem;'>
        📌 Profile Active: <strong style='color:#C7D2FE;'>{company} — {role}</strong> ({language})
    </div>
    """, unsafe_allow_html=True)
else:
    col_ra1, col_ra2 = st.columns(2)
    with col_ra1:
        role = st.selectbox("Target Job Role", KNOWN_ROLES)
        company = st.text_input("Target Company", value="TCS")
    with col_ra2:
        skills = st.multiselect("Current Skills",
                                 ["Python", "Java", "SQL", "DSA", "OOP", "React", "Node.js", "Git"],
                                 default=["Python", "DSA"])
        language = st.selectbox("Primary Programming Language", ["Python", "Java", "C++", "JavaScript"])

jd_text = st.text_area(
    "Paste Excerpt from Target Job Description (optional — helps tailor keywords)",
    height=110,
    placeholder="Paste job description requirements to extract targeted keywords..."
)
if jd_text.strip():
    jd_len = len(jd_text.strip())
    if jd_len > 5000:
        st.warning(f"⚠️ JD excerpt is {jd_len:,} characters — only the first 500 characters will be used for AI context.")

if st.button("💼 Generate Portfolio & Resume Blueprint", type="primary", use_container_width=True):
    # Input validation
    from backend.utils.validators import validate_role, validate_company, sanitize_html
    role_ok, role_err = validate_role(role)
    company_ok, company_err = validate_company(company)
    if not role_ok:
        st.error(f"❌ {role_err}")
        st.stop()
    if not company_ok:
        st.error(f"❌ {company_err}")
        st.stop()
    if not skills:
        st.error("❌ Please select at least one skill before generating recommendations.")
        st.stop()
    # Sanitize JD
    safe_jd = sanitize_html(jd_text, max_len=5000) if jd_text.strip() else ""
    with st.spinner("Compiling industry recommendations and project architectures..."):
        if DEMO_MODE:
            recommendations = {
                "portfolio_projects": [
                    f"Full-Stack CRUD REST API using {language} and SQLite with JWT authentication and documentation",
                    f"Automated Data Ingestion & ETL Pipeline in Python with Pandas for financial or retail data",
                    "Task Management Dashboard with real-time status tracking and unit test coverage",
                    f"Command-Line Systems Utility in {language} parsing structured logs and reporting anomalies",
                    "Personal Portfolio & Project Showcase hosted on GitHub Pages or Vercel with clean README",
                ],
                "github_tips": [
                    "Author a comprehensive README.md for every repository: problem context, architecture, setup steps, and tests",
                    "Include a requirements.txt or environment configuration file to enable effortless 1-click reproduction",
                    "Maintain continuous commit hygiene with conventional commits (e.g. feat:, fix:, docs:, test:)",
                    "Incorporate automated unit testing via GitHub Actions CI workflow to demonstrate code quality",
                    "Pin your 4 most technically challenging and polished repositories to your public GitHub profile",
                ],
                "resume_keywords": [
                    "Data Structures & Algorithms", "Object-Oriented Programming",
                    "REST APIs", "SQL / Database Design", "Git / Version Control",
                    f"{language} Programming", "Problem Solving", "CI/CD & Testing",
                    "Agile / Scrum Methodologies", "System Architecture",
                ],
                "skills_to_develop": [
                    s for s in ["System Design", "Docker & Containers", "Cloud (AWS / GCP)", "CI/CD Pipelines"]
                    if s not in skills
                ][:4],
                "source": "demo",
            }
        else:
            provider_info = get_provider_info()
            prompt = f"""You are a senior tech hiring consultant.
Provide strategic advice for a {role} applicant at {company}.
Current skills: {', '.join(skills)}. Preferred language: {language}.
{f'Job description excerpt: {safe_jd[:500]}' if safe_jd else ''}

Return valid JSON with keys:
- portfolio_projects: list of 5 high-impact project ideas tailored to the role
- github_tips: list of 5 actionable GitHub profile enhancement tips
- resume_keywords: list of 8 essential keywords for the resume
- skills_to_develop: list of 4 skills the candidate should learn next

IMPORTANT: All recommendations must be honest skill development advice."""
            result_text = generate(prompt)
            try:
                import json, re
                cleaned = result_text.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"```\w*\n?", "", cleaned).strip()
                recommendations = json.loads(cleaned)
                recommendations["source"] = "ai"
            except Exception:
                recommendations = {"error": result_text[:200], "source": "ai_raw"}
        st.session_state["resume_recommendations"] = recommendations

recs = st.session_state.get("resume_recommendations")
if recs:
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    if recs.get("source") == "demo":
        st.info("🟢 **Curated Mode** — Presenting vetted industry-standard recommendations.")
    elif recs.get("source") == "ai":
        st.success("✨ **AI-Generated Recommendations** — Tailored to your specified role & JD.")

    if "error" in recs:
        st.warning(f"Generation output format unexpected. Please retry. ({recs['error'][:100]})")
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["🛠️ Portfolio Projects", "🐙 GitHub Excellence", "📄 ATS Keywords", "📚 High-Priority Skills"])

        with tab1:
            st.markdown("<h4 style='color:#F8FAFC;'>Targeted Portfolio Projects:</h4>", unsafe_allow_html=True)
            for i, p in enumerate(recs.get("portfolio_projects", []), 1):
                show_info_card(p, f"#{i}", "#6366F1")

        with tab2:
            st.markdown("<h4 style='color:#F8FAFC;'>GitHub Profile Best Practices:</h4>", unsafe_allow_html=True)
            for tip in recs.get("github_tips", []):
                show_info_card(tip, "🐙", "#10B981")

        with tab3:
            st.markdown("<h4 style='color:#F8FAFC;'>Recommended ATS Resume Keywords:</h4>", unsafe_allow_html=True)
            keywords = recs.get("resume_keywords", [])
            kw_html = " ".join(
                f"<span style='background:rgba(99, 102, 241, 0.22); border:1px solid rgba(99, 102, 241, 0.45); border-radius:18px; padding:6px 14px; margin:4px; display:inline-block; font-weight:600; color:#E0E7FF; font-size:0.9rem;'>{kw}</span>"
                for kw in keywords
            )
            st.markdown(f"<div style='margin: 0.8rem 0;'>{kw_html}</div>", unsafe_allow_html=True)

        with tab4:
            st.markdown("<h4 style='color:#F8FAFC;'>Emerging Skills to Expand Your Profile:</h4>", unsafe_allow_html=True)
            for s in recs.get("skills_to_develop", []):
                show_info_card(s, "📚", "#F59E0B")
else:
    show_info_card("Click 'Generate Portfolio & Resume Blueprint' above to receive tailored recommendations.", "💼", "#06B6D4")
