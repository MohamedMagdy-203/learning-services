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
