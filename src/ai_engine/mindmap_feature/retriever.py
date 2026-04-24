import logging
from typing import List
from qdrant_client import AsyncQdrantClient
from src.core.config import Settings
from src.models.schemas import MindmapGenerationRequest
from src.core.exceptions import MindmapContentNotFoundError
from src.ai_engine.vector_store.shared_retriever import retrieve_content_chunks

logger = logging.getLogger(__name__)


async def retrieve_all_chunks_for_mindmap(
    request: MindmapGenerationRequest,
    client: AsyncQdrantClient,
    settings: Settings,
) -> List[str]:
    secondary_urls = [
        str(url) for url in request.urls if str(url) != str(request.primary_url)
    ]

    try:
        documents = await retrieve_content_chunks(
            primary_url=str(request.primary_url),
            secondary_urls=secondary_urls,
            client=client,
            settings=settings,
        )
        return [doc.page_content for doc in documents]

    except Exception as e:
        logger.error(
            "Failed to retrieve mindmap chunks | subtopic=%s", request.subtopic_name
        )
        raise MindmapContentNotFoundError(
            "No content found in vector store for the requested subtopic"
        ) from e
