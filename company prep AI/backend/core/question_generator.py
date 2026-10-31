"""
backend/core/question_generator.py
Generates interview questions across multiple categories.
Uses AI when available, falls back to curated question bank.
"""
try:
    from backend.services.llm_service import generate_json, generate, DEMO_NOTICE, get_provider_info
    from backend.config import DEMO_MODE
except ImportError:
    from services.llm_service import generate_json, generate, DEMO_NOTICE, get_provider_info
    from config import DEMO_MODE

# ---------------------------------------------------------------------------
# Question bank (fallback / demo)
# ---------------------------------------------------------------------------

TECHNICAL_QUESTIONS = {
    "Programming Fundamentals": [
        {"q": "What is the difference between stack and heap memory?", "a": "Stack stores local variables and function call info (LIFO); heap stores dynamically allocated memory."},
        {"q": "Explain pass by value vs pass by reference.", "a": "Pass by value copies the variable; changes don't affect original. Pass by reference passes the address; changes affect the original."},
        {"q": "What is a null pointer? What happens if you dereference it?", "a": "A pointer pointing to nothing. Dereferencing causes undefined behavior / segmentation fault."},
        {"q": "What is recursion? Give a simple example.", "a": "A function that calls itself with a base case to stop. Example: factorial(n) = n * factorial(n-1)."},
        {"q": "What is the difference between compilation and interpretation?", "a": "Compilation translates all code at once to machine code; interpretation translates line by line at runtime."},
    ],
    "OOP": [
        {"q": "Explain the four pillars of OOP.", "a": "Encapsulation (data hiding), Inheritance (code reuse), Polymorphism (many forms), Abstraction (hiding complexity)."},
        {"q": "What is method overloading vs method overriding?", "a": "Overloading: same name, different parameters (compile-time). Overriding: subclass redefines parent method (runtime)."},
        {"q": "What is an abstract class vs an interface?", "a": "Abstract class can have implementations; interface only has method signatures. A class can implement multiple interfaces."},
        {"q": "What is a constructor? Can a constructor be private?", "a": "Special method to initialize objects. Yes, a private constructor is used in Singleton pattern."},
        {"q": "Explain the SOLID principles.", "a": "Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion."},
    ],
    "Data Structures": [
        {"q": "What is the time complexity of binary search?", "a": "O(log n) — halves the search space each iteration."},
        {"q": "Explain the difference between a linked list and an array.", "a": "Array: fixed size, O(1) access; Linked list: dynamic size, O(n) access, O(1) insert/delete at head."},
        {"q": "What is a stack? Give a real-world use case.", "a": "LIFO structure. Used in function call stacks, undo operations, browser back button."},
        {"q": "What is a hash table and how does it handle collisions?", "a": "Maps keys to values via hash function. Collisions handled by chaining (linked list at bucket) or open addressing."},
        {"q": "What is the difference between BFS and DFS?", "a": "BFS explores level by level (uses queue); DFS explores depth-first (uses stack/recursion). BFS finds shortest path in unweighted graphs."},
    ],
    "Algorithms": [
        {"q": "What is the time complexity of merge sort?", "a": "O(n log n) in all cases. Space complexity O(n)."},
        {"q": "Explain dynamic programming with an example.", "a": "Breaking problem into overlapping subproblems and storing results. Example: Fibonacci with memoization."},
        {"q": "What is greedy algorithm? When does it fail?", "a": "Makes locally optimal choice at each step. Fails when local optimum doesn't lead to global optimum (e.g., coin problem with non-standard denominations)."},
        {"q": "Explain two-pointer technique.", "a": "Using two indices to traverse array/string efficiently. Used in pair sum problems, palindrome check. Reduces O(n²) to O(n)."},
        {"q": "What is the difference between O(n) and O(n log n)?", "a": "O(n) is linear — work proportional to input. O(n log n) grows slightly faster, typical of efficient sorting algorithms."},
    ],
    "DBMS & SQL": [
        {"q": "What is normalization? Explain 1NF, 2NF, 3NF.", "a": "1NF: atomic values, no repeating groups. 2NF: 1NF + no partial dependency. 3NF: 2NF + no transitive dependency."},
        {"q": "Difference between INNER JOIN and LEFT JOIN?", "a": "INNER JOIN: only matching rows. LEFT JOIN: all rows from left table, NULLs for unmatched right rows."},
        {"q": "What is ACID in databases?", "a": "Atomicity, Consistency, Isolation, Durability — properties ensuring reliable transactions."},
        {"q": "What is an index? How does it improve query performance?", "a": "Data structure (usually B-tree) on a column. Speeds up SELECT but slows INSERT/UPDATE. Avoids full table scans."},
        {"q": "What is a stored procedure?", "a": "Precompiled SQL code stored in the database. Executed by name. Reduces network traffic and allows code reuse."},
    ],
    "Operating Systems": [
        {"q": "What is the difference between a process and a thread?", "a": "Process: independent program in memory with its own resources. Thread: lightweight unit within a process sharing memory."},
        {"q": "What is a deadlock? What are the four necessary conditions?", "a": "State where processes wait indefinitely. Conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait."},
        {"q": "Explain virtual memory.", "a": "Technique that uses disk space as extended RAM, allowing programs larger than physical memory to run."},
        {"q": "What is paging and segmentation?", "a": "Paging: divides memory into fixed-size pages. Segmentation: divides into variable-size segments by logical meaning."},
        {"q": "What is a semaphore?", "a": "Synchronization primitive using a counter. Binary semaphore (mutex): 0 or 1. Counting semaphore: any value."},
    ],
    "Computer Networks": [
        {"q": "Explain the OSI model and its 7 layers.", "a": "Physical, Data Link, Network, Transport, Session, Presentation, Application — from bottom to top."},
        {"q": "What happens when you type a URL in a browser?", "a": "DNS lookup → TCP connection → HTTP request → Server processes → HTTP response → Browser renders."},
        {"q": "What is the difference between TCP and UDP?", "a": "TCP: reliable, ordered, connection-oriented. UDP: fast, unreliable, connectionless. TCP for web; UDP for streaming/gaming."},
        {"q": "What is an IP address? Difference between IPv4 and IPv6?", "a": "Unique address for a device. IPv4: 32-bit (4.3B addresses). IPv6: 128-bit (340 undecillion addresses)."},
        {"q": "What is HTTPS and why is it important?", "a": "HTTP over TLS/SSL. Encrypts data in transit, verifies server identity. Prevents eavesdropping and MITM attacks."},
    ],
}

