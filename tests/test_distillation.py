import json
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import HttpUrl
from src.ai_engine.distiller_engine.distiller import ContentDistiller
from src.models.distillation_schemas import SingleDistilledItem


def build_openai_response(data: dict):
    return MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps(data)))])


@pytest.mark.asyncio
async def test_primary_source_identification(monkeypatch):
    """
    Tests if the distiller correctly identifies the primary source
    and marks it with is_primary=True.
    """
    distiller = ContentDistiller()

    mock_client = MagicMock()
    mock_create = AsyncMock()
    mock_client.chat.completions.create = mock_create
    distiller.client = mock_client

    urls = [
        HttpUrl("https://primary-source.com"),
        HttpUrl("https://secondary-source.com"),
    ]
    primary_url = HttpUrl("https://primary-source.com")

    async def fake_retrieve(url):
        return ["Sample content for " + str(url)]

    monkeypatch.setattr(
        "src.ai_engine.distiller_engine.distiller.retrieve_chunks_by_url", fake_retrieve
    )

    # Mock OpenAI responses for both URLs
    mock_create.side_effect = [
        build_openai_response(
            {
                "key_terms": [{"term": "Primary", "definition": "Main source"}],
                "main_points": ["Point 1"],
                "examples": [],
            }
        ),
        build_openai_response(
            {
                "key_terms": [{"term": "Secondary", "definition": "Extra source"}],
                "main_points": ["Point A"],
                "examples": [],
            }
        ),
    ]

    results = await distiller.distill_multiple_urls(urls, primary_url=primary_url)

    assert len(results) == 2

    # Find primary and secondary results
    primary_res = next(r for r in results if str(r.url) == str(primary_url))
    secondary_res = next(r for r in results if str(r.url) != str(primary_url))

    assert primary_res.is_primary is True
    assert secondary_res.is_primary is False
    assert primary_res.distilled_content.key_terms[0].term == "Primary"


@pytest.mark.asyncio
async def test_distillation_with_partial_failure(monkeypatch):
    """
    Tests that if one URL fails, the others still succeed and
    exceptions are returned in the results list.
    """
    distiller = ContentDistiller()

    mock_client = MagicMock()
    mock_create = AsyncMock()
    mock_client.chat.completions.create = mock_create
    distiller.client = mock_client

    urls = [
        HttpUrl("https://success.com"),
        HttpUrl("https://fail.com"),
    ]

    async def fake_retrieve(url):
        if "fail" in str(url):
            raise Exception("Database connection error")
        return ["Success content"]

    monkeypatch.setattr(
        "src.ai_engine.distiller_engine.distiller.retrieve_chunks_by_url", fake_retrieve
    )

    mock_create.return_value = build_openai_response(
        {"key_terms": [], "main_points": ["Success"], "examples": []}
    )

    results = await distiller.distill_multiple_urls(urls)

    assert len(results) == 2
    # One should be a SingleDistilledItem, the other an Exception
    success_count = sum(1 for r in results if isinstance(r, SingleDistilledItem))
    error_count = sum(1 for r in results if isinstance(r, Exception))

    assert success_count == 1
    assert error_count == 1


@pytest.mark.asyncio
async def test_parallel_execution_speed(monkeypatch):
    """
    Ensures that multiple URLs are processed in parallel (not sequentially).
    """
    distiller = ContentDistiller()
    mock_client = MagicMock()
    mock_create = AsyncMock()
    distiller.client = mock_client
    mock_client.chat.completions.create = mock_create

    start_times = []

    async def slow_retrieve(url):
        start_times.append(asyncio.get_event_loop().time())
        await asyncio.sleep(0.5)  # Simulate network delay
        return ["Content"]

    monkeypatch.setattr(
        "src.ai_engine.distiller_engine.distiller.retrieve_chunks_by_url", slow_retrieve
    )

    mock_create.return_value = build_openai_response(
        {"key_terms": [], "main_points": [], "examples": []}
    )

    urls = [HttpUrl(f"https://url{i}.com") for i in range(3)]

    await distiller.distill_multiple_urls(urls)
    time_diff = max(start_times) - min(start_times)
    assert time_diff < 0.1  # Strong evidence of parallel execution

    # python -m pytest tests/test_distillation.py
