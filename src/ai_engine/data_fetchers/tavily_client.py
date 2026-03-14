from src.core.config import Settings
from src.models.schemas import RoadmapGenerationRequest
from src.ai_engine.data_fetchers.query_builder import query_builder
from tavily import AsyncTavilyClient  # type: ignore
from typing import Dict, Any, List
from src.core.exceptions import TavilyCallingError
from src.core.messages import TAVILY_CALLING_ERROR, TAVILY_CALLING_SUCCESSFULLY


async def fetch_subtopic_content(
    settings: Settings, requested_data: RoadmapGenerationRequest
) -> Dict[str, Any]:
    try:
        search_string = query_builder(requested_data)
        content: str = ""
        sources: List[Dict[str, str]] = []
        tavily_client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
        tavily_response: Dict[str, Any] = await tavily_client.search(
            query=search_string, include_raw_content=True
        )  # type: ignore

        for result in tavily_response.get("results", []):
            content += (result.get("raw_content") or "") + "\n\n"
            sources.append({"title": result.get("title"), "url": result.get("url")})
        return {
            "status": TAVILY_CALLING_SUCCESSFULLY,
            "content": content,
            "sources": sources,
        }
    except Exception as exc:
        raise TavilyCallingError(TAVILY_CALLING_ERROR) from exc
