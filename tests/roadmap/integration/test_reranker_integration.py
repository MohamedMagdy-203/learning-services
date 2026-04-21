import pytest
import logging
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import MOCK_VALID_RESPONSE
from src.core.config import Settings
from src.ai_engine.data_fetchers.cleaned_tavily_data import (
    fetch_and_clean_subtopic_content,
)
from src.ai_engine.llm_generators.reranker import rerank_sources

logging.basicConfig(level=logging.INFO)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_reranker_pipeline():
    real_settings = Settings()  # type: ignore
    mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)

    cleaned_sources = await fetch_and_clean_subtopic_content(
        settings=real_settings,
        requested_data=mock_request_data,
    )

    assert len(cleaned_sources) > 0

    result = await rerank_sources(
        requested_data=mock_request_data,
        cleaned_sources=cleaned_sources,
    )

    print("\n\n" + "=" * 60)
    print("LLM RERANKER FINAL RESULTS")
    print("=" * 60)

    for key, label in [
        ("best_course", "BEST COURSE"),
        ("best_video", "BEST VIDEO"),
        ("best_blog", "BEST BLOG"),
    ]:
        item = result.get(key)
        print(f"\n--- [ {label} ] ---")

        if item is None:
            print("  No source found for this category.")
            continue

        print(f"  Title      : {item.get('title')}")
        print(f"  URL        : {item.get('url')}")
        print(f"  Reason     : {item.get('reason')}")
        print(f"  raw_content: {'present' if item.get('raw_content') else 'missing'}")
        print(f"  Content Length: {len(item.get('raw_content', ''))} chars")

    print("\n" + "=" * 60 + "\n")

    for key in ("best_course", "best_video", "best_blog"):
        item = result.get(key)
        if item is not None:
            assert item.get("title"), f"{key} missing title"
            assert item.get("url"), f"{key} missing url"
            assert item.get("reason"), f"{key} missing reason"
            assert item.get("raw_content"), f"{key} missing raw_content"
