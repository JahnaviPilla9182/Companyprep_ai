"""
backend/core/progress_tracker.py
Handles all progress tracking logic: reading/writing completion status,
computing analytics, identifying weak topics.
"""
import pandas as pd
from typing import Optional

try:
    from database.db_manager import (
        upsert_progress_item, get_progress, get_progress_summary,
        get_completed_keys, get_weak_topics,
    )
except ImportError:
    from db_manager import (
        upsert_progress_item, get_progress, get_progress_summary,
        get_completed_keys, get_weak_topics,
    )


def mark_item(roadmap_id: int, week_number: int, item_type: str,
              item_key: str, item_label: str, is_completed: bool) -> None:
    """Mark a single roadmap item as completed or not."""
    upsert_progress_item(
        roadmap_id=roadmap_id,
        week_number=week_number,
        item_type=item_type,
        item_key=item_key,
        item_label=item_label,
        is_completed=is_completed,
    )


def get_summary(roadmap_id: int) -> dict:
    """Return progress summary statistics."""
    return get_progress_summary(roadmap_id)


def get_completed(roadmap_id: int) -> set:
    """Return set of completed item keys."""
    return get_completed_keys(roadmap_id)


def build_progress_dataframe(roadmap_id: int) -> pd.DataFrame:
    """Build a DataFrame of all progress items for analytics."""
    rows = get_progress(roadmap_id)
    if not rows:
        return pd.DataFrame(columns=["week_number", "item_type", "item_label", "is_completed", "completed_at"])
    df = pd.DataFrame(rows)
    df["is_completed"] = df["is_completed"].astype(bool)
    return df


def get_week_completion(roadmap_id: int) -> dict:
    """Return {week_number: pct_complete} for all weeks."""
    df = build_progress_dataframe(roadmap_id)
    if df.empty:
        return {}
    grouped = df.groupby("week_number").agg(
        total=("is_completed", "count"),
        done=("is_completed", "sum"),
    ).reset_index()
    grouped["pct"] = (grouped["done"] / grouped["total"] * 100).round(1)
    return {int(r["week_number"]): r["pct"] for _, r in grouped.iterrows()}


def get_strong_weak_topics(roadmap_id: int) -> tuple[list, list]:
    """
    Identify strong and weak topics based on item type='topic' completion.
    Returns (strong_topics, weak_topics).
    """
    df = build_progress_dataframe(roadmap_id)
    if df.empty:
        return [], []
    topic_df = df[df["item_type"] == "topic"]
    if topic_df.empty:
        return [], []
    strong = topic_df[topic_df["is_completed"] == True]["item_label"].tolist()
    weak = topic_df[topic_df["is_completed"] == False]["item_label"].tolist()
    return strong, weak


def get_recommended_next_steps(roadmap_id: int, weeks: list) -> list:
    """Return a list of recommended next steps based on incomplete items."""
    completed_keys = get_completed_keys(roadmap_id)
    steps = []
    for week in weeks:
        wn = week["week_number"]
        for topic in week.get("topics", []):
            key = f"topic_{wn}_{topic}"
            if key not in completed_keys:
                steps.append(f"Week {wn}: Complete '{topic}'")
                if len(steps) >= 5:
                    return steps
    return steps
