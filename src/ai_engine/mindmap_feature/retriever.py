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

PRIMARY_URL_CHUNKS_LIMIT = 50
SECONDARY_URL_CHUNKS_LIMIT = 20
QDRANT_SCROLL_TIMEOUT_SECONDS: int = 10


def _scroll_chunks_by_url(client, settings, url: HttpUrl, limit: int) -> List[str]:
    try:
        results, _ = client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.url",
                        match=MatchValue(value=str(url)),
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
                    url,
                    type(content).__name__,
                )

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
    client: QdrantClient | None = None,
    settings: Settings | None = None,
) -> List[str]:
    client = client or get_qdrant_client()
    settings = settings or get_settings()

    # primary_url gets higher limit, secondary URLs get lower limit
    sources = [
        (
            str(request.primary_url),
            PRIMARY_URL_CHUNKS_LIMIT,
        )
    ]

    tasks: List[Coroutine[Any, Any, List[str]]] = [
        asyncio.to_thread(_scroll_chunks_by_url, client, settings, url, limit)
        for url, limit in sources
    ]

    logger.info(
        "Retrieving chunks | subtopic=%s | urls=%d",
        request.subtopic_name,
        len(sources),
    )

    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_chunks: List[str] = []
    errors: List[Exception] = []

    for (url, _), result in zip(sources, results):
        if isinstance(result, Exception):
            logger.error("URL '%s' failed | error=%s", url, str(result))
            errors.append(result)
            continue
        chunks: List[str] = result  # type: ignore
        if chunks:
            logger.info("URL '%s' returned %d chunks", url, len(chunks))
            all_chunks.extend(chunks)
        else:
            logger.warning(
                "URL '%s' returned no chunks | subtopic=%s",
                url,
                request.subtopic_name,
            )

    if errors and not all_chunks:
        logger.error(
            "All URL retrievals failed | subtopic=%s | first_error=%s",
            request.subtopic_name,
            str(errors[0]),
        )
        raise MindmapRetrievalError(MindmapRetrievalError.DEFAULT_MESSAGE) from errors[
            0
        ]

    if not all_chunks:
        logger.error(
            "No chunks found across all URLs | subtopic=%s",
            request.subtopic_name,
        )
        raise MindmapContentNotFoundError(MindmapContentNotFoundError.DEFAULT_MESSAGE)

    logger.info(
        "Total chunks collected | count=%d | subtopic=%s",
        len(all_chunks),
        request.subtopic_name,
    )
    return all_chunks
