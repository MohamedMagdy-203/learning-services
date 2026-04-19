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
    "url": "[https://www.coursera.org/learn/introduction-to-databases](https://www.coursera.org/learn/introduction-to-databases)"
  },
  "best_video": {
    "title": "Database Fundamentals for Beginners - YouTube",
    "url": "[https://www.youtube.com/watch?v=example](https://www.youtube.com/watch?v=example)"
  },
  "best_blog": {
    "title": "Database Fundamentals | Microsoft Learn",
    "url": "[https://learn.microsoft.com/en-us/shows/dbfundamentals/](https://learn.microsoft.com/en-us/shows/dbfundamentals/)"
  }
}
```

---

## 2. Mindmap Generation

**Service Flow:**
The Main Backend requests a structured mind map based on previously stored content. The AI Service receives the request, retrieves content chunks from the vector database, and returns the generated mind map structure.

**Request Details:**

- **Method:** POST
- **Endpoint:** http://localhost:8000/api/v1/mindmap/generate
- **Content-Type:** application/json

**JSON Body (Sent by Main Backend):**

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "primary_url": "[https://www.coursera.org/learn/introduction-to-databases](https://www.coursera.org/learn/introduction-to-databases)",
  "target_subtopic_schema": {
      "Name": "Database Fundamentals",
      "Difficulty": "Beginner"
  },
  "weakness_schema": {
      "Topics": { "SQL": "Basic syntax" }
  }
}
```

**Response Details (Returned by AI Service):**

- **Status:** 200 OK

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "mindmap": {
    "root": "Database Fundamentals",
    "nodes": [
      {
        "id": "1",
        "topic": "Relational Databases",
        "details": "Explanation of tables, keys, and schemas."
      },
      {
        "id": "2",
        "topic": "SQL Basics",
        "details": "Focus on SELECT, INSERT, and JOIN operations."
      }
    ]
  }
}
```
