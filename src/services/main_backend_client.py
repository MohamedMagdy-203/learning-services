import httpx
from src.core.config import get_settings
from src.models.schemas import RoadmapGenerationRequest
from src.core.messages import (
    FETCH_ROADMAP_CONTEXT_SUCCESSFULY,
    FETCH_ROADMAP_CONTEXT_ERROR,
)
from typing import Any

settings = get_settings()


async def fetch_roadmap_context(user_id: str, subtopic_id: str) -> dict[str, Any] | str:
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
                "status": FETCH_ROADMAP_CONTEXT_SUCCESSFULY,
            }

        except httpx.HTTPError as exc:
            return f"{FETCH_ROADMAP_CONTEXT_ERROR} HTTP Exception for {exc.request.url} - {exc}"
