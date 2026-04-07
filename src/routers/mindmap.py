import logging
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.config import Settings, get_settings
from src.core.exceptions import FetchRoadmapContextError
from src.core.messages import FETCH_ROADMAP_CONTEXT_ERROR
from src.models.schemas import MindmapGenerationRequest, MindmapResponseSchema
from src.services.main_backend_client import fetch_roadmap_context

logger = logging.getLogger(__name__)

mindmap_router = APIRouter(prefix="/api/v1/mindmap", tags=["mindmap"])


@mindmap_router.post(
    "/",
    summary="Generate a mind map for a specific content source",
    response_model=MindmapResponseSchema,
)
async def generate_mindmap(
    request: MindmapGenerationRequest,
    app_settings: Settings = Depends(get_settings),
) -> MindmapResponseSchema:
    """
    Full pipeline:
    1. Fetch roadmap context (user profile + subtopic) from main backend.
    2. Search Qdrant for top-K chunks filtered by source URL.
    3. Build prompt from chunks + user profile.
    4. Call Gemini to generate the mind map.
    5. Parse and validate the LLM output.
    6. Return the structured mind map.
    """
    logger.info(
        "Mindmap generation request received | user: %s | subtopic: %s | source: %s",
        request.user_id,
        request.subtopic_id,
        request.source_type,
    )

    try:
        context = await fetch_roadmap_context(
            user_id=request.user_id,
            subtopic_id=request.subtopic_id,
            settings=app_settings,
        )
    except FetchRoadmapContextError:
        logger.error(
            "Failed to fetch roadmap context | user: %s | subtopic: %s",
            request.user_id,
            request.subtopic_id,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=FETCH_ROADMAP_CONTEXT_ERROR,
        )

    _requested_data = context["roadmap_context"]

    logger.info(
        "Roadmap context fetched successfully | user: %s | subtopic: %s",
        request.user_id,
        request.subtopic_id,
    )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Mindmap generation not fully implemented yet.",
    )