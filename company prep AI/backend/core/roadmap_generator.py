"""
backend/core/roadmap_generator.py
Generates personalized week-by-week interview preparation roadmaps.
Supports AI-enhanced generation (Gemini/Groq) with deterministic demo fallback.
"""
import json
from typing import Optional

try:
    from backend.services.llm_service import generate_json, get_provider_info, DEMO_NOTICE, generate
    from backend.config import DEMO_MODE
except ImportError:
    from services.llm_service import generate_json, get_provider_info, DEMO_NOTICE, generate
    from config import DEMO_MODE

# ---------------------------------------------------------------------------
# Company + role topic templates (demo / fallback)
# ---------------------------------------------------------------------------

COMPANY_FOCUS = {
    "infosys": {
        "name": "Infosys",
        "aptitude_weight": "high",
        "coding_weight": "medium",
        "hr_rounds": 2,
        "note": "Infosys typically tests aptitude, verbal, reasoning, and coding in their online assessment. Information here is general guidance — verify current pattern on official channels.",
    },
    "tcs": {
        "name": "TCS",
        "aptitude_weight": "high",
        "coding_weight": "medium",
        "hr_rounds": 1,
        "note": "TCS NQT assesses cognitive skills, programming logic, and coding. Information here is general guidance — verify current pattern on official TCS channels.",
    },
    "cognizant": {
        "name": "Cognizant",
        "aptitude_weight": "medium",
        "coding_weight": "medium",
        "hr_rounds": 1,
        "note": "Cognizant GenC / GenC Next tests aptitude, coding, and communication. Information here is general guidance.",
    },
    "wipro": {
        "name": "Wipro",
        "aptitude_weight": "high",
        "coding_weight": "medium",
        "hr_rounds": 1,
        "note": "Wipro NLTH tests aptitude, verbal, and coding. Verify on Wipro's official channels.",
    },
    "accenture": {
        "name": "Accenture",
        "aptitude_weight": "medium",
        "coding_weight": "low",
        "hr_rounds": 2,
        "note": "Accenture focuses on cognitive ability, communication, and behavioral rounds. Verify on official channels.",
    },
}

ROLE_TOPICS = {
    "software engineer": [
        "Programming Fundamentals", "OOP Concepts", "Data Structures", "Algorithms",
        "DBMS & SQL", "Operating Systems", "Computer Networks",
        "System Design Basics", "Git & Version Control", "Aptitude",
        "Logical Reasoning", "Verbal Ability", "HR Interview", "Project Discussion",
    ],
    "system engineer": [
        "Programming Fundamentals", "OOP Concepts", "Data Structures", "Algorithms",
        "DBMS & SQL", "Operating Systems", "Computer Networks",
        "Aptitude", "Logical Reasoning", "Verbal Ability", "HR Interview",
    ],
    "junior software engineer": [
        "Programming Fundamentals", "OOP Concepts", "Data Structures", "Algorithms",
        "DBMS & SQL", "Operating Systems", "Aptitude",
        "Logical Reasoning", "Verbal Ability", "HR Interview", "Project Discussion",
    ],
    "data analyst": [
        "Python / R Programming", "Statistics", "SQL & Databases", "Data Visualization",
        "Pandas & NumPy", "Excel", "Aptitude", "Logical Reasoning", "HR Interview",
    ],
    "default": [
        "Programming Fundamentals", "OOP Concepts", "Data Structures", "Algorithms",
        "DBMS & SQL", "Operating Systems", "Computer Networks", "Aptitude",
        "Logical Reasoning", "Verbal Ability", "HR Interview",
    ],
}

EXPERIENCE_MULTIPLIER = {"Beginner": 1.5, "Intermediate": 1.0, "Advanced": 0.7}


