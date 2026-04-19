# API Contract - AI Service and Main Backend Integration

## 1. Roadmap Content Generation

**Service Flow:**
The Main Backend requests roadmap content generation by sending user preferences and subtopic details. The AI Service receives this data, processes the search and ranking, and returns the curated learning resources.

**Request Details:**

- **Method:** POST
- **Endpoint:** http://localhost:8000/api/v1/roadmap/generate
- **Content-Type:** application/json

**JSON Body (Sent by Main Backend):**

```json
{
  "user_profile_schema": {
    "id": "user_123",
    "tracks": ["Backend Development"],
    "learningStyle": "Visual",
    "currentGoal": "Build scalable microservices",
    "studyTimePerWeek": "10-15 hours",
    "role": "STUDENT"
  },
  "target_subtopic_schema": {
    "Subtopic_id": "sub_456",
    "Name": "Database Fundamentals",
    "Description": "Basic concepts of relational and non-relational databases.",
    "Difficulty": "Beginner"
  },
  "weakness_schema": {
    "Topics": {
      "Concurrency": "Struggles with threading and async"
    }
  }
}
```

**Response Details (Returned by AI Service):**

- **Status:** 200 OK

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "best_course": {
    "title": "Introduction to Databases | Coursera",
    "url": "https://www.coursera.org/learn/introduction-to-databases"
  },
  "best_video": {
    "title": "Database Fundamentals for Beginners - YouTube",
    "url": "https://www.youtube.com/watch?v=example"
  },
  "best_blog": {
    "title": "Database Fundamentals | Microsoft Learn",
    "url": "https://learn.microsoft.com/en-us/shows/dbfundamentals/"
  }
}
```
