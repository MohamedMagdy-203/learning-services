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
        """
        Initialize the exception for a failed primary-source distillation.
        
        Records the failing primary source URL on the exception instance and sets the exception message to include that URL.
        
        Parameters:
            url (str): The URL of the primary source that failed to be distilled.
        """
        self.url = url
        super().__init__(f"Failed to distill primary source: {url}")


class NoDistilledContentError(Exception):
    """raised when all URLs fail to distill"""

    pass
