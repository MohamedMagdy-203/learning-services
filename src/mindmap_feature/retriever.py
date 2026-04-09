import asyncio
import logging
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


def _scroll_chunks_by_url(url: str, limit: int) -> list[str]:
    """
    Fetch all stored chunks for a single source URL using Qdrant scroll.

    We use scroll (not similarity_search) because we already know the exact
    URL — we want ALL content from that source, not a ranked subset.

    Args:
        url:   the exact URL stored in metadata.url during ingestion.
        limit: maximum number of chunks to retrieve for this source.

    Returns:
        A list of page_content strings for the given URL.
        Returns an empty list if the URL is not found in the collection.
    """
    client = get_qdrant_client()

    try:
        results, _ = client.scroll(
            collection_name=get_settings().QDRANT_COLLECTION_NAME,
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
        )

        chunks = [
            point.payload["page_content"]
            for point in results
            if point.payload and "page_content" in point.payload
        ]

        logger.info(
            "Scroll complete | url: %s | chunks found: %d",
            url,
            len(chunks),
        )
        return chunks

    except Exception:
        logger.exception("Qdrant scroll failed | url: %s", url)
        return []


async def retrieve_all_chunks_for_mindmap(
    request: MindmapGenerationRequest,
) -> list[str]:
    """
    Retrieve content chunks for all available source URLs in parallel.

    Fetches chunks from best_course_url, best_video_url, and best_blog_url
    concurrently using asyncio.to_thread (scroll is a blocking call).
    URLs that are None or return no chunks are skipped gracefully.

    If NO chunks are found across all three sources, raises
    MindmapContentNotFoundError — the router will translate this to a 404.

    Args:
        request: the full mindmap generation request containing the 3 URLs.

    Returns:
        A combined list of page_content strings from all available sources.

    Raises:
        MindmapContentNotFoundError: if all three sources return no content.
    """
    sources = [
        (request.best_course_url, CHUNKS_PER_COURSE, "course"),
        (request.best_video_url, CHUNKS_PER_VIDEO, "video"),
        (request.best_blog_url, CHUNKS_PER_BLOG, "blog"),
    ]

    # Only scroll URLs that were actually provided
    tasks = [
        asyncio.to_thread(_scroll_chunks_by_url, url, limit)
        for url, limit, _ in sources
        if url is not None
    ]

    source_labels = [
        label
        for _, _, label in sources
        if sources[[s[2] for s in sources].index(label)][0] is not None
    ]

    logger.info(
        "Retrieving chunks | subtopic: %s | sources: %s",
        request.subtopic_name,
        source_labels,
    )

    results = await asyncio.gather(*tasks)

    all_chunks: list[str] = []
    for label, chunks in zip(source_labels, results):
        if chunks:
            logger.info("Source '%s' — %d chunks retrieved", label, len(chunks))
            all_chunks.extend(chunks)
        else:
            logger.warning(
                "Source '%s' returned no chunks — skipping | subtopic: %s",
                label,
                request.subtopic_name,
            )

    if not all_chunks:
        logger.error(
            "No chunks found across all sources | subtopic: %s",
            request.subtopic_name,
        )
        raise MindmapContentNotFoundError(
            MindmapContentNotFoundError.DEFAULT_MESSAGE
        )

    logger.info(
        "Total chunks collected | count: %d | subtopic: %s",
        len(all_chunks),
        request.subtopic_name,
    )

    return all_chunks