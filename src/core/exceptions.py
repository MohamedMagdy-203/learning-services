class FetchRoadmapContextError(Exception):
    pass


class TavilyCallingError(Exception):
    DEFAULT_MESSAGE = "There is an error at calling Tavily"
