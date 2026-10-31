"""
pages/03_📅_Weekly_Roadmap.py
Displays the week-by-week preparation roadmap with interactive completion checkboxes.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import (
    get_roadmap_weeks, get_completed_keys, init_db,
    get_user_resume_checkpoint, get_roadmap
)
from components.ui_helpers import (
    show_header, show_empty_state, show_disclaimer, progress_bar_custom,
    topic_checkbox, show_resource_card, show_metric_card,
    init_session_auth, render_sidebar_auth, require_auth
)
from backend.core.progress_tracker import mark_item, get_summary
from backend.core.resource_manager import get_resources_for_topic

init_db()
st.set_page_config(page_title="Weekly Roadmap — CompanyPrep AI", page_icon="📅", layout="wide")

# Ensure session auth is synced & authenticated
require_auth()

with st.sidebar:
    render_sidebar_auth()

show_header("Weekly Roadmap",
            "Your week-by-week preparation plan. Check off topics and tasks as you complete them.", "📅")

roadmap_id = st.session_state.get("roadmap_id")
roadmap_data = st.session_state.get("roadmap_data")

# If roadmap is not in session state, attempt to restore from user checkpoint
if (not roadmap_id or not roadmap_data) and st.session_state.get("user_id"):
    cp = get_user_resume_checkpoint(st.session_state.user_id)
    if cp:
        roadmap_id = cp["roadmap_id"]
        roadmap_data = cp["roadmap_data"]
        st.session_state.roadmap_id = roadmap_id
        st.session_state.roadmap_data = roadmap_data
        st.session_state.roadmap_weeks = cp["weeks"]

if not roadmap_id or not roadmap_data:
    show_empty_state(
        "No active roadmap found. Create one first or log in!",
        "📭",
        "Navigate to 📋 Create Roadmap to build your schedule, or log in on the Home Dashboard to resume your progress."
    )
    st.stop()

weeks = st.session_state.get("roadmap_weeks") or get_roadmap_weeks(roadmap_id)
completed_keys = get_completed_keys(roadmap_id)

# Summary metrics row
summary = get_summary(roadmap_id)
col1, col2, col3, col4 = st.columns(4)
with col1:
    show_metric_card("Total Timeline", f"{roadmap_data.get('duration_weeks', 0)} Weeks", f"Allocated: {roadmap_data.get('weekly_hours', 0)}h/wk", "#6366F1")
with col2:
    show_metric_card("Completed Tasks", summary["completed"], "items checked off", "#10B981")
with col3:
    show_metric_card("Pending Items", summary["pending"], "topics & tasks left", "#F59E0B")
with col4:
    show_metric_card("Overall Progress", f"{summary['percent']}%", "roadmap completion", "#06B6D4")

progress_bar_custom("Overall Roadmap Completion", summary["percent"], color="#6366F1")
st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# Week selector dropdown with automatic resume week pre-selection
week_nums = [w["week_number"] for w in weeks]

resume_week_target = st.session_state.pop("selected_week_resume", None)
if resume_week_target is None and st.session_state.get("user_id"):
    cp = get_user_resume_checkpoint(st.session_state.user_id)
    if cp and cp.get("roadmap_id") == roadmap_id:
        resume_week_target = cp.get("resume_week", 1)

if resume_week_target is None:
    resume_week_target = 1

default_idx = week_nums.index(resume_week_target) if resume_week_target in week_nums else 0

selected_week = st.selectbox(
    "📅 Select Week to View",
    week_nums,
    index=default_idx,
    format_func=lambda x: f"Week {x} — {', '.join(next((w.get('topics',[]) for w in weeks if w['week_number'] == x), []))[:45]}..."
)

week = next((w for w in weeks if w["week_number"] == selected_week), None)
if not week:
    st.error("Week data not found.")
    st.stop()

# Styled Week Header Card
wn = week["week_number"]
topics = week.get("topics", [])
hours = week.get("estimated_hours", 0)

st.markdown(f"""
<div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
            border-radius: 16px; padding: 1.4rem 1.8rem; border: 1px solid rgba(99, 102, 241, 0.35);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25); margin-bottom: 1.5rem;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;'>
    <div>
        <div style='display: flex; align-items: center; gap: 0.6rem;'>
            <h2 style='color: #F8FAFC; margin: 0; font-size: 1.5rem; font-weight: 800;'>Week {wn} Curriculum</h2>
            <span style='background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4);
                         color: #C7D2FE; font-size: 0.78rem; font-weight: 700; padding: 0.2rem 0.7rem; border-radius: 20px;'>
                {len(topics)} Topics
            </span>
        </div>
        <p style='color: #94A3B8; margin: 0.35rem 0 0 0; font-size: 0.92rem;'>
            Key Focus: <strong style='color: #E2E8F0;'>{', '.join(topics)}</strong>
        </p>
    </div>
    <div>
        <span style='background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.4);
                     color: #67E8F9; font-size: 0.9rem; font-weight: 700; padding: 0.4rem 1rem; border-radius: 12px;'>
            ⏱️ {hours} Study Hours Target
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs for week content
t1, t2, t3, t4, t5 = st.tabs(["📚 Core Topics", "✅ Daily Tasks", "💻 Coding Exercises", "❓ Practice Questions", "🔗 Free Resources"])

