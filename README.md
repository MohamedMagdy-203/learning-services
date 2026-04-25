# Learning Services

## Table of Contents

- [Learning Services](#learning-services)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [System Architecture \& Workflow](#system-architecture--workflow)
    - [Step-by-Step Flow Explanation](#step-by-step-flow-explanation)
  - [Feature: Roadmap Generation](#feature-roadmap-generation)
  - [Feature: Mindmap Generation](#feature-mindmap-generation)
    - [Mindmap Flow](#mindmap-flow)
  - [Feature: Quiz Generation](#feature-quiz-generation)
  - [Feature: Summarization](#feature-summarization)
  - [Project Structure](#project-structure)
  - [Tech Stack](#tech-stack)
  - [Setup \& Installation](#setup--installation)
    - [1. Prerequisites](#1-prerequisites)
    - [2. Clone the Repository](#2-clone-the-repository)
    - [3. Environment Setup](#3-environment-setup)
    - [4. Start Qdrant](#4-start-qdrant)
    - [5. Install Dependencies](#5-install-dependencies)
    - [6. Setup Pre-commit Hooks](#6-setup-pre-commit-hooks)
  - [Running the Application](#running-the-application)
  - [Testing](#testing)
  - [Contribution Guidelines \& Git Workflow](#contribution-guidelines--git-workflow)
    - [1. Branching Strategy](#1-branching-strategy)
    - [2. Commits](#2-commits)
    - [3. Pull Requests](#3-pull-requests)
  - [License](#license)

---

## Overview

The **Learning Services** is an intelligent backend AI engine designed to generate personalized educational roadmaps and learning materials. By leveraging user profile data (such as learning styles, study time, and goals) alongside specific target subtopics, the system dynamically fetches, processes, and curates educational content.

It integrates:
- **Tavily API** for real-time web search
- **Google Gemini** as the core LLM for reranking and generation
- **Qdrant** as a vector database for semantic retrieval
- **HuggingFace** multilingual embeddings for Arabic & English support

---

## System Architecture & Workflow

```mermaid
flowchart TD
    A([Main Backend]) -->|POST /api/v1/roadmap/generate| B[Roadmap Router]

    B --> C[Query Builder]
    C --> D[Tavily Web Search]
    D --> E[Data Cleaner]
    E --> F[LLM Reranker - Gemini]

    F --> G{Best Sources}
    G --> G1[Best Course]
    G --> G2[Best Video]
    G --> G3[Best Blog]

    G1 & G2 & G3 -->|Background Task| H[Vector Store Pipeline]

    H --> H1[Deduplication Filter]
    H1 --> H2[Semantic Chunker]
    H2 --> H3[HuggingFace Embedder]
    H3 --> H4[(Qdrant Vector DB)]

    F -->|Ranked URLs| A

    A -->|POST /api/v1/mindmap/generate| I[Mindmap Router]
    A -->|POST /api/v1/summarize/generate| J[Summarization Router]

    I --> K[Qdrant Retriever - Scroll]
    K --> H4
    H4 --> K
    K --> L[Mindmap Prompt Builder]
    L --> M[Gemini LLM]
    M --> N[Mindmap Parser & Validator]
    N --> A

    J --> O[Shared Retriever - Scroll]
    O --> H4
    H4 --> O
    O --> P[Summarization Prompt Builder]
    P --> Q[OpenAI-compatible Gemini]
    Q --> R[JSON Parser]
    R --> A
```

### Step-by-Step Flow Explanation

1. **Input Collection** ΓÇö The Main Backend sends user profile (tracks, learning style, goals) and target subtopic (name, description, difficulty).
2. **Web Search & Extraction** ΓÇö A targeted query is built and sent to Tavily, fetching articles, courses (Coursera, Udemy), and YouTube videos. Raw content is cleaned (HTML tags, boilerplate, URLs removed).
3. **LLM Reranker / Judge** ΓÇö Gemini evaluates all sources and selects the single best course, video, and blog for this specific learner.
4. **Vector Store Pipeline** ΓÇö In the background, each selected source is deduplicated, semantically chunked, embedded, and stored in Qdrant.
5. **Content Generation** ΓÇö The user can then request a Mindmap or Summary. The system retrieves relevant chunks from Qdrant using `primary_url` filtering and feeds them to Gemini for generation.

---

## Feature: Roadmap Generation

Generates a personalized learning roadmap by searching, ranking, and returning the best course, video, and blog for a given subtopic.

```mermaid
sequenceDiagram
    participant MB as Main Backend
    participant RR as Roadmap Router
    participant TV as Tavily API
    participant LLM as Gemini Reranker
    participant QD as Qdrant

    MB->>RR: POST /api/v1/roadmap/generate
    RR->>TV: Search (query built from subtopic + user profile)
    TV-->>RR: Raw results (general + courses + videos)
    RR->>RR: Clean & filter content
    RR->>LLM: Rerank sources (user profile + cleaned sources)
    LLM-->>RR: best_course, best_video, best_blog
    RR-->>MB: Ranked result (title + url only)
    RR-)QD: Background ingestion (chunk + embed + store)
```

---

## Feature: Mindmap Generation

Generates a hierarchical mind map from content already stored in Qdrant for a specific subtopic source.

```mermaid
flowchart TD
    A([Main Backend]) -->|POST /api/v1/mindmap/generate| B[Mindmap Router]

    B --> C{Retrieve Chunks}
    C -->|primary_url filter - scroll| D[(Qdrant)]
    D --> C
    C -->|if primary insufficient| E[Secondary URLs - scroll]
    E --> D

    C --> F[Build Mindmap Prompt]
    F --> G[Gemini LLM\ntemp=0.2 ┬╖ max_tokens=8192\nresponse_mime_type=application/json]
    G --> H[Parse & Validate\nMindmapNodeSchema]
    H --> I([Return Mindmap Tree])
```

### Mindmap Flow

**Phase 1 ΓÇö Request & Context**
The router receives the request with `primary_url`, subtopic info, and user weaknesses. No additional backend call is made.

**Phase 2 ΓÇö Retrieval from Qdrant**
Chunks are fetched using strict `metadata.url` scroll-based retrieval (not similarity search). Primary URL is fetched first; secondary URLs supplement if needed.

**Phase 3 ΓÇö Generation & Response**
The chunks are assembled into a structured prompt. Gemini generates the mindmap. Output is parsed and validated into `MindmapNodeSchema` before returning.

---

## Feature: Quiz Generation

An AI-powered feature that transforms a learner's selected content source into a personalized quiz experience with adaptive difficulty and instant corrective feedback.

```mermaid
flowchart TD
    A([Main Backend]) -->|POST /api/v1/quiz/generate| B[Quiz Router]
    B --> C[Retrieve Chunks from Qdrant]
    C --> D[Build Quiz Prompt\nwith weaknesses + difficulty]
    D --> E[Gemini LLM]
    E --> F[Parse Questions]
    F --> G([Return Quiz])
    G --> H[Learner Answers]
    H --> I[Feedback Engine]
    I --> J[Weakness Summary]
```

---

## Feature: Summarization

Provides structured, beginner-friendly summaries by distilling content from Qdrant using vector scroll retrieval, then processing with an OpenAI-compatible Gemini pipeline.

```mermaid
sequenceDiagram
    participant MB as Main Backend
    participant SR as Summarization Router
    participant QD as Qdrant
    participant LLM as Gemini (via OpenAI client)

    MB->>SR: POST /api/v1/summarize/generate
    SR->>QD: Scroll by primary_url
    QD-->>SR: Relevant chunks (Documents)
    SR->>SR: Build prompt (subtopic + difficulty + weaknesses)
    SR->>LLM: Chat completion (JSON mode)
    LLM-->>SR: { "summary": "..." }
    SR-->>MB: { user_id, subtopic_id, primary_url, summary }
```

---

## Project Structure

```text
learning-services/
├── src/
│   ├── ai_engine/
│   │   ├── data_fetchers/
│   │   │   ├── cleaned_tavily_data.py      # Pipeline: fetch + clean subtopic content
│   │   │   ├── data_cleaner.py             # Regex-based text sanitization
│   │   │   ├── query_builder.py            # Build targeted search queries
│   │   │   ├── tavily_client.py            # Async Tavily web search wrapper
│   │   │   ├── chunks_retrieval.py         # Retrieve chunks from Qdrant by URL
│   │   │   └── qdrant_client_dependency.py # Shared AsyncQdrantClient (DI)
│   │   │
│   │   ├── llm_generators/
│   │   │   ├── reranker.py                 # LLM reranking orchestrator
│   │   │   ├── reranker_parser.py          # JSON parser + raw_content enricher
│   │   │   ├── reranker_prompt.py          # Reranker prompt builder
│   │   │   └── source_classifier.py        # URL-based source type classifier
│   │   │
│   │   ├── mindmap_feature/
│   │   │   ├── mindmap_generator.py        # Gemini mindmap generation
│   │   │   ├── mindmap_parser.py           # JSON → MindmapNodeSchema validator
│   │   │   ├── mindmap_prompt.py           # Mindmap prompt builder
│   │   │   └── retriever.py                # Retrieve chunks for mindmap
│   │   │
│   │   ├── summarization_engine/
│   │   │   ├── summarizer.py               # Summarization orchestrator
│   │   │   ├── summarization_prompt.py     # Summarization prompt builder
│   │   │   └── openai_client_dependency.py # Shared AsyncOpenAI client (DI)
│   │   │
│   │   ├── text_processing/
│   │   │   └── chunker.py                  # Semantic chunker (multilingual)
│   │   │
│   │   └── vector_store/
│   │       ├── embedder.py                 # HuggingFace embedding model loader
│   │       ├── filters.py                  # Deduplication by URL
│   │       ├── prepare_store_document.py   # Document preparation pipeline
│   │       ├── qdrant_client.py            # Sync QdrantClient + collection setup
│   │       ├── shared_retriever.py         # Shared scroll-based retriever
│   │       └── store.py                    # Ingestion entry point
│   │
│   ├── core/
│   │   ├── config.py                       # Pydantic BaseSettings
│   │   ├── constants.py                    # Global constants
│   │   ├── exceptions.py                   # Custom exception classes
│   │   ├── messages.py                     # Standardized response messages
│   │   └── mock_data.py                    # Static sample data for tests
│   │
│   ├── models/
│   │   ├── schemas.py                      # Pydantic schemas (Roadmap, Mindmap)
│   │   └── summarization_schemas.py        # Summarization request/response schemas
│   │
│   ├── routers/
│   │   ├── base.py                         # Root/welcome endpoint
│   │   ├── roadmap.py                      # Roadmap generation endpoints
│   │   ├── mindmap.py                      # Mindmap generation endpoints
│   │   └── summarization_router.py         # Summarization endpoints
│   │
│   ├── services/
│   │   └── main_backend_client.py          # HTTPX client for main backend
│   │
│   └── main.py                             # FastAPI app + startup/shutdown events
│
├── tests/
│   ├── mindmap/
│   │   ├── unit/test_mindmap_unit.py
│   │   └── integration/test_mindmap_integration.py
│   │
│   ├── roadmap/
│   │   ├── unit/
│   │   │   ├── test_reranker.py
│   │   │   ├── test_roadmap_router.py
│   │   │   ├── test_tavily_client.py
│   │   │   ├── test_vector_store_unit.py
│   │   │   ├── test_chunker.py
│   │   │   └── test_cleaned_tavily_data.py
│   │   │
│   │   └── integration/
│   │       ├── test_full_pipeline_integration.py
│   │       ├── test_chunker_integration.py
│   │       ├── test_reranker_integration.py
│   │       ├── test_tavily_integration.py
│   │       └── test_vector_store_integration.py
│   │
│   ├── summarization/
│   │   ├── unit/test_summarization_unit.py
│   │   └── integration/test_summarization_integration.py
│   │
│   └── test_config.py
│
├── docs/
│   ├── Roadmap_API_Contract.md
│   ├── Mindmap_API_Contract.md
│   ├── Summarization_API_contract.md
│   └── Qdrant_Schema.md
│
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| LLM | Google Gemini (via `google-genai` + OpenAI-compatible endpoint) |
| Vector DB | Qdrant (AsyncQdrantClient) |
| Embeddings | HuggingFace `paraphrase-multilingual-mpnet-base-v2` (768 dims) |
| Web Search | Tavily Python Client |
| HTTP Client | HTTPX |
| Text Splitting | LangChain SemanticChunker |
| Testing | Pytest + Pytest-Asyncio + Respx |
| Code Quality | Pre-commit, Black, Ruff |
| Database | PostgreSQL + SQLAlchemy (psycopg2) |

---

## Setup & Installation

### 1. Prerequisites

- Python 3.11+
- Docker (for Qdrant)

### 2. Clone the Repository

```bash
git clone <repo-url>
cd learning-services
```

### 3. Environment Setup

Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Create a `.env` file from the provided example:

```bash
cp .env.example .env
```

Fill in your keys:

```env
APP_NAME="Learning Services"
APP_VERSION="1.0.0"
MAIN_BACKEND_URL="http://localhost:3000"
TAVILY_API_KEY="your_tavily_key"
GEMINI_API_KEY="your_gemini_key"
QDRANT_URL="http://localhost:6333"
QDRANT_COLLECTION_NAME="learning_materials"
QUIZ_COLLECTION_NAME: str = "quiz_questions"
HF_TOKEN="your_huggingface_token"
```

### 4. Start Qdrant

```bash
docker-compose up -d
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Setup Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

---

## Running the Application

```bash
uvicorn src.main:app --reload
```

- API base: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Testing

Run all unit tests:

```bash
pytest -v -s
```

Run with live logs:

```bash
pytest -v -s --log-cli-level=INFO
```

Run integration tests (requires real API keys + running Qdrant):

```bash
pytest --integration -v -s --log-cli-level=INFO
```

Run a specific test file:

```bash
pytest tests/mindmap/unit/test_mindmap_unit.py -v
```

---

## Contribution Guidelines & Git Workflow

### 1. Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready code ΓÇö direct pushes **blocked** |
| `develop` | Integration branch ΓÇö all PRs target here |

**Feature branch naming:**

```
feat/feature-name     ΓåÆ feat/pdf-extraction
fix/bug-name          ΓåÆ fix/db-connection
chore/task-name       ΓåÆ chore/update-dependencies
docs/document-name    ΓåÆ docs/api-contracts
```

### 2. Commits

Use conventional commit messages:

```
Γ£à feat: add Tavily web search integration
Γ£à fix: handle empty pdf files during extraction
Γ£à chore: update requirements.txt
Γ¥î fixed bug
Γ¥î updated files
Γ¥î done
```

### 3. Pull Requests

- Direct pushes to `main` or `develop` are **blocked**
- Open a PR against `develop`
- Fill in the PR template
- Requires at least **1 approval** from the Team Lead
- All pre-commit checks and tests must pass

---

## License

This project is protected under a **Custom Educational & Contributor License**.

The source code is open for **personal learning and educational purposes only**. Commercial use, unauthorized redistribution, or use in production environments without explicit permission is strictly prohibited.

See the `LICENSE` file for full details.
