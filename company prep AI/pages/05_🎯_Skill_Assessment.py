"""
pages/05_🎯_Skill_Assessment.py
Interactive skill assessment with MCQ questions, scoring, and weak-area identification.
"""
import streamlit as st
import sys, os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.skill_assessment import get_assessment_questions, score_assessment
from database.db_manager import save_assessment, get_user_assessments, get_assessment_results, init_db, get_user_resume_checkpoint
from components.ui_helpers import (
    show_header, show_metric_card, show_disclaimer, progress_bar_custom,
    init_session_auth, render_sidebar_auth, require_auth
)

init_db()
st.set_page_config(page_title="Skill Assessment — CompanyPrep AI", page_icon="🎯", layout="wide")

require_auth()

with st.sidebar:
    render_sidebar_auth()
show_header("Skill Assessment",
            "Take a short diagnostic quiz to identify knowledge gaps and calibrate your roadmap priorities.", "🎯")

user_id = st.session_state.get("user_id", "default")
roadmap = st.session_state.get("roadmap_data")

tab1, tab2 = st.tabs(["📝 Take Assessment", "📊 Past Attempt History"])

with tab1:
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        experience_level = roadmap.get("experience_level", "Beginner") if roadmap else st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])
    with col_cfg2:
        job_role = roadmap.get("job_role", "Software Engineer") if roadmap else st.selectbox("Target Role", ["Software Engineer", "System Engineer", "Data Analyst"])
    company = roadmap.get("company", "General") if roadmap else "General"

    if "assessment_questions" not in st.session_state or st.button("🔄 Reload New Question Set"):
        qs = get_assessment_questions(experience_level=experience_level, role=job_role, count=10)
        st.session_state["assessment_questions"] = qs
        st.session_state["assessment_answers"] = {}
        st.session_state["assessment_submitted"] = False
        st.session_state["assessment_start_time"] = time.time()

    qs = st.session_state.get("assessment_questions", [])
    answers = st.session_state.get("assessment_answers", {})
    submitted = st.session_state.get("assessment_submitted", False)

    if not qs:
        st.info("No questions loaded. Click 'Reload New Question Set'.")
        st.stop()

    if not submitted:
        ans_count = len(answers)
        tot_count = len(qs)
        progress_bar_custom(f"Quiz Progress ({ans_count}/{tot_count} Answered)", (ans_count / tot_count) * 100, color="#6366F1")
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        for i, q in enumerate(qs):
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #131726 0%, #171D30 100%);
                        border-radius: 14px; padding: 1.2rem 1.4rem;
                        border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 1.2rem;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;'>
                    <span style='background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4);
                                 color: #C7D2FE; font-size: 0.78rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 20px;'>
                        Question {i+1} of {tot_count}
                    </span>
                    <span style='color: #94A3B8; font-size: 0.8rem; font-weight: 600;'>{q['category']}</span>
                </div>
                <div style='color: #F8FAFC; font-size: 1.05rem; font-weight: 600; line-height: 1.5;'>
                    {q['question']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            user_choice = st.radio(
                f"Options for Q{i+1}",
                options=q["options"],
                key=f"radio_{q['id']}",
                index=answers.get(q["id"], None),
                label_visibility="collapsed"
            )
            if user_choice:
                answers[q["id"]] = q["options"].index(user_choice)
                st.session_state["assessment_answers"] = answers
            st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

        col_sub, _ = st.columns([1, 2])
        with col_sub:
            if st.button("✅ Submit Assessment & Calculate Score", type="primary", use_container_width=True):
                if len(answers) < len(qs):
                    st.warning(f"⚠️ Please answer all {len(qs)} questions before submitting (currently answered: {len(answers)}).")
                else:
                    time_taken = int(time.time() - st.session_state.get("assessment_start_time", time.time()))
                    result = score_assessment(qs, answers)
                    st.session_state["assessment_result"] = result
                    st.session_state["assessment_submitted"] = True

                    # Save to DB
                    aid = save_assessment(
                        user_id=user_id,
                        roadmap_id=st.session_state.get("roadmap_id"),
                        company=company,
                        job_role=job_role,
                        experience_level=experience_level,
                        total_questions=result["total"],
                        correct_answers=result["correct"],
                        score_percent=result["score_percent"],
                        time_taken_seconds=time_taken,
                        topic_results=result["topic_results"],
                    )
                    st.session_state["last_assessment_id"] = aid
                    st.rerun()
    else:
        result = st.session_state.get("assessment_result", {})
        score = result.get("score_percent", 0)
        correct = result.get("correct", 0)
        total = result.get("total", 0)
        weak = result.get("weak_areas", [])

        # High-impact score badge card
        color = "#10B981" if score >= 70 else "#F59E0B" if score >= 40 else "#EF4444"
        feedback = "Outstanding Mastery! 🏆" if score >= 80 else "Good Foundation! Focus on weak topics. 📚" if score >= 50 else "Needs Focused Practice! Check the roadmap recommendations. 💪"

        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(19, 23, 38, 0.95), rgba(23, 29, 48, 0.95));
                    border-radius: 20px; padding: 2.2rem 1.8rem; text-align: center;
                    border: 2px solid {color}55; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.4), 0 0 24px {color}22;
                    margin: 1.5rem 0; position: relative;'>
            <div style='font-size: 3.6rem; font-weight: 800; color: {color}; letter-spacing: -0.03em;'>
                {score:.1f}%
            </div>
            <div style='color: #F8FAFC; font-size: 1.2rem; font-weight: 700; margin-top: 0.3rem;'>
                {correct} of {total} Questions Correct
            </div>
            <div style='color: #94A3B8; font-size: 0.95rem; margin-top: 0.6rem; font-weight: 500;'>
                {feedback}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Category breakdown
        st.subheader("📊 Category Performance Breakdown")
        for tr in result.get("topic_results", []):
            bar_color = "#10B981" if tr["score_percent"] >= 70 else "#F59E0B" if tr["score_percent"] >= 40 else "#EF4444"
            progress_bar_custom(f"{tr['topic']} ({tr['correct']}/{tr['total']})", tr["score_percent"], bar_color)

        if weak:
            st.markdown(f"""
            <div style='background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.35);
                        border-left: 4px solid #F59E0B; border-radius: 12px; padding: 0.9rem 1.2rem; margin: 1.2rem 0;
                        color: #FEF3C7; font-size: 0.92rem;'>
                ⚠️ <strong>Priority Revision Needed:</strong> {', '.join(weak)}
            </div>
            """, unsafe_allow_html=True)

        # Detailed results
        st.subheader("📋 Question-by-Question Detailed Review")
        for r in result.get("results", []):
            icon = "✅" if r["is_correct"] else "❌"
            border_c = "#10B981" if r["is_correct"] else "#EF4444"
            with st.expander(f"{icon} {r['question'][:75]}..."):
                st.markdown(f"**Your Answer:** <span style='color: {'#34D399' if r['is_correct'] else '#F87171'}; font-weight:600;'>{r['user_answer_text']}</span>", unsafe_allow_html=True)
                if not r["is_correct"]:
                    st.markdown(f"**Correct Answer:** <span style='color: #34D399; font-weight:600;'>{r['correct_answer_text']}</span>", unsafe_allow_html=True)
                st.info(f"💡 **Explanation:** {r['explanation']}")

        if st.button("🔄 Retake Another Assessment", use_container_width=True):
            for k in ["assessment_questions", "assessment_answers", "assessment_submitted", "assessment_result"]:
                st.session_state.pop(k, None)
            st.rerun()

with tab2:
    st.subheader("Past Assessment History")
    past = get_user_assessments(user_id)
    if not past:
        st.info("No past assessments on record. Take your first diagnostic quiz above!")
    else:
        for a in past:
            color = "#10B981" if a["score_percent"] >= 70 else "#F59E0B" if a["score_percent"] >= 40 else "#EF4444"
            with st.expander(f"📅 {a['attempted_at'][:10]} — Score: {a['score_percent']:.1f}% ({a['company']} - {a['job_role']})"):
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    st.metric("Total Score", f"{a['score_percent']:.1f}%")
                with col_p2:
                    st.metric("Correct Answers", f"{a['correct_answers']} / {a['total_questions']}")
                with col_p3:
                    st.metric("Level", a["experience_level"])

                st.markdown("**Per-Category Breakdown:**")
                results = get_assessment_results(a["assessment_id"])
                for r in results:
                    bcolor = "#10B981" if r["score_percent"] >= 70 else "#F59E0B" if r["score_percent"] >= 40 else "#EF4444"
                    progress_bar_custom(r["topic"], r["score_percent"], bcolor)
