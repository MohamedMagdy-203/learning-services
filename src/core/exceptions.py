class FetchRoadmapContextError(Exception):
    pass


class TavilyCallingError(Exception):
    DEFAULT_MESSAGE = "There is an error at calling Tavily"


class NoContentFoundError(Exception):
    """Custom exception raised when no content is found for a given query."""

    pass
