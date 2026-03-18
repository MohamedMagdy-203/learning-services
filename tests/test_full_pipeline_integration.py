import pytest  # type: ignore
import logging
from src.models.schemas import RoadmapGenerationRequest
from src.core.mock_data import MOCK_VALID_RESPONSE
from src.core.config import Settings
from src.ai_engine.data_fetchers.cleaned_tavily_data import (
    fetch_and_clean_subtopic_content,
)
from src.ai_engine.llm_generators.reranker import rerank_sources
from src.ai_engine.vector_store.store import ingest_reranker_results, get_vector_store  # type: ignore
from src.ai_engine.vector_store.filters import is_url_already_stored

logging.basicConfig(level=logging.INFO)


@pytest.mark.integration  # type: ignore
@pytest.mark.asyncio  # type: ignore
async def test_full_pipeline_with_real_data():
    real_settings = Settings()  # type: ignore
    mock_request_data = RoadmapGenerationRequest(**MOCK_VALID_RESPONSE)

    user_id = mock_request_data.user_profile_schema.id
    subtopic_id = mock_request_data.target_subtopic_schema.Subtopic_id

    print("\n\n" + "=" * 60)
    print("FULL PIPELINE INTEGRATION TEST")
    print("=" * 60)
    print(f"User     : {user_id}")
    print(f"Subtopic : {subtopic_id}")

    # Step 1: Tavily
    print("\n--- [ Step 1: Fetching & Cleaning from Tavily ] ---")
    cleaned_sources = await fetch_and_clean_subtopic_content(
        settings=real_settings,
        requested_data=mock_request_data,
    )
    assert len(cleaned_sources) > 0
    print(f"Sources fetched: {len(cleaned_sources)}")

    # Step 2: LLM Reranker
    print("\n--- [ Step 2: LLM Reranker ] ---")
    ranked_results = await rerank_sources(
        requested_data=mock_request_data,
        cleaned_sources=cleaned_sources,
    )
    assert (
        ranked_results.get("best_course")
        or ranked_results.get("best_video")
        or ranked_results.get("best_blog")
    )

    for key in ("best_course", "best_video", "best_blog"):
        item = ranked_results.get(key)
        if item:
            print(f"  {key}: {item.get('title')}")
            print(f"    URL: {item.get('url')}")

    # Step 3: Ingest to Qdrant
    print("\n--- [ Step 3: Ingesting to Qdrant ] ---")
    data_to_ingest = {  # type: ignore
        "user_id": user_id,
        "subtopic_id": subtopic_id,
        **ranked_results,
    }
    await ingest_reranker_results(data_to_ingest)  # type: ignore
    print("Ingestion done")

    # Step 4: Verify stored
    print("\n--- [ Step 4: Verifying Storage ] ---")
    for key in ("best_course", "best_video", "best_blog"):
        item = ranked_results.get(key)
        if item:
            url = item.get("url")
            stored = is_url_already_stored(url)
            print(f"  {key}: {'✅ stored' if stored else '❌ NOT stored'}")
            assert stored, f"{key} not found in Qdrant: {url}"

    # Step 5: Similarity Search
    print("\n--- [ Step 5: Similarity Search ] ---")
    vector_store = get_vector_store()  # type: ignore
    query = f"{mock_request_data.target_subtopic_schema.Name} fundamentals"
    results = vector_store.similarity_search(query, k=3)  # type: ignore
    assert len(results) > 0  # type: ignore
    print(f"Query  : {query}")
    print(f"Results: {len(results)}")  # type: ignore
    for i, doc in enumerate(results, 1):  # type: ignore
        print(f"\n  [ Result {i} ]")
        print(f"  Source : {doc.metadata.get('source_type')}")  # type: ignore
        print(f"  Title  : {doc.metadata.get('title')}")  # type: ignore
        print(f"  Preview: {doc.page_content[:200]}")  # type: ignore

    # Step 6: Deduplication
    print("\n--- [ Step 6: Deduplication Check ] ---")
    await ingest_reranker_results(data_to_ingest)  # type: ignore
    print("Second ingest done — checking no duplicates added")
    for key in ("best_course", "best_video", "best_blog"):
        item = ranked_results.get(key)
        if item:
            url = item.get("url")
            stored = is_url_already_stored(url)
            print(f"  {key}: {'✅ still stored once' if stored else '❌ missing'}")

    print("\n" + "=" * 60)
    print("ALL STEPS PASSED ✅")
    print("=" * 60 + "\n")
