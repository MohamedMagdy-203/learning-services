import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.documents import Document

from src.ai_engine.summarization_engine.summarizer import SummarizationService
from src.core.exceptions import NoContentFoundError


@pytest.fixture
def mock_dependencies():
    mock_openai = AsyncMock()
    mock_settings = MagicMock()

    mock_settings.LLM_MODEL_NAME = "gemini-3-flash-preview"
    mock_settings.LLM_TEMPERATURE = 0.3
    mock_settings.QDRANT_COLLECTION_NAME = "test_collection"

    return mock_openai, mock_settings


# SUCCESS CASE


@pytest.mark.asyncio
async def test_summarize_content_success(mock_dependencies, monkeypatch):
    """
    Should return valid summary when:
    - Qdrant returns documents
    - LLM returns valid JSON with 'summary'
    """
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_chunks_by_url",
        AsyncMock(return_value=[Document(page_content="Sample text")]),
    )

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"summary": "Valid summary"}'))
    ]
    mock_openai.chat.completions.create.return_value = mock_response

    result = await service.summarize_content(
        user_id="u1", subtopic_id="s1", primary_url="url", qdrant_client=AsyncMock()
    )

    assert result["summary"] == "Valid summary"
    assert result["user_id"] == "u1"
    assert result["subtopic_id"] == "s1"


#  NO CONTENT CASE
@pytest.mark.asyncio
async def test_summarize_content_no_data(mock_dependencies, monkeypatch):
    """
    Should return fallback summary when:
    - Qdrant raises NoContentFoundError
    """
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    async def mock_retrieve_error(*args, **kwargs):
        raise NoContentFoundError("No content")

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_chunks_by_url",
        mock_retrieve_error,
    )

    result = await service.summarize_content(
        user_id="u1", subtopic_id="s1", primary_url="url", qdrant_client=AsyncMock()
    )

    assert "summary" in result
    assert result["user_id"] == "u1"


# INVALID JSON


@pytest.mark.asyncio
async def test_summarize_fails_on_invalid_json(mock_dependencies, monkeypatch):
    """
    Should return error when:
    - LLM returns non-JSON response
    """
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_chunks_by_url",
        AsyncMock(return_value=[Document(page_content="Sample text")]),
    )

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Not JSON"))]
    mock_openai.chat.completions.create.return_value = mock_response

    result = await service.summarize_content(
        user_id="u1", subtopic_id="s1", primary_url="url", qdrant_client=AsyncMock()
    )

    assert "error" in result


# MISSING SUMMARY


@pytest.mark.asyncio
async def test_summarize_fails_on_missing_summary(mock_dependencies, monkeypatch):
    """
    Should return error when:
    - JSON does not contain 'summary'
    """
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_chunks_by_url",
        AsyncMock(return_value=[Document(page_content="Sample text")]),
    )

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"text": "no summary"}'))
    ]
    mock_openai.chat.completions.create.return_value = mock_response

    result = await service.summarize_content(
        user_id="u1", subtopic_id="s1", primary_url="url", qdrant_client=AsyncMock()
    )

    assert "error" in result


# EMPTY SUMMARY


@pytest.mark.asyncio
async def test_summarize_fails_on_empty_summary(mock_dependencies, monkeypatch):
    """
    Should return error when:
    - Summary is empty string
    """
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_chunks_by_url",
        AsyncMock(return_value=[Document(page_content="Sample text")]),
    )

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"summary": "   "}'))]
    mock_openai.chat.completions.create.return_value = mock_response

    result = await service.summarize_content(
        user_id="u1", subtopic_id="s1", primary_url="url", qdrant_client=AsyncMock()
    )

    assert "error" in result


# RETRIEVE FAILURE


@pytest.mark.asyncio
async def test_summarize_fails_on_retrieve_error(mock_dependencies, monkeypatch):
    """
    Should return error when:
    - Unexpected exception happens during retrieval
    """
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    async def mock_retrieve_fail(*args, **kwargs):
        raise Exception("DB failure")

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_chunks_by_url",
        mock_retrieve_fail,
    )

    result = await service.summarize_content(
        user_id="u1", subtopic_id="s1", primary_url="url", qdrant_client=AsyncMock()
    )

    assert "error" in result


# RETRY LOGIC


@pytest.mark.asyncio
async def test_llm_retry_success(mock_dependencies, monkeypatch):
    """
    Should retry LLM call:
    - First attempt fails
    - Second succeeds
    """
    mock_openai, mock_settings = mock_dependencies
    service = SummarizationService(mock_openai, mock_settings)

    monkeypatch.setattr(
        "src.ai_engine.summarization_engine.summarizer.retrieve_chunks_by_url",
        AsyncMock(return_value=[Document(page_content="Sample text")]),
    )

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"summary": "Recovered"}'))
    ]

    mock_openai.chat.completions.create.side_effect = [Exception("fail"), mock_response]

    result = await service.summarize_content(
        user_id="u1", subtopic_id="s1", primary_url="url", qdrant_client=AsyncMock()
    )

    assert result["summary"] == "Recovered"
    assert mock_openai.chat.completions.create.call_count == 2
