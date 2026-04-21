class TavilyCallingError(Exception):
    DEFAULT_MESSAGE = "There is an error at calling Tavily"


class NoContentFoundError(Exception):
    """Custom exception raised when no content is found for a given query."""

    pass


class MindmapContentNotFoundError(Exception):
    DEFAULT_MESSAGE = "No content found in vector store for the requested subtopic"


class MindmapRetrievalError(Exception):
    DEFAULT_MESSAGE = "Failed to retrieve content from vector store"
