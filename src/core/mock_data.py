from typing import Dict, Any

MOCK_VALID_RESPONSE: Dict[str, Any] = {  # type: ignore
    "user_profile_schema": {
        "id": "user_123",
        "tracks": ["Backend Development", "AI Engineering"],
        "learningStyle": "Visual",
        "currentGoal": "Build scalable microservices",
        "studyTimePerWeek": "10-15 hours",
        "role": "STUDENT",
    },
    "target_subtopic_schema": {  # type: ignore
        "Subtopic_id": "sub_456",
        "Name": "Database Fundamentals",
        "Description": """This module focuses on the persistence layer of software architecture, where the backend engineer is responsible for storing, retrieving, and managing data reliably. Unlike frontend state which is volatile and local to a user's device, the backend database is the centralized "source of truth" for an entire application. Students will learn to design data models that reflect business logic, ensuring data integrity through schemas and relationships. The curriculum covers the fundamental distinction between rigid, structured storage (SQL) and flexible, distributed storage (NoSQL). Mastery of this topic is critical for building applications that can handle user accounts, transactions, and content management without data loss or corruption.""",  # type: ignore
        "Difficulty": "Beginner",  # type: ignore
    },
    "weakness_schema": {
        "Topics": {
            "Data Modeling": "Struggles with designing efficient database schemas and defining relationships between tables",
            "SQL vs NoSQL": "Confused about when to use relational databases versus non-relational databases",
            "Normalization": "Has difficulty understanding normalization and avoiding data redundancy",
            "Query Writing": "Needs practice writing efficient SQL queries (JOINs, filtering, aggregation)",
            "Data Integrity": "Limited understanding of constraints like primary keys, foreign keys, and transactions",
        }
    },
}

MOCK_TAVILY_RESPONSE: Dict[str, Any] = {
    "results": [
        {
            "title": "SQL for Beginners — Full Database Course",
            "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "raw_content": "This full course covers SQL fundamentals including SELECT, INSERT, UPDATE, DELETE, JOINs, and database design for beginners. Learn how to create and manage relational databases from scratch.",
        },
        {
            "title": "Database Design and Normalization",
            "url": "https://www.geeksforgeeks.org/database-normalization-normal-forms/",
            "raw_content": "Database normalization is the process of organizing a relational database to reduce data redundancy and improve data integrity. Normal forms include 1NF, 2NF, 3NF, and BCNF.",
        },
    ]
}

MOCK_CLEANED_RESPONSE = [
    {
        "title": "The Complete SQL Bootcamp — Udemy",
        "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/",
        "raw_content": "Learn SQL from scratch with hands-on exercises. This course covers relational database design, SQL queries, JOINs, aggregations, subqueries, and database normalization for backend developers."
        * 20,
    },
    {
        "title": "Database Fundamentals for Beginners — YouTube",
        "url": "https://www.youtube.com/watch?v=wR0jg0eQsZA",
        "raw_content": "A visual step-by-step tutorial covering relational vs non-relational databases, entity-relationship diagrams, primary and foreign keys, and basic SQL syntax for complete beginners."
        * 20,
    },
    {
        "title": "SQL vs NoSQL — When to Use Which",
        "url": "https://www.mongodb.com/nosql-explained/nosql-vs-sql",
        "raw_content": "A comprehensive guide explaining the key differences between SQL and NoSQL databases, their use cases, trade-offs, and how to choose the right database for your backend application."
        * 20,
    },
]

MOCK_LLM_RESPONSE = """{
  "best_course": {
    "title": "The Complete SQL Bootcamp — Udemy",
    "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/",
    "reason": "Covers SQL and database design hands-on, directly addressing the learner's weaknesses in query writing and normalization."
  },
  "best_video": {
    "title": "Database Fundamentals for Beginners — YouTube",
    "url": "https://www.youtube.com/watch?v=wR0jg0eQsZA",
    "reason": "Visual tutorial perfectly suited for a visual learner starting from scratch with databases."
  },
  "best_blog": {
    "title": "SQL vs NoSQL — When to Use Which",
    "url": "https://www.mongodb.com/nosql-explained/nosql-vs-sql",
    "reason": "Directly addresses the learner's weakness in understanding when to use SQL vs NoSQL databases."
  }
}"""

MOCK_RANKED_RESULT = {
    "best_course": {
        "title": "The Complete SQL Bootcamp — Udemy",
        "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/",
        "reason": "Covers SQL and database design hands-on.",
        "raw_content": MOCK_CLEANED_RESPONSE[0]["raw_content"],
    },
    "best_video": {
        "title": "Database Fundamentals for Beginners — YouTube",
        "url": "https://www.youtube.com/watch?v=wR0jg0eQsZA",
        "reason": "Visual tutorial for visual learner.",
        "raw_content": MOCK_CLEANED_RESPONSE[1]["raw_content"],
    },
    "best_blog": {
        "title": "SQL vs NoSQL — When to Use Which",
        "url": "https://www.mongodb.com/nosql-explained/nosql-vs-sql",
        "reason": "Addresses SQL vs NoSQL weakness.",
        "raw_content": MOCK_CLEANED_RESPONSE[2]["raw_content"],
    },
}

