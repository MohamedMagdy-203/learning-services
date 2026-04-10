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


class PrimarySourceDistillationError(Exception):
    """raised when primary source distillation fails"""

    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Failed to distill primary source: {url}")


class NoDistilledContentError(Exception):
    """raised when all URLs fail to distill"""

    pass
