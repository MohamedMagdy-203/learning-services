# Learning Services API

## Table of Contents

- [Learning Services API](#learning-services-api)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [System Architecture \& Workflow](#system-architecture--workflow)
    - [Step-by-Step Flow Explanation](#step-by-step-flow-explanation)
  - [Project Structure](#project-structure)
  - [Tech Stack](#tech-stack)
  - [Setup \& Installation](#setup--installation)
    - [1. Prerequisites](#1-prerequisites)
    - [2. Clone the Repository](#2-clone-the-repository)
    - [3. Environment Setup](#3-environment-setup)
    - [4. Install Dependencies](#4-install-dependencies)
    - [5. Setup Pre-commit Hooks](#5-setup-pre-commit-hooks)
  - [Running the Application](#running-the-application)
  - [Testing](#testing)
  - [Contribution Guidelines \& Git Workflow](#contribution-guidelines--git-workflow)
    - [1. Branching Strategy](#1-branching-strategy)
    - [2. Commits](#2-commits)
    - [3. Pull Requests (PRs)](#3-pull-requests-prs)
  - [License](#license)

## Overview

The Learning Services API is an intelligent backend engine designed to
generate personalized educational roadmaps and learning materials. By
leveraging user profile data (such as learning styles, study time, and
goals) alongside specific target subtopics, the system dynamically
fetches, processes, and curates educational content. It utilizes
external tools like the Tavily API for web searching and integrates a
sophisticated Vector Database pipeline for processing and generating
quizzes, mindmaps, and summaries.

## System Architecture & Workflow

Below is the high-level data flow of the Learning Services AI Engine:

![System Architecture Flowchart](![alt text](Project_Flow_Diagram.png))

### Step-by-Step Flow Explanation

1. **Input Collection:** The system takes "Sign up preferences" (user
    tracks, learning style) and the "Target Subtopic" (name,
    description, difficulty).
2. **Web Search & Extraction:** A query is dynamically built and sent
    to the Tavily web search tool to fetch relevant articles, courses
    (Coursera, Udemy), and YouTube videos. The content is then extracted
    and cleaned (removing HTML tags, boilerplate text, and URLs).
3. **LLM Reranker / Judge:** The extracted content is evaluated by a
    Large Language Model (LLM) to determine its relevance and quality.
    The best sources are stored in the database and presented in the
    user's roadmap.
4. **Vector Database Pipeline:** When a user selects a specific content
    source, the system fetches the raw data (via PDF extraction, web
    scraping, or video transcript extraction). The text is cleaned,
    chunked into smaller pieces, converted into embeddings, and stored
    in a Vector Database.
5. **Content Generation:** The user can request specific outputs like a
    Quiz, Mindmap, or Summary. The system uses an LLM to reformulate the
    query, searches the Vector Database for the top K relevant chunks,
    and feeds them into another LLM to generate the final educational
    material, which is then stored in the database.

## Project Structure

The codebase is organized modularly to separate API routing, core configurations, data models, and the AI engine logic:

```text
learning-services/
├── src/
│   ├── ai_engine/                   # Core logic for data fetching, processing, and LLMs
│   │   ├── data_fetchers/           # Modules for retrieving and cleaning external data
│   │   │   ├── __init__.py
│   │   │   ├── cleaned_tavily_data.py # Pipeline orchestrator to fetch and clean subtopic content
│   │   │   ├── data_cleaner.py      # Regex-based text sanitization (removes HTML, boilerplate, URLs)
│   │   │   ├── query_builder.py     # Logic to construct targeted search queries based on user profile
│   │   │   └── tavily_client.py     # Async client wrapper for Tavily web search API
│   │   ├── llm_generators/          # Handlers for prompt building and Large Language Model calls
│   │   │   └── __init__.py
│   │   ├── text_processing/         # Logic for splitting text into manageable chunks and embeddings
│   │   │   └── __init__.py
│   │   └── vector_store/            # Database operations for storing and querying vector embeddings
│   │       └── __init__.py
│   ├── core/                        # Application-wide settings, utilities, and constants
│   │   ├── __init__.py
│   │   ├── config.py                # Pydantic BaseSettings for environment variables validation
│   │   ├── constants.py             # Global constant values used across the application
│   │   ├── exceptions.py            # Custom exception classes (e.g., TavilyCallingError)
│   │   ├── messages.py              # Standardized string messages for API responses
│   │   └── mock_data.py             # Static sample data used for testing and development fallback
│   ├── models/                      # Data structures and validation models
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic schemas (UserProfileSchema, TargetSubtopicSchema)
│   ├── routers/                     # FastAPI route definitions and controllers
│   │   ├── __init__.py
│   │   ├── base.py                  # Base router including the root/welcome API endpoint
│   │   └── data.py                  # Endpoints for data retrieval and processing requests
│   ├── services/                    # Clients for communicating with internal/external microservices
│   │   ├── __init__.py
│   │   └── main_backend_client.py   # HTTPX client to fetch roadmap context from the main backend
│   ├── __init__.py
│   └── main.py                      # FastAPI application instance and entry point
├── tests/                           # Automated testing suite (Unit & Integration tests)
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration and custom CLI options (e.g., --integration)
│   ├── test_cleaned_tavily_data.py  # Tests for the data fetching and cleaning pipeline
│   ├── test_config.py               # Unit tests verifying application configuration loading
│   ├── test_main_backend_client.py  # Mocked tests verifying the main backend HTTP client
│   ├── test_tavily_client.py        # Unit tests for Tavily API interactions (with mocked responses)
│   └── test_tavily_integration.py   # Real API integration tests verifying live Tavily web searches
├── .env.example                     # Template showing required environment variables
├── .gitignore                       # List of files and folders to be ignored by Git version control
├── .pre-commit-config.yaml          # Configuration for code formatting and linting hooks (Black, Ruff)
├── README.md                        # Main project documentation and contribution guidelines
└── requirements.txt                 # List of project Python dependencies and versions
```

## Tech Stack

- **Framework:** FastAPI
- **Validation:** Pydantic
- **Database / ORM:** SQLAlchemy, PostgreSQL (psycopg2-binary)
- **HTTP Client:** HTTPX
- **AI & Search:** Tavily Python Client, Tiktoken
- **Testing:** Pytest, Respx, Pytest-Asyncio
- **Code Quality:** Pre-commit, Black, Ruff

## Setup & Installation

### 1. Prerequisites

Ensure you have Python installed. It is highly recommended to use a
virtual environment to manage dependencies.

### 2. Clone the Repository

Clone the project to your local machine and navigate into the project
directory.

### 3. Environment Setup

Create a virtual environment and activate it:

``` bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

Create a `.env` file in the root directory based on the provided
example:

``` env
APP_NAME="Learning Services"
APP_VERSION="1.0.0"
MAIN_BACKEND_URL="http://localhost:3000"
TAVILY_API_KEY="Your Tavily api key"
```

### 4. Install Dependencies

Install the required Python packages from the requirements file:

``` bash
pip install -r requirements.txt
```

### 5. Setup Pre-commit Hooks

To ensure code quality, install the pre-commit hooks before making any
contributions:

``` bash
pip install pre-commit
pre-commit install
```

## Running the Application

To start the FastAPI development server, run:

``` bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`. You can view the
automatic API documentation by navigating to
`http://localhost:8000/docs`.

## Testing

The project uses `pytest` for testing.

To run all standard unit tests:

``` bash
pytest
```

To run integration tests (which make actual calls to external APIs like
Tavily), use the custom integration flag:

``` bash
pytest --integration
```

## Contribution Guidelines & Git Workflow

To maintain high code quality and avoid merge conflicts, all team
members **MUST** strictly follow these rules:

### 1. Branching Strategy

- **`main`**: Production-ready code ONLY. Direct pushes are blocked.
- **`develop`**: The integration branch. All feature branches must
    branch off from here and merge back here.

**Feature Branches Naming Convention:**

- `feat/feature-name` (e.g., `feat/pdf-extraction`)
- `fix/bug-name` (e.g., `fix/db-connection`)
- `chore/task-name` (e.g., `chore/update-dependencies`)
- `docs/document-name` (e.g., `docs/api-endpoints`)

### 2. Commits

Use descriptive, conventional commit messages:

- **Allowed:** `feat: add Tavily web search integration`
- **Allowed:** `fix: handle empty pdf files during extraction`
- **Allowed:** `chore: update requirements.txt`
- **Not Allowed:** `fixed bug` or `updated files` or `done`

### 3. Pull Requests (PRs)

- **Direct pushes to `main` or `develop` are BLOCKED.**
- Push your feature branch to GitHub and open a Pull Request against
    the `develop` branch.
- Fill out the provided PR Template.
- Wait for at least **1 Approval** (from the Team Lead) before
    merging.
- Ensure your code doesn't break existing functionality before
    requesting a review.

## License

MIT License

Copyright (c) 2026 Learning Services Team
