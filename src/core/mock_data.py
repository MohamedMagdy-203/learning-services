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
        "Name": "Database Fundamentals",
        "Description": """This module focuses on the persistence layer of software architecture, where the backend engineer is responsible for storing, retrieving, and managing data reliably. Unlike frontend state which is volatile and local to a user's device, the backend database is the centralized "source of truth" for an entire application. Students will learn to design data models that reflect business logic, ensuring data integrity through schemas and relationships. The curriculum covers the fundamental distinction between rigid, structured storage (SQL) and flexible, distributed storage (NoSQL). Mastery of this topic is critical for building applications that can handle user accounts, transactions, and content management without data loss or corruption.""",  # type: ignore
        "Difficulty": "Beginner",  # type: ignore
    },
    "weakness_schema": {
        "Topics": {
            "Concurrency": "Struggles with the difference between threading and async",
            "API Integration": "Needs practice with httpx",
        }
    },
}

MOCK_TAVILY_RESPONSE: Dict[str, Any] = {
    "results": [
        {
            "title": "Mastering Async/Await in Python",
            "url": "https://realpython.com/async-io-python/",
            "raw_content": "Asyncio is a library to write concurrent code using the async/await syntax. It is a perfect fit for IO-bound and high-level structured network code.",
        },
        {
            "title": "Python Concurrency vs Threading",
            "url": "https://example.com/python-concurrency",
            "raw_content": "The main difference between threading and async is that threading uses OS-level threads, while async uses an event loop on a single thread.",
        },
    ]
}
