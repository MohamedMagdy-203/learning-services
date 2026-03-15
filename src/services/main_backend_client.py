import httpx
from src.core.config import Settings
from src.models.schemas import RoadmapGenerationRequest
from src.core.messages import (
    FETCH_ROADMAP_CONTEXT_ERROR,
)
from typing import Any
from src.core.exceptions import FetchRoadmapContextError
import logging

logger = logging.getLogger(__name__)


async def fetch_roadmap_context(
    user_id: str, subtopic_id: str, settings: Settings
) -> dict[str, Any]:
    logger.info(
        "Fetching roadmap context | user: %s | subtopic: %s", user_id, subtopic_id
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{settings.MAIN_BACKEND_URL}/api/internal/roadmap-context/{user_id}/{subtopic_id}"
            )
            response.raise_for_status()
            roadmap_context = response.json()
            validated_data = RoadmapGenerationRequest(**roadmap_context)

            logger.info("Roadmap context fetched successfully | user: %s", user_id)
            return {
                "roadmap_context": validated_data,
            }

        except httpx.HTTPError as exc:
            logger.exception(
                "HTTP error fetching roadmap context | user: %s | subtopic: %s | error: %s",
                user_id,
                subtopic_id,
                exc,
            )
            raise FetchRoadmapContextError(FETCH_ROADMAP_CONTEXT_ERROR) from exc
