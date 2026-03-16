import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import MOCK_TAVILY_RESPONSE, MOCK_VALID_RESPONSE
from src.core.config import Settings
from src.core.exceptions import TavilyCallingError
from src.ai_engine.data_fetchers import tavily_client

mock_requested_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)
mock_settings = Settings(TAVILY_API_KEY="test_key_123")


@pytest.mark.asyncio
@patch("src.ai_engine.data_fetchers.tavily_client.AsyncTavilyClient")
async def test_fetch_subtopic_content_success(mock_tavily_class: MagicMock):
    mock_tavily_class.return_value.search = AsyncMock(return_value=MOCK_TAVILY_RESPONSE)
    result = await tavily_client.fetch_subtopic_content(
        settings=mock_settings, requested_data=mock_requested_data
    )

    assert "results" in result
    assert len(result["results"]) == 2

    first_result = result["results"][0]
    assert first_result["url"] == "https://realpython.com/async-io-python/"
    assert "Asyncio is a library" in first_result["raw_content"]
    assert "concurrent code" in first_result["raw_content"]


@pytest.mark.asyncio
@patch("src.ai_engine.data_fetchers.tavily_client.AsyncTavilyClient")
async def test_fetch_subtopic_content_error(mock_tavily_class: MagicMock):
    mock_tavily_class.return_value.search = AsyncMock(
        side_effect=Exception("Fake Network Error")
    )

    with pytest.raises(TavilyCallingError) as exc_info:
        await tavily_client.fetch_subtopic_content(
            settings=mock_settings, requested_data=mock_requested_data
        )

    assert exc_info.value.args[0] == TavilyCallingError.DEFAULT_MESSAGE
