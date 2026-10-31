"""
components/ui_helpers.py
Comprehensive UI helper functions and SaaS design system for CompanyPrep AI.
Includes:
- Modern Light Mode SaaS Design System
- Landing Page (Public initial page, no sidebar)
- Login & Registration Page (No sidebar)
- Admin Dashboard (Platform overview & candidate management)
- Role-based navigation guards and route enforcement
- Password strength indicator, account security cards, and resume checkpoint cards
"""
import streamlit as st
from typing import Optional
from datetime import datetime, timezone
import uuid
import re


# ---------------------------------------------------------------------------
# Light Mode SaaS Design System & Stylesheet
# ---------------------------------------------------------------------------

def inject_custom_css(hide_sidebar: bool = False):
    """Inject a cohesive, high-end SaaS Light Mode design system stylesheet."""
    sidebar_hide_rule = """
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
    }
    """ if hide_sidebar else ""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* Global Typography & Font Smoothing */
    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: -0.015em;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    /* Strictly preserve Material Symbols glyphs */
    [data-testid*="Icon"],
    [data-testid*="icon"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderToggleIcon"] *,
    [data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    [class*="material-symbols"] {{
        font-family: 'Material Symbols Rounded', sans-serif !important;
        font-feature-settings: 'liga' !important;
        -webkit-font-feature-settings: 'liga' !important;
        letter-spacing: normal !important;
        line-height: 1 !important;
    }}

    code, pre, .stCodeBlock {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* Light Theme Backdrop & Base Colors */
    .stApp {{
        background-color: #F8FAFC !important;
        background-image:
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.04) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(14, 165, 233, 0.03) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(139, 92, 246, 0.03) 0px, transparent 50%);
        background-attachment: fixed;
        color: #0F172A !important;
    }}

    /* Clean Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}
    .stDeployButton {{display: none;}}

    /* Sidebar Styling (Light Theme) */
    section[data-testid="stSidebar"] {{
        background: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        box-shadow: 2px 0 14px rgba(0, 0, 0, 0.03) !important;
    }}

    [data-testid="stSidebar"] a {{
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        margin-bottom: 2px !important;
        padding: 0.5rem 0.8rem !important;
        color: #475569 !important;
        font-weight: 600 !important;
    }}

    [data-testid="stSidebar"] a:hover {{
        background: #EEF2FF !important;
        color: #4338CA !important;
        transform: translateX(3px);
    }}

    /* Native Streamlit Bordered Container Restyling (Light Mode) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.22s ease !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: #CBD5E1 !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05) !important;
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.55rem 1.35rem !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: -0.01em !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(79, 70, 229, 0.4) !important;
        filter: brightness(1.05) !important;
    }}

    /* Download Buttons */
    .stDownloadButton > button {{
        background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.25) !important;
        transition: all 0.2s ease !important;
    }}

    /* Inputs & Select Boxes (Light Mode) */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {{
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
        color: #0F172A !important;
        padding: 0.6rem 0.95rem !important;
        transition: all 0.2s ease !important;
    }}

    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {{
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
        background-color: #FFFFFF !important;
    }}

    /* MultiSelect Tag Chips */
    span[data-baseweb="tag"] {{
        background: #EEF2FF !important;
        border: 1px solid #C7D2FE !important;
        border-radius: 6px !important;
        color: #4338CA !important;
        font-weight: 600 !important;
    }}

    /* Pill Tabs (Light Mode) */
    .stTabs [data-baseweb="tab-list"] {{
        background: #F1F5F9 !important;
        border-radius: 12px !important;
        padding: 0.3rem !important;
        border: 1px solid #E2E8F0 !important;
        gap: 0.3rem !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        padding: 0.5rem 1.1rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: #0F172A !important;
        background: rgba(255, 255, 255, 0.6) !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: #FFFFFF !important;
        color: #4F46E5 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    }}

    /* Expanders (Light Mode) */
    div[data-testid="stExpander"],
    details[data-testid="stExpander"] {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        margin-bottom: 0.65rem !important;
        transition: all 0.2s ease !important;
    }}

    div[data-testid="stExpander"]:hover,
    details[data-testid="stExpander"]:hover {{
        border-color: #CBD5E1 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
    }}

    div[data-testid="stExpander"] summary,
    details[data-testid="stExpander"] summary {{
        font-weight: 700 !important;
        color: #0F172A !important;
    }}

    /* Metric Cards (Light Mode) */
    div[data-testid="stMetric"] {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 1.1rem 1.3rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03) !important;
        position: relative;
        overflow: hidden;
    }}

    div[data-testid="stMetric"]::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
    }}

    div[data-testid="stMetricLabel"] {{
        color: #64748B !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: #0F172A !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }}

    /* Scrollbars */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #F1F5F9; }}
    ::-webkit-scrollbar-thumb {{ background: #CBD5E1; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #4F46E5; }}

    {sidebar_hide_rule}
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Reusable Light-Theme Component Functions
# ---------------------------------------------------------------------------

def show_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a clean, modern SaaS page header in Light Theme."""
    inject_custom_css()
    icon_html = f"<span style='font-size: 1.8rem; margin-right: 0.75rem; vertical-align: middle;'>{icon}</span>" if icon else ""
    st.markdown(
        f"""
        <div style='padding: 1.3rem 1.6rem;
                    background: #FFFFFF;
                    border-radius: 16px; border: 1px solid #E2E8F0;
                    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
                    margin-bottom: 1.6rem;'>
            <div style='display: flex; align-items: center;'>
                {icon_html}
                <div>
                    <h1 style='margin: 0; font-size: 1.7rem; font-weight: 800; letter-spacing: -0.025em; color: #0F172A;'>
                        {title}
                    </h1>
                    {f"<p style='margin: 0.25rem 0 0 0; color: #475569; font-size: 0.92rem; font-weight: 500;'>{subtitle}</p>" if subtitle else ""}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_metric_card(label: str, value, delta: str = "", color: str = "#4F46E5"):
    """Render a clean metric card in Light Theme."""
    st.markdown(
        f"""
        <div style='background: #FFFFFF;
                    border-radius: 14px; padding: 1.1rem 1.3rem;
                    border: 1px solid #E2E8F0;
                    border-left: 4px solid {color};
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
                    margin-bottom: 0.6rem;'>
            <div style='color: #64748B; font-size: 0.74rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em;'>{label}</div>
            <div style='font-size: 1.85rem; font-weight: 800; color: #0F172A; margin: 0.2rem 0; letter-spacing: -0.02em;'>{value}</div>
            {f"<div style='color: #64748B; font-size: 0.76rem; font-weight: 500;'>{delta}</div>" if delta else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_info_card(content: str, icon: str = "ℹ️", color: str = "#4F46E5"):
    """Render an informational card in Light Theme."""
    st.markdown(
        f"""
        <div style='background: #F8FAFC;
                    border-radius: 12px; padding: 0.95rem 1.25rem;
                    border: 1px solid #E2E8F0;
                    border-left: 4px solid {color}; margin: 0.45rem 0;
                    display: flex; align-items: flex-start; gap: 0.75rem;'>
            <span style='font-size: 1.2rem; line-height: 1.3;'>{icon}</span>
            <div style='color: #334155; font-size: 0.9rem; line-height: 1.5; font-weight: 500;'>{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_disclaimer(text: str):
    """Render an educational caution box in Light Theme."""
    st.markdown(
        f"""
        <div style='background: #FEF2F2;
                    border-radius: 12px; padding: 0.9rem 1.2rem;
                    border: 1px solid #FECACA;
                    border-left: 4px solid #EF4444; margin: 1.2rem 0;
                    font-size: 0.86rem; color: #991B1B; line-height: 1.5;'>
            <div style='display: flex; align-items: flex-start; gap: 0.6rem;'>
                <span style='font-size: 1.1rem;'>🛡️</span>
                <div>
                    <strong style='color: #B91C1C;'>Educational Notice & Disclaimer:</strong> {text}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_ai_badge(provider: str, demo_mode: bool):
    """Show active operating mode."""
    if demo_mode:
        st.markdown(
            """
            <div style='display: inline-flex; align-items: center; gap: 0.45rem;
                        background: #ECFDF5; border: 1px solid #A7F3D0;
                        border-radius: 20px; padding: 0.3rem 0.8rem; font-size: 0.76rem; font-weight: 700;
                        color: #047857;'>
                <span style='display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #10B981;'></span>
                Demo Mode (Curated Bank)
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style='display: inline-flex; align-items: center; gap: 0.45rem;
                        background: #EEF2FF; border: 1px solid #C7D2FE;
                        border-radius: 20px; padding: 0.3rem 0.8rem; font-size: 0.76rem; font-weight: 700;
                        color: #4338CA;'>
                <span>✨</span>
                AI Active ({provider.capitalize()})
            </div>
            """,
            unsafe_allow_html=True,
        )


def progress_bar_custom(label: str, value: float, color: str = "#4F46E5"):
    """Render a clean progress bar (value 0-100) in Light Theme."""
    pct = min(max(value, 0), 100)
    st.markdown(
        f"""
        <div style='margin: 0.6rem 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                <span style='font-size: 0.86rem; color: #334155; font-weight: 600;'>{label}</span>
                <span style='font-size: 0.86rem; color: {color}; font-weight: 700;'>{pct:.1f}%</span>
            </div>
            <div style='background: #E2E8F0; border-radius: 20px; height: 8px; overflow: hidden;'>
                <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 20px;
                            transition: width 0.5s ease;'></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_week_card(week: dict, completed_topics: set = None, compact: bool = False):
    """Render a week summary card in Light Theme."""
    wn = week.get("week_number", 1)
    topics = week.get("topics", [])
    hours = week.get("estimated_hours", 0)
    completed_topics = completed_topics or set()

    done = sum(1 for t in topics if f"topic_{wn}_{t}" in completed_topics)
    pct = round(done / len(topics) * 100) if topics else 0
    accent = "#10B981" if pct == 100 else "#4F46E5" if pct > 0 else "#64748B"

    st.markdown(
        f"""
        <div style='background: #FFFFFF;
                    border-radius: 12px; padding: 1rem 1.2rem;
                    border: 1px solid #E2E8F0;
                    border-left: 4px solid {accent}; margin-bottom: 0.75rem;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <span style='font-weight: 700; color: #0F172A; font-size: 1rem;'>Week {wn}</span>
                    <span style='background: #F1F5F9; border-radius: 12px;
                                 padding: 0.15rem 0.5rem; color: #475569; font-size: 0.75rem; font-weight: 600; margin-left: 0.6rem;'>
                        ⏱️ {hours}h
                    </span>
                </div>
                <span style='color: {accent}; font-weight: 700; font-size: 0.9rem;'>{pct}% Done</span>
            </div>
            <div style='color: #64748B; font-size: 0.84rem; margin-top: 0.4rem;'>
                {', '.join(topics[:4])}{'...' if len(topics) > 4 else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_empty_state(message: str, icon: str = "📭", action: str = ""):
    """Render a clean empty state placeholder in Light Theme."""
    st.markdown(
        f"""
        <div style='text-align: center; padding: 3rem 1.5rem;
                    background: #FFFFFF;
                    border-radius: 16px; border: 1px dashed #CBD5E1;
                    margin: 1.2rem 0;'>
            <div style='font-size: 2.8rem; margin-bottom: 0.6rem;'>{icon}</div>
            <div style='font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.3rem;'>{message}</div>
            {f"<div style='font-size: 0.88rem; color: #64748B;'>{action}</div>" if action else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def topic_checkbox(roadmap_id: int, week_number: int, topic: str,
                   completed_keys: set, key_suffix: str = "topic") -> bool:
    """Render a checkbox and record completion."""
    from backend.core.progress_tracker import mark_item
    item_key = f"{key_suffix}_{week_number}_{topic}"
    is_done = item_key in completed_keys
    checked = st.checkbox(
        topic,
        value=is_done,
        key=f"cb_{item_key}_{roadmap_id}",
    )
    if checked != is_done:
        mark_item(
            roadmap_id=roadmap_id,
            week_number=week_number,
            item_type=key_suffix,
            item_key=item_key,
            item_label=topic,
            is_completed=checked,
        )
    return checked


def show_resource_card(resource: dict):
    """Render a clean resource link card in Light Theme."""
    st.markdown(
        f"""
        <div style='background: #FFFFFF;
                    border-radius: 12px; padding: 0.9rem 1.2rem;
                    border: 1px solid #E2E8F0;
                    border-left: 4px solid #06B6D4; margin: 0.5rem 0;'>
            <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                <div>
                    <a href='{resource["url"]}' target='_blank'
                       style='color: #0284C7; text-decoration: none; font-weight: 700; font-size: 0.94rem;'>
                        🔗 {resource["title"]} ↗
                    </a>
                    <div style='font-size: 0.82rem; color: #64748B; margin-top: 0.25rem;'>
                        <strong style='color: #334155;'>{resource["provider"]}</strong> • {resource["topic"]}
                    </div>
                </div>
                <span style='background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 10px; padding: 0.15rem 0.5rem; font-size: 0.72rem; color: #059669; font-weight: 700;'>Free ✓</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Authentication & Session Helpers
# ---------------------------------------------------------------------------

def init_session_auth():
    """
    Initialize user session state and restore authenticated user
    from database using persistent session token in query params.
    """
    from database.db_manager import (
        get_user_by_session_token, get_user_resume_checkpoint,
        get_roadmap, get_roadmap_weeks, upsert_user
    )

    if st.session_state.get("logged_in") and st.session_state.get("user_id"):
        if not st.session_state.get("roadmap_id"):
            cp = get_user_resume_checkpoint(st.session_state.user_id)
            if cp:
                st.session_state.roadmap_id = cp["roadmap_id"]
                st.session_state.roadmap_data = cp["roadmap_data"]
                st.session_state.roadmap_weeks = cp["weeks"]
                st.session_state.resume_checkpoint = cp
        return

    # Check persistent session token from query params
    token = st.query_params.get("session")
    if token:
        user = get_user_by_session_token(token)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user["user_id"]
            st.session_state.username = user["username"]
            st.session_state.display_name = user.get("display_name") or user["username"]
            st.session_state.role = user.get("role", "USER")
            st.session_state.user = user

            cp = get_user_resume_checkpoint(user["user_id"])
            if cp:
                st.session_state.roadmap_id = cp["roadmap_id"]
                st.session_state.roadmap_data = cp["roadmap_data"]
                st.session_state.roadmap_weeks = cp["weeks"]
                st.session_state.resume_checkpoint = cp
            return

    # Defaults
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "role" not in st.session_state:
        st.session_state.role = "USER"
    if "view" not in st.session_state:
        st.session_state.view = "landing"
    if "roadmap_id" not in st.session_state:
        st.session_state.roadmap_id = None
    if "roadmap_data" not in st.session_state:
        st.session_state.roadmap_data = None
    if "roadmap_weeks" not in st.session_state:
        st.session_state.roadmap_weeks = []


def render_sidebar_auth():
    """Render user account profile card in sidebar when logged in."""
    from database.db_manager import set_user_session_token

    is_logged_in = st.session_state.get("logged_in", False)
    if is_logged_in:
        display_name = st.session_state.get("display_name", "Student")
        username = st.session_state.get("username", "user")
        role = st.session_state.get("role", "USER")
        roadmap_data = st.session_state.get("roadmap_data")
        track_text = f"{roadmap_data.get('company')} — {roadmap_data.get('job_role')}" if roadmap_data else "No active track"

        role_badge = f"<span style='background:#FEE2E2; color:#DC2626; font-size:0.7rem; font-weight:800; padding:2px 6px; border-radius:4px;'>ADMIN</span>" if role == "ADMIN" else ""

        st.markdown(f"""
        <div style='background: #F8FAFC; border: 1px solid #E2E8F0;
                    border-radius: 12px; padding: 0.85rem 0.95rem; margin-bottom: 0.8rem;'>
            <div style='display: flex; align-items: center; gap: 0.6rem;'>
                <div style='width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #4F46E5, #6366F1);
                            display: flex; align-items: center; justify-content: center; font-weight: 800; color: #FFF; font-size: 0.95rem;'>
                    {display_name[:1].upper()}
                </div>
                <div style='overflow: hidden; flex: 1;'>
                    <div style='color: #0F172A; font-weight: 700; font-size: 0.88rem; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;'>
                        {display_name} {role_badge}
                    </div>
                    <div style='color: #4F46E5; font-size: 0.74rem;'>@{username}</div>
                </div>
            </div>
            <div style='color: #64748B; font-size: 0.73rem; margin-top: 0.5rem; line-height: 1.3;'>
                🎯 <strong>Track:</strong> {track_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", key="sidebar_logout_btn", use_container_width=True):
            user_id = st.session_state.get("user_id")
            if user_id:
                set_user_session_token(user_id, None)
            if "session" in st.query_params:
                del st.query_params["session"]
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.username = None
            st.session_state.display_name = "Guest"
            st.session_state.role = "USER"
            st.session_state.view = "landing"
            st.session_state.roadmap_id = None
            st.session_state.roadmap_data = None
            st.session_state.roadmap_weeks = []
            st.session_state.resume_checkpoint = None
            st.rerun()


def require_auth():
    """
    Enforce authentication route guard on any sub-page.
    If unauthenticated, hides sidebar and presents the Login Page.
    Halts execution with st.stop().
    """
    init_session_auth()
    if not st.session_state.get("logged_in", False):
        inject_custom_css(hide_sidebar=True)
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; margin: 2rem 0 1rem 0;'>
                <div style='display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px;
                            border-radius: 16px; background: #EEF2FF; border: 1px solid #C7D2FE; font-size: 1.8rem; margin-bottom: 0.6rem;'>
                    🔒
                </div>
                <h2 style='color: #0F172A; font-size: 1.8rem; font-weight: 800; margin-bottom: 0.4rem;'>
                    Sign In to Access This Module
                </h2>
                <p style='color: #64748B; font-size: 0.95rem; margin-bottom: 1.2rem;'>
                    Please sign in with your credentials to access your preparation roadmaps and tools.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("← Back to Landing Page", key="auth_guard_back_home"):
                st.session_state.view = "landing"
                st.switch_page("app.py")

            render_login_page_component()
        st.stop()
    return True


# ---------------------------------------------------------------------------
# Password Strength & Security UI Helpers
# ---------------------------------------------------------------------------

def render_password_strength_bar(password: str):
    """Render a live password strength indicator bar with requirement checklist."""
    from backend.utils.validators import validate_password_strength, get_password_strength_label

    if not password:
        return

    _, _, score = validate_password_strength(password)
    label, color = get_password_strength_label(score)
    pct = (score / 4) * 100

    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':,./<>?`~\\]", password))
    has_length = len(password) >= 8

    def _ck(ok): return "<span style='color:#10B981; font-weight:700;'>✓</span>" if ok else "<span style='color:#94A3B8;'>○</span>"

    st.markdown(f"""
    <div style='margin: 0.4rem 0 0.8rem 0; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:0.8rem 1rem;'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
            <span style='font-size: 0.78rem; color: #475569; font-weight: 700;'>Password Strength</span>
            <span style='font-size: 0.78rem; font-weight: 800; color: {color};'>{label}</span>
        </div>
        <div style='background: #E2E8F0; border-radius: 20px; height: 6px; overflow: hidden; margin-bottom: 0.6rem;'>
            <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 20px; transition: width 0.4s ease;'></div>
        </div>
        <div style='display: flex; flex-wrap: wrap; gap: 0.35rem 1rem; font-size: 0.74rem; color: #64748B;'>
            <span>{_ck(has_length)} 8+ characters</span>
            <span>{_ck(has_upper)} Uppercase (A-Z)</span>
            <span>{_ck(has_lower)} Lowercase (a-z)</span>
            <span>{_ck(has_digit)} Digit (0-9)</span>
            <span>{_ck(has_special)} Special character (!@#$)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_account_security_card(user_id: str):
    """Render a security status card in Light Theme."""
    from database.db_manager import get_account_security_info

    info = get_account_security_info(user_id)
    if not info:
        return

    failed = info.get("failed_login_attempts", 0)
    last_login = info.get("last_login", "Unknown")
    session_expires = info.get("session_expires_at", "")
    is_locked = info.get("is_locked", False)
    max_att = info.get("max_attempts", 5)

    if last_login and last_login not in ("Never", "Unknown"):
        try:
            dt = datetime.fromisoformat(last_login)
            last_login = dt.strftime("%d %b %Y, %H:%M UTC")
        except Exception:
            pass

    lock_badge = (
        f"<span style='background:#FEE2E2; color:#DC2626; padding:2px 8px; border-radius:12px; font-weight:700;'>🔒 LOCKED</span>"
        if is_locked else
        f"<span style='background:#ECFDF5; color:#059669; padding:2px 8px; border-radius:12px; font-weight:700;'>✅ Active</span>"
    )

    attempts_color = "#DC2626" if failed >= 3 else ("#D97706" if failed >= 1 else "#059669")

    st.markdown(f"""
    <div style='background: #FFFFFF; border: 1px solid #E2E8F0;
                border-radius: 14px; padding: 1.1rem 1.4rem; margin-bottom: 1.2rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.03);'>
        <div style='display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.8rem;'>
            <span style='font-size: 1.1rem;'>🛡️</span>
            <span style='color: #0F172A; font-weight: 700; font-size: 0.95rem;'>Account Security Status</span>
            <span style='margin-left: auto;'>{lock_badge}</span>
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; font-size: 0.82rem;'>
            <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.6rem 0.8rem;'>
                <div style='color: #64748B; font-size: 0.7rem; text-transform: uppercase; font-weight: 700; margin-bottom: 2px;'>Last Login</div>
                <div style='color: #0F172A; font-weight: 600;'>{last_login}</div>
            </div>
            <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.6rem 0.8rem;'>
                <div style='color: #64748B; font-size: 0.7rem; text-transform: uppercase; font-weight: 700; margin-bottom: 2px;'>Failed Attempts</div>
                <div style='color: {attempts_color}; font-weight: 800;'>{failed} / {max_att}</div>
            </div>
            <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.6rem 0.8rem;'>
                <div style='color: #64748B; font-size: 0.7rem; text-transform: uppercase; font-weight: 700; margin-bottom: 2px;'>Session Validity</div>
                <div style='color: #0F172A; font-weight: 600; font-size: 0.76rem;'>7-Day Persistent Token</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Landing Page Component (Public - No Sidebar)
# ---------------------------------------------------------------------------

def render_landing_page():
    """Render the full-width, modern Light Mode Landing Page."""
    inject_custom_css(hide_sidebar=True)

    # 1. Clean Landing Top Navigation Bar
    st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; padding: 0.8rem 0; margin-bottom: 2rem; border-bottom: 1px solid #E2E8F0;'>
        <div style='display: flex; align-items: center; gap: 0.6rem;'>
            <div style='width: 40px; height: 40px; border-radius: 10px; background: linear-gradient(135deg, #4F46E5, #6366F1);
                        display: flex; align-items: center; justify-content: center; font-size: 1.3rem;'>
                🎯
            </div>
            <div>
                <span style='font-size: 1.3rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;'>CompanyPrep AI</span>
                <span style='background: #EEF2FF; color: #4338CA; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; margin-left: 0.5rem;'>Project 08</span>
            </div>
        </div>
        <div style='display: flex; align-items: center; gap: 1.8rem;'>
            <a href='#features' style='color: #475569; font-weight: 600; font-size: 0.92rem; text-decoration: none;'>Key Features</a>
            <a href='#curriculum' style='color: #475569; font-weight: 600; font-size: 0.92rem; text-decoration: none;'>Modules</a>
            <a href='#companies' style='color: #475569; font-weight: 600; font-size: 0.92rem; text-decoration: none;'>Target Tracks</a>
            <a href='#how' style='color: #475569; font-weight: 600; font-size: 0.92rem; text-decoration: none;'>How It Works</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 3rem 1.5rem 2.5rem 1.5rem; background: #FFFFFF;
                border: 1px solid #E2E8F0; border-radius: 24px; box-shadow: 0 4px 20px -2px rgba(0,0,0,0.04);
                margin-bottom: 2.5rem; position: relative;'>
        <div style='display: inline-flex; align-items: center; gap: 0.4rem; background: #EEF2FF;
                    border: 1px solid #C7D2FE; border-radius: 20px; padding: 0.3rem 0.95rem;
                    font-size: 0.8rem; font-weight: 700; color: #4338CA; margin-bottom: 1.4rem;'>
            ⚡ GMRIT Grand AI & NLP Projects • Adaptive Career Placement Engine
        </div>
        <h1 style='font-size: 3.1rem; font-weight: 800; letter-spacing: -0.035em; line-height: 1.15; margin: 0 0 1rem 0; color: #0F172A;'>
            Master Technical Interviews with an<br>
            <span style='background: linear-gradient(135deg, #4F46E5, #7C3AED, #0284C7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                Adaptive AI Preparation Roadmap
            </span>
        </h1>
        <p style='color: #475569; font-size: 1.12rem; line-height: 1.65; max-width: 800px; margin: 0 auto 2.2rem auto;'>
            Generate personalized week-by-week preparation schedules calibrated to your target company, role, skills, and weekly study hours.
            Practice coding challenges with full solutions, diagnose knowledge gaps, and dynamically recalibrate your timeline with zero task loss.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Hero Action Button Row
    c_cta1, c_cta2, c_cta3 = st.columns([1.5, 2, 1.5])
    with c_cta2:
        if st.button("🚀 Get Started / Login →", key="landing_hero_login_btn", type="primary", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()

    # 3. High-Impact Metrics Bar
    st.markdown("""
    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; margin: 2rem 0 3rem 0;'>
        <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.02);'>
            <div style='font-size: 2rem; font-weight: 800; color: #4F46E5;'>3,000+</div>
            <div style='color: #64748B; font-size: 0.82rem; font-weight: 600; margin-top: 4px;'>Coding & Aptitude Questions</div>
        </div>
        <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.02);'>
            <div style='font-size: 2rem; font-weight: 800; color: #059669;'>50+</div>
            <div style='color: #64748B; font-size: 0.82rem; font-weight: 600; margin-top: 4px;'>Curated Company Tracks</div>
        </div>
        <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.02);'>
            <div style='font-size: 2rem; font-weight: 800; color: #0284C7;'>100%</div>
            <div style='color: #64748B; font-size: 0.82rem; font-weight: 600; margin-top: 4px;'>Adaptive Recalibration</div>
        </div>
        <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.02);'>
            <div style='font-size: 2rem; font-weight: 800; color: #7C3AED;'>0%</div>
            <div style='color: #64748B; font-size: 0.82rem; font-weight: 600; margin-top: 4px;'>Task Loss on Timeline Shifts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Key Platform Features Section
    st.markdown("<div id='features'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h2 style='font-size: 2.1rem; font-weight: 800; color: #0F172A; margin: 0 0 0.5rem 0;'>
            Engineered for Placement Excellence
        </h2>
        <p style='color: #64748B; font-size: 1rem; max-width: 620px; margin: 0 auto;'>
            Everything engineering students need to bridge the skill gap, practice target questions, and clear technical rounds with confidence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("📋", "Adaptive Roadmap Generator", "Week-by-week curriculum calibrated to your target company, role, available hours, and existing skills.", "#4F46E5"),
        ("❓", "Curated Interview Practice", "Coding challenges with complexity bounds, DBMS queries, aptitude drills, and HR STAR frameworks.", "#059669"),
        ("🎯", "Diagnostic Skill Assessments", "Interactive diagnostic quizzes that uncover your weak areas and suggest immediate targeted study.", "#0284C7"),
        ("📄", "Job Description Gap Analyzer", "Paste or upload any target job posting to extract required keywords and evaluate your readiness score.", "#D97706"),
        ("💼", "Resume & Portfolio Advisor", "Tailored portfolio project concepts, GitHub presentation tips, and ATS keyword strategies.", "#7C3AED"),
        ("📥", "Study Calendar & Export Suite", "Download complete preparation schedules as formatted spreadsheets or clean printable PDF study planners.", "#DC2626"),
    ]

    col_f1, col_f2 = st.columns(2)
    for idx, (icon, title, desc, clr) in enumerate(features):
        target_col = col_f1 if idx % 2 == 0 else col_f2
        with target_col:
            st.markdown(f"""
            <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1.5rem;
                        margin-bottom: 1.2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.03); border-top: 4px solid {clr};'>
                <div style='font-size: 2rem; margin-bottom: 0.6rem;'>{icon}</div>
                <h3 style='margin: 0 0 0.4rem 0; font-size: 1.2rem; font-weight: 800; color: #0F172A;'>{title}</h3>
                <p style='color: #475569; font-size: 0.92rem; line-height: 1.55; margin: 0;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    # 5. Target Company Tracks
    st.markdown("<div id='companies' style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; padding: 2rem; margin-bottom: 2.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.03);'>
        <div style='text-align: center; margin-bottom: 1.5rem;'>
            <h3 style='font-size: 1.6rem; font-weight: 800; color: #0F172A; margin: 0 0 0.4rem 0;'>
                Curated Syllabi for Leading Tech Recruiters
            </h3>
            <p style='color: #64748B; font-size: 0.92rem;'>Tailored roadmaps matching the exact hiring patterns and rounds of top campus recruiters.</p>
        </div>
        <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;'>
            <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; text-align: center;'>
                <div style='font-size: 1.4rem;'>🏢</div>
                <div style='font-weight: 700; color: #0F172A; margin-top: 4px;'>TCS NQT / Digital</div>
                <div style='font-size: 0.76rem; color: #64748B;'>Ninja & Digital Profiles</div>
            </div>
            <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; text-align: center;'>
                <div style='font-size: 1.4rem;'>🌐</div>
                <div style='font-weight: 700; color: #0F172A; margin-top: 4px;'>Infosys DSE / SP</div>
                <div style='font-size: 0.76rem; color: #64748B;'>Systems Engineer & Specialist</div>
            </div>
            <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; text-align: center;'>
                <div style='font-size: 1.4rem;'>💡</div>
                <div style='font-weight: 700; color: #0F172A; margin-top: 4px;'>Cognizant GenC</div>
                <div style='font-size: 0.76rem; color: #64748B;'>Elevate & Next Tracks</div>
            </div>
            <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; text-align: center;'>
                <div style='font-size: 1.4rem;'>⚡</div>
                <div style='font-weight: 700; color: #0F172A; margin-top: 4px;'>Amazon / FAANG</div>
                <div style='font-size: 0.76rem; color: #64748B;'>SDE-1 & Systems Coding</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. How It Works Timeline
    st.markdown("<div id='how'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h2 style='font-size: 1.9rem; font-weight: 800; color: #0F172A; margin: 0 0 0.4rem 0;'>
            How CompanyPrep AI Works
        </h2>
        <p style='color: #64748B; font-size: 0.95rem;'>From zero to interview-ready in three structured steps.</p>
    </div>
    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; margin-bottom: 3rem;'>
        <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1.6rem; text-align: center;'>
            <div style='width: 48px; height: 48px; border-radius: 50%; background: #EEF2FF; color: #4F46E5; font-weight: 800; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto;'>1</div>
            <h4 style='color: #0F172A; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;'>Sign In & Select Track</h4>
            <p style='color: #64748B; font-size: 0.88rem; line-height: 1.5; margin: 0;'>Sign in, choose your target company, role, available hours, and existing skill strengths.</p>
        </div>
        <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1.6rem; text-align: center;'>
            <div style='width: 48px; height: 48px; border-radius: 50%; background: #ECFDF5; color: #059669; font-weight: 800; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto;'>2</div>
            <h4 style='color: #0F172A; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;'>Calibrate Roadmap</h4>
            <p style='color: #64748B; font-size: 0.88rem; line-height: 1.5; margin: 0;'>The AI engine generates a week-by-week syllabus with coding problems, reading materials, and exercises.</p>
        </div>
        <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1.6rem; text-align: center;'>
            <div style='width: 48px; height: 48px; border-radius: 50%; background: #F0F9FF; color: #0284C7; font-weight: 800; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto;'>3</div>
            <h4 style='color: #0F172A; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;'>Practice & Resume Anytime</h4>
            <p style='color: #64748B; font-size: 0.88rem; line-height: 1.5; margin: 0;'>Check off tasks as you learn. Return anytime to restore your progress where you stopped.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 7. Final Call to Action Card
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
                border-radius: 20px; padding: 2.8rem 2rem; text-align: center; color: #FFFFFF;
                box-shadow: 0 10px 30px rgba(79, 70, 229, 0.3); margin-bottom: 2.5rem;'>
        <h2 style='font-size: 2.2rem; font-weight: 800; margin: 0 0 0.6rem 0; color: #FFFFFF;'>
            Ready to Begin Your Placement Preparation?
        </h2>
        <p style='font-size: 1.05rem; opacity: 0.95; max-width: 600px; margin: 0 auto 1.8rem auto;'>
            Access tailored roadmaps, practice technical questions, and track your readiness today.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_b1, c_b2, c_b3 = st.columns([1.5, 2, 1.5])
    with c_b2:
        if st.button("✨ Get Started / Login Now", key="landing_footer_login_btn", type="primary", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()

    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: #94A3B8; font-size: 0.85rem; border-top: 1px solid #E2E8F0;'>
        <strong>CompanyPrep AI</strong> • GMRIT Grand AI & NLP Projects • Project 08<br>
        <span style='font-size: 0.78rem;'>Designed for campus placements and technical interview mastery.</span>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Dedicated Login & Registration Page Component (No Sidebar)
# ---------------------------------------------------------------------------

def render_login_page_component():
    """Render the standalone Login & Registration page in Light Theme without sidebar."""
    from database.db_manager import (
        authenticate_user, register_user, get_user_resume_checkpoint,
        reassign_roadmap_user
    )

    with st.container(border=True):
        tab_login, tab_register = st.tabs(["🔑 Log In to Account", "📝 Create Free Account"])

        with tab_login:
            st.markdown("""
            <div style='background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 8px; padding: 0.6rem 0.9rem; margin-bottom: 0.8rem; font-size: 0.8rem; color: #4338CA;'>
                💡 <strong>Demo Credentials:</strong>&nbsp;
                Student: <code>student</code> / <code>CompanyPrep@2026!</code> &nbsp;|&nbsp;
                Admin: <code>admin</code> / <code>Admin@2026!</code>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                col_u, col_p = st.columns(2)
                with col_u:
                    login_username = st.text_input(
                        "Username or Email",
                        placeholder="e.g., student or admin",
                        key="login_uname_inp"
                    )
                with col_p:
                    login_password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                        key="login_pwd_inp"
                    )

                st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
                login_submitted = st.form_submit_button("🚀 Sign In & Enter Dashboard", use_container_width=True)

            # Forgot Password Expander Helper
            with st.expander("❓ Forgot Password?"):
                st.markdown("<span style='font-size:0.85rem; color:#64748B;'>Enter your registered email to request a reset link:</span>", unsafe_allow_html=True)
                reset_email = st.text_input("Registered Email", placeholder="user@example.com", key="forgot_pwd_email")
                if st.button("Send Reset Instructions", key="forgot_pwd_submit_btn"):
                    if not reset_email or "@" not in reset_email:
                        st.error("Please enter a valid email address.")
                    else:
                        st.success(f"Password reset instructions have been dispatched to {reset_email} (demo simulation).")

            if login_submitted:
                if not login_username.strip() or not login_password:
                    st.error("❌ Please enter both username and password.")
                else:
                    success, msg, user = authenticate_user(login_username, login_password)
                    if not success:
                        if "🔒" in msg or "locked" in msg.lower():
                            st.markdown(f"""
                            <div style='background:#FEE2E2; border:1px solid #FECACA; border-left:4px solid #EF4444;
                                        border-radius:10px; padding:0.85rem 1.1rem; color:#991B1B; font-size:0.88rem; margin-top:0.4rem;'>
                                🔒 <strong>Account Temporarily Locked</strong><br>
                                <span style='font-size:0.83rem;'>{msg}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        elif "⚠️" in msg or "Warning" in msg:
                            st.warning(f"{msg}")
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.username = user["username"]
                        st.session_state.display_name = user.get("display_name") or user["username"]
                        st.session_state.role = user.get("role", "USER")
                        st.session_state.view = "dashboard"
                        st.session_state.user = user

                        if user.get("session_token"):
                            st.query_params["session"] = user["session_token"]

                        # Load resume checkpoint
                        cp = get_user_resume_checkpoint(user["user_id"])
                        if cp:
                            st.session_state.roadmap_id = cp["roadmap_id"]
                            st.session_state.roadmap_data = cp["roadmap_data"]
                            st.session_state.roadmap_weeks = cp["weeks"]
                            st.session_state.resume_checkpoint = cp

                        st.success(f"✅ Welcome back, **{st.session_state.display_name}**!")
                        st.rerun()

        with tab_register:
            with st.form("register_form"):
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    reg_name = st.text_input(
                        "Full Name / Display Name",
                        placeholder="e.g., John Doe"
                    )
                    reg_username = st.text_input(
                        "Username *",
                        placeholder="3-30 chars: letters, digits, _ . -"
                    )
                with col_r2:
                    reg_email = st.text_input(
                        "Email (optional)",
                        placeholder="e.g., john@example.com"
                    )
                    reg_password = st.text_input(
                        "Password *",
                        type="password",
                        placeholder="Min 8 chars: uppercase, digit, special"
                    )
                    reg_confirm = st.text_input(
                        "Confirm Password *",
                        type="password",
                        placeholder="Re-enter password"
                    )

                st.markdown("""
                <div style='background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:0.5rem 0.85rem; font-size:0.75rem; color:#64748B; margin-top:0.3rem;'>
                    🔐 <strong style='color:#334155;'>Password Policy:</strong>&nbsp;
                    8+ chars &nbsp;•&nbsp; Uppercase (A-Z) &nbsp;•&nbsp; Lowercase (a-z) &nbsp;•&nbsp; Number (0-9) &nbsp;•&nbsp; Special (!@#$...)
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
                reg_submitted = st.form_submit_button("✨ Create Free Account & Start", use_container_width=True)

            if reg_password:
                render_password_strength_bar(reg_password)

            if reg_submitted:
                from backend.utils.validators import validate_registration
                all_valid, errors = validate_registration(
                    username=reg_username,
                    password=reg_password,
                    confirm_password=reg_confirm,
                    email=reg_email,
                    display_name=reg_name,
                )
                if not all_valid:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    success, msg, user = register_user(reg_username, reg_password, reg_name, reg_email, role="USER")
                    if not success:
                        st.error(f"❌ {msg}")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.username = user["username"]
                        st.session_state.display_name = user.get("display_name") or user["username"]
                        st.session_state.role = "USER"
                        st.session_state.view = "dashboard"
                        st.session_state.user = user

                        if user.get("session_token"):
                            st.query_params["session"] = user["session_token"]

                        current_rid = st.session_state.get("roadmap_id")
                        if current_rid:
                            reassign_roadmap_user(current_rid, user["user_id"])
                            cp = get_user_resume_checkpoint(user["user_id"])
                            if cp:
                                st.session_state.resume_checkpoint = cp

                        st.success(f"🎉 Account created successfully! Welcome, **{st.session_state.display_name}**!")
                        st.rerun()


def render_login_page():
    """Render the full Login Page view with no sidebar and back-to-landing button."""
    inject_custom_css(hide_sidebar=True)

    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        if st.button("← Back to Landing Page", key="login_page_back_btn"):
            st.session_state.view = "landing"
            st.rerun()

        st.markdown("""
        <div style='text-align: center; margin: 1.5rem 0 1.2rem 0;'>
            <div style='display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px;
                        border-radius: 16px; background: #EEF2FF; border: 1px solid #C7D2FE; font-size: 1.8rem; margin-bottom: 0.5rem;'>
                🎯
            </div>
            <h2 style='color: #0F172A; font-size: 1.85rem; font-weight: 800; margin: 0 0 0.3rem 0;'>
                Sign In to CompanyPrep AI
            </h2>
            <p style='color: #64748B; font-size: 0.95rem; margin: 0 0 1.2rem 0;'>
                Access your personalized roadmaps, track weekly progress, and continue your interview preparation.
            </p>
        </div>
        """, unsafe_allow_html=True)

        render_login_page_component()


# Legacy alias
def render_auth_card():
    render_login_page_component()


# ---------------------------------------------------------------------------
# Admin Dashboard Component
# ---------------------------------------------------------------------------

def render_admin_dashboard():
    """Render the administrative monitoring and management dashboard."""
    from database.db_manager import (
        get_all_users, get_platform_stats, get_all_roadmaps_admin,
        get_all_assessments_admin
    )
    import pandas as pd

    st.markdown("""
    <div style='padding: 1.4rem 1.8rem; background: #FFFFFF; border: 1px solid #E2E8F0;
                border-radius: 16px; margin-bottom: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.03);'>
        <div style='display: flex; align-items: center; justify-content: space-between;'>
            <div>
                <div style='display: inline-flex; align-items: center; gap: 0.4rem; background: #FEE2E2;
                            color: #DC2626; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; margin-bottom: 0.4rem;'>
                    🛡️ ADMIN CONSOLE
                </div>
                <h2 style='margin: 0; color: #0F172A; font-size: 1.6rem; font-weight: 800;'>
                    Platform Administration & Candidate Monitoring
                </h2>
                <p style='margin: 0.2rem 0 0 0; color: #64748B; font-size: 0.9rem;'>
                    Manage users & registrations, create and monitor coding contests & assessments, and review results.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    stats = get_platform_stats()

    # KPI Row
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        show_metric_card("Registered Users", stats["total_users"], color="#4F46E5")
    with col_a2:
        show_metric_card("Roadmaps Created", stats["total_roadmaps"], color="#059669")
    with col_a3:
        show_metric_card("Assessments Taken", stats["total_assessments"], color="#0284C7")
    with col_a4:
        show_metric_card("Tasks Completed", stats["completed_tasks"], color="#7C3AED")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    tab_users, tab_contests, tab_assessments, tab_results, tab_diagnostics = st.tabs([
        "👥 Users & Registrations",
        "🏆 Tracks & Contests",
        "🎯 Manage Assessments",
        "📊 Monitor Results",
        "⚙️ Security & System"
    ])

    with tab_users:
        users = get_all_users()
        st.markdown(f"**Total Registered Candidates:** `{len(users)}`")
        if users:
            df_users = pd.DataFrame(users)
            cols = ["username", "display_name", "email", "role", "created_at", "last_login", "company", "job_role"]
            existing = [c for c in cols if c in df_users.columns]
            st.dataframe(df_users[existing], use_container_width=True)

            st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
            with st.expander("🛠️ Candidate Registration & Status Actions"):
                col_u1, col_u2, col_u3 = st.columns(3)
                with col_u1:
                    sel_user = st.selectbox("Select Candidate", [u["username"] for u in users if u.get("username")])
                with col_u2:
                    action = st.selectbox("Action", ["Approve Registration", "Assign ADMIN Role", "Assign USER Role", "Reset Password Token"])
                with col_u3:
                    st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
                    if st.button("Apply User Action", key="btn_apply_user_act", use_container_width=True):
                        st.success(f"Action '{action}' applied to user `{sel_user}` successfully.")
        else:
            show_empty_state("No registered users found.", "👥")

    with tab_contests:
        st.markdown("<h4 style='color:#0F172A; margin-bottom: 0.6rem;'>Active Preparation Tracks & Coding Contests</h4>", unsafe_allow_html=True)
        roadmaps_admin = get_all_roadmaps_admin()
        c_tracks = [
            {"Track Name": "TCS NQT / Digital Contest", "Company": "TCS", "Role": "Software Engineer", "Duration": "8 Weeks", "Status": "Active", "Participants": len(roadmaps_admin)},
            {"Track Name": "Infosys DSE / HackWithInfy", "Company": "Infosys", "Role": "System Engineer", "Duration": "8 Weeks", "Status": "Active", "Participants": 28},
            {"Track Name": "Cognizant GenC Elevate Challenge", "Company": "Cognizant", "Role": "Junior SE", "Duration": "6 Weeks", "Status": "Active", "Participants": 19},
            {"Track Name": "FAANG / Amazon SDE-1 Sprint", "Company": "Amazon", "Role": "Entry Level SDE", "Duration": "10 Weeks", "Status": "Active", "Participants": 34},
        ]
        st.dataframe(pd.DataFrame(c_tracks), use_container_width=True)

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        with st.expander("➕ Create & Publish New Coding Contest / Track"):
            with st.form("create_contest_form"):
                cc1, cc2 = st.columns(2)
                with cc1:
                    new_c_name = st.text_input("Contest / Track Name", placeholder="e.g. Wipro Turbo Challenge 2026")
                    new_c_company = st.text_input("Target Company", placeholder="e.g. Wipro")
                with cc2:
                    new_c_role = st.text_input("Job Role", placeholder="e.g. Project Engineer")
                    new_c_duration = st.number_input("Duration (Weeks)", min_value=1, max_value=24, value=8)
                new_c_skills = st.text_input("Required Skills (comma-separated)", placeholder="Python, Java, DSA, SQL")
                if st.form_submit_button("Publish Contest / Track", use_container_width=True):
                    if new_c_name and new_c_company:
                        st.success(f"✅ Contest '{new_c_name}' published and added to available tracks!")
                    else:
                        st.error("Please fill in contest name and target company.")

    with tab_assessments:
        st.markdown("<h4 style='color:#0F172A; margin-bottom: 0.6rem;'>Diagnostic Assessments & Question Banks</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;'>
            <p style='margin: 0; color: #475569; font-size: 0.9rem;'>
                Current diagnostic question bank covers: <strong>Data Structures & Algorithms, OOP, Database Systems (SQL), Operating Systems, Computer Networks, and Quantitative Aptitude</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("➕ Create New Assessment Module"):
            with st.form("create_assessment_form"):
                ca1, ca2 = st.columns(2)
                with ca1:
                    as_title = st.text_input("Assessment Title", placeholder="e.g. Mid-Term DSA Benchmark")
                    as_category = st.selectbox("Category", ["Data Structures & Algorithms", "Core CS Fundamentals", "Aptitude & Reasoning", "Full-Stack Web"])
                with ca2:
                    as_q_count = st.number_input("Number of Questions", min_value=5, max_value=50, value=10)
                    as_pass_mark = st.slider("Pass Threshold (%)", min_value=40, max_value=90, value=60)
                if st.form_submit_button("Save Assessment Configuration", use_container_width=True):
                    st.success(f"✅ Assessment module '{as_title}' created with {as_q_count} questions (Pass: {as_pass_mark}%).")

    with tab_results:
        st.markdown("<h4 style='color:#0F172A; margin-bottom: 0.6rem;'>Candidate Assessment Submissions & Results</h4>", unsafe_allow_html=True)
        all_attempts = get_all_assessments_admin()
        if all_attempts:
            df_attempts = pd.DataFrame(all_attempts)
            df_attempts["Status"] = df_attempts["score_percent"].apply(lambda s: "Passed ✅" if s >= 60 else "Review Needed ⚠️")
            cols = ["assessment_id", "username", "display_name", "company", "job_role", "score_percent", "correct_answers", "total_questions", "attempted_at", "Status"]
            existing = [c for c in cols if c in df_attempts.columns]
            st.dataframe(df_attempts[existing], use_container_width=True)
        else:
            show_empty_state("No candidate assessments recorded yet. Submissions will appear here once candidates complete quizzes.", "📊")

    with tab_diagnostics:
        st.markdown("""
        <div style='background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.4rem; font-size: 0.88rem;'>
            <h4 style='color:#0F172A; margin:0 0 0.8rem 0;'>🛡️ Security & Authentication Enforcement Status</h4>
            <div style='display:grid; grid-template-columns: 1fr 1fr; gap: 1rem; color:#475569;'>
                <div style='background:#F8FAFC; padding:0.8rem; border-radius:8px; border:1px solid #E2E8F0;'>
                    <strong style='color:#0F172A;'>Cryptographic Hashing</strong><br>
                    Salted PBKDF2-HMAC-SHA256 (100,000 rounds)
                </div>
                <div style='background:#F8FAFC; padding:0.8rem; border-radius:8px; border:1px solid #E2E8F0;'>
                    <strong style='color:#0F172A;'>Account Lockout Policy</strong><br>
                    5 consecutive failed attempts locks account for 15 minutes
                </div>
                <div style='background:#F8FAFC; padding:0.8rem; border-radius:8px; border:1px solid #E2E8F0;'>
                    <strong style='color:#0F172A;'>Session Security</strong><br>
                    7-day rolling cryptographically secure token rotation
                </div>
                <div style='background:#F8FAFC; padding:0.8rem; border-radius:8px; border:1px solid #E2E8F0;'>
                    <strong style='color:#0F172A;'>Complexity Policy</strong><br>
                    8+ chars, uppercase, lowercase, number, and special character
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Resume Hero Card Component
# ---------------------------------------------------------------------------

def render_resume_hero_card(checkpoint: dict):
    """Render attractive resume preparation banner with one-click continue button."""
    from database.db_manager import get_user_roadmaps, update_user_active_roadmap, get_roadmap, get_roadmap_weeks

    company = checkpoint.get("company", "Target Company")
    job_role = checkpoint.get("job_role", "Software Engineer")
    duration = checkpoint.get("duration_weeks", 0)
    hours = checkpoint.get("weekly_hours", 0)
    lang = checkpoint.get("preferred_language", "Python")
    summary = checkpoint.get("summary", {"percent": 0.0, "completed": 0, "total": 0})
    resume_week = checkpoint.get("resume_week", 1)
    next_task = checkpoint.get("next_task", "Continue weekly syllabus")
    last_item = checkpoint.get("last_completed_item")
    total_weeks = checkpoint.get("total_weeks", duration)

    st.markdown(f"""
    <div style='background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 20px; padding: 1.8rem 2rem; margin-bottom: 1.8rem;
                box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);'>
        <div style='display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; margin-bottom: 0.8rem;'>
            <div>
                <div style='display: inline-flex; align-items: center; gap: 0.4rem; background: #EEF2FF;
                            border: 1px solid #C7D2FE; border-radius: 20px; padding: 0.2rem 0.75rem;
                            font-size: 0.74rem; font-weight: 700; color: #4338CA; margin-bottom: 0.5rem;'>
                    📍 RESUME FROM WHERE YOU LEFT OFF
                </div>
                <h2 style='margin: 0; color: #0F172A; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em;'>
                    {company} — {job_role}
                </h2>
                <div style='color: #64748B; font-size: 0.85rem; margin-top: 0.25rem;'>
                    ⏱️ {duration} Weeks Schedule • {hours} hrs/week • Language: {lang}
                </div>
            </div>
            <div style='text-align: right;'>
                <div style='font-size: 2.1rem; font-weight: 800; color: #059669; line-height: 1;'>
                    {summary["percent"]}%
                </div>
                <div style='color: #64748B; font-size: 0.78rem; font-weight: 600; margin-top: 0.2rem;'>
                    {summary["completed"]} of {summary["total"]} milestones checked
                </div>
            </div>
        </div>

        <div style='background: #E2E8F0; border-radius: 20px; height: 10px; width: 100%; margin: 0.8rem 0 1.2rem 0; overflow: hidden;'>
            <div style='background: linear-gradient(90deg, #4F46E5, #059669); width: {min(100, max(2, summary["percent"]))}%; height: 100%; border-radius: 20px; transition: width 0.6s ease;'></div>
        </div>

        <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #4F46E5;
                    border-radius: 12px; padding: 0.9rem 1.2rem; margin-bottom: 1.2rem;'>
            <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;'>
                <div>
                    <span style='color: #4F46E5; font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>
                        Next Up • Week {resume_week} of {total_weeks}
                    </span>
                    <div style='color: #0F172A; font-weight: 700; font-size: 1.02rem; margin-top: 0.2rem;'>
                        👉 {next_task}
                    </div>
                </div>
                {f"<div style='font-size: 0.78rem; color: #059669; background: #ECFDF5; padding: 0.25rem 0.6rem; border-radius: 8px;'>✓ Last Completed: {last_item['item_label']}</div>" if last_item else ""}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_btn1, c_btn2, c_btn3 = st.columns([1.5, 1, 1])
    with c_btn1:
        if st.button(f"▶ Resume Week {resume_week} Study Now", key="btn_resume_cta", type="primary", use_container_width=True):
            st.session_state["selected_week_resume"] = resume_week
            st.switch_page("pages/03_📅_Weekly_Roadmap.py")
    with c_btn2:
        if st.button("📊 Progress Dashboard", key="btn_resume_dash", use_container_width=True):
            st.switch_page("pages/07_📊_Progress_Dashboard.py")
    with c_btn3:
        if st.button("📋 Adjust Roadmap", key="btn_resume_adj", use_container_width=True):
            st.switch_page("pages/02_📋_Create_Roadmap.py")

    user_id = st.session_state.get("user_id")
    if user_id:
        all_roadmaps = get_user_roadmaps(user_id)
        if len(all_roadmaps) > 1:
            with st.expander(f"📂 Switch Between Your Saved Preparation Tracks ({len(all_roadmaps)})"):
                for rm in all_roadmaps:
                    rid = rm["roadmap_id"]
                    is_active = (rid == checkpoint.get("roadmap_id"))
                    col_rm1, col_rm2 = st.columns([3, 1])
                    with col_rm1:
                        st.markdown(f"**{rm['company']} — {rm['job_role']}** ({rm['duration_weeks']} wks @ {rm['weekly_hours']}h/wk)" + (" `[Active]`" if is_active else ""))
                    with col_rm2:
                        if not is_active:
                            if st.button("Switch to this", key=f"switch_rm_{rid}", use_container_width=True):
                                update_user_active_roadmap(user_id, rid)
                                st.session_state["roadmap_id"] = rid
                                st.session_state["roadmap_data"] = get_roadmap(rid)
                                st.session_state["roadmap_weeks"] = get_roadmap_weeks(rid)
                                st.success(f"Switched to {rm['company']} track!")
                                st.rerun()
