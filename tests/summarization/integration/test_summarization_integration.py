import pytest
from pydantic import HttpUrl
from qdrant_client import AsyncQdrantClient
from openai import AsyncOpenAI

from src.core.config import get_settings
from src.ai_engine.summarization_engine.summarizer import SummarizationService
from src.models.summarization_schemas import SummarizationRequest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_full_pipeline():
    """
    Tests the real pipeline with Qdrant and LLM.
    Assumes 'https://learn.microsoft.com/en-us/shows/dbfundamentals/' is ingested.
    """
    settings = get_settings()
    qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)

    # We initialize real OpenAI client for integration testing
    openai_client = AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    service = SummarizationService(openai_client=openai_client, settings=settings)

    request = SummarizationRequest(
        user_id="user_int_1",
        subtopic_id="sub_int_1",
        urls=[HttpUrl("https://learn.microsoft.com/en-us/shows/dbfundamentals/")],
        primary_url=HttpUrl("https://learn.microsoft.com/en-us/shows/dbfundamentals/"),
        subtopic_name="Database Fundamentals",
        subtopic_difficulty="Beginner",
        weaknesses={"Data Integrity": "Limited understanding"},
    )

    result = await service.summarize_content(
        request=request, qdrant_client=qdrant_client
    )

    assert "error" not in result
    assert "summary" in result
    assert len(result["summary"]) > 0
    assert result["user_id"] == "user_int_1"
