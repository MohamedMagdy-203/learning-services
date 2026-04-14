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
## 3. Main Backend → AI Service (Distillation)

**Request**

```
POST http://localhost:8000/api/v1/dist/distill-content
```


```json
{
  "urls": [
    "https://example.com/course",
    "https://example.com/video",
    "https://example.com/blog"
  ],
  "primary_url": "https://example.com/video"
}

```

**Response**

```json
{
  "results": [
    {
      "url": "https://example.com/course",
      "is_primary": false,
      "distilled_content": {
        "key_terms": [
          { "term": "Database", "definition": "..." }
        ],
        "main_points": [
          "Point 1",
          "Point 2"
        ],
        "examples": [
          "Example 1"
        ]
      }
    },
    {
      "url": "https://example.com/video",
      "is_primary": true,
      "distilled_content": {
        "key_terms": [],
        "main_points": [
          "Important concept"
        ],
        "examples": []
      }
    }
  ]
}
```
## 4. Main Backend → AI Service (Quiz Bank Generation)

**Request**
```
POST http://localhost:8000/api/v1/quiz-bank/generate
```

```json
{
  "distilled_results": [
    {
      "url": "https://example.com/video",
      "is_primary": true,
      "distilled_content": {
        "key_terms": [],
        "main_points": ["Important concept"],
        "examples": []
      }
    },
    {
      "url": "https://example.com/blog",
      "is_primary": false,
      "distilled_content": {
        "key_terms": [],
        "main_points": ["Extra info"],
        "examples": []
      }
    }
  ],
  "subtopic_id": "sub_456",
  "primary_url": "https://example.com/video",
  "total_questions": 30
}

```

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
