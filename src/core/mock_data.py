from typing import Dict, Any

MOCK_VALID_RESPONSE: Dict[str, Any] = {
    "user_profile_schema": {
        "id": "user_123",
        "tracks": ["Backend Development", "AI Engineering"],
        "learningStyle": "Visual",
        "currentGoal": "Build scalable microservices",
        "studyTimePerWeek": "10-15 hours",
        "role": "STUDENT",
    },
    "target_subtopic_schema": {
        "Subtopic_id": "sub_456",
        "Name": "Database Fundamentals",
        "Description": """This module focuses on the persistence layer of software architecture, where the backend engineer is responsible for storing, retrieving, and managing data reliably. Unlike frontend state which is volatile and local to a user's device, the backend database is the centralized "source of truth" for an entire application. Students will learn to design data models that reflect business logic, ensuring data integrity through schemas and relationships. The curriculum covers the fundamental distinction between rigid, structured storage (SQL) and flexible, distributed storage (NoSQL). Mastery of this topic is critical for building applications that can handle user accounts, transactions, and content management without data loss or corruption.""",
        "Difficulty": "Beginner",
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
            "raw_content": """Welcome to this full SQL course for beginners. In this video we will cover everything you need to know to get started with relational databases.
We start by explaining what a database is and why we need one. A database is an organized collection of structured information or data, typically stored electronically in a computer system.
Next we look at tables, rows, and columns. Every table in a relational database represents an entity, such as users, products, or orders. Each row is a single record, and each column is an attribute of that entity.
We then move into writing your first SQL queries. The SELECT statement is used to retrieve data from a table. For example: SELECT * FROM users WHERE age > 18 ORDER BY name ASC.
After that we cover JOINs in detail. An INNER JOIN returns rows that have matching values in both tables. A LEFT JOIN returns all rows from the left table and the matched rows from the right table.
We also explain primary keys and foreign keys. A primary key uniquely identifies each record in a table. A foreign key is a field in one table that refers to the primary key in another table, establishing a relationship between the two.
Then we discuss database normalization. The goal of normalization is to reduce data redundancy and improve data integrity. First Normal Form requires that each column contains atomic values. Second Normal Form requires that all non-key attributes are fully dependent on the primary key.
Finally we introduce indexes and why they matter for query performance. An index allows the database engine to find rows much faster without scanning the entire table.""",
        },
        {
            "title": "Database Design and Normalization",
            "url": "https://www.geeksforgeeks.org/database-normalization-normal-forms/",
            "raw_content": """Database normalization is the process of organizing a relational database to reduce data redundancy and improve data integrity.
Normalization involves decomposing a table into smaller tables and defining relationships between them. The objective is to isolate data so that additions, deletions, and modifications of a field can be made in just one table and then propagated through the rest of the database via the defined relationships.
First Normal Form (1NF): A table is in 1NF if it contains only atomic values and each record is unique. There should be no repeating groups or arrays within a single column.
Second Normal Form (2NF): A table is in 2NF if it is in 1NF and every non-key attribute is fully functionally dependent on the entire primary key. This eliminates partial dependencies.
Third Normal Form (3NF): A table is in 3NF if it is in 2NF and there are no transitive dependencies, meaning non-key attributes do not depend on other non-key attributes.
Boyce-Codd Normal Form (BCNF): A stricter version of 3NF where every determinant must be a candidate key.
Understanding normal forms helps backend engineers design schemas that are maintainable and free from update anomalies. Denormalization is sometimes applied intentionally in read-heavy systems for performance reasons.""",
        },
    ]
}

