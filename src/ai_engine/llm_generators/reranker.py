import logging
from typing import Any
from google.genai import types  # type: ignore
from google import genai  # type: ignore
from src.models.schemas import RoadmapGenerationRequest
from src.ai_engine.llm_generators.reranker_prompt import build_reranker_prompt
from src.ai_engine.llm_generators.reranker_parser import (
    parse_reranker_response,
    enrich_with_raw_content,
)
from src.core.config import get_settings

logger = logging.getLogger(__name__)

_client: genai.Client | None = None  # type: ignore


def _get_client() -> genai.Client:  # type: ignore
    global _client
    if _client is None:
        _client = genai.Client(  # type: ignore
            api_key=get_settings().GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=1000000),  # type: ignore
        )
    return _client  # type: ignore


async def rerank_sources(
    requested_data: RoadmapGenerationRequest,
    cleaned_sources: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Orchestrates the LLM reranking pipeline:
    1. Builds the prompt from user profile + sources.
    2. Calls the LLM.
    3. Parses the JSON response.
    4. Enriches each picked source with its full raw_content.
    """
    if not cleaned_sources:
        logger.warning("No sources provided to reranker — returning empty result")
        return {"best_course": None, "best_video": None, "best_blog": None}

    sources_by_url: dict[str, dict[str, Any]] = {
        source["url"]: source for source in cleaned_sources
    }

    prompt = build_reranker_prompt(requested_data, cleaned_sources)

    logger.info(
        "Sending %d sources to LLM reranker | subtopic: %s",
        len(cleaned_sources),
        requested_data.target_subtopic_schema.Name,
    )

    response = await _get_client().aio.models.generate_content(  # type: ignore
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    try:
        result = parse_reranker_response(response.text)  # type: ignore
    except Exception as exc:
        logger.exception("Failed to parse LLM reranker response")
        raise ValueError("LLM returned an invalid response format") from exc

    result = enrich_with_raw_content(result, sources_by_url)

    logger.info(
        "LLM reranker done | course: %s | video: %s | blog: %s",
        (
            result.get("best_course", {}).get("title")
            if result.get("best_course")
            else "None"
        ),
        (
            result.get("best_video", {}).get("title")
            if result.get("best_video")
            else "None"
        ),
        result.get("best_blog", {}).get("title") if result.get("best_blog") else "None",
    )

    return result
