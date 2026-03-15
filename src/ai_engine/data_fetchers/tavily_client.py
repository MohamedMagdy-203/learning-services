from src.core.config import Settings
from src.models.schemas import RoadmapGenerationRequest
from src.ai_engine.data_fetchers.query_builder import query_builder
from tavily import AsyncTavilyClient  # type: ignore
from typing import Dict, Any, List
from src.core.exceptions import TavilyCallingError
import logging

logger = logging.getLogger(__name__)


async def fetch_subtopic_content(
    settings: Settings, requested_data: RoadmapGenerationRequest
) -> Dict[str, Any]:
    try:
        search_string = query_builder(requested_data)
        logger.info("Tavily search started | query: %s", search_string)

        content: str = ""
        sources: List[Dict[str, str]] = []
        tavily_client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
        tavily_response: Dict[str, Any] = await tavily_client.search(  # type: ignore
            query=search_string, include_raw_content=True, timeout=10.0
        )

        for result in tavily_response.get("results", []):
            content += (result.get("raw_content") or "") + "\n\n"
            sources.append({"title": result.get("title"), "url": result.get("url")})

        logger.info("Tavily search done | sources found: %d", len(sources))
        return {
            "content": content,
            "sources": sources,
        }
    except Exception as exc:
        logger.exception("Tavily call failed | query: %s", search_string)  # type: ignore
        raise TavilyCallingError(TavilyCallingError.DEFAULT_MESSAGE) from exc
