import logging
import asyncio
from typing import Dict, Any
from tavily import AsyncTavilyClient  # type: ignore
from src.core.config import Settings
from src.models.schemas import RoadmapGenerationRequest
from src.ai_engine.data_fetchers.query_builder import query_builder
from src.core.exceptions import TavilyCallingError
from src.ai_engine.data_fetchers.youtube_client import fetch_video_transcript

logger = logging.getLogger(__name__)


async def process_search_result(result: Dict[str, Any]) -> Dict[str, str]:
    url = result.get("url", "")
    title = result.get("title", "")
    raw_content = result.get("raw_content", "")

    if "youtube.com" in url or "youtu.be" in url:
        youtube_content = await fetch_video_transcript(url)
        if youtube_content:
            raw_content = youtube_content
        else:
            raw_content = "Transcript not available for this video."

    return {"title": title, "url": url, "raw_content": raw_content}


async def fetch_subtopic_content(
    settings: Settings, requested_data: RoadmapGenerationRequest
) -> Dict[str, Any]:
    search_string = ""
    try:
        search_string = query_builder(requested_data)
        logger.info("Tavily search started | query: %s", search_string)

        tavily_client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
        tavily_response: Dict[str, Any] = await tavily_client.search(  # type: ignore
            query=search_string, include_raw_content=True, timeout=10.0
        )

        tasks = [
            process_search_result(result)
            for result in tavily_response.get("results", [])
        ]

        results_list = await asyncio.gather(*tasks)

        logger.info("Tavily search done | sources processed: %d", len(results_list))
        return {"results": list(results_list)}

    except Exception as exc:
        logger.exception("Tavily call failed | query: %s", search_string)
        raise TavilyCallingError(TavilyCallingError.DEFAULT_MESSAGE) from exc