CODING_QUESTIONS = [
    {
        "title": "Two Sum",
        "difficulty": "Easy",
        "problem": "Given an array of integers nums and an integer target, return indices of two numbers that add up to target.",
        "input_example": "nums = [2, 7, 11, 15], target = 9",
        "output_example": "[0, 1]",
        "approach": "Use a hash map to store each number and its index. For each element, check if (target - element) is in the map.",
        "python_solution": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
    },
    {
        "title": "Reverse a String",
        "difficulty": "Easy",
        "problem": "Write a function to reverse a string in-place.",
        "input_example": "s = ['h','e','l','l','o']",
        "output_example": "['o','l','l','e','h']",
        "approach": "Use two pointers starting from both ends, swap, move inward.",
        "python_solution": "def reverse_string(s):\n    l, r = 0, len(s) - 1\n    while l < r:\n        s[l], s[r] = s[r], s[l]\n        l += 1; r -= 1",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
    },
    {
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "problem": "Given a string s containing '(', ')', '{', '}', '[', ']', determine if the input string is valid.",
        "input_example": 's = "()[]{}"',
        "output_example": "True",
        "approach": "Use a stack. Push opening brackets; for closing brackets, check if top of stack matches.",
        "python_solution": "def is_valid(s):\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for c in s:\n        if c in mapping:\n            if not stack or stack[-1] != mapping[c]: return False\n            stack.pop()\n        else:\n            stack.append(c)\n    return not stack",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
    },
    {
        "title": "Binary Search",
        "difficulty": "Easy",
        "problem": "Given a sorted array and a target, return the index of target, or -1 if not found.",
        "input_example": "nums = [-1,0,3,5,9,12], target = 9",
        "output_example": "4",
        "approach": "Use two pointers l and r. Compute mid. If nums[mid] == target, return mid. Narrow search range.",
        "python_solution": "def search(nums, target):\n    l, r = 0, len(nums) - 1\n    while l <= r:\n        mid = (l + r) // 2\n        if nums[mid] == target: return mid\n        elif nums[mid] < target: l = mid + 1\n        else: r = mid - 1\n    return -1",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
    },
    {
        "title": "Maximum Subarray (Kadane's Algorithm)",
        "difficulty": "Medium",
        "problem": "Given an integer array, find the contiguous subarray with the largest sum.",
        "input_example": "nums = [-2,1,-3,4,-1,2,1,-5,4]",
        "output_example": "6",
        "approach": "Track current sum and max sum. At each step, decide whether to extend current subarray or start fresh.",
        "python_solution": "def max_sub_array(nums):\n    cur = max_sum = nums[0]\n    for n in nums[1:]:\n        cur = max(n, cur + n)\n        max_sum = max(max_sum, cur)\n    return max_sum",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
    },
]

