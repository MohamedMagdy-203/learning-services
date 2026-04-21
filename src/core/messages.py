WELCOME_MESSAGE = "Welcome to Learning Services API"
SERVER_RUNNING_SUCCESSFULLY = "The server is running successfully"
FETCH_ROADMAP_CONTEXT_ERROR = "Failed to fetch roadmap context"


# Retrieval
RETRIEVE_CHUNKS_START = "Starting chunk retrieval for URL: %s"
RETRIEVE_CHUNKS_SUCCESS = "Retrieved %s chunks for URL: %s"
NO_CONTENT_FOUND = "No content found for URL: {url}"
RETRIEVE_CHUNKS_ERROR = "Error retrieving chunks for URL: %s | Error: %s"
QDRANT_RETRIEVE_FAILED = "Failed to retrieve data from Qdrant: {error}"
RETRIEVE_MULTI_URL_START = "Starting multi-url chunk retrieval for URLs: %s"
RETRIEVE_MULTI_URL_SKIP_URL = "Skipping failed URL: %s | Reason: %s"
NO_CONTENT_FOUND_PRIMARY = "No content found for primary URL: {primary_url}"
NO_CONTENT_FOUND_ALL = "No content found for any provided URLs"
RETRIEVE_MULTI_URL_SUCCESS = "Multi-url retrieval success. Total documents: %s"


# Bank Questions

EMPTY_SOURCE_CONTENT = "Source content is empty."
NO_QUESTIONS_FOUND = "No questions found in LLM response for {source_url}."
LLM_API_ERROR = "LLM API error for {source_url}: {error}"
GENERATION_STARTED = "Starting question generation for subtopic {subtopic_id}."
SKIP_QUESTION = "Invalid question skipped: {error}"
QUIZ_GENERATED_SUCCESSFULLY = "Quiz generated successfully: {count} questions"
BANK_GENERATION_FAILED = (
    "Failed to generate quiz bank for subtopic {subtopic_id}: {error}"
)
FALLBACK_TRIGGERED = "Fallback triggered: {missing} missing"
INVALID_JSON = "Invalid JSON from LLM, retrying..."
LLM_TIMEOUT = "LLM timeout (attempt {attempt})"
LLM_RETRY_ERROR = "LLM error (attempt {attempt}): {error}"
SECONDARY_SOURCE_FAILED = "Secondary source {index} failed: {error}"
LESS_THAN_TWO_SECONDARY = "Less than 2 secondary docs received"
INVALID_QUESTION_COUNT = (
    "Invalid number of questions ({num_questions}) requested for source: {source_url}. "
)
