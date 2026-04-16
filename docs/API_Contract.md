# API Contract — AI Service ↔ Main Backend

## 1. AI Service → Main Backend

**Request**

```
GET http://localhost:3000/api/internal/roadmap-context/{user_id}/{subtopic_id}
```

**Response**

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
    "Description": "...",
    "Difficulty": "Beginner"
},
  "weakness_schema": {
    "Topics": {
      "Concurrency": "Struggles with threading and async"
    }
  }
}
```

---

## 2. Main Backend → AI Service

**Request**

```
GET http://localhost:8000/api/v1/data/roadmap-content/{user_id}/{subtopic_id}
```

**Response**

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "best_course": { "title": "...", "url": "..." },
  "best_video":  { "title": "...", "url": "..." },
  "best_blog":   { "title": "...", "url": "..." }
}
```

## 3.Main Backend → AI Service (Summarization)

**Request**

```http
POST http://localhost:8000/api/v1/summarize/generate
```
```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "primary_url": "https://example.com/article"
}
```

**Response**

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "primary_url": "https://example.com/article",
  "summary": "This article explains the basics of database normalization and why it is important..."
}
```
