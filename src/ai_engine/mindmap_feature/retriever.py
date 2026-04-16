import asyncio
import logging
from typing import List, Coroutine, Any
from qdrant_client.models import Filter, FieldCondition, MatchValue
from src.ai_engine.vector_store.qdrant_client import get_qdrant_client
from src.core.config import get_settings, Settings
from src.core.exceptions import MindmapContentNotFoundError, MindmapRetrievalError
from src.models.schemas import MindmapGenerationRequest
from pydantic import HttpUrl
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)

# Maximum number of chunks to fetch for the primary URL
CHUNKS_PER_PRIMARY_URL = 50

# Explicit hardcoded timeout — not implied to be configurable via settings
QDRANT_SCROLL_TIMEOUT_SECONDS: int = 10


def _scroll_chunks_by_url(
    client, settings, primary_url: HttpUrl, limit: int
) -> List[str]:
    """
    Fetch up to ``limit`` stored chunks for a single source URL using one
    Qdrant scroll call.
    Args:
        url: the exact URL stored in metadata.url during ingestion
        limit: maximum number of chunks to retrieve for this source
    Returns:
        List[str]: page_content strings belonging to this URL, capped by
        ``limit``
    """

    try:
        results, _ = client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.url",
                        match=MatchValue(value=str(primary_url)),
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False,
            timeout=QDRANT_SCROLL_TIMEOUT_SECONDS,
        )

        chunks: List[str] = []

        for point in results:
            if not point.payload:
                continue
            content = point.payload.get("page_content")
            if isinstance(content, str):
                chunks.append(content)
            elif content is not None:
                logger.warning(
                    "Skipping non-string page_content | url=%s | type=%s",
                    primary_url,
                    type(content).__name__,
                )

        logger.info(
            "Scroll complete | url=%s | chunks_found=%d",
            primary_url,
            len(chunks),
        )

        return chunks

    except Exception as e:
        logger.error(
            "Qdrant scroll failed | url=%s | error=%s",
            primary_url,
            str(e),
        )
        raise


async def retrieve_all_chunks_for_mindmap(
    request: MindmapGenerationRequest,
    client: QdrantClient | None = None,
    settings: Settings | None = None,
) -> List[str]:
    """
    Retrieve content chunks from the vector store for the primary source URL.

    Args:
        request: MindmapGenerationRequest containing the primary_url.
        client: Optional QdrantClient instance (injected).
        settings: Optional Settings instance (injected).

    Returns:
        List[str]: Retrieved chunks for the primary source.

    Raises:
        MindmapRetrievalError: if the Qdrant fetch fails.
        MindmapContentNotFoundError: if the fetch succeeds but returns no chunks.
    """
    client = client or get_qdrant_client()
    settings = settings or get_settings()

    sources = [
        ("PRIMARY_URL", request.primary_url, CHUNKS_PER_PRIMARY_URL),
    ]

    tasks: List[Coroutine[Any, Any, List[str]]] = []
    labels: List[str] = []

    for label, primary_url, limit in sources:
        if primary_url:
            tasks.append(
                asyncio.to_thread(
                    _scroll_chunks_by_url, client, settings, primary_url, limit
                )
            )
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

    # Qdrant/network failure — surfaces as service error, not "content not found"
    if errors and not all_chunks:
        logger.error(
            "All source retrievals failed | subtopic=%s | first_error=%s",
            request.subtopic_name,
            str(errors[0]),
        )
        raise MindmapRetrievalError(MindmapRetrievalError.DEFAULT_MESSAGE) from errors[
            0
        ]

    # The fetch succeeded but the primary source returned zero chunks
    if not all_chunks:
        logger.error(
            "No chunks found across all sources | subtopic=%s",
            request.subtopic_name,
        )
        raise MindmapContentNotFoundError(MindmapContentNotFoundError.DEFAULT_MESSAGE)

    logger.info(
        "Total chunks collected | count=%d | subtopic=%s",
        len(all_chunks),
        request.subtopic_name,
    )

    return all_chunks
