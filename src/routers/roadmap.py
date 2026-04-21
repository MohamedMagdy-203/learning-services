import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from src.core.config import Settings, get_settings
from src.ai_engine.data_fetchers.cleaned_tavily_data import (
    fetch_and_clean_subtopic_content,
)
from src.ai_engine.llm_generators.reranker import rerank_sources
from src.core.exceptions import TavilyCallingError
from src.models.schemas import (
    RankedSourceSchema,
    RoadmapRankedResultSchema,
    RoadmapGenerationRequest,
)
from src.ai_engine.vector_store.store import ingest_reranker_results

logger = logging.getLogger(__name__)

roadmap_router = APIRouter(prefix="/api/v1/roadmap", tags=["roadmap"])


async def _ingest_with_logging(data: dict) -> None:  # type: ignore
    try:
        await ingest_reranker_results(data)  # type: ignore
    except Exception:
        logger.exception(
            "Background ingestion failed | user: %s | subtopic: %s",
            data.get("user_id"),  # type: ignore
            data.get("subtopic_id"),  # type: ignore
        )


@roadmap_router.post(
    "/generate",
    summary="Fetch, clean, and rank learning content for a subtopic",
    response_model=RoadmapRankedResultSchema,
)
async def generate_roadmap_endpoint(
    request: RoadmapGenerationRequest,
    background_tasks: BackgroundTasks,
    app_settings: Settings = Depends(get_settings),
) -> RoadmapRankedResultSchema:
    """
    Full pipeline:
    1. Receive roadmap context (user profile + subtopic) directly from main backend via POST body.
    2. Build a targeted search query and fetch content via Tavily.
    3. Clean and filter raw content.
    4. Send sources + user profile to LLM reranker.
    5. Save the ranked content to Qdrant (in background).
    6. Return the best course, video, and blog for this learner.
    """
    user_id = request.user_profile_schema.id
    subtopic_id = request.target_subtopic_schema.Subtopic_id

    logger.info(
        "Roadmap content request received | user: %s | subtopic: %s",
        user_id,
        subtopic_id,
    )

    # 1. Tavily Search & Cleaning
    try:
        cleaned_sources = await fetch_and_clean_subtopic_content(
            settings=app_settings,
            requested_data=request,
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

    # 2. LLM Reranking
    try:
        ranked_results = await rerank_sources(
            requested_data=request,
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

    # 3. Background Ingestion (Qdrant)
    data_to_ingest = {
        "user_id": user_id,
        "subtopic_id": subtopic_id,
        "best_course": ranked_results.get("best_course"),
        "best_video": ranked_results.get("best_video"),
        "best_blog": ranked_results.get("best_blog"),
    }

    background_tasks.add_task(_ingest_with_logging, data_to_ingest)

    # 4. Return Final Results
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
