"""
pages/02_📋_Create_Roadmap.py
Onboarding form to create a personalized interview preparation roadmap.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.validators import (
    validate_onboarding, KNOWN_COMPANIES, KNOWN_ROLES, EXPERIENCE_LEVELS, LANGUAGES
)
from backend.core.roadmap_generator import generate_roadmap, adapt_roadmap
from database.db_manager import (
    save_roadmap, save_roadmap_weeks, get_roadmap, get_roadmap_weeks,
    get_completed_keys, init_db
)
from components.ui_helpers import (
    show_header, show_disclaimer, show_info_card, show_metric_card,
    init_session_auth, render_sidebar_auth, require_auth
)
from backend.services.llm_service import get_provider_info

init_db()

st.set_page_config(page_title="Create Roadmap — CompanyPrep AI", page_icon="📋", layout="wide")

require_auth()

with st.sidebar:
    render_sidebar_auth()

show_header("Create Preparation Roadmap",
            "Configure your target company, role, available hours, and duration to generate a personalized curriculum.", "📋")

# Check if roadmap exists
existing_roadmap_id = st.session_state.get("roadmap_id")
existing_roadmap = st.session_state.get("roadmap_data")

if existing_roadmap:
    st.markdown(f"""
    <div style='background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.35);
                border-left: 4px solid #6366F1; border-radius: 12px; padding: 0.9rem 1.2rem; margin-bottom: 1.2rem;'>
        <span style='color: #E0E7FF; font-weight: 600;'>
            📌 Active Roadmap Loaded: <strong>{existing_roadmap.get('company')} — {existing_roadmap.get('job_role')}</strong> ({existing_roadmap.get('duration_weeks')} wks @ {existing_roadmap.get('weekly_hours')}h/wk).
        </span>
    </div>
    """, unsafe_allow_html=True)

# Skills options
SKILL_OPTIONS = [
    "Python", "Java", "C++", "C", "JavaScript", "SQL", "Data Structures",
    "Algorithms", "OOP", "DBMS", "Operating Systems", "Computer Networks",
    "System Design", "Machine Learning", "Git", "Linux", "React", "Node.js",
    "Django", "Flask", "Spring Boot", "HTML/CSS", "REST APIs", "Docker",
    "AWS", "MySQL", "MongoDB", "Problem Solving", "Communication Skills",
]

tab1, tab2 = st.tabs(["🆕 Build New Preparation Roadmap", "🔄 Adaptive Roadmap Calibration"])

with tab1:
    with st.form("roadmap_form"):
        st.markdown("<h3 style='color:#F8FAFC; font-weight:700; font-size:1.2rem; margin-bottom:0.8rem;'>🎯 Target Company & Role Profile</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            company_options = ["Select a company..."] + KNOWN_COMPANIES + ["Other (type below)"]
            company_select = st.selectbox("Target Company *", company_options)
            company_custom = ""
            if company_select == "Other (type below)" or company_select == "Select a company...":
                company_custom = st.text_input("Enter company name *", placeholder="e.g., Infosys, TCS, Amazon...")
            company = company_custom if company_select in ["Other (type below)", "Select a company..."] else company_select

            role_options = ["Select a role..."] + KNOWN_ROLES + ["Other (type below)"]
            role_select = st.selectbox("Target Job Role *", role_options)
            role_custom = ""
            if role_select == "Other (type below)" or role_select == "Select a role...":
                role_custom = st.text_input("Enter job role *", placeholder="e.g., Software Engineer, Cloud Associate...")
            job_role = role_custom if role_select in ["Other (type below)", "Select a role..."] else role_select

            experience_level = st.selectbox("Current Experience Level *", EXPERIENCE_LEVELS)
            preferred_language = st.selectbox("Primary Programming Language *", LANGUAGES)

        with col2:
            skills = st.multiselect(
                "Current Technical Skills *",
                SKILL_OPTIONS,
                default=["Python", "SQL", "OOP"],
                help="Select all skills you currently possess. You can add additional skills below."
            )
            custom_skills = st.text_input("Additional specific skills (comma-separated)",
                                           placeholder="e.g., Pandas, NumPy, Redis, GraphQL")
            weekly_hours = st.slider("Available Weekly Study Hours *", min_value=1, max_value=40,
                                      value=10, help="How many hours per week can you realistically dedicate?")
            duration_weeks = st.slider("Target Preparation Duration (weeks) *", min_value=1, max_value=26,
                                        value=8, help="How many weeks until your target interview date?")

        st.markdown("<h3 style='color:#F8FAFC; font-weight:700; font-size:1.2rem; margin-top:1rem; margin-bottom:0.8rem;'>📄 Optional Context</h3>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            interview_date = st.date_input("Target Interview Date (optional)", value=None)
        with col4:
            pass

        job_description = st.text_area(
            "Paste Target Job Description (optional — helps tailor recommended topics)",
            height=130,
            placeholder="Paste excerpts from the official job description here to optimize topic priority..."
        )

        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Generate My Personalized Roadmap", use_container_width=True)

    if submitted:
        # Combine skills
        all_skills = list(skills)
        if custom_skills.strip():
            all_skills.extend([s.strip() for s in custom_skills.split(",") if s.strip()])

        # Sanitize text inputs
        from backend.utils.validators import strip_html_tags, sanitize_html
        clean_company = strip_html_tags(company.strip())
        clean_role = strip_html_tags(job_role.strip())
        clean_jd = sanitize_html(job_description, max_len=5000) if job_description.strip() else ""

        data = {
            "company": clean_company,
            "job_role": clean_role,
            "skills": all_skills,
            "experience_level": experience_level,
            "weekly_hours": weekly_hours,
            "duration_weeks": duration_weeks,
        }

        valid, errors = validate_onboarding(data)
        if not valid:
            st.markdown("""
            <div style='background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.3);
                        border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.5rem;'>
                <div style='color: #F87171; font-weight: 700; margin-bottom: 0.4rem;'>⚠️ Please fix the following errors:</div>
            """, unsafe_allow_html=True)
            for err in errors:
                st.markdown(f"<div style='color:#FCA5A5; font-size:0.88rem; padding:0.2rem 0;'>• {err}</div>",
                            unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            if existing_roadmap and not st.session_state.get("_confirm_overwrite"):
                st.warning("⚠️ You already have an active roadmap. Click 'Generate My Personalized Roadmap' again to confirm replacing it.")
                st.session_state["_confirm_overwrite"] = True
                st.stop()

            st.session_state["_confirm_overwrite"] = False

            with st.spinner("🤖 Calibrating syllabus and building week-by-week schedule..."):
                provider_info = get_provider_info()
                roadmap = generate_roadmap(
                    company=clean_company,
                    job_role=clean_role,
                    skills=all_skills,
                    experience_level=experience_level,
                    weekly_hours=weekly_hours,
                    duration_weeks=duration_weeks,
                    language=preferred_language,
                    job_description=clean_jd,
                )
                # Save to DB
                user_id = st.session_state.get("user_id", "default")
                roadmap_id = save_roadmap(
                    user_id=user_id,
                    company=clean_company,
                    job_role=clean_role,
                    experience_level=experience_level,
                    weekly_hours=weekly_hours,
                    duration_weeks=duration_weeks,
                    skills=all_skills,
                    preferred_language=preferred_language,
                    job_description=clean_jd,
                    interview_date=str(interview_date) if interview_date else "",
                    ai_provider=provider_info["provider"],
                )
                save_roadmap_weeks(roadmap_id, roadmap["weeks"])
                # Store in session
                st.session_state["roadmap_id"] = roadmap_id
                st.session_state["roadmap_data"] = roadmap
                st.session_state["roadmap_weeks"] = roadmap["weeks"]

            st.success(f"✅ Roadmap successfully generated for **{company} — {job_role}**!")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%);
                        border-radius: 16px; padding: 1.4rem 1.6rem; border: 1px solid rgba(16, 185, 129, 0.35);
                        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25); margin: 1.2rem 0;'>
                <h4 style='color: #F8FAFC; margin: 0 0 0.5rem 0; font-size: 1.15rem; font-weight: 700;'>Plan Successfully Generated</h4>
                <div style='display: flex; gap: 1.2rem; flex-wrap: wrap; color: #CBD5E1; font-size: 0.9rem;'>
                    <span>📅 <strong>Timeline:</strong> {duration_weeks} Weeks</span>
                    <span>⏱️ <strong>Workload:</strong> {weekly_hours} hrs/week</span>
                    <span>🎯 <strong>Level:</strong> {experience_level}</span>
                    <span>📦 <strong>Total Modules:</strong> {len(roadmap['weeks'])} Weeks</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            show_disclaimer(roadmap["disclaimer"])
            st.info("👉 Head over to **📅 Weekly Roadmap** to inspect your week-by-week curriculum, or **📊 Progress Dashboard** to monitor milestones.")

with tab2:
    if not existing_roadmap:
        st.info("Please create a roadmap first. Then you can use this tab to adapt it dynamically.")
    else:
        st.markdown("<h3 style='color:#F8FAFC; font-weight:700; font-size:1.2rem; margin-bottom:0.4rem;'>🔄 Adaptive Roadmap Recalibration</h3>", unsafe_allow_html=True)
        show_info_card(
            "Need to change study hours or timeline? The adaptive engine recalculates topic distributions while strictly preserving all your completed tasks.",
            "💡"
        )
        rd = existing_roadmap
        col1, col2 = st.columns(2)
        with col1:
            new_hours = st.slider("Updated Weekly Study Hours", 1, 40, int(rd.get("weekly_hours", 10)))
            new_duration = st.slider("Updated Timeline (weeks)", 1, 26, int(rd.get("duration_weeks", 8)))
        with col2:
            new_exp = st.selectbox("Updated Experience Level",
                                    EXPERIENCE_LEVELS,
                                    index=EXPERIENCE_LEVELS.index(rd.get("experience_level", "Beginner")))
            new_skills = st.multiselect("Updated Skills Set", SKILL_OPTIONS,
                                         default=[s for s in rd.get("skills", []) if s in SKILL_OPTIONS])

        if st.button("🔄 Recalibrate & Adapt Roadmap", type="primary", use_container_width=True):
            rid = st.session_state.get("roadmap_id")
            completed_keys = get_completed_keys(rid) if rid else set()
            with st.spinner("Adapting your schedule with zero task loss..."):
                new_roadmap, changes = adapt_roadmap(
                    existing_roadmap=rd,
                    completed_keys=completed_keys,
                    new_weekly_hours=new_hours,
                    new_duration_weeks=new_duration,
                    new_experience_level=new_exp,
                    new_skills=new_skills,
                )
                if rid:
                    save_roadmap_weeks(rid, new_roadmap["weeks"])
                    from database.db_manager import update_roadmap_settings
                    update_roadmap_settings(rid, new_hours, new_duration, new_exp, new_skills)

                st.session_state["roadmap_data"] = new_roadmap
                st.session_state["roadmap_weeks"] = new_roadmap["weeks"]

            st.success("✅ Roadmap successfully adapted!")
            st.markdown("<h4 style='color:#F8FAFC; margin-top:1rem;'>Audit Log of Changes:</h4>", unsafe_allow_html=True)
            for ch in changes:
                st.markdown(f"• <span style='color:#CBD5E1;'>{ch}</span>", unsafe_allow_html=True)
