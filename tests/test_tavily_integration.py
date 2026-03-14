import pytest
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import MOCK_VALID_RESPONSE
from src.core.config import Settings
from src.ai_engine.data_fetchers import tavily_client
from src.core.messages import TAVILY_CALLING_SUCCESSFULLY


@pytest.mark.asyncio
async def test_real_tavily_api_call():
    real_settings = Settings()

    mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)

    result = await tavily_client.fetch_subtopic_content(
        settings=real_settings, requested_data=mock_request_data
    )

    assert result["status"] == TAVILY_CALLING_SUCCESSFULLY
    assert len(result["content"]) > 100
    assert len(result["sources"]) > 0

    print("\n\n" + "=" * 50)
    print("REAL DATA FROM TAVILY")
    print("=" * 50)
    print(f"Found {len(result['sources'])} sources.")
    print("Sources URLs:")
    for source in result["sources"]:
        print(f" - {source['url']}")
    print("-" * 50)
    print("Content Sneak Peek")
    print(result["content"] + "...\n")
    print("=" * 50 + "\n")
