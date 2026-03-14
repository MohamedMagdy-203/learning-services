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
        "Name": "Async/Await in Python",
        "Description": "Understanding asynchronous programming and non-blocking I/O.",
        "Difficulty": "Intermediate",
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
