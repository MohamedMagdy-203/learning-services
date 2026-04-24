class TavilyCallingError(Exception):
    DEFAULT_MESSAGE = "There is an error at calling Tavily"


class NoContentFoundError(Exception):
    """Raised when no content is found for a given URL."""

    pass


class LLMGenerationError(Exception):
    """Exception raised when there's an error during LLM question generation."""

    pass


class InvalidLLMResponseError(Exception):
    """Exception raised when the LLM response is not in the expected format."""

    pass


class MindmapContentNotFoundError(Exception):
    DEFAULT_MESSAGE = "No content found in vector store for the requested subtopic"


class MindmapRetrievalError(Exception):
    DEFAULT_MESSAGE = "Failed to retrieve content from vector store"
