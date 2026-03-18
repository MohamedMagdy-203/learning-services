import logging
from typing import Dict, Any
from langchain_qdrant import QdrantVectorStore  # type: ignore
from src.ai_engine.vector_store.embedder import get_embeddings  # type: ignore
from src.ai_engine.vector_store.qdrant_client import (
    get_qdrant_client,
    ensure_collection_exists,
)
from src.ai_engine.vector_store.prepare_store_document import prepare_documents  # type: ignore
from src.core.config import get_settings
import asyncio

logger = logging.getLogger(__name__)


def get_vector_store() -> QdrantVectorStore:  # type: ignore
    ensure_collection_exists()
    client = get_qdrant_client()
    return QdrantVectorStore(
        client=client,
        collection_name=get_settings().QDRANT_COLLECTION_NAME,
        embedding=get_embeddings(),
    )  # type: ignore


async def ingest_reranker_results(reranker_data: Dict[str, Any]) -> None:
    """Main ingestion entry point."""
    all_documents = await prepare_documents(reranker_data)  # type: ignore

    if all_documents:
        logger.info("Uploading %d new chunks to Qdrant...", len(all_documents))  # type: ignore
        vector_store = get_vector_store()  # type: ignore
        await asyncio.to_thread(vector_store.add_documents, all_documents)  # type: ignore
        logger.info("Successfully ingested new documents.")
    else:
        logger.info("No new documents needed to be uploaded.")
