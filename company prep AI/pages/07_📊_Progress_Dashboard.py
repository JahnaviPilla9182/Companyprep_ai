"""
pages/07_📊_Progress_Dashboard.py
Interactive preparation analytics & progress dashboard.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import get_roadmap_weeks, get_progress_summary, init_db, get_user_resume_checkpoint
from backend.core.progress_tracker import (
    build_progress_dataframe, get_week_completion,
    get_strong_weak_topics, get_recommended_next_steps
)
from components.ui_helpers import (
    show_header, show_empty_state, show_metric_card,
    progress_bar_custom, show_info_card, init_session_auth, render_sidebar_auth,
    require_auth
)

init_db()
st.set_page_config(page_title="Progress Dashboard — CompanyPrep AI", page_icon="📊", layout="wide")

require_auth()

with st.sidebar:
    render_sidebar_auth()

show_header("Preparation Progress Dashboard",
            "Real-time analytics, curriculum completion rates, and personalized next actions.", "📊")

roadmap_id = st.session_state.get("roadmap_id")
roadmap_data = st.session_state.get("roadmap_data")

if not roadmap_id and st.session_state.get("user_id"):
    cp = get_user_resume_checkpoint(st.session_state.user_id)
    if cp:
        roadmap_id = cp["roadmap_id"]
        roadmap_data = cp["roadmap_data"]
        st.session_state.roadmap_id = roadmap_id
        st.session_state.roadmap_data = roadmap_data
        st.session_state.roadmap_weeks = cp["weeks"]

if not roadmap_id:
    show_empty_state(
        "No active roadmap found. Create or select a company track first!",
        "📊",
        "Navigate to 📋 Create Roadmap or launch a track from the Home Dashboard."
    )
    st.stop()

weeks = st.session_state.get("roadmap_weeks") or get_roadmap_weeks(roadmap_id)
summary = get_progress_summary(roadmap_id)
df = build_progress_dataframe(roadmap_id)
week_completion = get_week_completion(roadmap_id)
strong, weak = get_strong_weak_topics(roadmap_id)
next_steps = get_recommended_next_steps(roadmap_id, weeks)

# Header KPI metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    show_metric_card("Overall Progress", f"{summary['percent']}%", f"{summary['total']} total curriculum items", "#6366F1")
with col2:
    show_metric_card("Tasks Completed", summary["completed"], "items checked off", "#10B981")
with col3:
    show_metric_card("Pending Work", summary["pending"], "milestones remaining", "#F59E0B")
with col4:
    by_type = summary.get("by_type", {})
    exercises_done = by_type.get("exercise", {}).get("completed", 0)
    show_metric_card("Coding Done", exercises_done, "exercises completed", "#06B6D4")

progress_bar_custom("Overall Curriculum Completion", summary["percent"], color="#6366F1")
st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📈 Progress Analytics", "📅 Week-by-Week Trajectory", "💪 Strength & Focus Areas", "🎯 Recommended Next Steps"])

with tab1:
    if df.empty:
        show_info_card("No items completed yet. Open the Weekly Roadmap and check off completed topics and coding tasks!", "📭", "#06B6D4")
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            with st.container(border=True):
                st.markdown("<h4 style='color:#F8FAFC; margin:0 0 0.8rem 0; font-size:1.05rem;'>Completion by Category</h4>", unsafe_allow_html=True)
                type_df = df.groupby("item_type").agg(
                    total=("is_completed", "count"),
                    done=("is_completed", "sum")
                ).reset_index()
                type_df["pct"] = (type_df["done"] / type_df["total"] * 100).round(1)
                st.bar_chart(type_df.set_index("item_type")["pct"])

        with col_b:
            with st.container(border=True):
                st.markdown("<h4 style='color:#F8FAFC; margin:0 0 0.8rem 0; font-size:1.05rem;'>Status Breakdown</h4>", unsafe_allow_html=True)
                status_df = pd.DataFrame({
                    "Status": ["Completed", "Pending"],
                    "Count": [summary["completed"], summary["pending"]]
                })
                st.bar_chart(status_df.set_index("Status"))

with tab2:
    st.markdown("<h4 style='color:#F8FAFC; margin:0 0 0.8rem 0; font-size:1.1rem;'>Weekly Completion Trajectory</h4>", unsafe_allow_html=True)
    if not week_completion:
        show_info_card("Start checking off daily tasks in the Weekly Roadmap to visualize your weekly progress curve.", "📅", "#6366F1")
    else:
        for wn, pct in sorted(week_completion.items()):
            color = "#10B981" if pct >= 80 else "#6366F1" if pct >= 40 else "#F59E0B"
            progress_bar_custom(f"Week {wn} Progress", pct, color)

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            wk_df = pd.DataFrame([
                {"Week": f"Wk {wn}", "Completion %": pct}
                for wn, pct in sorted(week_completion.items())
            ])
            st.bar_chart(wk_df.set_index("Week"))

with tab3:
    col_s, col_w = st.columns(2)
    with col_s:
        with st.container(border=True):
            st.markdown("<h4 style='color:#34D399; margin:0 0 0.8rem 0; font-size:1.05rem;'>💪 Mastered Topics</h4>", unsafe_allow_html=True)
            if strong:
                chips = " ".join([f"<span style='background:rgba(16, 185, 129, 0.2); border:1px solid rgba(16, 185, 129, 0.4); color:#6EE7B7; border-radius:14px; padding:4px 12px; margin:4px; display:inline-block; font-size:0.86rem; font-weight:600;'>✓ {t}</span>" for t in strong])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.info("Check off completed topics in the Weekly Roadmap to record strengths.")

    with col_w:
        with st.container(border=True):
            st.markdown("<h4 style='color:#FBBF24; margin:0 0 0.8rem 0; font-size:1.05rem;'>📚 Topics Needing Focus</h4>", unsafe_allow_html=True)
            if weak:
                chips = " ".join([f"<span style='background:rgba(245, 158, 11, 0.2); border:1px solid rgba(245, 158, 11, 0.4); color:#FDE68A; border-radius:14px; padding:4px 12px; margin:4px; display:inline-block; font-size:0.86rem; font-weight:600;'>⚠️ {t}</span>" for t in weak])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.success("🎉 All started topics have been checked off! Keep up the momentum.")

with tab4:
    st.markdown("<h4 style='color:#F8FAFC; margin:0 0 0.8rem 0; font-size:1.1rem;'>🎯 Recommended Action Items</h4>", unsafe_allow_html=True)
    if next_steps:
        for step in next_steps:
            show_info_card(step, "→", "#6366F1")
    else:
        st.success("🎉 Excellent! All scheduled tasks are up to date.")

    # Assessment summary
    from database.db_manager import get_user_assessments
    assessments = get_user_assessments(st.session_state.get("user_id", ""))
    if assessments:
        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#F8FAFC; margin:0 0 0.8rem 0; font-size:1.05rem;'>📝 Past Diagnostic Quiz History</h4>", unsafe_allow_html=True)
        with st.container(border=True):
            a_df = pd.DataFrame(assessments)[["attempted_at", "score_percent", "company", "job_role"]]
            a_df["attempted_at"] = a_df["attempted_at"].str[:10]
            a_df.columns = ["Date", "Score (%)", "Company", "Role"]
            st.dataframe(a_df, use_container_width=True)
