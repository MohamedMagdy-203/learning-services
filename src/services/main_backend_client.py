import httpx
from src.core.config import Settings
from src.models.schemas import RoadmapGenerationRequest
from src.core.messages import (
    FETCH_ROADMAP_CONTEXT_SUCCESSFULLY,
    FETCH_ROADMAP_CONTEXT_ERROR,
)
from typing import Any
from src.core.exceptions import FetchRoadmapContextError


async def fetch_roadmap_context(
    user_id: str, subtopic_id: str, settings: Settings
) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            roadmap_context_request = await client.get(
                f"{settings.MAIN_BACKEND_URL}/api/internal/roadmap-context/{user_id}/{subtopic_id}"
            )
            roadmap_context_request.raise_for_status()
            roadmap_context = roadmap_context_request.json()
            validation_roadmap_context_data = RoadmapGenerationRequest(
                **roadmap_context
            )
            return {
                "roadmap_context": validation_roadmap_context_data,
                "status": FETCH_ROADMAP_CONTEXT_SUCCESSFULLY,
            }

        except httpx.HTTPError as exc:
            raise FetchRoadmapContextError(FETCH_ROADMAP_CONTEXT_ERROR) from exc