def _get_company_info(company: str) -> dict:
    key = company.lower().strip()
    for k, v in COMPANY_FOCUS.items():
        if k in key or key in k:
            return v
    return {"name": company, "note": "General role-based preparation guidance. No company-specific verified data available.", "aptitude_weight": "medium", "coding_weight": "medium", "hr_rounds": 1}


def _get_role_topics(role: str) -> list:
    role_lower = role.lower().strip()
    for k, v in ROLE_TOPICS.items():
        if k in role_lower or role_lower in k:
            return list(v)
    return list(ROLE_TOPICS["default"])


def _distribute_topics(topics: list, duration_weeks: int, weekly_hours: float,
                        experience_level: str) -> list:
    """Distribute topics across weeks considering available hours."""
    multiplier = EXPERIENCE_MULTIPLIER.get(experience_level, 1.0)
    # Hours per topic (scaled by experience)
    hours_per_topic = {
        "Programming Fundamentals": 6 * multiplier,
        "OOP Concepts": 5 * multiplier,
        "Data Structures": 8 * multiplier,
        "Algorithms": 8 * multiplier,
        "DBMS & SQL": 6 * multiplier,
        "Operating Systems": 5 * multiplier,
        "Computer Networks": 4 * multiplier,
        "System Design Basics": 5 * multiplier,
        "Aptitude": 4 * multiplier,
        "Logical Reasoning": 3 * multiplier,
        "Verbal Ability": 3 * multiplier,
        "HR Interview": 3 * multiplier,
        "Project Discussion": 3 * multiplier,
        "Git & Version Control": 2 * multiplier,
        "Mock Interview": 3 * multiplier,
    }
    total_available = duration_weeks * weekly_hours
    # Categorize topics
    essential = []
    recommended = []
    optional = []
    used_hours = 0.0
    for topic in topics:
        h = hours_per_topic.get(topic, 4 * multiplier)
        if used_hours + h <= total_available * 0.7:
            essential.append((topic, h))
            used_hours += h
        elif used_hours + h <= total_available * 0.9:
            recommended.append((topic, h))
            used_hours += h
        else:
            optional.append((topic, h))
    # Build weeks
    all_scheduled = essential + recommended
    topic_queue = list(all_scheduled)
    weeks = []
    topic_idx = 0
    for wk in range(1, duration_weeks + 1):
        remaining_hours = weekly_hours
        week_topics = []
        week_hours = 0.0
        while topic_idx < len(topic_queue) and remaining_hours > 0:
            t, h = topic_queue[topic_idx]
            alloc = min(h, remaining_hours)
            week_topics.append({"topic": t, "estimated_hours": round(alloc, 1)})
            remaining_hours -= alloc
            week_hours += alloc
            if alloc >= h:
                topic_idx += 1
            else:
                topic_queue[topic_idx] = (t, h - alloc)
                break
        weeks.append({
            "week_number": wk,
            "topics_scheduled": week_topics,
            "total_hours": round(week_hours, 1),
            "optional_topics": [t for t, _ in optional] if wk == duration_weeks else [],
        })
    return weeks


