import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import MOCK_VALID_RESPONSE
from src.core.exceptions import FetchRoadmapContextError
from src.core.config import Settings, get_settings


mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)

mock_settings = Settings(
    TAVILY_API_KEY="test_key",
    GEMINI_API_KEY="test_key",
)


def override_get_settings():
    return mock_settings


app.dependency_overrides[get_settings] = override_get_settings


@pytest.mark.asyncio
@patch("src.routers.mindmap.fetch_roadmap_context", new_callable=AsyncMock)
async def test_generate_mindmap_fetches_context_successfully(mock_context: AsyncMock):
    mock_context.return_value = {"roadmap_context": mock_request_data}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/mindmap/",
            json={
                "user_id": "user_123",
                "subtopic_id": "sub_456",
                "source_type": "best_video",
            },
        )

    assert response.status_code == 501
    assert mock_context.called
    call_kwargs = mock_context.call_args.kwargs
    assert call_kwargs["user_id"] == "user_123"
    assert call_kwargs["subtopic_id"] == "sub_456"


@pytest.mark.asyncio
@patch("src.routers.mindmap.fetch_roadmap_context", new_callable=AsyncMock)
async def test_generate_mindmap_context_error_returns_502(mock_context: AsyncMock):
    mock_context.side_effect = FetchRoadmapContextError("error")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/mindmap/",
            json={
                "user_id": "user_123",
                "subtopic_id": "sub_456",
                "source_type": "best_video",
            },
        )

    assert response.status_code == 502
    assert response.json()["detail"] == "Failed to fetch roadmap context"


@pytest.mark.asyncio
async def test_generate_mindmap_missing_user_id_returns_422():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/mindmap/",
            json={
                "subtopic_id": "sub_456",
                "source_type": "best_video",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_mindmap_missing_subtopic_id_returns_422():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/mindmap/",
            json={
                "user_id": "user_123",
                "source_type": "best_video",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_mindmap_missing_source_type_returns_422():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/mindmap/",
            json={
                "user_id": "user_123",
                "subtopic_id": "sub_456",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_mindmap_empty_body_returns_422():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/mindmap/", json={})

    assert response.status_code == 422