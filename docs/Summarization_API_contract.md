# 1. Main Backend → AI Service (Summarization)

**Request**

```http
POST http://localhost:8000/api/v1/summarize/generate
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

# 2.AI Service  → Main Backend(Summarization)

**Response**

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "primary_url": "https://example.com/article",
  "summary": "This article explains the basics of database normalization and why it is important..."
}
```