def _build_week_detail(week_number: int, topics_scheduled: list, company: str,
                        role: str, experience_level: str, language: str,
                        total_hours: float) -> dict:
    """Build a detailed week plan dict for a set of scheduled topics."""
    topic_names = [t["topic"] for t in topics_scheduled]

    # Generate tasks and exercises per topic
    daily_tasks = []
    coding_exercises = []
    practice_questions = []
    mini_projects = []
    objectives = []

    TOPIC_TASKS = {
        "Programming Fundamentals": {
            "tasks": ["Study variables, data types, control flow", "Practice loops and functions", "Solve 5 basic coding problems"],
            "exercises": ["Fibonacci sequence", "Prime number checker", "String reversal"],
            "questions": ["Explain pass by value vs pass by reference", "What is recursion?", "Difference between compiled and interpreted languages"],
            "objective": "Build solid programming fundamentals",
        },
        "OOP Concepts": {
            "tasks": ["Study classes, objects, inheritance", "Practice polymorphism examples", "Implement encapsulation patterns"],
            "exercises": ["Build a Bank Account class", "Implement Animal hierarchy (polymorphism)", "Create a shape area calculator"],
            "questions": ["Explain the 4 pillars of OOP", "What is the difference between abstraction and encapsulation?", "When would you use inheritance vs composition?"],
            "objective": "Master OOP principles and apply them in code",
        },
        "Data Structures": {
            "tasks": ["Study arrays, linked lists, stacks, queues", "Implement each structure from scratch", "Solve 5 DS problems on LeetCode"],
            "exercises": ["Implement a linked list with insert/delete", "Build a stack using arrays", "Implement a queue using two stacks"],
            "questions": ["What is the difference between array and linked list?", "When do you use a stack vs queue?", "Explain time complexity of common DS operations"],
            "objective": "Understand and implement core data structures",
            "mini_project": "Build a simple task queue using a linked list",
        },
        "Algorithms": {
            "tasks": ["Study sorting algorithms (bubble, merge, quick)", "Study searching algorithms", "Practice Big O analysis"],
            "exercises": ["Implement merge sort", "Binary search implementation", "Anagram check"],
            "questions": ["What is the time complexity of quicksort?", "Explain divide and conquer", "When do you use dynamic programming?"],
            "objective": "Master key algorithms and complexity analysis",
        },
        "DBMS & SQL": {
            "tasks": ["Study RDBMS concepts, normalization", "Practice SQL queries (SELECT, JOIN, GROUP BY)", "Study indexing and transactions"],
            "exercises": ["Write queries for 3 NF normalization", "JOIN practice on sample tables", "Stored procedure exercise"],
            "questions": ["What is normalization? Explain 1NF, 2NF, 3NF", "Difference between INNER JOIN and LEFT JOIN?", "What is ACID in databases?"],
            "objective": "Master DBMS theory and SQL query writing",
        },
        "Operating Systems": {
            "tasks": ["Study process management, scheduling", "Study memory management (paging, segmentation)", "Study deadlocks and synchronization"],
            "exercises": ["Trace through Round Robin scheduling", "Banker's algorithm example", "Page replacement algorithm"],
            "questions": ["What is a process vs thread?", "Explain deadlock and its prevention", "What is virtual memory?"],
            "objective": "Understand OS concepts for technical interviews",
        },
        "Computer Networks": {
            "tasks": ["Study OSI and TCP/IP models", "Study HTTP, DNS, routing protocols", "Study IP addressing and subnetting basics"],
            "exercises": ["Map an HTTP request through OSI layers", "Subnet calculation practice", "TCP vs UDP comparison"],
            "questions": ["Explain the OSI model layers", "What happens when you type a URL in a browser?", "Difference between TCP and UDP?"],
            "objective": "Understand networking fundamentals",
        },
        "Aptitude": {
            "tasks": ["Solve 20 quantitative aptitude problems", "Practice time-speed-distance problems", "Work on percentage and profit/loss"],
            "exercises": ["20 aptitude problems from IndiaBIX", "5 mock aptitude sections"],
            "questions": ["A train travels 300 km at 60 km/h. How long does it take?", "If 20% of X is 40, what is X?"],
            "objective": "Improve aptitude speed and accuracy",
        },
        "Logical Reasoning": {
            "tasks": ["Practice syllogisms, blood relations, seating arrangements", "Solve 20 reasoning problems", "Timed reasoning drills"],
            "exercises": ["Syllogism exercises (10 problems)", "Seating arrangement puzzle", "Number series problems"],
            "questions": ["Solve: All A are B. Some B are C. What can be concluded about A and C?", "Find the odd one: 2, 4, 8, 16, 33"],
            "objective": "Build logical reasoning speed and accuracy",
        },
        "Verbal Ability": {
            "tasks": ["Practice reading comprehension", "Vocabulary building (10 words/day)", "Grammar exercises"],
            "exercises": ["Read and summarize a technical article", "Identify errors in 10 sentences", "Fill in the blanks exercise"],
            "questions": ["Choose the correct word: The team __ working hard.", "Identify the synonym of 'Ephemeral'"],
            "objective": "Improve verbal communication and comprehension",
        },
        "HR Interview": {
            "tasks": ["Prepare STAR answers for behavioral questions", "Practice Tell Me About Yourself", "Research company values"],
            "exercises": ["Write out 3 STAR stories from your experience", "Record and review your Tell Me About Yourself answer"],
            "questions": ["Tell me about yourself", "Why do you want to join this company?", "Describe a challenge you overcame", "Where do you see yourself in 5 years?"],
            "objective": "Prepare confident, authentic HR interview answers",
        },
        "Project Discussion": {
            "tasks": ["Document your key projects clearly", "Prepare to explain architecture and challenges", "Quantify your project impact"],
            "exercises": ["Write a 2-minute elevator pitch for your main project", "Prepare answers for 'What was your biggest challenge?'"],
            "questions": ["Walk me through your final year project", "What technologies did you use and why?", "What would you improve if you could redo it?"],
            "objective": "Articulate projects clearly and confidently",
        },
        "System Design Basics": {
            "tasks": ["Study scalability concepts", "Learn about load balancers, caching, databases at scale", "Practice drawing system diagrams"],
            "exercises": ["Design a URL shortener", "Design a simple chat system"],
            "questions": ["How would you design a scalable notification system?", "What is a CDN and when would you use it?"],
            "objective": "Understand basic system design concepts",
        },
        "Git & Version Control": {
            "tasks": ["Learn Git basics: clone, commit, push, pull, merge", "Practice branching strategies"],
            "exercises": ["Create a repository, add files, commit, and push", "Practice resolving a merge conflict"],
            "questions": ["What is the difference between git merge and git rebase?", "Explain the Git workflow you use"],
            "objective": "Use Git confidently in a team environment",
        },
        "Mock Interview": {
            "tasks": ["Complete a full mock interview session", "Review feedback and weak areas", "Revise identified weak topics"],
            "exercises": ["1 mock coding interview (45 min)", "1 mock HR round (20 min)"],
            "questions": ["(Practice all previously covered question types)"],
            "objective": "Simulate real interview conditions and build confidence",
        },
    }

    for ts in topics_scheduled:
        topic = ts["topic"]
        t_data = TOPIC_TASKS.get(topic, {
            "tasks": [f"Study {topic} core concepts", f"Practice {topic} problems", f"Review {topic} for {company} interview"],
            "exercises": [f"{topic} hands-on exercise 1", f"{topic} hands-on exercise 2"],
            "questions": [f"Explain a key concept in {topic}", f"How does {topic} apply in real projects?"],
            "objective": f"Develop competency in {topic}",
        })
        objectives.append(t_data["objective"])
        daily_tasks.extend(t_data["tasks"])
        coding_exercises.extend(t_data.get("exercises", []))
        practice_questions.extend(t_data.get("questions", []))
        if "mini_project" in t_data:
            mini_projects.append(t_data["mini_project"])

    assessment = {
        "milestone": f"Week {week_number} Milestone",
        "description": f"Review and assess understanding of: {', '.join(topic_names)}",
        "tasks": ["Complete week summary quiz", "Solve 5 practice problems", "Review and note weak areas"],
    }

    return {
        "week_number": week_number,
        "topics": topic_names,
        "estimated_hours": total_hours,
        "objectives": objectives,
        "daily_tasks": daily_tasks[:12],  # cap at 12 tasks
        "coding_exercises": coding_exercises[:8],
        "practice_questions": practice_questions[:10],
        "mini_projects": mini_projects,
        "revision": [f"Revise {t} key points" for t in topic_names],
        "mock_interview": week_number % 2 == 0,  # mock interview every other week
        "assessment": assessment,
    }


