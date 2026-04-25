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
FALLBACK_ATTEMPT_FAILED = "Fallback attempt {attempt} failed: {error}"
NO_PRIMARY_DOCUMENTS_FOUND = "No primary documents found."


# Bank Questions
PRIMARY_URL_NOT_IN_URLS = "primary_url must be included in urls"
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
SECONDARY_SOURCE_FAILED = "Secondary source {index} failed: {error}"
LESS_THAN_TWO_SECONDARY = "Less than 2 secondary docs received"
INVALID_QUESTION_COUNT = (
    "Invalid number of questions ({num_questions}) requested for source: {source_url}. "
)

UNABLE_TO_REACH_TARGET = (
    "Unable to reach target question count. "
    "Generated only {current} out of {target} unique questions."
)
FALLBACK_ROUND_LOG = "Fallback round {round}: generating {batch} questions"

# Adaptive Engine
STOPPING_QUIZ = "Stopping quiz. Reason: {reason}"
NO_MORE_QUESTIONS = "No more questions. Ending quiz."


NO_QUESTIONS_AVAILABLE = "No questions available in this bank"
REQUIRED_IDS = "bank_id and user_id are required"
AI_QUESTION_GENERATION_FAILED = (
    "Failed to generate questions from AI engine. Please try again."
)
AI_INSUFFICIENT_URL_CONTENT = (
    "The provided URLs do not contain enough content to generate questions."
)


# Logging
RETRIEVE_CHUNKS_START = "Attempting to retrieve chunks for URL: %s"
RETRIEVE_CHUNKS_SUCCESS = "Retrieved %d chunks for URL: %s"
RETRIEVE_CHUNKS_ERROR = "Error retrieving chunks from Qdrant for URL %s: %s"

# Errors

QDRANT_RETRIEVE_FAILED = "Failed to retrieve chunks from Qdrant: {error}"

# Summarization Logs
SUMMARIZATION_START = "Starting summarization for URL: %s"
SUMMARIZATION_INVOKE_LLM = "Invoking LLM for summarization..."
SUMMARIZATION_SUCCESS = "Summary generated successfully."

# Retrieval Logs
RETRIEVE_ERROR = "Error retrieving chunks for URL %s: %s"


# LLM Errors
LLM_INVOCATION_ERROR = "Error during LLM invocation: %s"

# API Responses
NO_CONTENT_RESPONSE = "No content found to summarize."
RETRIEVE_FAILED_RESPONSE = "Failed to retrieve content for summarization."
LLM_FAILED_RESPONSE = "LLM failed to generate summary"

AI_INVALID_JSON = "AI failed to return valid JSON: %s"
AI_MISSING_SUMMARY = "AI response missing 'summary' field or empty: %s"
MINDMAP_CONTENT_NOT_FOUND_ERROR = (
    "No content found in vector store for this subtopic. "
    "Please ensure the sources are ingested first."
)

MINDMAP_RETRIEVAL_ERROR = "Failed to retrieve content. Please try again later."
