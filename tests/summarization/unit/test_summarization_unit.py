import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.documents import Document
from pydantic import HttpUrl

from src.ai_engine.summarization_engine.summarizer import SummarizationService
from src.core.exceptions import NoContentFoundError
from src.models.summarization_schemas import SummarizationRequest


@pytest.fixture
def mock_dependencies():
    mock_openai = AsyncMock()
    mock_settings = MagicMock()
    mock_settings.LLM_MODEL_NAME = "gemini-3-flash-preview"
    mock_settings.LLM_TEMPERATURE = 0.3
    mock_settings.PRIMARY_URL_CHUNKS_LIMIT = 15
    return mock_openai, mock_settings


@pytest.fixture
def sample_request():
    return SummarizationRequest(
        user_id="user_123",
        subtopic_id="sub_456",
        urls=[HttpUrl("https://example.com")],
        primary_url=HttpUrl("https://example.com"),
        subtopic_name="Test Topic",
        subtopic_difficulty="Beginner",
        weaknesses={"Concept A": "Needs help"},
    )


@pytest.mark.asyncio
async def test_summarize_content_success(
    mock_dependencies, monkeypatch, sample_request
):
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_content_chunks",
        AsyncMock(return_value=[Document(page_content="Sample text")]),
    )

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"summary": "Valid summary"}'))
    ]
    mock_openai.chat.completions.create.return_value = mock_response

    result = await service.summarize_content(
        request=sample_request, qdrant_client=AsyncMock()
    )

    assert result["summary"] == "Valid summary"
    assert result["user_id"] == "user_123"


@pytest.mark.asyncio
async def test_summarize_content_no_data(
    mock_dependencies, monkeypatch, sample_request
):
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_content_chunks",
        AsyncMock(side_effect=NoContentFoundError("No content")),
    )

    result = await service.summarize_content(
        request=sample_request, qdrant_client=AsyncMock()
    )
    assert "summary" in result
    assert result["user_id"] == "user_123"


@pytest.mark.asyncio
async def test_summarize_fails_on_invalid_json(
    mock_dependencies, monkeypatch, sample_request
):
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_content_chunks",
        AsyncMock(return_value=[Document(page_content="Sample text")]),
    )

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Not JSON"))]
    mock_openai.chat.completions.create.return_value = mock_response

    result = await service.summarize_content(
        request=sample_request, qdrant_client=AsyncMock()
    )
    assert "error" in result
