"""
backend/core/export_manager.py
Handles CSV and PDF export of study calendars and roadmaps.
"""
import csv
import io
from datetime import datetime, timezone
from typing import Optional

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


def _safe_pdf_str(text: str) -> str:
    """Sanitize string for standard FPDF core fonts (latin-1)."""
    if not text:
        return ""
    replacements = {
        "—": "-",
        "–": "-",
        "•": "*",
        "…": "...",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "\u2022": "*",
        "\u2013": "-",
        "\u2014": "-",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


def export_roadmap_csv(roadmap: dict, weeks: list) -> bytes:
    """
    Export the roadmap as a CSV file.
    Returns bytes suitable for Streamlit download_button.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Week", "Day", "Topic", "Learning Objective",
        "Estimated Hours", "Task Description", "Completion Status"
    ])

    company = roadmap.get("company", "")
    role = roadmap.get("job_role", "")

    if not weeks:
        writer.writerow(["No roadmap data available", "", "", "", "", "", ""])
        return output.getvalue().encode("utf-8")

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for week in weeks:
        wn = week.get("week_number", 1)
        topics = week.get("topics", [])
        objectives = week.get("objectives", [])
        tasks = week.get("daily_tasks", [])
        hours = week.get("estimated_hours", 0)
        hours_per_topic = round(hours / max(len(topics), 1), 1)

        for i, topic in enumerate(topics):
            objective = objectives[i] if i < len(objectives) else f"Study {topic}"
            day_idx = i % 7
            task_idx = i * 2
            task1 = tasks[task_idx] if task_idx < len(tasks) else f"Study {topic} core concepts"
            task2 = tasks[task_idx + 1] if task_idx + 1 < len(tasks) else f"Practice {topic} problems"
            writer.writerow([
                f"Week {wn}",
                day_names[day_idx],
                topic,
                objective,
                hours_per_topic,
                f"{task1}; {task2}",
                "Pending"
            ])

        # Assessment row
        assessment = week.get("assessment", {})
        writer.writerow([
            f"Week {wn}",
            "Sunday",
            "Assessment / Revision",
            assessment.get("milestone", f"Week {wn} Assessment"),
            1.0,
            assessment.get("description", "Review and assess the week's topics"),
            "Pending"
        ])

    return output.getvalue().encode("utf-8")


def export_roadmap_pdf(roadmap: dict, weeks: list) -> bytes:
    """
    Export the roadmap as a PDF file.
    Returns bytes suitable for Streamlit download_button.
    Uses fpdf2. Falls back to a simple text-based format if unavailable or on error.
    """
    if not FPDF_AVAILABLE:
        text = _roadmap_to_text(roadmap, weeks)
        return text.encode("utf-8")

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_fill_color(108, 99, 255)
        pdf.set_text_color(255, 255, 255)
        pdf.rect(0, 0, 210, 25, "F")
        pdf.set_xy(10, 7)
        pdf.cell(0, 12, "CompanyPrep AI - Interview Preparation Roadmap", new_x="LMARGIN", new_y="NEXT")

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 11)
        pdf.ln(5)

        # Metadata
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Preparation Profile", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        company_str = _safe_pdf_str(roadmap.get("company", "N/A"))
        role_str = _safe_pdf_str(roadmap.get("job_role", "N/A"))
        exp_str = _safe_pdf_str(roadmap.get("experience_level", "N/A"))

        pdf.cell(0, 6, f"Company: {company_str}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Role: {role_str}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Experience Level: {exp_str}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Duration: {roadmap.get('duration_weeks', 0)} weeks | Weekly Hours: {roadmap.get('weekly_hours', 0)}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Disclaimer
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100, 100, 100)
        disclaimer = _safe_pdf_str(roadmap.get("disclaimer", ""))
        if disclaimer:
            pdf.multi_cell(0, 5, f"Note: {disclaimer[:200]}")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

        # Weeks
        for week in weeks:
            wn = week.get("week_number", 1)
            topics = [_safe_pdf_str(t) for t in week.get("topics", [])]
            hours = week.get("estimated_hours", 0)

            # Week header
            pdf.set_fill_color(230, 228, 255)
            pdf.set_font("Helvetica", "B", 12)
            header_topics = ", ".join(topics[:3]) + ("..." if len(topics) > 3 else "")
            pdf.cell(0, 8, f"Week {wn} - {header_topics} ({hours}h)",
                     new_x="LMARGIN", new_y="NEXT", fill=True)
            pdf.ln(1)

            # Objectives
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Objectives:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            for obj in week.get("objectives", [])[:3]:
                pdf.cell(5)
                pdf.cell(0, 5, f"- {_safe_pdf_str(obj[:80])}", new_x="LMARGIN", new_y="NEXT")

            # Topics
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Topics:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(5)
            pdf.cell(0, 5, ", ".join(topics), new_x="LMARGIN", new_y="NEXT")

            # Tasks
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Key Tasks:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            for task in week.get("daily_tasks", [])[:4]:
                pdf.cell(5)
                pdf.cell(0, 5, f"- {_safe_pdf_str(task[:80])}", new_x="LMARGIN", new_y="NEXT")

            # Assessment
            assessment = week.get("assessment", {})
            if assessment:
                pdf.set_font("Helvetica", "B", 10)
                milestone_str = _safe_pdf_str(assessment.get("milestone", ""))
                pdf.cell(0, 6, f"Milestone: {milestone_str}", new_x="LMARGIN", new_y="NEXT")

            pdf.ln(4)

        pdf_bytes = bytes(pdf.output())
        return pdf_bytes
    except Exception:
        # Graceful fallback to text if PDF formatting encounters an issue
        return _roadmap_to_text(roadmap, weeks).encode("utf-8")


def _roadmap_to_text(roadmap: dict, weeks: list) -> str:
    """Convert roadmap to plain text (PDF fallback)."""
    lines = [
        "COMPANYPREP AI - INTERVIEW PREPARATION ROADMAP",
        "=" * 50,
        f"Company: {roadmap.get('company', '')}",
        f"Role: {roadmap.get('job_role', '')}",
        f"Duration: {roadmap.get('duration_weeks', 0)} weeks",
        f"Weekly Hours: {roadmap.get('weekly_hours', 0)}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
        "",
    ]
    for week in weeks:
        wn = week.get("week_number", 1)
        lines.append(f"\nWEEK {wn}")
        lines.append("-" * 30)
        lines.append(f"Topics: {', '.join(week.get('topics', []))}")
        lines.append(f"Hours: {week.get('estimated_hours', 0)}")
        for task in week.get("daily_tasks", [])[:5]:
            lines.append(f"  - {task}")
        assessment = week.get("assessment", {})
        if assessment:
            lines.append(f"Milestone: {assessment.get('milestone', '')}")
    return "\n".join(lines)