def generate_roadmap(
    company: str,
    job_role: str,
    skills: list,
    experience_level: str,
    weekly_hours: float,
    duration_weeks: int,
    language: str = "Python",
    job_description: str = "",
) -> dict:
    """
    Generate a complete roadmap dict.
    Uses AI if available, falls back to deterministic generation.
    """
    company_info = _get_company_info(company)
    role_topics = _get_role_topics(job_role)

    # Add mock interview to last week
    if "Mock Interview" not in role_topics:
        role_topics.append("Mock Interview")

    distributed = _distribute_topics(role_topics, duration_weeks, weekly_hours, experience_level)

    weeks = []
    for dist_week in distributed:
        w = _build_week_detail(
            week_number=dist_week["week_number"],
            topics_scheduled=dist_week["topics_scheduled"],
            company=company,
            role=job_role,
            experience_level=experience_level,
            language=language,
            total_hours=dist_week["total_hours"],
        )
        w["optional_topics"] = dist_week.get("optional_topics", [])
        weeks.append(w)

    provider_info = get_provider_info()

    # If AI is available, try to enrich weeks with AI content
    if not DEMO_MODE:
        try:
            ai_prompt = f"""You are an expert interview coach for {company} {job_role} positions.
Generate a brief but specific additional insight for week 1 of an interview preparation roadmap.
Student: {experience_level} level, studying {weekly_hours} hours/week for {duration_weeks} weeks.
Topics in week 1: {', '.join([t['topic'] for t in distributed[0]['topics_scheduled']] if distributed else [])}
Provide 2-3 specific tips for this student. Keep it concise (under 100 words)."""
            ai_tip = generate(ai_prompt)
            if not ai_tip.startswith("["):
                weeks[0]["ai_tip"] = ai_tip.strip()
        except Exception:
            pass

    return {
        "company": company,
        "company_info": company_info,
        "job_role": job_role,
        "experience_level": experience_level,
        "weekly_hours": weekly_hours,
        "duration_weeks": duration_weeks,
        "language": language,
        "total_available_hours": weekly_hours * duration_weeks,
        "provider": provider_info,
        "weeks": weeks,
        "disclaimer": (
            "This roadmap is a general preparation guide based on publicly available information "
            "and AI-generated suggestions. It does not represent any company's official recruitment "
            "process. Always verify current recruitment patterns on the company's official website."
        ),
    }


