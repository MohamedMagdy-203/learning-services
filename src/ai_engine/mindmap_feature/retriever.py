import asyncio
import logging
from typing import List, Coroutine, Any
from qdrant_client.models import Filter, FieldCondition, MatchValue
from src.ai_engine.vector_store.qdrant_client import get_qdrant_client
from src.core.config import get_settings
from src.core.exceptions import MindmapContentNotFoundError
from src.models.schemas import MindmapGenerationRequest

logger = logging.getLogger(__name__)

# Chunks fetched per source — course gets more because it has richer structure
CHUNKS_PER_COURSE: int = 10
CHUNKS_PER_VIDEO: int = 8
CHUNKS_PER_BLOG: int = 8


def _scroll_chunks_by_url(url: str, limit: int) -> List[str]:
    """
    Fetch all stored chunks for a single source URL using Qdrant scroll.

    Args:
        url: the exact URL stored in metadata.url during ingestion
        limit: maximum number of chunks to retrieve for this source

    Returns:
        List[str]: page_content strings belonging to this URL
    """

    client = get_qdrant_client()
    settings = get_settings()
    try:
        results, _ = client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.url",
                        match=MatchValue(value=url),
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False,
            timeout=getattr(settings, "QDRANT_TIMEOUT_SECONDS", 10)
        )

        chunks: List[str] = []

        for point in results:
            if point.payload and "page_content" in point.payload:
                chunks.append(point.payload["page_content"])

        logger.info(
            "Scroll complete | url=%s | chunks_found=%d",
            url,
            len(chunks),
        )

        return chunks

    except Exception as e:
        logger.error(
            "Qdrant scroll failed | url=%s | error=%s",
            url,
            str(e),
        )
        raise


async def retrieve_all_chunks_for_mindmap(
    request: MindmapGenerationRequest,
) -> List[str]:
    """
    Retrieve content chunks from course/video/blog sources concurrently.

    Args:
        request: MindmapGenerationRequest containing source URLs

    Returns:
        List[str]: combined chunks from all available sources

    Raises:
        MindmapContentNotFoundError: if no content is found
    """

    sources = [
        ("course", request.best_course_url, CHUNKS_PER_COURSE),
        ("video", request.best_video_url, CHUNKS_PER_VIDEO),
        ("blog", request.best_blog_url, CHUNKS_PER_BLOG),
    ]

    tasks: List[Coroutine[Any, Any, List[str]]] = []
    labels: List[str] = []

    for label, url, limit in sources:
        if url:
            tasks.append(asyncio.to_thread(_scroll_chunks_by_url, url, limit))
            labels.append(label)

    logger.info(
        "Retrieving chunks | subtopic=%s | sources=%s",
        request.subtopic_name,
        labels,
    )

    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_chunks: List[str] = []
    errors: List[Exception] = []
    for label, result in zip(labels, results, strict=True):
        if isinstance(result, Exception):
            logger.error("Source '%s' failed | error=%s", label, str(result))
            errors.append(result)
            continue
        chunks: List[str] = result  # type: ignore  
        if chunks:
            logger.info(
                "Source '%s' returned %d chunks",
                label,
                len(chunks),
            )
            all_chunks.extend(chunks)
        else:
            logger.warning(
                "Source '%s' returned no chunks | subtopic=%s",
                label,
                request.subtopic_name,
            )
    if not all_chunks:
        if errors:
            raise errors[0]
        logger.error(
            "No chunks found across all sources | subtopic=%s",
            request.subtopic_name,
        )
        raise MindmapContentNotFoundError(
            MindmapContentNotFoundError.DEFAULT_MESSAGE
        )


    logger.info(
        "Total chunks collected | count=%d | subtopic=%s",
        len(all_chunks),
        request.subtopic_name,
    )

    return all_chunks


