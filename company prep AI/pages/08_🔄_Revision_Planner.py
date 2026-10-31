"""
pages/08_🔄_Revision_Planner.py
Personalized revision plan based on weak areas and remaining time.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.revision_planner import generate_revision_plan
from components.ui_helpers import (
    show_header, show_empty_state, show_info_card, show_disclaimer,
    show_metric_card, init_session_auth, render_sidebar_auth, require_auth
)

st.set_page_config(page_title="Revision Planner — CompanyPrep AI", page_icon="🔄", layout="wide")

require_auth()

with st.sidebar:
    render_sidebar_auth()
show_header("Targeted Revision Planner",
            "Generate a high-yield revision schedule prioritizing weak areas and pending checklist items.", "🔄")

roadmap_id = st.session_state.get("roadmap_id")
roadmap_data = st.session_state.get("roadmap_data")
user_id = st.session_state.get("user_id", "default")

if not roadmap_id:
    show_empty_state("No active roadmap found. Create one first!", "🔄",
                     "Navigate to 📋 Create Roadmap")
    st.stop()

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.08) 100%);
            border-radius: 16px; padding: 1.4rem; border: 1px solid rgba(99, 102, 241, 0.3); margin-bottom: 1.2rem;'>
    <h4 style='color: #F8FAFC; margin: 0 0 0.8rem 0; font-size: 1.15rem; font-weight: 700;'>⚙️ Revision Time Allocation</h4>
""", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    hours_per_day = st.slider("Daily Revision Study Hours", 0.5, 8.0, 2.5, step=0.5)
with col2:
    remaining_days = st.slider("Days Remaining Until Interview", 1, 60, 14)

st.markdown("</div>", unsafe_allow_html=True)

if st.button("📅 Generate High-Yield Revision Schedule", type="primary", use_container_width=True):
    with st.spinner("Prioritizing weak topics and constructing daily schedule..."):
        plan = generate_revision_plan(
            roadmap_id=roadmap_id,
            weeks=st.session_state.get("roadmap_weeks", []),
            user_id=user_id,
            available_hours_per_day=hours_per_day,
            remaining_days=remaining_days,
        )
        st.session_state["revision_plan"] = plan

plan = st.session_state.get("revision_plan")
if not plan:
    show_info_card("Set your revision parameters above and click 'Generate High-Yield Revision Schedule'.", "📅", "#06B6D4")
    st.stop()

st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#F8FAFC; font-weight:800; font-size:1.35rem; margin-bottom:0.8rem;'>📊 Revision Overview</h3>", unsafe_allow_html=True)

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    show_metric_card("Time Window", f"{plan['remaining_days']} Days", "until interview", "#6366F1")
with col_r2:
    show_metric_card("Total Hours", f"{plan['total_revision_hours']} hrs", f"@{hours_per_day}h per day", "#10B981")
with col_r3:
    show_metric_card("Priority Focus", f"{len(plan['weak_topics'])} Topics", "weak areas identified", "#F59E0B")

if plan.get("weak_topics"):
    st.markdown(f"""
    <div style='background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.35);
                border-radius: 12px; padding: 0.85rem 1.2rem; margin: 1rem 0; color: #FEF3C7; font-size: 0.92rem;'>
        ⚠️ <strong>Priority Topics to Revise:</strong> {', '.join(plan['weak_topics'])}
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📅 Daily Study Schedule", "🏆 Milestones & Checkpoints", "💡 High-Yield Exam Tips"])

with tab1:
    for day in plan.get("daily_plans", []):
        icon = "🤝" if day.get("mock_practice") else "📚"
        with st.expander(f"{icon} Day {day['day']} — Focus: {day['focus_topic']} ({day['hours']}h)"):
            st.markdown(f"**Strategic Importance:** <span style='color:#CBD5E1;'>{day['why_important']}</span>", unsafe_allow_html=True)
            st.markdown("**Tasks for Today:**")
            for task in day.get("tasks", []):
                st.markdown(f"• <span style='color:#E2E8F0;'>{task}</span>", unsafe_allow_html=True)
            if day.get("mock_practice"):
                st.info("🎤 **Mock Interview Checkpoint:** Schedule a 30-minute practice interview session today.")

with tab2:
    for m in plan.get("milestones", []):
        with st.expander(f"🏆 Milestone Checkpoint: Day {m['day']} — {m['milestone']}"):
            for task in m.get("tasks", []):
                st.markdown(f"• <span style='color:#CBD5E1;'>{task}</span>", unsafe_allow_html=True)

with tab3:
    st.subheader("💡 Strategic Preparation Advice")
    for tip in plan.get("tips", []):
        show_info_card(tip, "💡", "#06B6D4")

show_disclaimer(
    "Revision planner schedules are designed for spaced repetition and active recall. Adjust daily workload to avoid fatigue."
)
