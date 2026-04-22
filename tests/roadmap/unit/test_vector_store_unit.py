import pytest  # type: ignore
from unittest.mock import patch, MagicMock
from src.ai_engine.vector_store.prepare_store_document import prepare_documents  # type: ignore
from src.ai_engine.vector_store.store import ingest_reranker_results
from src.core.mock_data import MOCK_RANKED_RESULT
from langchain_core.documents import Document  # type: ignore


@pytest.fixture  # type: ignore
def sample_reranker_input():
    data = MOCK_RANKED_RESULT.copy()
    data["user_id"] = "user_123"  # type: ignore
    data["subtopic_id"] = "sub_456"  # type: ignore
    return data


@pytest.mark.asyncio  # type: ignore
@patch("src.ai_engine.text_processing.chunker.get_embeddings")
@patch("src.ai_engine.vector_store.prepare_store_document.is_url_already_stored")
@patch("src.ai_engine.text_processing.chunker.chunk_text")
async def test_prepare_documents_with_mock_data(
    mock_chunk, mock_is_stored, mock_get_embeddings, sample_reranker_input
):
    mock_is_stored.side_effect = lambda url: "udemy.com" in url
    mock_chunk.return_value = ["chunk1", "chunk2"]
    documents = await prepare_documents(sample_reranker_input)  # type: ignore

    assert len(documents) > 0  # type: ignore

    urls_in_docs = [doc.metadata["url"] for doc in documents]  # type: ignore
    assert not any("udemy.com" in url for url in urls_in_docs)  # type: ignore

    assert documents[0].metadata["url"] is not None  # type: ignore
    assert documents[0].metadata["source_type"] is not None  # type: ignore
    logger_urls = [doc.metadata["url"] for doc in documents]  # type: ignore
    assert "youtube.com" in str(logger_urls)  # type: ignore


@pytest.mark.asyncio
@patch("src.ai_engine.vector_store.store.get_embeddings")
@patch("src.ai_engine.vector_store.store.get_vector_store")
@patch("src.ai_engine.vector_store.store.prepare_documents")
async def test_ingest_calls_qdrant_correctly(
    mock_prepare,  # type: ignore
    mock_get_store,  # type: ignore
    mock_get_embeddings,
    sample_reranker_input,
):
    mock_vector_store = MagicMock()
    mock_get_store.return_value = mock_vector_store
    mock_prepare.return_value = [MagicMock(spec=Document)]

    await ingest_reranker_results(sample_reranker_input)  # type: ignore

    assert mock_vector_store.add_documents.called
