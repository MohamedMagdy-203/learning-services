# API Contract — Mind Map Feature

## AI Service ↔ Main Backend

---

## Overview

The Mind Map feature requires **one synchronous call from the Main Backend to the AI Service**.
The Main Backend is responsible for providing the required context, specifically the exact `primary_url` that the user is currently studying. The AI Service relies on this URL to fetch pre-ingested content from the Vector Database (Qdrant).

```text
Main Backend ──── POST /api/v1/mindmap/generate ────► AI Service
                                                    │
                                                    ├──► Qdrant (Retrieve chunks by primary_url)
                                                    │
                                                    ├──► Gemini LLM (Generate JSON mindmap)
                                                    │
Main Backend ◄─── MindmapResponseSchema ────────────┘
```

---

## 1. Request: Main Backend → AI Service

**Endpoint:** `POST /api/v1/mindmap/generate`
**Content-Type:** `application/json`

### Request Body Example

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

 | Field                 | Type          | Required | Description                                                                                                   |
 | --------------------- | ------------- | -------- | ------------------------------------------------------------------------------------------------------------- |
 | `user_id`             | string        | **Yes**  | Unique user identifier.                                                                                       |
 | `subtopic_id`         | string        | **Yes**  | Unique subtopic identifier.                                                                                   |
+| `urls`                | string[]      | **Yes**  | All candidate source URLs for the subtopic. The selected `primary_url` must be one of these values.          |
 | `primary_url`         | string (URL)  | **Yes**  | The exact URL of the content the user wants to generate a mind map for (Must match the URL stored in Qdrant). |
 | `subtopic_name`       | string        | **Yes**  | The main title of the subtopic. Used as the Root node of the mind map.                                        |
 | `subtopic_difficulty` | string        | **Yes**  | Controls the depth and complexity of the generated mind map.                                                  |
 | `weaknesses`          | object \| null | **No**  | Key-Value pairs of user weaknesses to prioritize in the mind map.                                             |

> ⚠️ **CRITICAL:** The `primary_url` sent here MUST exactly match the URL stored in Qdrant.
> ❗ **IMPORTANT NOTE:** The size of the generated mind map is **NOT fixed**. The number of nodes and branches returned depends dynamically on the content retrieved from the vector database.

---

## 2. Response: AI Service → Main Backend

### Success Response — HTTP 200 OK

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "mindmap": {
    "topic": "Database Fundamentals",
    "children": [
      {
        "topic": "Relational Database Basics",
        "children": [
          { "topic": "Terminology and Concepts", "children": [] },
          { "topic": "Database Components", "children": [] }
        ]
      },
      {
        "topic": "Database Design",
        "children": [
          { "topic": "Schema and Modeling", "children": [] },
          { "topic": "Data Integrity and Keys", "children": [] },
          { "topic": "Normalization", "children": [] }
        ]
      }
    ]
  }
}
```

### Response Schema

| Field         | Type        | Description                     |
| ------------- | ----------- | ------------------------------- |
| `user_id`     | string      | Echoed from the request.        |
| `subtopic_id` | string      | Echoed from the request.        |
| `mindmap`     | MindmapNode | Root node of the mind map tree. |

### MindmapNode (Recursive Structure)

| Field      | Type          | Description                                                    |
| ---------- | ------------- | -------------------------------------------------------------- |
| `topic`    | string        | Node label — concise, represents a single concept.             |
| `children` | MindmapNode[] | Child nodes. Returns an empty array `[]` if it is a leaf node. |

### Mind Map Structure Guarantees

* **Root Node:** Always exactly equals the `subtopic_name` from the request.
* **Dynamic Branching:** The number of branches is **dynamic and content-driven** — there is no fixed size.
* **Soft Limits:** Typically ranges between **2 to 15 main branches**, but may vary based on content richness.
* **Nesting Depth:** Maximum of **3 levels deep** (Root → Main Branch → Sub-topic → Detail).

---

## 3. Error Handling

| HTTP Status                 | Error Code             | Detail Message / Reason                                            |
| --------------------------- | ---------------------- | ------------------------------------------------------------------ |
| `422 Unprocessable Entity`  | `VALIDATION_ERROR`     | Missing or invalid fields in the request body.                     |
| `404 Not Found`             | `CONTENT_NOT_FOUND`    | No content found in vector store for the given `primary_url`.      |
| `503 Service Unavailable`   | `RETRIEVAL_ERROR`      | Failed to retrieve content from vector store (Qdrant unavailable). |
| `500 Internal Server Error` | `LLM_GENERATION_ERROR` | LLM failed to return valid JSON or timeout occurred.               |

---

## 4. Architectural Prerequisites

To successfully generate a Mind Map, the content must already exist in the AI Service's Vector Database.

### Expected Flow

1. **Trigger Ingestion:**
   `GET /api/v1/data/roadmap-content/{user_id}/{subtopic_id}` → content is fetched and stored in Qdrant.

2. **User Selection:**
   User selects a learning resource.

3. **Generate Mind Map:**
   `POST /api/v1/mindmap/generate` using the selected `primary_url`.

---

## 5. Internal Processing Flow (AI Service)

1. **Retrieve (Smart Fallback):** - Fetch chunks strictly from the `primary_url` first (up to 50 chunks).
   - If the primary content is insufficient (< 50 chunks), fetch from the remaining secondary `urls` concurrently as a fallback.
   - Cap the total retrieved chunks at 50 to optimize the LLM context window.
2. **Prompt Construction:** Combine chunks + subtopic context + weaknesses.
3. **LLM Generation:** Generate structured JSON mind map.
4. **Validation:** Ensure response matches schema before returning.