with t1:
    st.subheader("📚 Weekly Learning Objectives")
    objectives = week.get("objectives", [])
    for i, topic in enumerate(topics):
        obj = objectives[i] if i < len(objectives) else f"Master core concepts of {topic}"
        col_a, col_b = st.columns([0.65, 0.35])
        with col_a:
            topic_checkbox(roadmap_id, wn, topic, completed_keys, key_suffix="topic")
        with col_b:
            st.caption(f"🎯 Objective: {obj}")

    optional = week.get("optional_topics", [])
    if optional:
        with st.expander("📌 Optional Topics (Extended Learning)"):
            st.markdown("<p style='color:#94A3B8; font-size:0.88rem;'>Explore these if you have completed the core topics ahead of schedule:</p>", unsafe_allow_html=True)
            for t in optional:
                st.markdown(f"• <strong style='color:#E2E8F0;'>{t}</strong>", unsafe_allow_html=True)

    if week.get("mock_interview"):
        st.info("🎤 **Mock Interview Checkpoint:** Conduct a 30-minute peer mock interview covering this week's topics.")

with t2:
    st.subheader("✅ Daily Study & Revision Tasks")
    tasks = week.get("daily_tasks", [])
    for i, task in enumerate(tasks):
        item_key = f"task_{wn}_{i}"
        is_done = item_key in completed_keys
        checked = st.checkbox(task, value=is_done, key=f"task_cb_{roadmap_id}_{wn}_{i}")
        if checked != is_done:
            mark_item(roadmap_id, wn, "task", item_key, task, checked)

    revision = week.get("revision", [])
    if revision:
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        st.subheader("🔁 Active Recall & Revision")
        for r in revision:
            st.markdown(f"• <span style='color:#CBD5E1;'>{r}</span>", unsafe_allow_html=True)

    assessment = week.get("assessment", {})
    if assessment:
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        st.subheader("🏆 Weekly Milestone Checkpoint")
        item_key = f"assessment_{wn}"
        is_done = item_key in completed_keys
        milestone_label = assessment.get("milestone", f"Week {wn} Milestone Assessment")
        checked = st.checkbox(
            f"🎯 {milestone_label}",
            value=is_done,
            key=f"asmt_cb_{roadmap_id}_{wn}"
        )
        if checked != is_done:
            mark_item(roadmap_id, wn, "assessment", item_key, milestone_label, checked)
        st.caption(assessment.get("description", "Complete the checkpoint to test your mastery."))

with t3:
    st.subheader("💻 Hands-on Coding Problems")
    exercises = week.get("coding_exercises", [])
    mini = week.get("mini_projects", [])
    if exercises:
        for i, ex in enumerate(exercises):
            item_key = f"exercise_{wn}_{i}"
            is_done = item_key in completed_keys
            checked = st.checkbox(f"🖥️ {ex}", value=is_done, key=f"ex_cb_{roadmap_id}_{wn}_{i}")
            if checked != is_done:
                mark_item(roadmap_id, wn, "exercise", item_key, ex, checked)

    if mini:
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        st.subheader("🛠️ Mini Project / Implementation")
        for i, p in enumerate(mini):
            item_key = f"project_{wn}_{i}"
            is_done = item_key in completed_keys
            checked = st.checkbox(f"🚀 {p}", value=is_done, key=f"proj_cb_{roadmap_id}_{wn}_{i}")
            if checked != is_done:
                mark_item(roadmap_id, wn, "project", item_key, p, checked)

    if not exercises and not mini:
        st.info("No dedicated coding exercises scheduled for this foundational week.")

with t4:
    st.subheader("❓ Topic Practice Questions")
    questions = week.get("practice_questions", [])
    if questions:
        for i, q in enumerate(questions):
            with st.expander(f"Question {i+1}: {q[:80]}..."):
                st.markdown(f"<p style='font-size:1.02rem; color:#F8FAFC;'>{q}</p>", unsafe_allow_html=True)
                item_key = f"question_{wn}_{i}"
                is_done = item_key in completed_keys
                checked = st.checkbox("Mark as practiced & understood", value=is_done,
                                       key=f"q_cb_{roadmap_id}_{wn}_{i}")
                if checked != is_done:
                    mark_item(roadmap_id, wn, "question", item_key, q[:100], checked)
    else:
        st.info("No practice questions specified for this week.")

with t5:
    st.subheader("🔗 Curated Free Learning Resources")
    resources_shown = set()
    for topic in topics:
        rs = get_resources_for_topic(topic)
        for r in rs:
            if r["url"] not in resources_shown:
                show_resource_card(r)
                resources_shown.add(r["url"])
    if not resources_shown:
        st.info("Visit official documentation, GeeksforGeeks, or LeetCode for additional free study materials.")

# Previous / Next week navigation buttons
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
ncol1, ncol2 = st.columns(2)
with ncol1:
    if selected_week > 1:
        if st.button("← Previous Week", use_container_width=True):
            st.session_state["_selected_week"] = selected_week - 1
            st.rerun()
with ncol2:
    if selected_week < len(weeks):
        if st.button("Next Week →", use_container_width=True):
            st.session_state["_selected_week"] = selected_week + 1
            st.rerun()
