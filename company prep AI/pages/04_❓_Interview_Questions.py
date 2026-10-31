"""
pages/04_❓_Interview_Questions.py
Generate and practice interview questions across 7 categories.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.question_generator import generate_questions
from backend.utils.validators import KNOWN_COMPANIES, KNOWN_ROLES, EXPERIENCE_LEVELS, LANGUAGES
from components.ui_helpers import (
    show_header, show_empty_state, show_disclaimer, show_info_card,
    init_session_auth, render_sidebar_auth, require_auth
)
from backend.services.llm_service import get_provider_info

st.set_page_config(page_title="Interview Questions — CompanyPrep AI", page_icon="❓", layout="wide")

require_auth()

show_header("Interview Question Practice",
            "Targeted technical, coding, DBMS, aptitude, reasoning, and HR interview questions.", "❓")

roadmap = st.session_state.get("roadmap_data")

# Sidebar configuration
with st.sidebar:
    render_sidebar_auth()
    st.markdown("<p style='font-size:0.8rem; text-transform:uppercase; font-weight:700; color:#A5B4FC; letter-spacing:0.06em; margin-bottom:0.4rem;'>⚙️ Question Settings</p>", unsafe_allow_html=True)
    if roadmap:
        company = roadmap.get("company", "Generic")
        job_role = roadmap.get("job_role", "Software Engineer")
        skills = roadmap.get("skills", [])
        experience_level = roadmap.get("experience_level", "Beginner")
        language = roadmap.get("language", "Python")
        st.info(f"Using Roadmap Target: **{company} — {job_role}**")
    else:
        company = st.text_input("Target Company", value="TCS")
        job_role = st.selectbox("Target Role", KNOWN_ROLES)
        experience_level = st.selectbox("Experience Level", EXPERIENCE_LEVELS)
        language = st.selectbox("Programming Language", LANGUAGES)
        skills = st.multiselect("Skills", ["Python", "Java", "DSA", "SQL", "OOP", "DBMS"], default=["Python", "SQL"])

    categories = st.multiselect(
        "Question Categories",
        ["Technical", "Coding", "DSA", "SQL", "Aptitude", "HR", "Behavioral"],
        default=["Technical", "Coding", "Aptitude", "HR"]
    )
    num_per_cat = st.slider("Questions Per Category", 3, 10, 5)
    generate_btn = st.button("🎲 Generate & Refresh Questions", type="primary", use_container_width=True)

if generate_btn or "questions_data" not in st.session_state:
    with st.spinner("Generating targeted questions..."):
        questions = generate_questions(
            company=company,
            job_role=job_role,
            skills=skills,
            experience_level=experience_level,
            language=language,
            categories=categories,
            num_per_category=num_per_cat,
        )
        st.session_state["questions_data"] = questions

questions = st.session_state.get("questions_data", {})
provider_info = get_provider_info()

if not questions:
    show_empty_state("No questions generated yet.", "❓", "Click 'Generate & Refresh Questions' in the sidebar.")
    st.stop()

# Disclaimer
if "_disclaimer" in questions:
    show_disclaimer(questions["_disclaimer"])

# Category tabs
cats = [k for k in questions.keys() if not k.startswith("_")]
if not cats:
    st.info("No questions available for the selected categories.")
    st.stop()

tabs = st.tabs([f"📌 {cat}" for cat in cats])
for tab, cat in zip(tabs, cats):
    with tab:
        cat_questions = questions[cat]
        st.markdown(f"<div style='margin: 0.6rem 0 1.2rem 0;'><h3 style='margin:0; color:#F8FAFC; font-weight:800; font-size:1.3rem;'>{cat} Practice Questions</h3><span style='color:#94A3B8; font-size:0.85rem;'>{len(cat_questions)} questions available</span></div>", unsafe_allow_html=True)

        if cat == "Coding":
            for i, q in enumerate(cat_questions):
                diff = q.get("difficulty", "Medium")
                diff_color = "#10B981" if diff.lower() == "easy" else "#F59E0B" if diff.lower() == "medium" else "#EF4444"
                title = q.get("title", f"Coding Challenge {i+1}")

                with st.expander(f"🖥️ {title} — [{diff}]"):
                    st.markdown(f"""
                    <div style='background: rgba(99, 102, 241, 0.08); border-left: 3px solid #6366F1;
                                border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 0.9rem;'>
                        <strong style='color:#E2E8F0;'>Problem Statement:</strong><br>
                        <span style='color:#CBD5E1;'>{q.get('problem', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    c_in, c_out = st.columns(2)
                    with c_in:
                        st.caption("Input Example:")
                        st.code(q.get('input_example', ''), language="text")
                    with c_out:
                        st.caption("Expected Output:")
                        st.code(q.get('output_example', ''), language="text")

                    st.markdown(f"**Recommended Approach:** <span style='color:#CBD5E1;'>{q.get('approach', '')}</span>", unsafe_allow_html=True)

                    st.markdown(f"""
                    <details style='margin-top: 0.8rem; background: rgba(0,0,0,0.3); border: 1px solid rgba(99,102,241,0.3);
                                   border-radius: 8px; padding: 0.7rem 1rem;'>
                        <summary style='cursor: pointer; font-weight: 700; color: #A5B4FC; font-size: 0.9rem;'>
                            👁️ Reveal Complete Solution ({language})
                        </summary>
                        <div style='margin-top: 0.8rem;'>
                            <pre style='background: #0D1117; color: #58A6FF; padding: 0.8rem; border-radius: 6px; overflow-x: auto; font-size: 0.85rem;'><code>{q.get("python_solution", "")}</code></pre>
                            <div style='display:flex; gap:1.2rem; background:rgba(0,0,0,0.25); padding:0.5rem 0.8rem; border-radius:8px; margin-top:0.5rem;'>
                                <span style='color:#94A3B8; font-size:0.85rem;'>⏱️ Time Complexity: <strong style='color:#38BDF8;'>{q.get('time_complexity', 'O(n)')}</strong></span>
                                <span style='color:#94A3B8; font-size:0.85rem;'>💾 Space Complexity: <strong style='color:#A5B4FC;'>{q.get('space_complexity', 'O(1)')}</strong></span>
                            </div>
                        </div>
                    </details>
                    """, unsafe_allow_html=True)

        elif cat in ["Technical", "SQL", "DSA"]:
            for i, q in enumerate(cat_questions):
                q_text = q.get("question", "")
                cat_label = q.get("category", cat)
                with st.expander(f"Q{i+1}: {q_text[:75]}..."):
                    st.markdown(f"""
                    <div style='background: #141828; border-radius: 10px; padding: 1rem 1.2rem;
                                border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 0.8rem;'>
                        <span style='background: rgba(99, 102, 241, 0.2); color: #C7D2FE; font-size: 0.75rem;
                                     font-weight: 700; padding: 2px 8px; border-radius: 6px;'>{cat_label}</span>
                        <h4 style='color: #F8FAFC; margin: 0.5rem 0 0 0; font-size: 1.05rem; font-weight: 600;'>{q_text}</h4>
                    </div>
                    <details style='background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.08);
                                   border-radius: 8px; padding: 0.7rem 1rem;'>
                        <summary style='cursor: pointer; font-weight: 700; color: #38BDF8; font-size: 0.9rem;'>
                            💡 Reveal Model Answer
                        </summary>
                        <div style='color:#CBD5E1; line-height:1.6; margin-top:0.6rem;'>{q.get('answer', 'Answer not available')}</div>
                    </details>
                    """, unsafe_allow_html=True)

        elif cat == "Aptitude":
            for i, q in enumerate(cat_questions):
                q_text = q.get("q", "")
                with st.expander(f"Q{i+1}: {q_text[:75]}..."):
                    expl_html = f"<p style='color: #94A3B8; font-size: 0.92rem;'><strong>Explanation:</strong> {q['explanation']}</p>" if q.get("explanation") else ""
                    st.markdown(f"""
                    <div style='background: #141828; border-radius: 10px; padding: 1rem 1.2rem;
                                border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 0.8rem;'>
                        <span style='background: rgba(6, 182, 212, 0.2); color: #67E8F9; font-size: 0.75rem;
                                     font-weight: 700; padding: 2px 8px; border-radius: 6px;'>Quantitative & Logical</span>
                        <h4 style='color: #F8FAFC; margin: 0.5rem 0 0 0; font-size: 1.02rem; font-weight: 600;'>{q_text}</h4>
                    </div>
                    <details style='background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25);
                                   border-radius: 8px; padding: 0.7rem 1rem;'>
                        <summary style='cursor: pointer; font-weight: 700; color: #34D399; font-size: 0.9rem;'>
                            👁️ Reveal Answer Key & Step-by-Step Explanation
                        </summary>
                        <div style='margin-top:0.6rem;'>
                            <div style='background: rgba(16, 185, 129, 0.15); border-left: 3px solid #10B981;
                                        padding: 0.6rem 0.9rem; border-radius: 6px; margin-bottom: 0.5rem;'>
                                <strong style='color: #34D399;'>Correct Answer:</strong> <span style='color: #F1F5F9;'>{q.get('a', '')}</span>
                            </div>
                            {expl_html}
                        </div>
                    </details>
                    """, unsafe_allow_html=True)

        elif cat == "HR":
            for i, q in enumerate(cat_questions):
                q_text = q.get("q", "")
                with st.expander(f"Q{i+1}: {q_text[:75]}..."):
                    st.markdown(f"""
                    <div style='background: #141828; border-radius: 10px; padding: 1rem 1.2rem;
                                border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 0.8rem;'>
                        <span style='background: rgba(245, 158, 11, 0.2); color: #FCD34D; font-size: 0.75rem;
                                     font-weight: 700; padding: 2px 8px; border-radius: 6px;'>Behavioral / Culture Fit</span>
                        <h4 style='color: #F8FAFC; margin: 0.5rem 0 0 0; font-size: 1.02rem; font-weight: 600;'>{q_text}</h4>
                    </div>
                    <div style='margin-bottom:0.6rem;'>
                        <strong>Recommended Framework:</strong> <span style='color:#C7D2FE;'>{q.get('framework', 'STAR Framework')}</span>
                    </div>
                    <details style='background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25);
                                   border-radius: 8px; padding: 0.7rem 1rem;'>
                        <summary style='cursor: pointer; font-weight: 700; color: #FCD34D; font-size: 0.9rem;'>
                            📋 Sample Exemplar Response
                        </summary>
                        <div style='color: #E2E8F0; line-height: 1.5; margin-top: 0.6rem;'>{q.get('sample', '')}</div>
                    </details>
                    """, unsafe_allow_html=True)

        elif cat == "AI Generated":
            st.warning("⚠️ These questions are generated dynamically by Generative AI based on your profile.")
            for i, q in enumerate(cat_questions):
                with st.expander(f"Q{i+1}: {str(q.get('question', ''))[:75]}..."):
                    st.markdown(f"**Question:** {q.get('question', '')}")
                    st.caption(f"Topic: {q.get('topic', 'General')}")
                    st.markdown(f"""
                    <details style='background: rgba(0,0,0,0.25); border-radius: 8px; padding: 0.6rem 0.9rem;'>
                        <summary style='cursor: pointer; font-weight: 700; color: #A5B4FC;'>View Answer</summary>
                        <div style='margin-top:0.5rem; color:#CBD5E1;'>{q.get('answer', '')}</div>
                    </details>
                    """, unsafe_allow_html=True)
        else:
            for i, q in enumerate(cat_questions):
                with st.expander(f"Q{i+1}: {str(q)[:75]}..."):
                    st.write(q)
