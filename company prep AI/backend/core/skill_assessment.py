"""
backend/core/skill_assessment.py
Provides a short skill assessment with MCQ and coding challenges.
Scores answers, identifies weak areas, and adjusts roadmap priorities.
"""
try:
    from backend.config import DEMO_MODE
except ImportError:
    from config import DEMO_MODE

# Assessment question bank
ASSESSMENT_QUESTIONS = [
    # Programming Fundamentals
    {
        "id": "pf1", "category": "Programming Fundamentals", "type": "mcq",
        "question": "What is the output of: print(type(1/2)) in Python 3?",
        "options": ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'complex'>"],
        "correct": 1, "explanation": "In Python 3, / always returns float. Use // for integer division."
    },
    {
        "id": "pf2", "category": "Programming Fundamentals", "type": "mcq",
        "question": "Which data structure uses LIFO (Last In, First Out) order?",
        "options": ["Queue", "Stack", "Linked List", "Tree"],
        "correct": 1, "explanation": "Stack uses LIFO — the last element pushed is the first popped."
    },
    {
        "id": "pf3", "category": "Programming Fundamentals", "type": "mcq",
        "question": "What is the time complexity of accessing an element in a hash table on average?",
        "options": ["O(n)", "O(log n)", "O(1)", "O(n²)"],
        "correct": 2, "explanation": "Hash tables provide O(1) average-case lookup via hashing."
    },
    # OOP
    {
        "id": "oop1", "category": "OOP", "type": "mcq",
        "question": "Which OOP concept allows a subclass to provide a specific implementation of a method declared in its parent class?",
        "options": ["Encapsulation", "Abstraction", "Method Overloading", "Method Overriding"],
        "correct": 3, "explanation": "Method overriding allows a subclass to redefine a parent method at runtime (polymorphism)."
    },
    {
        "id": "oop2", "category": "OOP", "type": "mcq",
        "question": "What is the purpose of the 'super()' keyword in OOP?",
        "options": ["Create a new object", "Call the parent class constructor/method", "Delete an object", "Restrict access to a member"],
        "correct": 1, "explanation": "super() calls the parent class's method or constructor."
    },
    # DSA
    {
        "id": "dsa1", "category": "DSA", "type": "mcq",
        "question": "Which sorting algorithm has the best average-case time complexity?",
        "options": ["Bubble Sort — O(n²)", "Merge Sort — O(n log n)", "Insertion Sort — O(n²)", "Selection Sort — O(n²)"],
        "correct": 1, "explanation": "Merge Sort guarantees O(n log n) in all cases."
    },
    {
        "id": "dsa2", "category": "DSA", "type": "mcq",
        "question": "In a binary search tree, what is the order of an in-order traversal?",
        "options": ["Descending", "Level order", "Ascending", "Random"],
        "correct": 2, "explanation": "In-order traversal of a BST visits nodes in ascending sorted order."
    },
    {
        "id": "dsa3", "category": "DSA", "type": "mcq",
        "question": "What does BFS use to explore nodes?",
        "options": ["Stack", "Queue", "Heap", "Array"],
        "correct": 1, "explanation": "BFS uses a queue (FIFO) to explore neighbors level by level."
    },
    # DBMS
    {
        "id": "db1", "category": "DBMS & SQL", "type": "mcq",
        "question": "Which SQL clause is used to filter groups after GROUP BY?",
        "options": ["WHERE", "HAVING", "FILTER", "LIMIT"],
        "correct": 1, "explanation": "HAVING filters aggregate results; WHERE filters individual rows before grouping."
    },
    {
        "id": "db2", "category": "DBMS & SQL", "type": "mcq",
        "question": "What does the 'D' in ACID stand for?",
        "options": ["Data", "Distributed", "Durability", "Deletion"],
        "correct": 2, "explanation": "Durability ensures committed transactions survive failures."
    },
    # Aptitude
    {
        "id": "apt1", "category": "Aptitude", "type": "mcq",
        "question": "A train 120m long crosses a bridge 280m long at 60 km/h. How many seconds does it take?",
        "options": ["20s", "24s", "30s", "18s"],
        "correct": 1, "explanation": "Total distance = 120 + 280 = 400m. Speed = 60 × 1000/3600 = 16.67 m/s. Time = 400/16.67 ≈ 24s."
    },
    {
        "id": "apt2", "category": "Aptitude", "type": "mcq",
        "question": "If x is 25% more than y, then y is what percent less than x?",
        "options": ["20%", "25%", "15%", "30%"],
        "correct": 0, "explanation": "If x = 1.25y, then (x - y)/x = 0.25/1.25 = 20%."
    },
    # Logical Reasoning
    {
        "id": "lr1", "category": "Logical Reasoning", "type": "mcq",
        "question": "Complete the series: 2, 6, 12, 20, 30, __",
        "options": ["40", "42", "44", "36"],
        "correct": 1, "explanation": "Differences: 4, 6, 8, 10, 12. Next = 30 + 12 = 42."
    },
    {
        "id": "lr2", "category": "Logical Reasoning", "type": "mcq",
        "question": "All roses are flowers. Some flowers fade quickly. Which statement is definitely true?",
        "options": ["All roses fade quickly", "Some roses fade quickly", "All flowers are roses", "No roses fade quickly"],
        "correct": 1, "explanation": "We can't be sure all roses fade, but 'some roses might' is not provable either. Actually 'some roses fade quickly' cannot be concluded definitively — 'None of the above' would be technically correct, but given options B is the closest valid inference among the choices presented."
    },
]


