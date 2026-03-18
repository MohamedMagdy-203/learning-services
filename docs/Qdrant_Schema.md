# Qdrant Vector Store — Schema Reference

## Collection Configuration

| Property | Value |
|----------|-------|
| Collection Name | `learning_materials` (configurable via `QDRANT_COLLECTION_NAME`) |
| Vector Size | `768` (must match embedding model) |
| Distance Metric | `COSINE` |
| Qdrant URL | `http://localhost:6333` (configurable via `QDRANT_URL`) |

---

## Document Schema

Each point in Qdrant has two parts:

### Vector

A 768-dimensional float array generated from `page_content` by the embedding model.

### Payload (Metadata)

| Field | Type | Description |
|-------|------|-------------|
| `source_type` | string | One of: `best_course` \| `best_video` \| `best_blog` |
| `title` | string | Title of the source |
| `url` | string | Full URL — used as unique identifier for deduplication |

> **Note:** `user_id` and `subtopic_id` are NOT stored in Qdrant.
> The relationship between a user and a content source is managed by the Main Backend.

---

## Full Example

```json
{
  "page_content": "Database normalization is the process of organizing a relational database...",
  "metadata": {
    "source_type": "best_video",
    "title": "Database Fundamentals Tutorial for Beginners - YouTube",
    "url": "https://www.youtube.com/watch?v=RPkzMR59x50"
  }
}
```

---

## Embedding Model

| Property | Value |
|----------|-------|
| Model | `paraphrase-multilingual-mpnet-base-v2` |
| Dimensions | `768` |
| Language Support | Arabic + English |

> ⚠️ If you change the embedding model, delete the Qdrant collection and recreate it.

---

## Deduplication

Before storing, the system checks if `metadata.url` already exists in Qdrant.
If found — content is skipped, no re-embedding.

> ⚠️ Deduplication is exact URL match. URLs with different query params are treated as different sources.

## How to Query

for example:

```python
results = vector_store.similarity_search(
    query="explain normalization",
    k=5,
    filter={"must": [{"key": "metadata.url", "match": {"value": url}}]}
)
```