arabic_content = (
    """
    قواعد البيانات هي المكون الأساسي في أي تطبيق برمجي حديث.
    تنقسم قواعد البيانات إلى نوعين رئيسيين: قواعد البيانات العلائقية مثل PostgreSQL و MySQL،
    وقواعد البيانات غير العلائقية مثل MongoDB و Redis.
    قواعد البيانات العلائقية تستخدم لغة SQL للتعامل مع البيانات المنظمة.
    أما قواعد البيانات غير العلائقية فتتميز بمرونتها في التعامل مع البيانات غير المنظمة.
    يعتمد اختيار نوع قاعدة البيانات على طبيعة البيانات ومتطلبات التطبيق.
    التطبيقات التي تحتاج إلى علاقات معقدة بين البيانات تستفيد من قواعد البيانات العلائقية.
    بينما التطبيقات التي تحتاج إلى مرونة وسرعة في التخزين تستفيد من قواعد البيانات غير العلائقية.
    """
    * 10
)

# ── Mindmap Mock Data ──

MOCK_MINDMAP_REQUEST: Dict[str, Any] = {
    "user_id": "user_123",
    "subtopic_id": "sub_456",
    "best_course_url": "https://www.udemy.com/course/the-complete-sql-bootcamp/",
    "best_video_url": "https://www.youtube.com/watch?v=wR0jg0eQsZA",
    "best_blog_url": "https://www.mongodb.com/nosql-explained/nosql-vs-sql",
    "subtopic_name": "Database Fundamentals",
    "subtopic_description": (
        "This module focuses on the persistence layer of software architecture, "
        "where the backend engineer is responsible for storing, retrieving, and "
        "managing data reliably."
    ),
    "subtopic_difficulty": "Beginner",
    "weaknesses": {
        "Data Modeling": "Struggles with designing efficient database schemas",
        "SQL vs NoSQL": "Confused about when to use relational vs non-relational databases",
        "Normalization": "Has difficulty understanding normalization",
        "Query Writing": "Needs practice writing efficient SQL queries",
        "Data Integrity": "Limited understanding of constraints like primary keys",
    },
}

MOCK_MINDMAP_REQUEST_ONE_SOURCE: Dict[str, Any] = {
    **MOCK_MINDMAP_REQUEST,
    "best_course_url": None,
    "best_video_url": None,
    "best_blog_url": "https://www.mongodb.com/nosql-explained/nosql-vs-sql",
}

MOCK_MINDMAP_REQUEST_NO_SOURCES: Dict[str, Any] = {
    **MOCK_MINDMAP_REQUEST,
    "best_course_url": None,
    "best_video_url": None,
    "best_blog_url": None,
}

MOCK_MINDMAP_CHUNKS: list[str] = [
    "Database normalization is the process of organizing a relational database "
    "to reduce data redundancy and improve data integrity. Normal forms: 1NF, 2NF, 3NF.",
    "SQL databases use structured query language for defining and manipulating data. "
    "They enforce a rigid schema with tables, rows, and columns.",
    "NoSQL databases provide flexible schemas for unstructured data. "
    "Types include document, key-value, column-family, and graph databases.",
    "Primary keys uniquely identify each record in a table. "
    "Foreign keys create relationships between tables.",
    "JOINs allow querying data across multiple related tables. "
    "Types: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN.",
    "Transactions ensure ACID properties: Atomicity, Consistency, Isolation, Durability.",
]

MOCK_MINDMAP_RESPONSE: Dict[str, Any] = {
    "topic": "Database Fundamentals",
    "children": [
        {
            "topic": "SQL Databases",
            "children": [
                {"topic": "Tables and Schemas", "children": []},
                {"topic": "SQL Queries", "children": []},
                {"topic": "JOINs", "children": []},
            ],
        },
        {
            "topic": "NoSQL Databases",
            "children": [
                {"topic": "Document Stores", "children": []},
                {"topic": "Key-Value Stores", "children": []},
                {"topic": "When to use NoSQL", "children": []},
            ],
        },
        {
            "topic": "Data Modeling",
            "children": [
                {"topic": "Primary Keys", "children": []},
                {"topic": "Foreign Keys", "children": []},
                {"topic": "Relationships", "children": []},
            ],
        },
        {
            "topic": "Normalization",
            "children": [
                {"topic": "1NF", "children": []},
                {"topic": "2NF", "children": []},
                {"topic": "3NF", "children": []},
            ],
        },
        {
            "topic": "Data Integrity",
            "children": [
                {"topic": "Constraints", "children": []},
                {"topic": "Transactions and ACID", "children": []},
            ],
        },
    ],
}

