"""
pages/11_📥_Export_Calendar.py
Export the study calendar as CSV or PDF.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.export_manager import export_roadmap_csv, export_roadmap_pdf
from database.db_manager import get_roadmap, get_roadmap_weeks, init_db
from components.ui_helpers import (
    show_header, show_empty_state, show_disclaimer, show_info_card, show_metric_card,
    init_session_auth, render_sidebar_auth, require_auth
)

init_db()
st.set_page_config(page_title="Export Calendar — CompanyPrep AI", page_icon="📥", layout="wide")

require_auth()

with st.sidebar:
    render_sidebar_auth()
show_header("Export Study Calendar",
            "Download your tailored interview preparation schedule as a spreadsheet CSV or printable PDF guide.", "📥")

roadmap_id = st.session_state.get("roadmap_id")
roadmap_data = st.session_state.get("roadmap_data")

if not roadmap_id:
    st.markdown("""
    <div style='background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3);
                border-left: 4px solid #EF4444; border-radius: 12px; padding: 1.1rem 1.4rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 0.6rem;'>
            <span style='font-size: 1.4rem;'>⚠️</span>
            <div>
                <div style='color: #F87171; font-weight: 700; font-size: 1rem;'>No Active Roadmap Found</div>
                <div style='color: #FCA5A5; font-size: 0.85rem; margin-top: 0.2rem;'>
                    Please create a preparation roadmap first before exporting your study calendar.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📋 Create Roadmap Now", type="primary"):
        st.switch_page("pages/02_📋_Create_Roadmap.py")
    st.stop()

weeks = st.session_state.get("roadmap_weeks") or get_roadmap_weeks(roadmap_id)
meta = get_roadmap(roadmap_id)

if not weeks or len(weeks) == 0:
    show_empty_state("Roadmap has no weekly data. Try regenerating your roadmap.", "📭",
                     "Go to 📋 Create Roadmap to generate a new plan.")
    st.stop()


# Preview KPI metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    show_metric_card("Company", meta.get("company", "") if meta else roadmap_data.get("company", ""), "target employer", "#6366F1")
with col2:
    show_metric_card("Role", meta.get("job_role", "") if meta else roadmap_data.get("job_role", ""), "target profile", "#10B981")
with col3:
    show_metric_card("Timeline", f"{len(weeks)} Weeks", "preparation duration", "#F59E0B")
with col4:
    tot_topics = sum(len(w.get('topics',[])) for w in weeks)
    show_metric_card("Curriculum", f"{tot_topics} Topics", "total subjects", "#06B6D4")

st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#F8FAFC; font-weight:800; font-size:1.35rem; margin-bottom:0.8rem;'>📥 Export Options</h3>", unsafe_allow_html=True)

col_csv, col_pdf = st.columns(2)

with col_csv:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #121626 0%, #171C30 100%);
                border-radius: 18px; padding: 1.8rem; text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.09);
                box-shadow: 0 6px 22px rgba(0, 0, 0, 0.28); margin-bottom: 0.9rem;'>
        <div style='font-size: 2.6rem; margin-bottom: 0.5rem;'>📊</div>
        <h3 style='color: #F8FAFC; margin: 0 0 0.4rem 0; font-size: 1.25rem; font-weight: 700;'>Spreadsheet CSV Export</h3>
        <p style='color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 1.2rem;'>
            Download your week-by-week study calendar in CSV format. Compatible with Microsoft Excel, Google Sheets, Notion, and Apple Numbers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    roadmap = roadmap_data or {}
    csv_bytes = export_roadmap_csv(roadmap, weeks)
    company_name = roadmap.get("company", "company").replace(" ", "_")
    st.download_button(
        label="📊 Download CSV Study Calendar",
        data=csv_bytes,
        file_name=f"companyprep_{company_name}_roadmap.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_csv"
    )

with col_pdf:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #121626 0%, #171C30 100%);
                border-radius: 18px; padding: 1.8rem; text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.09);
                box-shadow: 0 6px 22px rgba(0, 0, 0, 0.28); margin-bottom: 0.9rem;'>
        <div style='font-size: 2.6rem; margin-bottom: 0.5rem;'>📄</div>
        <h3 style='color: #F8FAFC; margin: 0 0 0.4rem 0; font-size: 1.25rem; font-weight: 700;'>Printable PDF Document</h3>
        <p style='color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 1.2rem;'>
            High-resolution formatted PDF study syllabus. Perfect for printing, annotating on tablets, or offline preparation tracking.
        </p>
    </div>
    """, unsafe_allow_html=True)

    pdf_bytes = export_roadmap_pdf(roadmap, weeks)
    ext = ".pdf" if len(pdf_bytes) > 200 and pdf_bytes[:4] == b'%PDF' else ".txt"
    st.download_button(
        label="📄 Download Printable PDF Guide",
        data=pdf_bytes,
        file_name=f"companyprep_{company_name}_roadmap{ext}",
        mime="application/pdf" if ext == ".pdf" else "text/plain",
        use_container_width=True,
        key="download_pdf"
    )

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# Table preview
st.markdown("<h3 style='color:#F8FAFC; font-weight:800; font-size:1.35rem; margin-bottom:0.8rem;'>👀 Calendar Schedule Preview</h3>", unsafe_allow_html=True)
import pandas as pd
preview_rows = []
for week in weeks[:6]:
    for topic in week.get("topics", []):
        preview_rows.append({
            "Week": f"Week {week['week_number']}",
            "Topic": topic,
            "Target Hours": round(week.get("estimated_hours", 0) / max(len(week.get("topics", ["x"])), 1), 1),
            "Milestone": week.get("assessment", {}).get("milestone", "Weekly Checkpoint"),
            "Status": "Pending"
        })
if preview_rows:
    st.dataframe(pd.DataFrame(preview_rows), use_container_width=True)

show_disclaimer(
    "Exported documents contain only your curriculum schedule. No personal credentials or private data are saved in the download."
)
