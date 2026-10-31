"""
pages/09_⚖️_Compare_Roadmaps.py
Compare preparation roadmaps for two companies or job roles side by side.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.roadmap_generator import generate_roadmap, _get_role_topics
from backend.utils.validators import KNOWN_COMPANIES, KNOWN_ROLES, EXPERIENCE_LEVELS, LANGUAGES
from components.ui_helpers import (
    show_header, show_disclaimer, show_metric_card, show_info_card,
    init_session_auth, render_sidebar_auth, require_auth
)

st.set_page_config(page_title="Compare Roadmaps — CompanyPrep AI", page_icon="⚖️", layout="wide")

require_auth()

with st.sidebar:
    render_sidebar_auth()
show_header("Compare Preparation Roadmaps",
            "Evaluate preparation requirements and curriculum overlap for two companies or job roles side by side.", "⚖️")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.08) 100%);
                border-radius: 16px; padding: 1.4rem; border: 1px solid rgba(99, 102, 241, 0.3); margin-bottom: 1rem;'>
        <h4 style='color: #F8FAFC; margin: 0 0 0.8rem 0; font-size: 1.15rem; font-weight: 700;'>📋 Target Profile A</h4>
    """, unsafe_allow_html=True)
    company_a = st.selectbox("Company A", KNOWN_COMPANIES, index=0, key="comp_a")
    role_a = st.selectbox("Role A", KNOWN_ROLES, index=0, key="role_a")
    exp_a = st.selectbox("Experience Level A", EXPERIENCE_LEVELS, key="exp_a")
    weeks_a = st.slider("Target Duration A (weeks)", 4, 26, 8, key="dur_a")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(59, 130, 246, 0.08) 100%);
                border-radius: 16px; padding: 1.4rem; border: 1px solid rgba(6, 182, 212, 0.3); margin-bottom: 1rem;'>
        <h4 style='color: #F8FAFC; margin: 0 0 0.8rem 0; font-size: 1.15rem; font-weight: 700;'>📋 Target Profile B</h4>
    """, unsafe_allow_html=True)
    company_b = st.selectbox("Company B", KNOWN_COMPANIES, index=1, key="comp_b")
    role_b = st.selectbox("Role B", KNOWN_ROLES, index=1, key="role_b")
    exp_b = st.selectbox("Experience Level B", EXPERIENCE_LEVELS, key="exp_b")
    weeks_b = st.slider("Target Duration B (weeks)", 4, 26, 8, key="dur_b")
    st.markdown("</div>", unsafe_allow_html=True)

if st.button("⚖️ Compare Syllabi & Skill Overlap", type="primary", use_container_width=True):
    with st.spinner("Analyzing curriculum intersections and topic overlap..."):
        topics_a = set(_get_role_topics(role_a))
        topics_b = set(_get_role_topics(role_b))

        common = sorted(topics_a & topics_b)
        only_a = sorted(topics_a - topics_b)
        only_b = sorted(topics_b - topics_a)

        st.session_state["comparison"] = {
            "company_a": company_a, "role_a": role_a, "topics_a": sorted(topics_a),
            "company_b": company_b, "role_b": role_b, "topics_b": sorted(topics_b),
            "common": common, "only_a": only_a, "only_b": only_b,
        }

comp = st.session_state.get("comparison")
if comp:
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#F8FAFC; font-weight:800; font-size:1.35rem; margin-bottom:0.8rem;'>📊 Overlap Metrics</h3>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        show_metric_card(f"{comp['role_a']}", len(comp["topics_a"]), f"at {comp['company_a']}", "#6366F1")
    with m2:
        show_metric_card("Shared Topics", len(comp["common"]), "applicable to both", "#10B981")
    with m3:
        show_metric_card(f"{comp['role_b']}", len(comp["topics_b"]), f"at {comp['company_b']}", "#06B6D4")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 3 Column Breakdown
    col_a, col_common, col_b = st.columns([1, 1, 1])

    with col_a:
        st.markdown(f"""
        <div style='background:#121626; border-radius:14px; padding:1.2rem; border:1px solid rgba(255,255,255,0.08); border-top:3px solid #6366F1;'>
            <h4 style='color:#C7D2FE; margin:0 0 0.8rem 0; font-size:1rem; font-weight:700;'>Only in {comp['role_a']}</h4>
        """, unsafe_allow_html=True)
        if comp["only_a"]:
            for t in comp["only_a"]:
                st.markdown(f"<span style='background:rgba(99, 102, 241, 0.2); border:1px solid rgba(99, 102, 241, 0.4); border-radius:6px; padding:3px 8px; margin:2px; display:inline-block; font-size:0.82rem; color:#E0E7FF;'>{t}</span>", unsafe_allow_html=True)
        else:
            st.info("No unique topics found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_common:
        st.markdown("""
        <div style='background:#121626; border-radius:14px; padding:1.2rem; border:1px solid rgba(255,255,255,0.08); border-top:3px solid #10B981;'>
            <h4 style='color:#6EE7B7; margin:0 0 0.8rem 0; font-size:1rem; font-weight:700;'>Shared Core Topics</h4>
        """, unsafe_allow_html=True)
        for t in comp["common"]:
            st.markdown(f"<span style='background:rgba(16, 185, 129, 0.2); border:1px solid rgba(16, 185, 129, 0.4); border-radius:6px; padding:3px 8px; margin:2px; display:inline-block; font-size:0.82rem; color:#A7F3D0;'>✓ {t}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div style='background:#121626; border-radius:14px; padding:1.2rem; border:1px solid rgba(255,255,255,0.08); border-top:3px solid #06B6D4;'>
            <h4 style='color:#67E8F9; margin:0 0 0.8rem 0; font-size:1rem; font-weight:700;'>Only in {comp['role_b']}</h4>
        """, unsafe_allow_html=True)
        if comp["only_b"]:
            for t in comp["only_b"]:
                st.markdown(f"<span style='background:rgba(6, 182, 212, 0.2); border:1px solid rgba(6, 182, 212, 0.4); border-radius:6px; padding:3px 8px; margin:2px; display:inline-block; font-size:0.82rem; color:#CFFAFE;'>{t}</span>", unsafe_allow_html=True)
        else:
            st.info("No unique topics found.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    pct_overlap = round(len(comp["common"]) / max(len(comp["topics_a"] + comp["topics_b"]) / 2, 1) * 100)
    show_info_card(
        f"<strong>{pct_overlap}% Curriculum Overlap</strong> — Preparing for shared fundamentals ({', '.join(comp['common'][:4])}) prepares you simultaneously for both opportunities.",
        "💡",
        "#10B981"
    )

    import pandas as pd
    comparison_table = []
    all_topics = sorted(set(comp["topics_a"]) | set(comp["topics_b"]))
    for t in all_topics:
        comparison_table.append({
            "Topic": t,
            f"{comp['role_a']} ({comp['company_a']})": "✅ Required" if t in comp["topics_a"] else "—",
            f"{comp['role_b']} ({comp['company_b']})": "✅ Required" if t in comp["topics_b"] else "—",
        })
    st.dataframe(pd.DataFrame(comparison_table), use_container_width=True)

show_disclaimer(
    "Comparison results represent general industry hiring trends for entry-level roles. Always confirm specific round cutoffs and patterns with official campus placement notices."
)