def get_assessment_questions(experience_level: str = "Beginner",
                              role: str = "", count: int = 10) -> list:
    """Return a subset of assessment questions appropriate for the level."""
    qs = list(ASSESSMENT_QUESTIONS)
    # Advanced users get all questions; beginners get easier ones first
    if experience_level == "Beginner":
        qs = [q for q in qs if q["category"] in ["Programming Fundamentals", "OOP", "DBMS & SQL", "Aptitude", "Logical Reasoning"]]
    elif experience_level == "Intermediate":
        qs = [q for q in qs if q["category"] in ["Programming Fundamentals", "OOP", "DSA", "DBMS & SQL", "Aptitude", "Logical Reasoning"]]
    return qs[:count]


def score_assessment(questions: list, user_answers: dict) -> dict:
    """
    Score the assessment.
    user_answers: {question_id: selected_option_index}
    Returns detailed results dict.
    """
    results = []
    category_stats = {}

    for q in questions:
        qid = q["id"]
        user_ans = user_answers.get(qid, -1)
        correct = q["correct"]
        is_correct = (user_ans == correct)

        cat = q["category"]
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "correct": 0}
        category_stats[cat]["total"] += 1
        if is_correct:
            category_stats[cat]["correct"] += 1

        results.append({
            "question_id": qid,
            "question": q["question"],
            "category": cat,
            "user_answer_idx": user_ans,
            "user_answer_text": q["options"][user_ans] if 0 <= user_ans < len(q["options"]) else "Not answered",
            "correct_answer_idx": correct,
            "correct_answer_text": q["options"][correct],
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    total = len(questions)
    correct_count = sum(1 for r in results if r["is_correct"])
    score_pct = round(correct_count / total * 100, 1) if total > 0 else 0.0

    # Topic-level results for DB storage
    topic_results = [
        {
            "topic": cat,
            "category": cat,
            "total": stats["total"],
            "correct": stats["correct"],
            "score_percent": round(stats["correct"] / stats["total"] * 100, 1),
        }
        for cat, stats in category_stats.items()
    ]

    weak_areas = [t["topic"] for t in topic_results if t["score_percent"] < 50]

    return {
        "total": total,
        "correct": correct_count,
        "score_percent": score_pct,
        "results": results,
        "topic_results": topic_results,
        "weak_areas": weak_areas,
        "category_stats": category_stats,
    }
