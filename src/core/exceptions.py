class FetchRoadmapContextError(Exception):
    pass


class TavilyCallingError(Exception):
    DEFAULT_MESSAGE = "There is an error at calling Tavily"


class MindmapContentNotFoundError(Exception):
    DEFAULT_MESSAGE = "No content found in vector store for the requested subtopic"