_COURSE_RAW_CONTENT = """Welcome to The Complete SQL Bootcamp. This course is designed for absolute beginners who want to master SQL and relational databases from the ground up.

Section 1 — Introduction to Databases:
A database is a structured collection of data. Relational databases organize data into tables with rows and columns. Popular relational database systems include PostgreSQL, MySQL, and SQLite. We will be using PostgreSQL throughout this course.

Section 2 — Setting Up Your Environment:
Install PostgreSQL and pgAdmin on your machine. Connect to a local database server. Create your first database using the CREATE DATABASE command. Understand the difference between a database server, a database, a schema, and a table.

Section 3 — SQL Fundamentals:
The SELECT statement retrieves data from one or more tables. Use WHERE to filter rows, ORDER BY to sort results, and LIMIT to restrict the number of rows returned. Aggregate functions like COUNT, SUM, AVG, MIN, and MAX summarize data across multiple rows. The GROUP BY clause groups rows that share a value so aggregate functions can be applied per group. The HAVING clause filters groups after aggregation, similar to WHERE for rows.

Section 4 — Joins:
A JOIN combines rows from two or more tables based on a related column. INNER JOIN returns only rows with matching values in both tables. LEFT JOIN returns all rows from the left table and matching rows from the right, with NULLs where there is no match. RIGHT JOIN is the mirror of LEFT JOIN. FULL OUTER JOIN returns all rows from both tables. Self-joins allow a table to be joined with itself, useful for hierarchical data like employee-manager relationships.

Section 5 — Database Design and Normalization:
Good schema design starts with identifying entities and their attributes. Entity-Relationship (ER) diagrams visually represent the data model. Primary keys uniquely identify each row in a table. Foreign keys link rows in one table to rows in another, enforcing referential integrity. Normalization reduces redundancy by ensuring each piece of information is stored only once. We cover 1NF, 2NF, and 3NF with practical examples.

Section 6 — Advanced SQL:
Subqueries allow nesting one query inside another. Common Table Expressions (CTEs) with the WITH keyword make complex queries more readable. Window functions like ROW_NUMBER, RANK, and LAG operate on a set of rows related to the current row. Indexes speed up data retrieval at the cost of additional storage and slower writes. EXPLAIN and EXPLAIN ANALYZE help you understand and optimize query execution plans.

Section 7 — Transactions and Data Integrity:
A transaction is a sequence of operations performed as a single logical unit of work. Transactions follow the ACID properties: Atomicity, Consistency, Isolation, and Durability. Use BEGIN, COMMIT, and ROLLBACK to manage transactions. Constraints like NOT NULL, UNIQUE, CHECK, and DEFAULT enforce data integrity at the database level."""

_VIDEO_RAW_CONTENT = """Hey everyone welcome back. Today we are going to talk about database fundamentals and I think this is one of the most important topics for any backend developer.

So first things first what even is a database. A database is basically just a place where you store your data in an organized way so you can retrieve it later efficiently. Think of it like a really well organized filing cabinet.

Now there are two main types of databases you will hear about. Relational databases and non-relational databases. Relational databases store data in tables that are related to each other. Non-relational databases store data in other formats like documents, key-value pairs, or graphs.

Let me show you a simple example. Imagine you are building a social media app. You might have a users table with columns like id, username, email, and created_at. You might have a posts table with columns like id, user_id, content, and created_at. The user_id column in the posts table is a foreign key that points to the id column in the users table. This is how relationships work.

Now let us talk about SQL. SQL stands for Structured Query Language and it is the language you use to interact with relational databases. A basic SELECT query looks like this. SELECT username, email FROM users WHERE created_at > 2024-01-01. This retrieves the username and email of all users who signed up after January first 2024.

JOINs are super important. If you want to get all posts along with the username of whoever wrote them you would write something like this. SELECT users.username, posts.content FROM posts INNER JOIN users ON posts.user_id equals users.id. The INNER JOIN connects the two tables on the matching id.

Indexes are another key concept. Without an index the database has to scan every single row in a table to find what you are looking for. That is called a full table scan and it is slow. An index is like the index at the back of a book. It lets the database jump directly to the right rows.

Finally let us touch on NoSQL. MongoDB is probably the most popular NoSQL database. Instead of tables it uses collections. Instead of rows it uses documents which look like JSON objects. NoSQL databases are great when your data structure is flexible or changes frequently, or when you need to scale horizontally across many servers."""

_BLOG_RAW_CONTENT = """SQL vs NoSQL: When to Use Which

Choosing the right type of database is one of the most consequential architectural decisions you will make when building a backend system. This guide breaks down the differences between SQL and NoSQL databases and gives you a practical framework for choosing between them.

What is a SQL Database?
SQL databases, also called relational databases, store data in tables with a fixed schema. Each table has predefined columns with specific data types. Rows represent individual records. Tables are related to each other through foreign keys. Popular SQL databases include PostgreSQL, MySQL, SQLite, and Microsoft SQL Server.

SQL databases enforce ACID properties:
Atomicity ensures that a transaction is treated as a single unit that either fully succeeds or fully fails.
Consistency ensures the database always moves from one valid state to another.
Isolation ensures concurrent transactions do not interfere with each other.
Durability ensures that committed transactions survive system failures.

What is a NoSQL Database?
NoSQL databases store data in formats other than relational tables. The four main categories are document stores (MongoDB, Firestore), key-value stores (Redis, DynamoDB), wide-column stores (Cassandra, HBase), and graph databases (Neo4j). NoSQL databases typically sacrifice some ACID guarantees in exchange for horizontal scalability and schema flexibility.

When to Use SQL:
Your data has clear relationships that benefit from JOINs and foreign key constraints. You need strong transactional guarantees, for example in financial systems, e-commerce order processing, or healthcare records. Your schema is relatively stable and well-understood upfront. You need complex reporting or analytical queries.

When to Use NoSQL:
Your data structure is highly variable or evolves rapidly, such as user-generated content or product catalogs with different attributes per item. You need to scale horizontally across many servers to handle massive write volumes. You are building real-time applications where low latency matters more than strict consistency. You are storing large amounts of unstructured or semi-structured data like logs, events, or JSON blobs.

The Myth of Mutual Exclusivity:
Most production systems use both. A typical architecture might use PostgreSQL for user accounts, orders, and financial data, Redis for caching and session storage, and MongoDB or Firestore for flexible content storage. Choosing SQL vs NoSQL is not an all-or-nothing decision but a per-use-case decision within your overall system design."""

