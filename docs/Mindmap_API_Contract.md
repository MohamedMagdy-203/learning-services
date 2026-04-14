# API Contract — Mind Map Feature
## AI Service ↔ Main Backend

---

## Overview

The Mind Map feature requires **one call from the Main Backend to the AI Service**.
The Main Backend is responsible for gathering all required context and sending it
in a single request. The AI Service does not call the Main Backend for this feature.

```
Main Backend ──── POST /api/v1/mindmap/ ────► AI Service
                                                    │
                                              Qdrant (scroll by URL)
                                                    │
                                              Gemini (generate mindmap)
                                                    │
Main Backend ◄─── MindmapResponseSchema ───────────┘
```

---

## 1. Main Backend → AI Service

### Request

```
POST http://localhost:8000/api/v1/mindmap/
Content-Type: application/json
```

### Request Body

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",

  "best_course_url": "https://www.udemy.com/course/the-complete-sql-bootcamp/",
  "best_video_url": "https://www.youtube.com/watch?v=wR0jg0eQsZA",
  "best_blog_url": "https://www.postgresqltutorial.com/",

  "subtopic_name": "Database Fundamentals",
  "subtopic_difficulty": "Beginner",

  "weaknesses": {
    "Normalization": "Struggles with 2NF and 3NF concepts",
    "Joins": "Confuses INNER JOIN with LEFT JOIN"
  }
}
```

### Field Reference

  -------------------------------------------------------------------------------------
  Field                 Type           Required        Description
  --------------------- -------------- -------------- --------------
  user_id               string         Yes             Unique user
                                                       identifier

  subtopic_id           string         Yes               Unique
                                                        subtopic
                                                        identifier

  best_course_url       string \| null No               Course URL
                                                        stored in
                                                         Qdrant

  best_video_url        string \| null No               Video URL
                                                        stored in
                                                         Qdrant

  best_blog_url         string \| null No               Blog URL
                                                        stored in
                                                        Qdrant

  subtopic_name         string         Yes               Root node of
                                                        the mindmap

  subtopic_difficulty   string         Yes              Controls depth
                                                       and complexity
                                                        of the mindmap

  weaknesses            object         Yes               Key: topic
                                                         name ---
                                                         Value:
                                                         weakness
                                                         description
  -------------------------------------------------------------------------------------
> ⚠️ At least one of `best_course_url`, `best_video_url`, `best_blog_url` must be non-null.
> If all three are null, the AI Service returns HTTP 404.

> ⚠️ The URLs sent here must be the **exact same URLs** returned by
> `GET /api/v1/data/roadmap-content/{user_id}/{subtopic_id}`.
> The AI Service uses them to look up chunks in Qdrant — any mismatch returns no content.

---

## 2. AI Service → Main Backend

### Success Response — HTTP 200

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "mindmap": {
    "topic": "Database Fundamentals",
    "children": [
      {
        "topic": "Relational Model",
        "children": [
          {
            "topic": "Tables and Rows",
            "children": []
          },
          {
            "topic": "Primary Keys",
            "children": []
          },
          {
            "topic": "Foreign Keys",
            "children": [
              { "topic": "Referential Integrity", "children": [] }
            ]
          }
        ]
      },
      {
        "topic": "SQL Basics",
        "children": [
          { "topic": "SELECT", "children": [] },
          { "topic": "INSERT / UPDATE / DELETE", "children": [] },
          { "topic": "JOIN Types", "children": [] }
        ]
      }
    ]
  }
}
```

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Echoed from the request |
| `subtopic_id` | string | Echoed from the request |
| `mindmap` | MindmapNode | Root node of the mind map tree |

### MindmapNode (recursive)

| Field | Type | Description |
|-------|------|-------------|
| `topic` | string | Node label — concise, no full sentences |
| `children` | MindmapNode[] | Child nodes. Empty array `[]` for leaf nodes |

### Mind Map Structure Guarantees

| Property | Value |
|----------|-------|
| Root node topic | Exactly equals `subtopic_name` from the request |
| Main branches | 4 to 6 |
| Sub-topics per branch | 2 to 4 |
| Maximum nesting depth | 3 levels (branch → sub-topic → detail) |

---

## 3. Error Responses

| HTTP Status | When | Detail message |
|-------------|------|----------------|
| `404 Not Found` | All URLs are null, or all sources returned zero chunks from Qdrant | `"No content found in vector store for this subtopic. Please ensure the sources are ingested first."` |
| `503 Service Unavailable` | Qdrant is unreachable or scroll failed | `"Failed to retrieve content. Please try again later."` |
| `500 Internal Server Error` | Gemini returned invalid or unparseable response | `"Failed to generate mind map. Please try again later."` |

---

## 4. Prerequisite — Content Must Be Ingested First

The Mind Map endpoint reads from Qdrant. Content is ingested automatically
when `GET /api/v1/data/roadmap-content/{user_id}/{subtopic_id}` is called.

**Correct call order:**

```
1. GET  /api/v1/data/roadmap-content/{user_id}/{subtopic_id}
        → returns best_course, best_video, best_blog (title + url)
        → triggers background ingestion into Qdrant

2. POST /api/v1/mindmap/
        → send the 3 URLs from step 1 in the request body
        → AI Service reads chunks from Qdrant and generates the mind map
```

> ⚠️ If step 2 is called before step 1 completes ingestion, the AI Service
> will return HTTP 404 because no chunks exist yet in Qdrant for those URLs.

---

## 5. Data Flow Inside the AI Service (Internal Reference)

```
POST /api/v1/mindmap/
        │
        ▼
retrieve_all_chunks_for_mindmap()
  • Qdrant scroll by metadata.url for each non-null URL
  • 10 chunks for course, 8 for video, 8 for blog
  • Runs concurrently via asyncio.gather
        │
        ▼
build_mindmap_prompt()
  • Combines chunks + subtopic_name + subtopic_difficulty + weaknesses
        │
        ▼
Gemini gemini-2.5-flash-lite
  • temperature=0.2, max_output_tokens=2048
        │
        ▼
parse_mindmap_response()
  • Strips markdown fences → json.loads → MindmapNodeSchema validation
        │
        ▼
HTTP 200 — MindmapResponseSchema
```
