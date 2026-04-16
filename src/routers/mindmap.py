import logging
from fastapi import APIRouter, HTTPException, status, Depends
from qdrant_client import QdrantClient

from src.core.config import get_settings, Settings
from src.core.exceptions import MindmapContentNotFoundError, MindmapRetrievalError
from src.core.messages import MINDMAP_CONTENT_NOT_FOUND_ERROR, MINDMAP_RETRIEVAL_ERROR
from src.models.schemas import MindmapGenerationRequest, MindmapResponseSchema
from src.ai_engine.vector_store.qdrant_client import get_qdrant_client
from src.ai_engine.mindmap_feature.retriever import retrieve_all_chunks_for_mindmap
from src.ai_engine.mindmap_feature.mindmap_generator import generate_mindmap

logger = logging.getLogger(__name__)

mindmap_router = APIRouter(prefix="/api/v1/mindmap", tags=["mindmap"])


@mindmap_router.post(
    "/generate",
    summary="Generate a mind map from stored content for a subtopic",
    response_model=MindmapResponseSchema,
)
async def generate_mindmap_endpoint(
    request: MindmapGenerationRequest,
    client: QdrantClient = Depends(get_qdrant_client),
    settings: Settings = Depends(get_settings),
) -> MindmapResponseSchema:
    """
    Full pipeline:
    1. Fetch all stored chunks from Qdrant for the primary source URL.
    2. Build a structured prompt from chunks + subtopic context + weaknesses.
    3. Call Gemini to generate the mind map.
    4. Parse and validate the LLM output.
    5. Return the structured mind map.

    The Main Backend sends all required context (subtopic info, weaknesses,
    and the primary URL) directly in the request body.
    """
    logger.info(
        "Mindmap request received | user: %s | subtopic: %s | url: %s",
        request.user_id,
        request.subtopic_id,
        request.primary_url,
    )

    try:
        chunks = await retrieve_all_chunks_for_mindmap(
            request=request, client=client, settings=settings
        )
    except MindmapContentNotFoundError:
        logger.error(
            "No content found in Qdrant | user: %s | subtopic: %s",
            request.user_id,
            request.subtopic_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MINDMAP_CONTENT_NOT_FOUND_ERROR,
        )
    except MindmapRetrievalError:
        logger.error(
            "Qdrant retrieval failed | user: %s | subtopic: %s",
            request.user_id,
            request.subtopic_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=MINDMAP_RETRIEVAL_ERROR,
        )

    logger.info(
        "Chunks ready | user: %s | subtopic: %s | total chunks: %d",
        request.user_id,
        request.subtopic_id,
        len(chunks),
    )

    try:
        mindmap = await generate_mindmap(request=request, chunks=chunks)
    except ValueError as exc:
        logger.error(
            "Gemini returned invalid response | user: %s | subtopic: %s | error: %s",
            request.user_id,
            request.subtopic_id,
            str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate mind map. Please try again later.",
        ) from exc
    except Exception as exc:
        logger.exception(
            "Gemini generation failed unexpectedly | user: %s | subtopic: %s",
            request.user_id,
            request.subtopic_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate mind map. Please try again later.",
        ) from exc

    logger.info(
        "Mindmap generated successfully | user: %s | subtopic: %s",
        request.user_id,
        request.subtopic_id,
    )

    return MindmapResponseSchema(
        user_id=request.user_id,
        subtopic_id=request.subtopic_id,
        mindmap=mindmap,
    )
