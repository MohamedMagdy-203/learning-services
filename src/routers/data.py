import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.config import Settings, get_settings
from src.services.main_backend_client import fetch_roadmap_context
from src.ai_engine.data_fetchers.cleaned_tavily_data import (
    fetch_and_clean_subtopic_content,
)
from src.core.exceptions import FetchRoadmapContextError, TavilyCallingError
from src.core.messages import FETCH_ROADMAP_CONTEXT_ERROR
from typing import Any

logger = logging.getLogger(__name__)

data_router = APIRouter(prefix="/api/v1/data", tags=["data"])


@data_router.get(
    "/roadmap-content/{user_id}/{subtopic_id}",
    summary="Fetch and process roadmap content for a subtopic",
    response_description="A list of cleaned and relevant sources for the given subtopic",
)
async def get_roadmap_content(
    user_id: str,
    subtopic_id: str,
    app_settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """
    Orchestrates the full data pipeline for a given user and subtopic:

    1. Fetches the roadmap context (user profile + subtopic details) from the main backend.
    2. Builds a targeted search query based on the user's profile.
    3. Fetches relevant content from the web via Tavily.
    4. Cleans and filters the raw content.
    5. Returns a structured list of sources ready for LLM processing.
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

    logger.info(
        "Roadmap content ready | user: %s | subtopic: %s | sources: %d",
        user_id,
        subtopic_id,
        len(cleaned_sources),
    )

    return {
        "user_id": user_id,
        "subtopic_id": subtopic_id,
        "subtopic_name": requested_data.target_subtopic_schema.Name,
        "total_sources": len(cleaned_sources),
        "sources": cleaned_sources,
    }
