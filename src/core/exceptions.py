class FetchRoadmapContextError(Exception):
    pass


class TavilyCallingError(Exception):
    DEFAULT_MESSAGE = "There is an error at calling Tavily"
class NoContentFoundError(Exception):
    """Raised when no content is found for a given URL."""
    pass

class DistillationError(Exception):
    """Raised when LLM fails to distill content."""
    pass
