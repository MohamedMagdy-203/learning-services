import pytest
import respx
import httpx
from src.core.config import Settings
from src.services.main_backend_client import fetch_roadmap_context
from src.core.exceptions import FetchRoadmapContextError
from src.core.mock_data import MOCK_VALID_RESPONSE


@pytest.mark.asyncio
@respx.mock
async def test_fetch_roadmap_success():
    settings = Settings()  # type: ignore
    user_id = "user_123"
    subtopic_id = "sub_456"
    url = f"{settings.MAIN_BACKEND_URL}/api/internal/roadmap-context/{user_id}/{subtopic_id}"
    respx.get(url).mock(return_value=httpx.Response(200, json=MOCK_VALID_RESPONSE))
    result = await fetch_roadmap_context(user_id, subtopic_id, settings)

    assert result["roadmap_context"].user_profile_schema.id == "user_123"
    assert (
        result["roadmap_context"].target_subtopic_schema.Name == "Database Fundamentals"
    )


@pytest.mark.asyncio
@respx.mock
async def test_fetch_roadmap_raises_error():
    settings = Settings()  # type: ignore
    user_id = "user_123"
    subtopic_id = "sub_456"
    url = f"{settings.MAIN_BACKEND_URL}/api/internal/roadmap-context/{user_id}/{subtopic_id}"
    respx.get(url).mock(return_value=httpx.Response(500))

    with pytest.raises(FetchRoadmapContextError):
        await fetch_roadmap_context(user_id, subtopic_id, settings)
