"""
backend/core/resource_manager.py
Manages curated free learning resources for interview preparation topics.
All links are well-known, publicly accessible free resources.
"""
from typing import Optional

# Curated resource database — only reputable free platforms
RESOURCES = [
    # DSA
    {"topic": "Data Structures", "category": "DSA", "title": "GeeksforGeeks — Data Structures",
     "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/data-structures/", "free": True},
    {"topic": "Algorithms", "category": "DSA", "title": "GeeksforGeeks — Algorithms",
     "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/", "free": True},
    {"topic": "DSA", "category": "DSA", "title": "LeetCode — Practice Problems",
     "provider": "LeetCode", "url": "https://leetcode.com/problemset/all/", "free": True},
    {"topic": "DSA", "category": "DSA", "title": "Neetcode — DSA Roadmap & Solutions",
     "provider": "Neetcode", "url": "https://neetcode.io/roadmap", "free": True},
    {"topic": "DSA", "category": "DSA", "title": "CS50 — Introduction to Computer Science (Harvard)",
     "provider": "edX / Harvard", "url": "https://cs50.harvard.edu/x/", "free": True},
    # Programming
    {"topic": "Python", "category": "Programming", "title": "Official Python Tutorial",
     "provider": "Python.org", "url": "https://docs.python.org/3/tutorial/", "free": True},
    {"topic": "Java", "category": "Programming", "title": "Java SE Documentation",
     "provider": "Oracle", "url": "https://docs.oracle.com/en/java/", "free": True},
    {"topic": "C++", "category": "Programming", "title": "cppreference.com",
     "provider": "cppreference", "url": "https://en.cppreference.com/w/", "free": True},
    {"topic": "Programming Fundamentals", "category": "Programming",
     "title": "W3Schools — Programming Tutorials",
     "provider": "W3Schools", "url": "https://www.w3schools.com/", "free": True},
    # OOP
    {"topic": "OOP", "category": "Programming", "title": "GeeksforGeeks — OOP Concepts",
     "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/", "free": True},
    # DBMS / SQL
    {"topic": "SQL", "category": "DBMS", "title": "SQLZoo — Interactive SQL Tutorial",
     "provider": "SQLZoo", "url": "https://sqlzoo.net/", "free": True},
    {"topic": "DBMS", "category": "DBMS", "title": "GeeksforGeeks — DBMS",
     "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/dbms/", "free": True},
    {"topic": "SQL", "category": "DBMS", "title": "W3Schools — SQL Tutorial",
     "provider": "W3Schools", "url": "https://www.w3schools.com/sql/", "free": True},
    {"topic": "SQL", "category": "DBMS", "title": "LeetCode — Database Problems",
     "provider": "LeetCode", "url": "https://leetcode.com/problemset/database/", "free": True},
    # OS
    {"topic": "Operating Systems", "category": "CS Fundamentals",
     "title": "GeeksforGeeks — Operating Systems",
     "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/operating-systems/", "free": True},
    # CN
    {"topic": "Computer Networks", "category": "CS Fundamentals",
     "title": "GeeksforGeeks — Computer Networks",
     "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/computer-network-tutorials/", "free": True},
    # Aptitude
    {"topic": "Aptitude", "category": "Aptitude", "title": "IndiaBIX — Aptitude Questions",
     "provider": "IndiaBIX", "url": "https://www.indiabix.com/aptitude/questions-and-answers/", "free": True},
    {"topic": "Aptitude", "category": "Aptitude", "title": "GeeksforGeeks — Aptitude",
     "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/aptitude-gq/", "free": True},
    # Logical Reasoning
    {"topic": "Logical Reasoning", "category": "Aptitude",
     "title": "IndiaBIX — Logical Reasoning",
     "provider": "IndiaBIX", "url": "https://www.indiabix.com/logical-reasoning/questions-and-answers/", "free": True},
    # Verbal
    {"topic": "Verbal Ability", "category": "Communication",
     "title": "IndiaBIX — Verbal Ability",
     "provider": "IndiaBIX", "url": "https://www.indiabix.com/verbal-ability/questions-and-answers/", "free": True},
    # System Design
    {"topic": "System Design", "category": "Technical",
     "title": "System Design Primer (GitHub)",
     "provider": "GitHub", "url": "https://github.com/donnemartin/system-design-primer", "free": True},
    # Git
    {"topic": "Git", "category": "Tools", "title": "Pro Git Book (Free)",
     "provider": "git-scm.com", "url": "https://git-scm.com/book/en/v2", "free": True},
    # HR / Behavioral
    {"topic": "HR Interview", "category": "HR",
     "title": "GeeksforGeeks — HR Interview Questions",
     "provider": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/hr-interview-questions/", "free": True},
    # Mock Interviews
    {"topic": "Mock Interview", "category": "Practice",
     "title": "Pramp — Free Mock Interviews",
     "provider": "Pramp", "url": "https://www.pramp.com/", "free": True},
    {"topic": "Mock Interview", "category": "Practice",
     "title": "InterviewBit — Practice Platform",
     "provider": "InterviewBit", "url": "https://www.interviewbit.com/", "free": True},
    # Company Specific
    {"topic": "TCS Interview", "category": "Company",
     "title": "TCS iON Career Edge (Free Online Course)",
     "provider": "TCS", "url": "https://learning.tcsionhub.in/", "free": True},
    {"topic": "Infosys Interview", "category": "Company",
     "title": "Infosys — Springboard (Free Courses)",
     "provider": "Infosys", "url": "https://www.infosysbpm.com/springboard/pages/index.aspx", "free": True},
]


def get_resources_for_topic(topic: str, category: Optional[str] = None) -> list[dict]:
    """Return resources matching topic (case-insensitive substring) and optional category."""
    topic_lower = topic.lower()
    results = []
    for r in RESOURCES:
        if topic_lower in r["topic"].lower() or topic_lower in r["title"].lower():
            if category is None or r["category"].lower() == category.lower():
                results.append(r)
    return results


def get_resources_for_roadmap(weeks: list[dict]) -> list[dict]:
    """Aggregate resources for all topics appearing in a roadmap."""
    seen_urls = set()
    results = []
    for week in weeks:
        topics = week.get("topics", [])
        for topic in topics:
            for r in get_resources_for_topic(topic):
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    results.append(r)
    return results


def get_all_resources() -> list[dict]:
    """Return all curated resources."""
    return list(RESOURCES)


def get_categories() -> list[str]:
    """Return all unique categories."""
    return sorted(set(r["category"] for r in RESOURCES))
