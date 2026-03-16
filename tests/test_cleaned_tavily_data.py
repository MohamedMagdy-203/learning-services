import pytest
import logging
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import MOCK_VALID_RESPONSE
from src.core.config import Settings
from src.ai_engine.data_fetchers import cleaned_tavily_data

logging.basicConfig(level=logging.INFO)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_and_clean_subtopic_content():
    real_settings = Settings()  # type: ignore
    mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)

    result = await cleaned_tavily_data.fetch_and_clean_subtopic_content(
        settings=real_settings,
        requested_data=mock_request_data,
    )

    assert len(result) > 0

    print("\n\n" + "=" * 50)
    print("CLEANED DATA FROM TAVILY")
    print("=" * 50)
    print(f"Found {len(result)} sources.")

    for i, source in enumerate(result, 1):
        print(f"\n--- [ Source {i}: {source['title']} ] ---")
        print(f"URL: {source['url']}")
        print(f"Content Length: {len(source['raw_content'])} chars")
        print(f"Content Preview:\n{source['raw_content'][:500]}")
        print("." * 30)

    print("=" * 50 + "\n")
