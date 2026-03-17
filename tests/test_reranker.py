import pytest  # type: ignore
from unittest.mock import patch, MagicMock, AsyncMock
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import (
    MOCK_VALID_RESPONSE,
    MOCK_CLEANED_RESPONSE,
    MOCK_LLM_RESPONSE,
)
from src.ai_engine.llm_generators.reranker import rerank_sources

mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)


@pytest.mark.asyncio  # type: ignore
@patch("src.ai_engine.llm_generators.reranker._client")
async def test_rerank_sources_success(mock_client: MagicMock):
    mock_response = MagicMock()
    mock_response.text = MOCK_LLM_RESPONSE
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    result = await rerank_sources(
        requested_data=mock_request_data,
        cleaned_sources=MOCK_CLEANED_RESPONSE,
    )

    assert result["best_course"]["title"] == "The Complete SQL Bootcamp — Udemy"
    assert (
        result["best_course"]["url"]
        == "https://www.udemy.com/course/the-complete-sql-bootcamp/"
    )
    assert result["best_course"]["raw_content"] is not None

    assert (
        result["best_video"]["title"] == "Database Fundamentals for Beginners — YouTube"
    )

    assert result["best_video"]["raw_content"] is not None

    assert result["best_blog"]["title"] == "SQL vs NoSQL — When to Use Which"
    assert result["best_blog"]["raw_content"] is not None


@pytest.mark.asyncio  # type: ignore
@patch("src.ai_engine.llm_generators.reranker._client")
async def test_rerank_sources_enriches_raw_content(mock_client: MagicMock):
    mock_response = MagicMock()
    mock_response.text = MOCK_LLM_RESPONSE
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    result = await rerank_sources(
        requested_data=mock_request_data,
        cleaned_sources=MOCK_CLEANED_RESPONSE,
    )

    assert (
        result["best_course"]["raw_content"] == MOCK_CLEANED_RESPONSE[0]["raw_content"]
    )
    assert (
        result["best_video"]["raw_content"] == MOCK_CLEANED_RESPONSE[1]["raw_content"]
    )
    assert result["best_blog"]["raw_content"] == MOCK_CLEANED_RESPONSE[2]["raw_content"]


@pytest.mark.asyncio  # type: ignore
async def test_rerank_sources_empty_input():
    result = await rerank_sources(
        requested_data=mock_request_data,
        cleaned_sources=[],
    )

    assert result["best_course"] is None
    assert result["best_video"] is None
    assert result["best_blog"] is None


@pytest.mark.asyncio  # type: ignore
@patch("src.ai_engine.llm_generators.reranker._client")
async def test_rerank_sources_invalid_llm_response(mock_client: MagicMock):
    mock_response = MagicMock()
    mock_response.text = "this is not valid json at all"
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with pytest.raises(ValueError, match="LLM returned an invalid response format"):  # type: ignore
        await rerank_sources(
            requested_data=mock_request_data,
            cleaned_sources=MOCK_CLEANED_RESPONSE,
        )
