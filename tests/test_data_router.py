import pytest  # type: ignore
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import (
    MOCK_VALID_RESPONSE,
    MOCK_CLEANED_RESPONSE,
    MOCK_RANKED_RESULT,
)
from src.core.exceptions import FetchRoadmapContextError, TavilyCallingError


mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)


@pytest.mark.asyncio  # type: ignore
@patch("src.routers.data.fetch_roadmap_context", new_callable=AsyncMock)
@patch("src.routers.data.fetch_and_clean_subtopic_content", new_callable=AsyncMock)
@patch("src.routers.data.rerank_sources", new_callable=AsyncMock)
async def test_get_roadmap_content_success(
    mock_rerank: AsyncMock,
    mock_clean: AsyncMock,
    mock_context: AsyncMock,
):
    mock_context.return_value = {"roadmap_context": mock_request_data}
    mock_clean.return_value = MOCK_CLEANED_RESPONSE
    mock_rerank.return_value = MOCK_RANKED_RESULT

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/data/roadmap-content/user_123/sub_456")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_123"
    assert data["subtopic_id"] == "sub_456"
    assert data["best_course"]["title"] == "The Complete SQL Bootcamp — Udemy"
    assert (
        data["best_course"]["url"]
        == "https://www.udemy.com/course/the-complete-sql-bootcamp/"
    )

    assert (
        data["best_video"]["title"] == "Database Fundamentals for Beginners — YouTube"
    )
    assert data["best_blog"]["title"] == "SQL vs NoSQL — When to Use Which"
    assert "raw_content" not in data["best_course"]
    assert "raw_content" not in data["best_video"]
    assert "raw_content" not in data["best_blog"]


@pytest.mark.asyncio  # type: ignore
@patch("src.routers.data.fetch_roadmap_context", new_callable=AsyncMock)
async def test_get_roadmap_content_context_error(mock_context: AsyncMock):
    mock_context.side_effect = FetchRoadmapContextError("error")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/data/roadmap-content/user_123/sub_456")

    assert response.status_code == 502


@pytest.mark.asyncio  # type: ignore
@patch("src.routers.data.fetch_roadmap_context", new_callable=AsyncMock)
@patch("src.routers.data.fetch_and_clean_subtopic_content", new_callable=AsyncMock)
async def test_get_roadmap_content_tavily_error(
    mock_clean: AsyncMock,
    mock_context: AsyncMock,
):
    mock_context.return_value = {"roadmap_context": mock_request_data}
    mock_clean.side_effect = TavilyCallingError("error")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/data/roadmap-content/user_123/sub_456")

    assert response.status_code == 503


@pytest.mark.asyncio  # type: ignore
@patch("src.routers.data.fetch_roadmap_context", new_callable=AsyncMock)
@patch("src.routers.data.fetch_and_clean_subtopic_content", new_callable=AsyncMock)
@patch("src.routers.data.rerank_sources", new_callable=AsyncMock)
async def test_get_roadmap_content_reranker_error(
    mock_rerank: AsyncMock,
    mock_clean: AsyncMock,
    mock_context: AsyncMock,
):
    mock_context.return_value = {"roadmap_context": mock_request_data}
    mock_clean.return_value = MOCK_CLEANED_RESPONSE
    mock_rerank.side_effect = ValueError("LLM returned an invalid response format")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/data/roadmap-content/user_123/sub_456")

    assert response.status_code == 500
