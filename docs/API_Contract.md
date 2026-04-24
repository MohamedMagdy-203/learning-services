# API Contract — AI Service ↔ Main Backend

## 1. AI Service → Main Backend

**Request**

```http
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

```http
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
## 3. Main Backend → AI Service (Quiz Bank Generation)

**Request**

```http
POST http://localhost:8000/api/v1/quiz-bank/generate
```


```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "urls": [
    "https://www.coursera.org/learn/introduction-to-databases",
    "https://www.youtube.com/watch?v=xxx",
    "https://www.mongodb.com/nosql-explained"
  ],
  "primary_url": "https://www.youtube.com/watch?v=xxx",
  "subtopic_name": "Database Fundamentals",
  "subtopic_difficulty": "Beginner",
  "weaknesses": {
    "Normalization": "Struggles with 2NF and 3NF concepts"
  }
}

```
- `primary_url` must be one of the URLs provided in `urls`.

**Response**

```json

{
  "quiz_id": "quiz_789",
  "subtopic_id": "sub_456",
  "questions": [
    {
      "question_id": "q1",
      "subtopic_id": "sub_456",
      "source_url": "https://example.com/video",
      "difficulty": "medium",
      "content": "What is ...?",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "Because ..."
    }
  ]
}

```
