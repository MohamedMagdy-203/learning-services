# API Contract — AI Service ↔ Main Backend

## 1. Main Backend → AI Service (Quiz Bank Generation)

**Request**

```http
POST http://localhost:8000/api/v1/question-bank/generate
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
  "bank_id": "bank_123",
  "subtopic_id": "sub_456",
  "questions_count": 100,
  "message": "Question bank generated and stored successfully."
}

```

## 2. Main Backend → AI Service (Quiz start)

**Request**

```http
POST /api/v1/quiz/start
```


```json
{
  "bank_id": "bank_123",
  "user_id": "user_123"
}

```

**Response**

```json

{
  "session_id": "session_001",
  "status": "ongoing",
  "question": {
    "question_id": "q1",
    "difficulty": "medium",
    "content": "...",
    "options": ["A", "B","c","D"],
    "correct_answer": "A",
    "explanations": {
    "A": "Correct because ...",
    "B": "Wrong because ...",
    "C": "Wrong because ...",
    "D": "Wrong because ..."
  },

    }
}

```



## 3. Main Backend → AI Service (Quiz Answer)

**Request**

```http
POST /api/v1/quiz/answer
```


```json
{
  "session_id": "session_001",
  "question_id": "q1",
  "is_correct": true,
  "response_time": 12.4
}

```

**Response**

```json
{
  "session_id": "session_001",
  "status": "ongoing",
  "next_question": {
    "question_id": "q2",
    "difficulty": "medium",
    "content": "...",
    "options": ["A", "B","c","D"],
    "correct_answer": "A",
    "explanations": {
    "A": "Correct because ...",
    "B": "Wrong because ...",
    "C": "Wrong because ...",
    "D": "Wrong because ..."
  },

  }
}
```
### If quiz ended

**Response**

```json
{
  "session_id": "session_001",
  "status": "finished",
  "summary": {
    "total_questions_answered": 10,
    "correct_answers": 8,
    "average_response_time": 9.3,
    "final_confidence_score": 0.82
  }
}

```