APTITUDE_QUESTIONS = [
    {"q": "A train 150m long passes a pole in 15 seconds. What is its speed in km/h?",
     "a": "36 km/h", "explanation": "Speed = 150/15 = 10 m/s = 10 × 18/5 = 36 km/h"},
    {"q": "If 20% of a number is 80, what is the number?",
     "a": "400", "explanation": "20% × x = 80 → x = 80/0.2 = 400"},
    {"q": "A can do a job in 12 days and B in 18 days. How many days together?",
     "a": "7.2 days", "explanation": "Combined rate = 1/12 + 1/18 = 5/36. Days = 36/5 = 7.2"},
    {"q": "What is 15% of 240?", "a": "36", "explanation": "240 × 0.15 = 36"},
    {"q": "The ratio of boys to girls in a class is 4:3. If there are 35 students, how many boys?",
     "a": "20", "explanation": "Boys = 4/7 × 35 = 20"},
]

HR_QUESTIONS = [
    {"q": "Tell me about yourself.",
     "framework": "Present: current role/education → Past: relevant background → Future: why this company/role.",
     "sample": "I'm a final-year Computer Science student at [College]. I've built projects in Python and Java, and I'm passionate about backend development. I'm excited about joining [Company] because of its focus on innovation and scale."},
    {"q": "Why do you want to join this company?",
     "framework": "Research the company's values, products, culture. Align your goals with them.",
     "sample": "I admire [Company]'s commitment to technology excellence and its growth trajectory. Your engineering culture and the chance to work on large-scale systems align with my career goals."},
    {"q": "What is your greatest strength?",
     "framework": "Choose a strength relevant to the role. Give a specific example.",
     "sample": "My greatest strength is problem-solving. During my internship, I reduced a process runtime by 40% by rethinking the algorithm. I enjoy breaking down complex problems."},
    {"q": "Describe a challenge you faced and how you overcame it.",
     "framework": "STAR: Situation → Task → Action → Result.",
     "sample": "In my final year project, our team fell behind schedule. I reorganized tasks, held daily check-ins, and we delivered on time. This taught me the value of proactive communication."},
    {"q": "Where do you see yourself in 5 years?",
     "framework": "Show ambition aligned with company growth. Avoid overly specific or off-brand goals.",
     "sample": "I aim to become a strong software engineer, contributing to impactful projects. In 5 years, I hope to be leading modules or mentoring newer team members, growing with [Company]."},
]


def generate_questions(
    company: str,
    job_role: str,
    skills: list,
    experience_level: str,
    language: str = "Python",
    categories: list = None,
    num_per_category: int = 5,
) -> dict:
    """
    Generate interview questions for the given profile.
    Returns dict keyed by category.
    """
    if categories is None:
        categories = ["Technical", "Coding", "DSA", "SQL", "Aptitude", "HR", "Behavioral"]

    provider_info = get_provider_info()
    questions = {}

    # Technical questions
    if "Technical" in categories:
        tech_qs = []
        for cat, qs in TECHNICAL_QUESTIONS.items():
            tech_qs.extend([{"category": cat, "question": q["q"], "answer": q["a"], "source": "curated"} for q in qs[:2]])
        questions["Technical"] = tech_qs[:num_per_category * 2]

    # Coding questions
    if "Coding" in categories or "DSA" in categories:
        questions["Coding"] = CODING_QUESTIONS[:num_per_category]

    # SQL
    if "SQL" in categories:
        questions["SQL"] = [
            {"category": "DBMS & SQL", "question": q["q"], "answer": q["a"], "source": "curated"}
            for q in TECHNICAL_QUESTIONS.get("DBMS & SQL", [])[:num_per_category]
        ]

    # Aptitude
    if "Aptitude" in categories:
        questions["Aptitude"] = APTITUDE_QUESTIONS[:num_per_category]

    # HR
    if "HR" in categories or "Behavioral" in categories:
        questions["HR"] = HR_QUESTIONS[:num_per_category]

    # AI enrichment
    if not DEMO_MODE:
        try:
            ai_prompt = f"""Generate 3 {experience_level}-level technical interview questions for a {job_role} position at {company}.
Focus on {language} programming. For each question provide:
- question: the interview question
- answer: concise but complete answer
- topic: the topic area
Return as JSON array: [{{"question": ..., "answer": ..., "topic": ...}}]"""
            ai_qs = generate_json(ai_prompt, fallback=[])
            if isinstance(ai_qs, list) and ai_qs:
                questions["AI Generated"] = [
                    {"question": q.get("question", ""), "answer": q.get("answer", ""),
                     "topic": q.get("topic", ""), "source": "ai_generated",
                     "label": "⚠️ AI-Generated Practice Question — Not a verified past question"}
                    for q in ai_qs
                ]
        except Exception:
            pass

    questions["_provider"] = provider_info
    questions["_disclaimer"] = (
        "Questions marked 'AI-Generated' are practice questions generated by AI. "
        "They are NOT verified past interview questions from any company."
    )
    return questions
