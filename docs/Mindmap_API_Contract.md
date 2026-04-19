# API Contract - Mind Map Generation

## Overview

The Mind Map feature requires a synchronous call from the Main Backend to the AI Service. The Main Backend provides the user's context, the target subtopic, and the URLs of the learning materials. The AI Service processes this data and returns a structured hierarchical mind map.

**Service Flow:**
The Main Backend sends the request containing the subtopic details and the relevant URLs. The AI Service generates a dynamically branched mind map tailored to the content and the user's weaknesses, and returns it as a structured JSON object.

---

## 1. Request Details

- **Method:** POST
- **Endpoint:** `http://localhost:8000/api/v1/mindmap/generate`
- **Content-Type:** `application/json`

### JSON Body (Sent by Main Backend)

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "urls": [
    "https://www.coursera.org/learn/introduction-to-databases",
    "https://www.youtube.com/watch?v=xxx",
    "https://www.mongodb.com/nosql-explained"
  ],
  "primary_url": "https://www.coursera.org/learn/introduction-to-databases",
  "subtopic_name": "Database Fundamentals",
  "subtopic_difficulty": "Beginner",
  "weaknesses": {
    "Normalization": "Struggles with 2NF and 3NF concepts"
  }
}
```

### Field Definitions

| Field                 | Type          | Required | Description                                                                                                   |
| --------------------- | ------------- | -------- | ------------------------------------------------------------------------------------------------------------- |
| `user_id`             | string        | **Yes** | Unique user identifier.                                                                                       |
| `subtopic_id`         | string        | **Yes** | Unique subtopic identifier.                                                                                   |
| `urls`                | string[]      | **Yes** | All candidate source URLs for the subtopic.                                                                   |
| `primary_url`         | string (URL)  | **Yes** | The exact URL of the primary content the user is studying (Must be one of the values in the `urls` array).    |
| `subtopic_name`       | string        | **Yes** | The main title of the subtopic. Used as the Root node of the mind map.                                        |
| `subtopic_difficulty` | string        | **Yes** | Controls the depth and complexity of the generated mind map.                                                  |
| `weaknesses`          | object / null | **No** | Key-Value pairs of user weaknesses to prioritize in the mind map generation.                                  |

---

## 2. Response Details

- **Status:** 200 OK

### JSON Body (Returned by AI Service)

```json
{
  "user_id": "user_123",
  "subtopic_id": "sub_456",
  "mindmap": {
    "topic": "Database Fundamentals",
    "description": "Comprehensive overview of relational database principles.",
    "children": [
      {
        "topic": "Core Concepts",
        "description": "Foundational blocks of DBMS.",
        "children": [
          {
            "topic": "Relational Model",
            "description": "",
            "children": []
          }
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
* **Dynamic Branching:** The number of branches is dynamically generated based on the content (typically ranges between 2 to 15 main branches).
* **Nesting Depth:** Maximum of 3 levels deep (Root -> Main Branch -> Sub-topic -> Detail).

---

## 3. Error Handling

| HTTP Status                 | Error Code             | Detail Message / Reason                                            |
| --------------------------- | ---------------------- | ------------------------------------------------------------------ |
| `422 Unprocessable Entity`  | `VALIDATION_ERROR`     | Missing or invalid fields in the request body.                     |
| `404 Not Found`             | `CONTENT_NOT_FOUND`    | No stored content found for the provided URLs.                     |
| `503 Service Unavailable`   | `RETRIEVAL_ERROR`      | Failed to retrieve content due to internal database unavailability.|
| `500 Internal Server Error` | `LLM_GENERATION_ERROR` | AI Engine failed to generate a valid mind map structure.           |

---

## 4. Prerequisites

**Important:** The Mind Map generation relies on content that has been previously fetched and processed. The Main Backend must ensure that the `POST /api/v1/roadmap/generate` endpoint has been successfully called for the given `user_id` and `subtopic_id` before requesting a Mind Map.
