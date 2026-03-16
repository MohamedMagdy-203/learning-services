import logging
import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from tavily import AsyncTavilyClient  # type: ignore
from src.core.config import Settings
from src.models.schemas import RoadmapGenerationRequest
from src.ai_engine.data_fetchers.query_builder import query_builder
from src.core.exceptions import TavilyCallingError

logger = logging.getLogger(__name__)


async def _tavily_search(client: Any, **kwargs: Any) -> list[Dict[str, Any]]:
    response: Dict[str, Any] = await client.search(**kwargs)
    results: list[Dict[str, Any]] = response.get("results", [])
    return results


async def process_search_result(result: Dict[str, Any]) -> Optional[Dict[str, str]]:
    url: str = result.get("url") or ""
    title: str = result.get("title") or ""
    raw_content: str = result.get("raw_content") or ""

    if not raw_content or len(raw_content) < 50:
        logger.info("Filtered out result with empty or short content: %s", url)
        return None

    return {"title": title, "url": url, "raw_content": raw_content}


async def fetch_subtopic_content(
    settings: Settings, requested_data: RoadmapGenerationRequest
) -> Dict[str, Any]:
    search_string = ""
    try:
        search_string = query_builder(requested_data)
        if len(search_string) > 400:
            search_string = search_string[:395] + "..."

        logger.info("Tavily search started | query: %s", search_string)

        client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)

        general_results, course_results, youtube_results = await asyncio.gather(
            _tavily_search(
                client,
                query=search_string,
                include_raw_content=True,
                max_results=7,
            ),
            _tavily_search(
                client,
                query=search_string,
                include_raw_content=True,
                max_results=5,
                include_domains=["coursera.org", "udemy.com"],
            ),
            _tavily_search(
                client,
                query=search_string,
                include_raw_content=True,
                max_results=5,
                include_domains=["youtube.com"],
            ),
        )

        all_results: list[Dict[str, Any]] = (
            general_results + course_results + youtube_results
        )

        tasks = [process_search_result(result) for result in all_results]
        results_list = await asyncio.gather(*tasks)
        valid_results: list[Dict[str, str]] = [
            res for res in results_list if res is not None
        ]

        seen_content: set[str] = set()
        unique_results: list[Dict[str, str]] = []
        for r in valid_results:
            parsed = urlparse(r["url"])
            fingerprint = parsed.netloc + parsed.path
            if fingerprint not in seen_content:
                seen_content.add(fingerprint)
                unique_results.append(r)

        logger.info(
            "Tavily search done | valid sources processed: %d", len(unique_results)
        )
        return {"results": unique_results}

    except Exception as exc:
        logger.exception("Tavily call failed | query: %s", search_string)
        raise TavilyCallingError(TavilyCallingError.DEFAULT_MESSAGE) from exc
