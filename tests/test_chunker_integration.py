import pytest  # type: ignore
import logging
from src.ai_engine.text_processing.chunker import chunk_text
from src.ai_engine.data_fetchers.cleaned_tavily_data import (
    fetch_and_clean_subtopic_content,
)
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import MOCK_VALID_RESPONSE
from src.core.config import Settings

logging.basicConfig(level=logging.INFO)


@pytest.mark.integration  # type: ignore
@pytest.mark.asyncio  # type: ignore
async def test_chunk_real_tavily_content():
    real_settings = Settings()  # type: ignore
    mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)

    cleaned_sources = await fetch_and_clean_subtopic_content(
        settings=real_settings,
        requested_data=mock_request_data,
    )

    assert len(cleaned_sources) > 0

    print("\n\n" + "=" * 60)
    print("CHUNKING RESULTS — REAL TAVILY CONTENT")
    print("=" * 60)

    for i, source in enumerate(cleaned_sources[:3], 1):
        chunks = chunk_text(source["raw_content"])

        print(f"\n--- [ Source {i}: {source['title']} ] ---")
        print(f"URL            : {source['url']}")
        print(f"Input length   : {len(source['raw_content'])} chars")
        print(f"Chunks produced: {len(chunks)}")

        for j, chunk in enumerate(chunks, 1):
            print(f"\n  [ Chunk {j} ]")
            print(f"  Length : {len(chunk)} chars")
            print(f"  Preview: {chunk[:300]}")
            print("  " + "." * 40)

        print("-" * 60)

    print("=" * 60 + "\n")
