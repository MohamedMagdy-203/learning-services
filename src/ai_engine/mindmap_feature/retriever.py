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

    url_str = str(request.primary_url)
    logger.info(
        "Retrieving chunks | subtopic=%s | primary_url=%s",
        request.subtopic_name,
        url_str,
    )

    all_chunks: List[str] = []
    errors: List[Exception] = []

    try:
        # Step 1: Try to fetch strictly from primary URL
        primary_chunks = await asyncio.to_thread(
            _scroll_chunks_by_url,
            client,
            settings,
            request.primary_url,
            PRIMARY_URL_CHUNKS_LIMIT,
        )
        all_chunks.extend(primary_chunks)
    except Exception as exc:
        logger.error("Primary URL retrieval failed | error=%s", str(exc))
        errors.append(exc)

    # Step 2: Fallback logic - If primary is not enough, fetch from secondary URLs
    if len(all_chunks) < PRIMARY_URL_CHUNKS_LIMIT:
        secondary_urls = [url for url in request.urls if url != request.primary_url]

        if secondary_urls:
            logger.info(
                "Primary URL yielded %d chunks. Fetching from %d secondary URLs as fallback...",
                len(all_chunks),
                len(secondary_urls),
            )

            tasks: List[Coroutine[Any, Any, List[str]]] = [
                asyncio.to_thread(
                    _scroll_chunks_by_url,
                    client,
                    settings,
                    url,
                    SECONDARY_URL_CHUNKS_LIMIT,
                )
                for url in secondary_urls
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for url, res in zip(secondary_urls, results, strict=True):
                if isinstance(res, Exception):
                    logger.error("Secondary URL '%s' failed | error=%s", url, str(res))
                    continue

                chunks: List[str] = res  # type: ignore
                if chunks:
                    logger.info(
                        "Secondary URL '%s' returned %d chunks", url, len(chunks)
                    )
                    all_chunks.extend(chunks)

            # Cap total chunks to avoid exceeding LLM context window
            all_chunks = all_chunks[:PRIMARY_URL_CHUNKS_LIMIT]

    # Step 3: Handle complete failure
    if not all_chunks:
        if errors:
            raise MindmapRetrievalError(
                MindmapRetrievalError.DEFAULT_MESSAGE
            ) from errors[0]
        logger.error(
            "No chunks found across all URLs | subtopic=%s", request.subtopic_name
        )
        raise MindmapContentNotFoundError(MindmapContentNotFoundError.DEFAULT_MESSAGE)

    logger.info(
        "Total chunks collected | count=%d | subtopic=%s",
        len(all_chunks),
        request.subtopic_name,
    )
    return all_chunks
