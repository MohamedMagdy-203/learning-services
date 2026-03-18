import pytest  # type: ignore
import logging
from src.ai_engine.vector_store.store import ingest_reranker_results, get_vector_store  # type: ignore
from src.ai_engine.vector_store.filters import is_url_already_stored
from src.core.mock_data import MOCK_RANKED_RESULT

logging.basicConfig(level=logging.INFO)

SAMPLE_INPUT = {  # type: ignore
    **MOCK_RANKED_RESULT,
    "user_id": "test_user_123",
    "subtopic_id": "test_sub_456",
}


@pytest.mark.integration  # type: ignore
def test_ingest_and_verify_stored():
    ingest_reranker_results(SAMPLE_INPUT)  # type: ignore

    print("\n\n" + "=" * 60)
    print("VECTOR STORE INTEGRATION TEST")
    print("=" * 60)

    for key in ("best_course", "best_video", "best_blog"):
        source = MOCK_RANKED_RESULT.get(key)
        if source:
            url = source["url"]
            stored = is_url_already_stored(url)
            print(f"\n--- [ {key.upper()} ] ---")
            print(f"  URL    : {url}")
            print(f"  Stored : {'✅ YES' if stored else '❌ NO'}")
            assert stored, f"{key} URL not found in Qdrant: {url}"

    print("\n" + "=" * 60 + "\n")


@pytest.mark.integration  # type: ignore
def test_similarity_search():
    vector_store = get_vector_store()  # type: ignore

    query = "What is the difference between SQL and NoSQL databases?"
    results = vector_store.similarity_search(query, k=3)  # type: ignore

    print("\n\n" + "=" * 60)
    print("SIMILARITY SEARCH RESULTS")
    print("=" * 60)
    print(f"Query: {query}")
    print(f"Results found: {len(results)}")  # type: ignore

    for i, doc in enumerate(results, 1):  # type: ignore
        print(f"\n--- [ Result {i} ] ---")
        print(f"  Source  : {doc.metadata.get('source_type')}")  # type: ignore
        print(f"  Title   : {doc.metadata.get('title')}")  # type: ignore
        print(f"  URL     : {doc.metadata.get('url')}")  # type: ignore
        print(f"  Preview : {doc.page_content[:200]}")  # type: ignore

    assert len(results) > 0  # type: ignore

    print("\n" + "=" * 60 + "\n")


@pytest.mark.integration  # type: ignore
def test_url_deduplication():
    url = MOCK_RANKED_RESULT["best_blog"]["url"]

    before = is_url_already_stored(url)
    ingest_reranker_results(SAMPLE_INPUT)  # type: ignore
    after = is_url_already_stored(url)

    print("\n\n" + "=" * 60)
    print("DEDUPLICATION TEST")
    print("=" * 60)
    print(f"URL     : {url}")
    print(f"Before  : {'stored' if before else 'not stored'}")
    print(f"After   : {'stored' if after else 'not stored'}")
    print("=" * 60 + "\n")

    assert after is True
