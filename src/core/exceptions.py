class TavilyCallingError(Exception):
    DEFAULT_MESSAGE = "There is an error at calling Tavily"


class NoContentFoundError(Exception):
    DEFAULT_MESSAGE = "No content found for the given URL"


class LLMGenerationError(Exception):
    DEFAULT_MESSAGE = "Error during LLM question generation"


class InvalidLLMResponseError(Exception):
    DEFAULT_MESSAGE = "LLM response is not in the expected format"


class MindmapContentNotFoundError(Exception):
    DEFAULT_MESSAGE = "No content found in vector store for the requested subtopic"


class MindmapRetrievalError(Exception):
    DEFAULT_MESSAGE = "Failed to retrieve content from vector store"
