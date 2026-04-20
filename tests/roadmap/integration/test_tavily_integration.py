import pytest
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import MOCK_VALID_RESPONSE
from src.core.config import Settings
from src.ai_engine.data_fetchers import tavily_client
import logging

logging.basicConfig(level=logging.INFO)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_tavily_api_call():
    real_settings = Settings()  # type: ignore

    mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)

    result = await tavily_client.fetch_subtopic_content(
        settings=real_settings, requested_data=mock_request_data
    )

    assert "results" in result
    assert len(result["results"]) > 0
    assert len(result["results"][0]["raw_content"]) > 100

    print("\n\n" + "=" * 50)
    print("REAL DATA FROM TAVILY")
    print("=" * 50)
    print(f"Found {len(result['results'])} sources.")

    print("Sources URLs:")
    for source in result["results"]:
        print(f" - {source['url']}")

    print("-" * 50)
    print("All Content Returned:\n")

    for i, source in enumerate(result["results"], 1):
        print(f"--- [ Source {i} Content ] ---")
        print(source["raw_content"])
        print("\n" + "." * 30 + "\n")

    print("=" * 50 + "\n")
