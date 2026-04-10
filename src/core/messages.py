WELCOME_MESSAGE = "Welcome to Learning Services API"
SERVER_RUNNING_SUCCESSFULLY = "The server is running successfully"
FETCH_ROADMAP_CONTEXT_ERROR = "Failed to fetch roadmap context"

NO_CONTENT_FOUND = "No content found for this URL."
DISTILLATION_JSON_ERROR = "Failed to parse LLM response as JSON"
DISTILLATION_GENERAL_ERROR = "Failed to distill content"
CONTENT_TRUNCATED_NOTE = "Content truncated to stay within context limits for the LLM."
CONTENT_TRUNCATED_SYSTEM_NOTE = "\n\n[SYSTEM NOTE: The content was truncated due to length limits. Please distill based on the available text above.]"
PRIMARY_SOURCE_REQUIRED_ERROR = "Critical Error: The primary source ({url}) is required for question generation but failed to distill."
NO_CONTENT_DISTILLED_ERROR = (
    "Failed to distill any of the provided content URLs. Please check your sources."
)
