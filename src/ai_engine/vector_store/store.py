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
import time

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
    start_time = time.time()
    get_embeddings()
    all_documents = await prepare_documents(reranker_data)  # type: ignore

    if all_documents:
        print(f"Uploading {len(all_documents)} new chunks to Qdrant...")
        logger.info("Uploading %d new chunks to Qdrant...", len(all_documents))  # type: ignore
        vector_store = get_vector_store()  # type: ignore
        await asyncio.to_thread(vector_store.add_documents, all_documents)  # type: ignore
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Successfully ingested new documents in {execution_time:.2f} seconds!")
        logger.info(
            "Successfully ingested new documents in %.2f seconds!", execution_time
        )
    else:
        end_time = time.time()
        execution_time = end_time - start_time
        print(
            f"No new documents needed to be uploaded. Finished in {execution_time:.2f} seconds."
        )
        logger.info(
            "No new documents needed to be uploaded. Finished in %.2f seconds.",
            execution_time,
        )
