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


INVALID_QUESTION_COUNT = "Cannot generate {num_questions} questions. Number of questions must be positive for source {source_url}."
EMPTY_SOURCE_CONTENT = "Source content for {source_url} is empty."
INVALID_JSON_FORMAT = "LLM response for {source_url} is not valid JSON."
NO_QUESTIONS_FOUND = "No questions found in LLM response for {source_url}."
VALIDATION_FAILED = "Question validation failed for subtopic {subtopic_id}."
LLM_API_ERROR = "LLM API error for {source_url}: {error}"
GENERATION_STARTED = "Starting question generation for subtopic {subtopic_id}."
GENERATION_COMPLETED = "Generated {count} questions for subtopic {subtopic_id}."
PROMPT_GENERATION_ERROR = "Error generating prompt for source {source_url}: {error}"
INVALID_JSON = "Invalid JSON returned from LLM"
SKIP_QUESTION = "Invalid question skipped: {e}"
FEWER_EXPECTED_QUESTIONS = "Generated fewer questions than expected"
QUIZ_GENERATED_SUCCESSFULLY = "Quiz generated successfully: {count} questions"
BANK_GENERATION_FAILED = "Failed to generate quiz bank"
