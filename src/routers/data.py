import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.config import Settings, get_settings
from src.services.main_backend_client import fetch_roadmap_context
from src.ai_engine.data_fetchers.cleaned_tavily_data import (
    fetch_and_clean_subtopic_content,
)
from src.ai_engine.llm_generators.reranker import rerank_sources
from src.core.exceptions import FetchRoadmapContextError, TavilyCallingError
from src.core.messages import FETCH_ROADMAP_CONTEXT_ERROR
from src.models.schemas import RankedSourceSchema, RoadmapRankedResultSchema

logger = logging.getLogger(__name__)

data_router = APIRouter(prefix="/api/v1/data", tags=["data"])


@data_router.get(
    "/roadmap-content/{user_id}/{subtopic_id}",
    summary="Fetch, clean, and rank learning content for a subtopic",
    response_model=RoadmapRankedResultSchema,
)
async def get_roadmap_content(
    user_id: str,
    subtopic_id: str,
    app_settings: Settings = Depends(get_settings),
) -> RoadmapRankedResultSchema:
    """
    Full pipeline:
    1. Fetch roadmap context (user profile + subtopic) from main backend.
    2. Build a targeted search query and fetch content via Tavily.
    3. Clean and filter raw content.
    4. Send sources + user profile to LLM reranker.
    5. Return the best course, video, and blog for this learner.
    """
    logger.info(
        "Roadmap content request received | user: %s | subtopic: %s",
        user_id,
        subtopic_id,
    )

    try:
        context = await fetch_roadmap_context(
            user_id=user_id,
            subtopic_id=subtopic_id,
            settings=app_settings,
        )
    except FetchRoadmapContextError:
        logger.error(
            "Failed to fetch roadmap context | user: %s | subtopic: %s",
            user_id,
            subtopic_id,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=FETCH_ROADMAP_CONTEXT_ERROR,
        )

    requested_data = context["roadmap_context"]

    try:
        cleaned_sources = await fetch_and_clean_subtopic_content(
            settings=app_settings,
            requested_data=requested_data,
        )
    except TavilyCallingError:
        logger.error(
            "Tavily search failed | user: %s | subtopic: %s",
            user_id,
            subtopic_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to fetch learning content. Please try again later.",
        )

    try:
        ranked_results = await rerank_sources(
            requested_data=requested_data,
            cleaned_sources=cleaned_sources,
        )
    except ValueError:
        logger.error(
            "LLM reranker failed | user: %s | subtopic: %s",
            user_id,
            subtopic_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rank learning content. Please try again later.",
        )

    logger.info(
        "Roadmap content pipeline complete | user: %s | subtopic: %s",
        user_id,
        subtopic_id,
    )

    return RoadmapRankedResultSchema(
        user_id=user_id,
        subtopic_id=subtopic_id,
        best_course=(
            RankedSourceSchema(**ranked_results["best_course"])
            if ranked_results.get("best_course")
            else None
        ),
        best_video=(
            RankedSourceSchema(**ranked_results["best_video"])
            if ranked_results.get("best_video")
            else None
        ),
        best_blog=(
            RankedSourceSchema(**ranked_results["best_blog"])
            if ranked_results.get("best_blog")
            else None
        ),
    )