MOCK_CLEANED_RESPONSE = [
    {
        "title": "The Complete SQL Bootcamp — Udemy",
        "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/",
        "raw_content": _COURSE_RAW_CONTENT,
    },
    {
        "title": "Database Fundamentals for Beginners — YouTube",
        "url": "https://www.youtube.com/watch?v=wR0jg0eQsZA",
        "raw_content": _VIDEO_RAW_CONTENT,
    },
    {
        "title": "SQL vs NoSQL — When to Use Which",
        "url": "https://www.mongodb.com/nosql-explained/nosql-vs-sql",
        "raw_content": _BLOG_RAW_CONTENT,
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
        "raw_content": _COURSE_RAW_CONTENT,
    },
    "best_video": {
        "title": "Database Fundamentals for Beginners — YouTube",
        "url": "https://www.youtube.com/watch?v=wR0jg0eQsZA",
        "reason": "Visual tutorial for visual learner.",
        "raw_content": _VIDEO_RAW_CONTENT,
    },
    "best_blog": {
        "title": "SQL vs NoSQL — When to Use Which",
        "url": "https://www.mongodb.com/nosql-explained/nosql-vs-sql",
        "reason": "Addresses SQL vs NoSQL weakness.",
        "raw_content": _BLOG_RAW_CONTENT,
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

MOCK_Qdrant_Schema = {
    "page_content": "Database normalization is the process of organizing a relational database...",
    "metadata": {
        "source_type": "best_video",
        "title": "Database Fundamentals Tutorial for Beginners - YouTube",
        "url": "https://www.youtube.com/watch?v=RPkzMR59x50",
    },
}

# ── Mindmap Mock Data ──

MOCK_MINDMAP_REQUEST: Dict[str, Any] = {
    "user_id": "user_123",
    "subtopic_id": "sub_456",
    "urls": [
        "https://www.coursera.org/learn/introduction-to-databases",
        "https://www.classcentral.com/course/youtube-database-fundamentals-for-beginners-database-tutorial-141003",
        "https://learn.microsoft.com/en-us/shows/dbfundamentals/",
    ],
    "primary_url": "https://learn.microsoft.com/en-us/shows/dbfundamentals/",
    "subtopic_name": "Database Fundamentals",
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
    "urls": [
        "https://learn.microsoft.com/en-us/shows/dbfundamentals/",
    ],
    "primary_url": "https://learn.microsoft.com/en-us/shows/dbfundamentals/",
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
    "description": "Core concepts of databases.",
    "children": [
        {
            "topic": "SQL Databases",
            "description": "Relational systems.",
            "children": [
                {"topic": "Tables and Schemas", "description": "", "children": []},
                {"topic": "SQL Queries", "description": "", "children": []},
                {"topic": "JOINs", "description": "", "children": []},
            ],
        },
        {
            "topic": "NoSQL Databases",
            "description": "Non-relational systems.",
            "children": [
                {"topic": "Document Stores", "description": "", "children": []},
                {"topic": "Key-Value Stores", "description": "", "children": []},
                {"topic": "When to use NoSQL", "description": "", "children": []},
            ],
        },
        {
            "topic": "Data Modeling",
            "description": "Designing data structures.",
            "children": [
                {"topic": "Primary Keys", "description": "", "children": []},
                {"topic": "Foreign Keys", "description": "", "children": []},
                {"topic": "Relationships", "description": "", "children": []},
            ],
        },
        {
            "topic": "Normalization",
            "description": "Reducing data redundancy.",
            "children": [
                {"topic": "1NF", "description": "", "children": []},
                {"topic": "2NF", "description": "", "children": []},
                {"topic": "3NF", "description": "", "children": []},
            ],
        },
        {
            "topic": "Data Integrity",
            "description": "Ensuring data accuracy and consistency.",
            "children": [
                {"topic": "Constraints", "description": "", "children": []},
                {"topic": "Transactions and ACID", "description": "", "children": []},
            ],
        },
    ],
}
