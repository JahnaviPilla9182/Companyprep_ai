"""
app.py — CompanyPrep AI Entry Point & Role-Based Dashboard
Architecture:
- Landing Page (Public default initial route, no sidebar)
- Login Page (Standalone auth view, no sidebar)
- Role-Based Dashboards (User Dashboard & Admin Dashboard with dedicated sidebar)
"""
import streamlit as st
import uuid
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

# Initialize DB on first run
from database.db_manager import (
    init_db, upsert_user, save_roadmap, save_roadmap_weeks,
    get_progress_summary, get_roadmap, get_roadmap_weeks,
    get_user_resume_checkpoint, update_user_active_roadmap,
    get_user_assessments
)
init_db()

# Page config
st.set_page_config(
    page_title="CompanyPrep AI — Technical Interview Preparation",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.ui_helpers import (
    inject_custom_css, show_header, show_metric_card,
    show_empty_state, show_disclaimer, show_info_card, show_ai_badge,
    progress_bar_custom, init_session_auth, render_sidebar_auth,
    render_login_page, render_landing_page, render_admin_dashboard,
    render_resume_hero_card, render_account_security_card
)
from backend.services.llm_service import get_provider_info
from backend.core.roadmap_generator import generate_roadmap

# Restore session state & auth token
init_session_auth()

# Sync query params with view state
if "view" in st.query_params:
    requested_view = st.query_params["view"]
    if requested_view in ("landing", "login", "dashboard"):
        st.session_state.view = requested_view

user_is_logged_in = st.session_state.get("logged_in", False)

# ---------------------------------------------------------------------------
# Unauthenticated Navigation Flow: Landing Page -> Login Page
# ---------------------------------------------------------------------------
if not user_is_logged_in:
    current_view = st.session_state.get("view", "landing")
    if current_view == "login":
        render_login_page()
        st.stop()
    else:
        render_landing_page()
        st.stop()

# ---------------------------------------------------------------------------
# Authenticated Navigation Flow: Role-Based Dashboard (with Sidebar)
# ---------------------------------------------------------------------------
inject_custom_css(hide_sidebar=False)

user_id = st.session_state.get("user_id")
user_role = st.session_state.get("role", "USER")
display_name = st.session_state.get("display_name", "Student")

# ---- Dashboard Sidebar ----
with st.sidebar:
    st.markdown("""
    <div style='padding: 0.8rem 0.5rem 0.5rem 0.5rem;'>
        <div style='display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.4rem;'>
            <div style='width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #4F46E5, #6366F1);
                        display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #FFF;'>
                🎯
            </div>
            <div>
                <h3 style='margin:0; font-size:1.1rem; font-weight:800; color:#0F172A;'>CompanyPrep AI</h3>
                <span style='color:#64748B; font-size:0.75rem; font-weight:600;'>GMRIT Project 08</span>
            </div>
        </div>
    </div>
    <hr style='border: none; height: 1px; background: #E2E8F0; margin: 0.5rem 0 0.8rem 0;'>
    """, unsafe_allow_html=True)

    # User Profile & Sign Out
    render_sidebar_auth()

    provider_info = get_provider_info()
    show_ai_badge(provider_info["provider"], provider_info["demo_mode"])

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#64748B; letter-spacing:0.06em; margin-bottom:0.4rem;'>Modules</p>", unsafe_allow_html=True)
    st.page_link("app.py", label="🏠 Home Dashboard")
    st.page_link("pages/02_📋_Create_Roadmap.py", label="📋 Create Roadmap")
    st.page_link("pages/03_📅_Weekly_Roadmap.py", label="📅 Weekly Roadmap")
    st.page_link("pages/04_❓_Interview_Questions.py", label="❓ Interview Questions")
    st.page_link("pages/05_🎯_Skill_Assessment.py", label="🎯 Skill Assessment")
    st.page_link("pages/06_📄_JD_Analyzer.py", label="📄 JD Analyzer")
    st.page_link("pages/07_📊_Progress_Dashboard.py", label="📊 Progress Dashboard")
    st.page_link("pages/08_🔄_Revision_Planner.py", label="🔄 Revision Planner")
    st.page_link("pages/09_⚖️_Compare_Roadmaps.py", label="⚖️ Compare Roadmaps")
    st.page_link("pages/10_💼_Resume_Advisor.py", label="💼 Resume Advisor")
    st.page_link("pages/11_📥_Export_Calendar.py", label="📥 Export Calendar")

    st.markdown("""
    <hr style='border: none; height: 1px; background: #E2E8F0; margin: 1.4rem 0 0.8rem 0;'>
    <div style='font-size: 0.75rem; color: #64748B; text-align: center;'>
        CompanyPrep AI • v1.0<br>
        <span style='color: #94A3B8;'>GMRIT Student Project 08</span>
    </div>
    """, unsafe_allow_html=True)


# ---- Role-Based Main Content ----
if user_role == "ADMIN":
    # -----------------------------------------------------------------------
    # Admin Dashboard
    # -----------------------------------------------------------------------
    render_admin_dashboard()
else:
    # -----------------------------------------------------------------------
    # User Dashboard
    # -----------------------------------------------------------------------
    # Welcome Banner
    st.markdown(f"""
    <div style='padding: 1.8rem 2rem; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.03); margin-bottom: 1.8rem;'>
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;'>
            <div>
                <div style='display: inline-flex; align-items: center; gap: 0.4rem; background: #EEF2FF;
                            color: #4338CA; font-size: 0.75rem; font-weight: 700; padding: 2px 10px; border-radius: 12px; margin-bottom: 0.5rem;'>
                    ⚡ STUDENT DASHBOARD
                </div>
                <h1 style='font-size: 2.2rem; font-weight: 800; color: #0F172A; margin: 0 0 0.4rem 0;'>
                    Welcome back, {display_name}! 👋
                </h1>
                <p style='color: #64748B; font-size: 0.98rem; margin: 0; max-width: 800px;'>
                    Track your registered interview preparation tracks, resume where you stopped, review past assessment scores, and practice coding challenges.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active Registered Tracks & Resume Checkpoint
    checkpoint = get_user_resume_checkpoint(user_id) if user_id else None
    if checkpoint:
        if not st.session_state.get("roadmap_id"):
            st.session_state.roadmap_id = checkpoint["roadmap_id"]
            st.session_state.roadmap_data = checkpoint["roadmap_data"]
            st.session_state.roadmap_weeks = checkpoint["weeks"]
        render_resume_hero_card(checkpoint)
    else:
        st.markdown("""
        <div style='background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 16px; padding: 1.8rem; text-align: center; margin-bottom: 1.8rem;'>
            <div style='font-size: 2.2rem; margin-bottom: 0.4rem;'>📋</div>
            <h3 style='margin: 0 0 0.3rem 0; color: #0F172A; font-size: 1.2rem; font-weight: 700;'>No Active Track Registered Yet</h3>
            <p style='color: #64748B; font-size: 0.92rem; margin: 0 0 1.2rem 0; max-width: 580px; margin-inline: auto;'>
                Select one of the 1-click curated company tracks below or build a custom curriculum to start generating and tracking your tasks.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Previous Submissions & Assessment Results
    st.markdown("<h3 style='color:#0F172A; font-weight:800; font-size:1.3rem; margin: 1.5rem 0 0.6rem 0;'>📊 Previous Submissions & Assessment Results</h3>", unsafe_allow_html=True)
    user_assessments = get_user_assessments(user_id) if user_id else []
    if user_assessments:
        avg_score = round(sum(a["score_percent"] for a in user_assessments) / len(user_assessments), 1)
        passed_count = sum(1 for a in user_assessments if a["score_percent"] >= 60)
        col_as1, col_as2, col_as3, col_as4 = st.columns(4)
        with col_as1:
            show_metric_card("Total Attempts", len(user_assessments), color="#4F46E5")
        with col_as2:
            show_metric_card("Average Score", f"{avg_score}%", color="#059669")
        with col_as3:
            show_metric_card("Passed Assessments", f"{passed_count} / {len(user_assessments)}", color="#0284C7")
        with col_as4:
            show_metric_card("Latest Score", f"{user_assessments[0]['score_percent']}%", color="#7C3AED")

        import pandas as pd
        df_as = pd.DataFrame(user_assessments)
        df_as["Status"] = df_as["score_percent"].apply(lambda s: "Passed ✅" if s >= 60 else "Review Needed ⚠️")
        cols = ["company", "job_role", "score_percent", "correct_answers", "total_questions", "attempted_at", "Status"]
        existing = [c for c in cols if c in df_as.columns]
        st.dataframe(df_as[existing], use_container_width=True)
    else:
        col_empty1, col_empty2 = st.columns([3, 1])
        with col_empty1:
            st.markdown("""
            <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.02);'>
                <div style='font-weight: 700; color: #0F172A; font-size: 1rem; margin-bottom: 0.2rem;'>🎯 Upcoming / Unattempted Diagnostic Assessment</div>
                <p style='color: #64748B; font-size: 0.88rem; margin: 0;'>
                    Take our 10-question MCQ diagnostic quiz to evaluate your technical readiness across DSA, OOP, DBMS, OS, and Networks. Your weaknesses will automatically calibrate your roadmap.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_empty2:
            st.page_link("pages/05_🎯_Skill_Assessment.py", label="🎯 Take Assessment Now", use_container_width=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 1-Click Target Company Tracks (Available Contests)
    st.markdown("<h3 style='color:#0F172A; font-weight:800; font-size:1.3rem; margin-bottom:0.3rem;'>⚡ Available Target Company Tracks & Contests</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:0.9rem; margin-bottom:1rem;'>Select a verified curriculum track to preview focus areas and generate your schedule instantly.</p>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container(border=True):
            st.markdown("""
            <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;'>
                <span style='font-size: 1.4rem;'>🔷</span>
                <h4 style='margin: 0; color: #0F172A; font-size: 1.1rem; font-weight: 800;'>Infosys</h4>
            </div>
            <p style='color: #0284C7; font-size: 0.8rem; font-weight: 700; margin: 0 0 0.5rem 0;'>System Engineer</p>
            <p style='color: #475569; font-size: 0.82rem; line-height: 1.45; margin: 0 0 0.8rem 0;'>
                Focus on Pseudo-code, Logical Reasoning, OOP, and Python/Java foundations.
            </p>
            <div style='color: #64748B; font-size: 0.75rem; margin-bottom: 0.8rem;'>
                ⏱️ 8 Weeks • 10 hrs/week
            </div>
            """, unsafe_allow_html=True)
            if st.button("Generate Infosys Track", key="btn_infosys", use_container_width=True):
                with st.spinner("Building Infosys preparation track..."):
                    rm = generate_roadmap("Infosys", "System Engineer", ["Python", "SQL", "OOP"], "Beginner", 10, 8, "Python")
                    rid = save_roadmap(st.session_state.user_id, "Infosys", "System Engineer", "Beginner", 10, 8, ["Python", "SQL", "OOP"], "Python", "", "", "demo")
                    save_roadmap_weeks(rid, rm["weeks"])
                    st.session_state.roadmap_id = rid
                    st.session_state.roadmap_data = rm
                    st.session_state.roadmap_weeks = rm["weeks"]
                    st.success("✅ Infosys Roadmap generated!")
                    st.rerun()

    with c2:
        with st.container(border=True):
            st.markdown("""
            <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;'>
                <span style='font-size: 1.4rem;'>🟣</span>
                <h4 style='margin: 0; color: #0F172A; font-size: 1.1rem; font-weight: 800;'>TCS</h4>
            </div>
            <p style='color: #7C3AED; font-size: 0.8rem; font-weight: 700; margin: 0 0 0.5rem 0;'>Software Engineer</p>
            <p style='color: #475569; font-size: 0.82rem; line-height: 1.45; margin: 0 0 0.8rem 0;'>
                NQT Cognitive Ability, Advanced Coding, DSA problem solving, and DBMS queries.
            </p>
            <div style='color: #64748B; font-size: 0.75rem; margin-bottom: 0.8rem;'>
                ⏱️ 8 Weeks • 12 hrs/week
            </div>
            """, unsafe_allow_html=True)
            if st.button("Generate TCS Track", key="btn_tcs", use_container_width=True):
                with st.spinner("Building TCS preparation track..."):
                    rm = generate_roadmap("TCS", "Software Engineer", ["Python", "SQL", "DSA"], "Beginner", 12, 8, "Python")
                    rid = save_roadmap(st.session_state.user_id, "TCS", "Software Engineer", "Beginner", 12, 8, ["Python", "SQL", "DSA"], "Python", "", "", "demo")
                    save_roadmap_weeks(rid, rm["weeks"])
                    st.session_state.roadmap_id = rid
                    st.session_state.roadmap_data = rm
                    st.session_state.roadmap_weeks = rm["weeks"]
                    st.success("✅ TCS Roadmap generated!")
                    st.rerun()

    with c3:
        with st.container(border=True):
            st.markdown("""
            <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;'>
                <span style='font-size: 1.4rem;'>💠</span>
                <h4 style='margin: 0; color: #0F172A; font-size: 1.1rem; font-weight: 800;'>Cognizant</h4>
            </div>
            <p style='color: #0284C7; font-size: 0.8rem; font-weight: 700; margin: 0 0 0.5rem 0;'>Junior SE (GenC)</p>
            <p style='color: #475569; font-size: 0.82rem; line-height: 1.45; margin: 0 0 0.8rem 0;'>
                Automata Fix code debugging, Quantitative Aptitude, and CS fundamentals.
            </p>
            <div style='color: #64748B; font-size: 0.75rem; margin-bottom: 0.8rem;'>
                ⏱️ 6 Weeks • 10 hrs/week
            </div>
            """, unsafe_allow_html=True)
            if st.button("Generate Cognizant Track", key="btn_cts", use_container_width=True):
                with st.spinner("Building Cognizant preparation track..."):
                    rm = generate_roadmap("Cognizant", "Junior Software Engineer", ["Python", "SQL", "OOP"], "Beginner", 10, 6, "Python")
                    rid = save_roadmap(st.session_state.user_id, "Cognizant", "Junior Software Engineer", "Beginner", 10, 6, ["Python", "SQL", "OOP"], "Python", "", "", "demo")
                    save_roadmap_weeks(rid, rm["weeks"])
                    st.session_state.roadmap_id = rid
                    st.session_state.roadmap_data = rm
                    st.session_state.roadmap_weeks = rm["weeks"]
                    st.success("✅ Cognizant Roadmap generated!")
                    st.rerun()

    with c4:
        with st.container(border=True):
            st.markdown("""
            <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;'>
                <span style='font-size: 1.4rem;'>🟢</span>
                <h4 style='margin: 0; color: #0F172A; font-size: 1.1rem; font-weight: 800;'>Generic SDE</h4>
            </div>
            <p style='color: #059669; font-size: 0.8rem; font-weight: 700; margin: 0 0 0.5rem 0;'>Entry Level Developer</p>
            <p style='color: #475569; font-size: 0.82rem; line-height: 1.45; margin: 0 0 0.8rem 0;'>
                Comprehensive CS fundamentals, DSA patterns, System Design basics, and Git.
            </p>
            <div style='color: #64748B; font-size: 0.75rem; margin-bottom: 0.8rem;'>
                ⏱️ 10 Weeks • 12 hrs/week
            </div>
            """, unsafe_allow_html=True)
            if st.button("Generate SDE Track", key="btn_sde", use_container_width=True):
                with st.spinner("Building Generic SDE preparation track..."):
                    rm = generate_roadmap("Generic Software Developer", "Software Developer", ["Python", "SQL", "DSA", "OOP"], "Beginner", 12, 10, "Python")
                    rid = save_roadmap(st.session_state.user_id, "Generic Software Developer", "Software Developer", "Beginner", 12, 10, ["Python", "SQL", "DSA", "OOP"], "Python", "", "", "demo")
                    save_roadmap_weeks(rid, rm["weeks"])
                    st.session_state.roadmap_id = rid
                    st.session_state.roadmap_data = rm
                    st.session_state.roadmap_weeks = rm["weeks"]
                    st.success("✅ Generic SDE Roadmap generated!")
                    st.rerun()

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Core Preparation Modules
    st.markdown("<h3 style='color:#0F172A; font-weight:800; font-size:1.3rem; margin-bottom:0.3rem;'>🛠️ Essential Preparation Modules</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:0.9rem; margin-bottom:1rem;'>Everything you need to systematically prepare, practice, and test readiness.</p>", unsafe_allow_html=True)

    mcol1, mcol2, mcol3 = st.columns(3)

    with mcol1:
        with st.container(border=True):
            st.markdown("""
            <div style='font-size: 1.8rem; margin-bottom: 0.4rem;'>❓</div>
            <h4 style='color: #0F172A; margin: 0 0 0.3rem 0; font-size: 1.05rem; font-weight: 700;'>Interview Questions</h4>
            <p style='color: #64748B; font-size: 0.85rem; line-height: 1.45; margin-bottom: 0.8rem;'>
                Practice coding challenges with complete code solutions and complexity analysis, aptitude, and HR questions.
            </p>
            """, unsafe_allow_html=True)
            st.page_link("pages/04_❓_Interview_Questions.py", label="→ Practice Questions", use_container_width=True)

    with mcol2:
        with st.container(border=True):
            st.markdown("""
            <div style='font-size: 1.8rem; margin-bottom: 0.4rem;'>🎯</div>
            <h4 style='color: #0F172A; margin: 0 0 0.3rem 0; font-size: 1.05rem; font-weight: 700;'>Skill Assessment</h4>
            <p style='color: #64748B; font-size: 0.85rem; line-height: 1.45; margin-bottom: 0.8rem;'>
                10-question MCQ diagnostic quiz pinpointing topic-level weaknesses to calibrate your roadmap priorities.
            </p>
            """, unsafe_allow_html=True)
            st.page_link("pages/05_🎯_Skill_Assessment.py", label="→ Take Assessment", use_container_width=True)

    with mcol3:
        with st.container(border=True):
            st.markdown("""
            <div style='font-size: 1.8rem; margin-bottom: 0.4rem;'>📄</div>
            <h4 style='color: #0F172A; margin: 0 0 0.3rem 0; font-size: 1.05rem; font-weight: 700;'>JD Gap Analyzer</h4>
            <p style='color: #64748B; font-size: 0.85rem; line-height: 1.45; margin-bottom: 0.8rem;'>
                Paste or upload job descriptions to extract skill requirements and compute your candidate readiness score.
            </p>
            """, unsafe_allow_html=True)
            st.page_link("pages/06_📄_JD_Analyzer.py", label="→ Analyze JD", use_container_width=True)

    mcol4, mcol5, mcol6 = st.columns(3)

    with mcol4:
        with st.container(border=True):
            st.markdown("""
            <div style='font-size: 1.8rem; margin-bottom: 0.4rem;'>🔄</div>
            <h4 style='color: #0F172A; margin: 0 0 0.3rem 0; font-size: 1.05rem; font-weight: 700;'>Revision Planner</h4>
            <p style='color: #64748B; font-size: 0.85rem; line-height: 1.45; margin-bottom: 0.8rem;'>
                Focused daily revision schedules targeting weak areas leading up to your interview date.
            </p>
            """, unsafe_allow_html=True)
            st.page_link("pages/08_🔄_Revision_Planner.py", label="→ Plan Revision", use_container_width=True)

    with mcol5:
        with st.container(border=True):
            st.markdown("""
            <div style='font-size: 1.8rem; margin-bottom: 0.4rem;'>⚖️</div>
            <h4 style='color: #0F172A; margin: 0 0 0.3rem 0; font-size: 1.05rem; font-weight: 700;'>Compare Roadmaps</h4>
            <p style='color: #64748B; font-size: 0.85rem; line-height: 1.45; margin-bottom: 0.8rem;'>
                Side-by-side curriculum overlap comparison between two companies or job roles.
            </p>
            """, unsafe_allow_html=True)
            st.page_link("pages/09_⚖️_Compare_Roadmaps.py", label="→ Compare Tracks", use_container_width=True)

    with mcol6:
        with st.container(border=True):
            st.markdown("""
            <div style='font-size: 1.8rem; margin-bottom: 0.4rem;'>📥</div>
            <h4 style='color: #0F172A; margin: 0 0 0.3rem 0; font-size: 1.05rem; font-weight: 700;'>Export Study Plan</h4>
            <p style='color: #64748B; font-size: 0.85rem; line-height: 1.45; margin-bottom: 0.8rem;'>
                Download your customized study schedule as a spreadsheet CSV or printable PDF guide.
            </p>
            """, unsafe_allow_html=True)
            st.page_link("pages/11_📥_Export_Calendar.py", label="→ Export Plan", use_container_width=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Account Settings & Security Card
    render_account_security_card(user_id)

# Global Footer Disclaimer
show_disclaimer(
    "CompanyPrep AI is an educational preparation assistant developed under GMRIT Student Project guidelines (Project 08). "
    "It does not promise, warrant, or guarantee job placement, interview clearing, salary packages, or official recruitment selections. "
    "Company-specific curriculum models are general preparation guidance based on standard industry hiring patterns and are not official "
    "recruitment disclosures."
)
