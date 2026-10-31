"""
backend/core/revision_planner.py
Creates personalized revision plans based on weak topics, assessment results,
pending tasks, and available study hours.
"""
try:
    from backend.core.progress_tracker import get_strong_weak_topics, build_progress_dataframe
except ImportError:
    try:
        from core.progress_tracker import get_strong_weak_topics, build_progress_dataframe
    except ImportError:
        pass

try:
    from database.db_manager import get_weak_topics, get_user_assessments, get_assessment_results
except ImportError:
    try:
        from db_manager import get_weak_topics, get_user_assessments, get_assessment_results
    except ImportError:
        pass


TOPIC_REVISION_RESOURCES = {
    "Data Structures": [
        "Solve 10 LeetCode easy DS problems",
        "Re-implement linked list, stack, queue from scratch",
        "Watch a DS visualization video",
    ],
    "Algorithms": [
        "Revise sorting algorithms with code",
        "Practice 5 binary search variants",
        "Study divide & conquer examples",
    ],
    "DBMS & SQL": [
        "Write 10 SQL queries (JOINs, GROUP BY, subqueries)",
        "Revise normalization rules with examples",
        "Practice on SQLZoo",
    ],
    "OOP": [
        "Re-read SOLID principles",
        "Implement a design pattern (Factory, Singleton)",
        "Write 5 OOP interview answers",
    ],
    "Operating Systems": [
        "Revise process scheduling algorithms",
        "Revise deadlock conditions and solutions",
        "Practice OS MCQs on GeeksforGeeks",
    ],
    "Computer Networks": [
        "Draw and explain the OSI model",
        "Trace an HTTP request step by step",
        "Practice networking MCQs",
    ],
    "Aptitude": [
        "Solve 20 timed aptitude questions",
        "Focus on time-speed-distance and percentages",
        "Practice mock aptitude sections",
    ],
    "Logical Reasoning": [
        "Solve 15 syllogism problems",
        "Practice blood relations and seating arrangements",
        "Timed reasoning drills (10 min)",
    ],
}


def generate_revision_plan(
    roadmap_id: int,
    weeks: list,
    user_id: str,
    available_hours_per_day: float = 2.0,
    remaining_days: int = 14,
) -> dict:
    """
    Generate a revision plan based on weak topics and pending tasks.
    """
    # Get weak topics from assessments
    try:
        weak_from_assessment = get_weak_topics(user_id)
    except Exception:
        weak_from_assessment = []

    # Get weak topics from progress
    try:
        _, weak_from_progress = get_strong_weak_topics(roadmap_id)
    except Exception:
        weak_from_progress = []

    # Combine and deduplicate
    all_weak = list(dict.fromkeys(weak_from_assessment + weak_from_progress))

    # Build daily tasks
    total_hours = available_hours_per_day * remaining_days
    daily_plans = []

    if not all_weak:
        # No weak topics — general revision
        all_weak = ["Programming Fundamentals", "DSA", "Aptitude", "HR Interview"]

    # Distribute topics across days
    topic_idx = 0
    for day in range(1, min(remaining_days + 1, 15)):
        topic = all_weak[topic_idx % len(all_weak)]
        resources = TOPIC_REVISION_RESOURCES.get(topic, [
            f"Revise {topic} core concepts",
            f"Solve 5 {topic} practice problems",
        ])
        day_plan = {
            "day": day,
            "focus_topic": topic,
            "hours": available_hours_per_day,
            "tasks": resources[:2],
            "mock_practice": day % 3 == 0,  # mock every 3rd day
            "why_important": f"'{topic}' was identified as a weak area. Focused revision improves retention and confidence.",
        }
        if day % 3 == 0:
            day_plan["tasks"].append("30-minute mock interview practice")
        daily_plans.append(day_plan)
        topic_idx += 1

    # Milestone reassessment
    milestones = []
    for i in range(0, min(remaining_days, 14), 7):
        milestones.append({
            "day": i + 7,
            "milestone": f"Week {i // 7 + 1} Revision Checkpoint",
            "tasks": ["Attempt a mini-assessment on revised topics", "Review and note remaining gaps"],
        })

    return {
        "weak_topics": all_weak,
        "remaining_days": remaining_days,
        "total_revision_hours": round(total_hours, 1),
        "daily_plans": daily_plans,
        "milestones": milestones,
        "tips": [
            "Spend extra 30 minutes on your weakest topic daily.",
            "Use active recall — close notes and write what you remember.",
            "Do timed practice to build exam speed.",
            "Review mistakes immediately after practice.",
        ],
    }
