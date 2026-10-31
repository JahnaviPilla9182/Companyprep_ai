"""
pages/06_📄_JD_Analyzer.py
Analyzes job descriptions to extract skills and generate gap analysis.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.job_analyzer import analyze_job_description, read_uploaded_file
from backend.utils.validators import validate_file_upload
from components.ui_helpers import (
    show_header, show_disclaimer, progress_bar_custom, show_info_card,
    show_metric_card, init_session_auth, render_sidebar_auth, require_auth
)

st.set_page_config(page_title="JD Analyzer — CompanyPrep AI", page_icon="📄", layout="wide")

require_auth()

with st.sidebar:
    render_sidebar_auth()
show_header("Job Description Analyzer",
            "Paste or upload a target job description to extract required skills and perform a quantitative gap analysis.", "📄")

roadmap = st.session_state.get("roadmap_data")
user_skills = roadmap.get("skills", []) if roadmap else []
company = roadmap.get("company", "") if roadmap else ""
role = roadmap.get("job_role", "") if roadmap else ""

if roadmap:
    st.markdown(f"""
    <div style='background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.35);
                border-radius: 12px; padding: 0.8rem 1.2rem; margin-bottom: 1rem;'>
        📌 Profile Active: <strong style='color:#C7D2FE;'>{company} — {role}</strong> (Skills: {', '.join(user_skills[:6])}...)
    </div>
    """, unsafe_allow_html=True)
else:
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        user_skills_input = st.text_input(
            "Your current skills (comma-separated)",
            value="Python, SQL, OOP, Git, DBMS",
            placeholder="Python, Java, SQL, OOP..."
        )
        user_skills = [s.strip() for s in user_skills_input.split(",") if s.strip()]
    with col_u2:
        role = st.text_input("Target Job Role", value="Software Engineer")
    company = ""

st.markdown("<h3 style='color:#F8FAFC; font-weight:700; font-size:1.2rem; margin:1rem 0 0.6rem 0;'>📥 Submit Target Job Description</h3>", unsafe_allow_html=True)
tab_paste, tab_upload = st.tabs(["📝 Paste Plain Text", "📎 Upload Plain Text File (.txt)"])

jd_text = ""
with tab_paste:
    jd_text_input = st.text_area(
        "Paste Job Description Here",
        height=220,
        placeholder="Paste full job description including requirements and responsibilities..."
    )
    char_count = len(jd_text_input.strip())
    if jd_text_input.strip():
        color = "#EF4444" if char_count < 50 else ("#10B981" if char_count <= 10000 else "#EF4444")
        st.markdown(
            f"<div style='font-size:0.75rem; color:{color}; text-align:right; margin-top:-0.5rem;'>"
            f"{char_count:,} / 10,000 characters"
            f"{'  ✓' if 50 <= char_count <= 10000 else '  ⚠ Must be 50–10,000 chars'}"
            "</div>",
            unsafe_allow_html=True
        )
    if st.button("🔍 Analyze JD & Compare Skills", type="primary", key="analyze_paste"):
        from backend.utils.validators import validate_jd_text, sanitize_html
        ok, err = validate_jd_text(jd_text_input)
        if not ok:
            st.error(f"❌ {err}")
        else:
            jd_text = sanitize_html(jd_text_input, max_len=10000)
            st.session_state["jd_text"] = jd_text
            st.session_state["trigger_analysis"] = True

with tab_upload:
    uploaded = st.file_uploader(
        "Upload JD File (.txt format)",
        type=["txt"],
        help="Upload a UTF-8 text file containing the job description."
    )
    if uploaded:
        ok, err = validate_file_upload(uploaded, allowed_types=[".txt"], max_mb=2.0)
        if not ok:
            st.error(f"❌ {err}")
        else:
            content, read_err = read_uploaded_file(uploaded)
            if read_err:
                st.error(f"❌ {read_err}")
            else:
                from backend.utils.validators import validate_jd_text, sanitize_html
                ok2, err2 = validate_jd_text(content)
                if not ok2:
                    st.error(f"❌ {err2}")
                else:
                    clean_content = sanitize_html(content, max_len=10000)
                    st.success(f"✅ File loaded: {uploaded.name} ({len(clean_content):,} characters)")
                    st.session_state["jd_text"] = clean_content
                    st.session_state["trigger_analysis"] = True

# Trigger analysis
if st.session_state.get("trigger_analysis"):
    st.session_state["trigger_analysis"] = False
    jd = st.session_state.get("jd_text", "")
    if not jd or len(jd.strip()) < 50:
        st.error("❌ Job description is too short. Please provide a complete job description (minimum 50 characters).")
    else:
        with st.spinner("Extracting required skills, technologies, and computing match score..."):
            result = analyze_job_description(
                jd_text=jd,
                user_skills=user_skills,
                company=company,
                role=role,
            )
            st.session_state["jd_result"] = result

result = st.session_state.get("jd_result")
if result:
    if "error" in result:
        st.error(result["error"])
    else:
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#F8FAFC; font-weight:800; font-size:1.35rem; margin-bottom:0.8rem;'>📊 Quantitative Gap Analysis</h3>", unsafe_allow_html=True)
        gap = result.get("gap_summary", {})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            show_metric_card("Required Skills", gap.get("total_required", 0), "skills in JD", "#6366F1")
        with col2:
            show_metric_card("Demonstrated", gap.get("you_have", 0), "matching your profile", "#10B981")
        with col3:
            show_metric_card("Skill Gaps", gap.get("you_need", 0), "skills to develop", "#F59E0B")
        with col4:
            cov = gap.get("coverage_pct", 0)
            show_metric_card("Coverage Rate", f"{cov}%", "readiness score", "#06B6D4")

        progress_bar_custom("Candidate Match Coverage", gap.get("coverage_pct", 0),
                             color="#10B981" if gap.get("coverage_pct", 0) >= 70 else "#F59E0B")

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.04) 100%);
                        border-radius: 16px; padding: 1.3rem; border: 1px solid rgba(16, 185, 129, 0.25);'>
                <h4 style='color:#34D399; margin:0 0 0.8rem 0; font-size:1.1rem; font-weight:700;'>
                    ✅ Skills Already Demonstrated
                </h4>
            """, unsafe_allow_html=True)
            matched = result.get("matched_skills", [])
            if matched:
                chips = " ".join([f"<span style='background:rgba(16, 185, 129, 0.2); border:1px solid rgba(16, 185, 129, 0.4); color:#6EE7B7; border-radius:14px; padding:3px 10px; margin:3px; display:inline-block; font-size:0.85rem; font-weight:600;'>✓ {s}</span>" for s in matched])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.info("No matching skills found from your current profile.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(185, 28, 28, 0.04) 100%);
                        border-radius: 16px; padding: 1.3rem; border: 1px solid rgba(239, 68, 68, 0.25);'>
                <h4 style='color:#F87171; margin:0 0 0.8rem 0; font-size:1.1rem; font-weight:700;'>
                    📚 Missing Skills to Prioritize
                </h4>
            """, unsafe_allow_html=True)
            missing = result.get("missing_skills", [])
            if missing:
                chips = " ".join([f"<span style='background:rgba(239, 68, 68, 0.2); border:1px solid rgba(239, 68, 68, 0.4); color:#FCA5A5; border-radius:14px; padding:3px 10px; margin:3px; display:inline-block; font-size:0.85rem; font-weight:600;'>✗ {s}</span>" for s in missing])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.success("Great! Full coverage detected for the extracted keywords.")
            st.markdown("</div>", unsafe_allow_html=True)

        if result.get("responsibilities"):
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            with st.expander("📋 Extracted Key Responsibilities"):
                for r in result["responsibilities"]:
                    st.markdown(f"• <span style='color:#CBD5E1;'>{r}</span>", unsafe_allow_html=True)

        if result.get("ai_insights"):
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            st.subheader("🤖 AI Insights & Recommended Priorities")
            ai = result["ai_insights"]
            if "key_skills" in ai:
                st.markdown(f"**Key Focus:** {', '.join(ai['key_skills'])}")
            if "preparation_tips" in ai:
                st.markdown("**Preparation Recommendations:**")
                for tip in ai.get("preparation_tips", []):
                    show_info_card(tip, "💡", "#6366F1")

        show_disclaimer(result.get("source_note", "Analysis is generated by parsing submitted text."))
else:
    show_info_card("Paste a job description above and click 'Analyze JD & Compare Skills' to view your tailored gap report.", "📄", "#06B6D4")
