WELCOME_MESSAGE = "Welcome to Learning Services API"
SERVER_RUNNING_SUCCESSFULLY = "The server is running successfully"
FETCH_ROADMAP_CONTEXT_ERROR = "Failed to fetch roadmap context"


# Logging
RETRIEVE_CHUNKS_START = "Attempting to retrieve chunks for URL: %s"
RETRIEVE_CHUNKS_SUCCESS = "Retrieved %d chunks for URL: %s"
RETRIEVE_CHUNKS_ERROR = "Error retrieving chunks from Qdrant for URL %s: %s"

# Errors
NO_CONTENT_FOUND = "No content found for URL: {url}"
QDRANT_RETRIEVE_FAILED = "Failed to retrieve chunks from Qdrant: {error}"

# Summarization Logs
SUMMARIZATION_START = "Starting summarization for URL: %s"
SUMMARIZATION_INVOKE_LLM = "Invoking LLM for summarization..."
SUMMARIZATION_SUCCESS = "Summary generated successfully."

# Retrieval Logs
RETRIEVE_ERROR = "Error retrieving chunks for URL %s: %s"
NO_CONTENT_WARNING = "No content found for URL: %s"

# LLM Errors
LLM_INVOCATION_ERROR = "Error during LLM invocation: %s"

# API Responses
NO_CONTENT_RESPONSE = "No content found to summarize."
RETRIEVE_FAILED_RESPONSE = "Failed to retrieve content for summarization."
LLM_FAILED_RESPONSE = " LLM Failed to generate summary"

AI_INVALID_JSON = "AI failed to return valid JSON: %s"
AI_MISSING_SUMMARY = "AI response missing 'summary' field or empty: %s"
