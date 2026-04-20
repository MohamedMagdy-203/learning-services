import pytest  # type: ignore
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.core.mock_data import (
    MOCK_VALID_RESPONSE,
    MOCK_CLEANED_RESPONSE,
    MOCK_RANKED_RESULT,
)
from src.core.exceptions import TavilyCallingError


@pytest.mark.asyncio  # type: ignore
@patch("src.routers.roadmap.ingest_reranker_results", new_callable=AsyncMock)
@patch("src.routers.roadmap.fetch_and_clean_subtopic_content", new_callable=AsyncMock)
@patch("src.routers.roadmap.rerank_sources", new_callable=AsyncMock)
async def test_generate_roadmap_success(
    mock_rerank: AsyncMock,
    mock_clean: AsyncMock,
    mock_ingest: AsyncMock,
):
    """Test successful generation of roadmap content."""
    mock_clean.return_value = MOCK_CLEANED_RESPONSE
    mock_rerank.return_value = MOCK_RANKED_RESULT

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/roadmap/generate", json=MOCK_VALID_RESPONSE
        )

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

    mock_ingest.assert_called_once()


@pytest.mark.asyncio  # type: ignore
async def test_generate_roadmap_validation_error():
    """Test 422 Unprocessable Entity when payload is invalid or missing."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/roadmap/generate", json={"invalid": "data"}
        )

    assert response.status_code == 422


@pytest.mark.asyncio  # type: ignore
@patch("src.routers.roadmap.fetch_and_clean_subtopic_content", new_callable=AsyncMock)
async def test_generate_roadmap_tavily_error(
    mock_clean: AsyncMock,
):
    """Test 503 error when Tavily search fails."""
    mock_clean.side_effect = TavilyCallingError("error")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/roadmap/generate", json=MOCK_VALID_RESPONSE
        )

    assert response.status_code == 503


@pytest.mark.asyncio  # type: ignore
@patch("src.routers.roadmap.fetch_and_clean_subtopic_content", new_callable=AsyncMock)
@patch("src.routers.roadmap.rerank_sources", new_callable=AsyncMock)
async def test_generate_roadmap_reranker_error(
    mock_rerank: AsyncMock,
    mock_clean: AsyncMock,
):
    """Test 500 error when LLM fails to rank sources."""
    mock_clean.return_value = MOCK_CLEANED_RESPONSE
    mock_rerank.side_effect = ValueError("LLM returned an invalid response format")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/roadmap/generate", json=MOCK_VALID_RESPONSE
        )

    assert response.status_code == 500