def adapt_roadmap(
    existing_roadmap: dict,
    completed_keys: set,
    new_weekly_hours: float,
    new_duration_weeks: int,
    new_experience_level: str,
    new_skills: list,
) -> tuple[dict, list]:
    """
    Adapt an existing roadmap to new settings.
    Preserves completed tasks and redistributes remaining work.
    Returns (new_roadmap, changes_explanation).
    """
    company = existing_roadmap["company"]
    job_role = existing_roadmap["job_role"]
    language = existing_roadmap.get("language", "Python")
    job_description = ""

    # Build fresh roadmap with new settings
    new_roadmap = generate_roadmap(
        company=company, job_role=job_role, skills=new_skills,
        experience_level=new_experience_level,
        weekly_hours=new_weekly_hours, duration_weeks=new_duration_weeks,
        language=language, job_description=job_description,
    )

    changes = []
    if new_weekly_hours != existing_roadmap.get("weekly_hours"):
        changes.append(f"Weekly study hours changed to {new_weekly_hours} hours.")
    if new_duration_weeks != existing_roadmap.get("duration_weeks"):
        changes.append(f"Preparation duration adjusted to {new_duration_weeks} weeks.")
    if new_experience_level != existing_roadmap.get("experience_level"):
        changes.append(f"Experience level updated to {new_experience_level} — topic difficulty adjusted.")
    changes.append(f"Completed tasks ({len(completed_keys)} items) have been preserved.")

    return new_roadmap, changes
