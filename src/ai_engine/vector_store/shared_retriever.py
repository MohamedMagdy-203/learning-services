import asyncio
import logging
from typing import List
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from langchain_core.documents import Document
from src.core.config import Settings
from src.core.exceptions import NoContentFoundError

logger = logging.getLogger(__name__)


def build_metadata(payload: dict) -> dict:
    raw_meta = payload.get("metadata", {})
    return {
        "source_type": raw_meta.get("source_type", payload.get("source_type")),
        "title": raw_meta.get("title", payload.get("title")),
        "url": raw_meta.get("url", payload.get("url")),
    }


async def _scroll_documents_by_url(
    url: str, client: AsyncQdrantClient, settings: Settings, limit: int
) -> List[Document]:
    all_documents: List[Document] = []
    next_page_offset = None

    try:
        while True:
            scroll_result, next_page_offset = await client.scroll(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="metadata.url", match=MatchValue(value=url))
                    ]
                ),
                limit=limit - len(all_documents),
                with_payload=True,
                with_vectors=False,
                offset=next_page_offset,
            )

            for record in scroll_result:
                if record.payload and "page_content" in record.payload:
                    all_documents.append(
                        Document(
                            page_content=record.payload["page_content"],
                            metadata=build_metadata(record.payload),
                        )
                    )

            if next_page_offset is None or len(all_documents) >= limit:
                break

        return all_documents[:limit]
    except Exception as e:
        logger.error("Qdrant scroll failed | url=%s | error=%s", url, str(e))
        raise


async def retrieve_content_chunks(
    primary_url: str,
    secondary_urls: List[str],
    client: AsyncQdrantClient,
    settings: Settings,
) -> List[Document]:
    logger.info("Retrieving chunks | primary_url=%s", primary_url)
    all_documents: List[Document] = []

    try:
        primary_docs = await _scroll_documents_by_url(
            url=primary_url,
            client=client,
            settings=settings,
            limit=settings.PRIMARY_URL_CHUNKS_LIMIT,
        )
        all_documents.extend(primary_docs)
    except Exception as exc:
        logger.error("Primary URL retrieval failed | error=%s", str(exc))

    if len(all_documents) < settings.PRIMARY_URL_CHUNKS_LIMIT and secondary_urls:
        logger.info(
            "Primary URL yielded %d chunks. Fetching from secondary URLs...",
            len(all_documents),
        )

        tasks = [
            _scroll_documents_by_url(
                url=url,
                client=client,
                settings=settings,
                limit=settings.SECONDARY_URL_CHUNKS_LIMIT,
            )
            for url in secondary_urls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for url, res in zip(secondary_urls, results):
            if isinstance(res, Exception):
                logger.error("Secondary URL '%s' failed", url)
                continue
            if res:
                all_documents.extend(res)  # type: ignore

        all_documents = all_documents[: settings.PRIMARY_URL_CHUNKS_LIMIT]

    if not all_documents:
        raise NoContentFoundError("No content found across all URLs.")

    logger.info("Total chunks collected | count=%d", len(all_documents))
    return all_documents
