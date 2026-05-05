import logging
import asyncio
from typing import List

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from langchain_core.documents import Document

from src.core.config import Settings
from src.core.exceptions import NoContentFoundError
from src.core.messages import (
    RETRIEVE_CHUNKS_START,
    RETRIEVE_CHUNKS_SUCCESS,
    RETRIEVE_ERROR,
    RETRIEVE_MULTI_URL_START,
    RETRIEVE_MULTI_URL_SUCCESS,
    RETRIEVE_MULTI_URL_SKIP_URL,
    NO_CONTENT_FOUND,
    NO_CONTENT_FOUND_PRIMARY,
    NO_CONTENT_FOUND_ALL,
    QDRANT_RETRIEVE_FAILED,
)

logger = logging.getLogger(__name__)


def build_metadata(payload: dict) -> dict:
    """
    Extracts and standardizes metadata fields from Qdrant payload
    to ensure consistent structure for downstream processing.
    """
    raw_meta = payload.get("metadata", {})

    url = raw_meta.get("url") or payload.get("url")

    return {
        "source_type": raw_meta.get("source_type", payload.get("source_type")),
        "title": raw_meta.get("title", payload.get("title")),
        "url": url,
    }


async def _retrieve_chunks_single_url(
    url: str,
    client: AsyncQdrantClient,
    settings: Settings,
    limit: int = 100,
) -> List[Document]:
    """
    Retrieve all chunks for a single URL.
    """

    logger.info(RETRIEVE_CHUNKS_START, url)

    all_documents: List[Document] = []
    next_page_offset = None

    try:
        while True:
            scroll_result, next_page_offset = await client.scroll(
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

            if next_page_offset is None:
                break

        if not all_documents:
            raise NoContentFoundError(NO_CONTENT_FOUND.format(url=url))

        logger.info(RETRIEVE_CHUNKS_SUCCESS, len(all_documents), url)
        return all_documents

    except NoContentFoundError:
        raise

    except Exception as e:
        logger.error(RETRIEVE_ERROR, url, str(e))
        raise RuntimeError(QDRANT_RETRIEVE_FAILED.format(error=str(e))) from e


async def retrieve_chunks_multi_urls(
    urls: List[str],
    primary_url: str,
    client: AsyncQdrantClient,
    settings: Settings,
    limit: int = 100,
) -> List[Document]:
    """
    Retrieve chunks from multiple URLs in parallel.
    """

    logger.info(RETRIEVE_MULTI_URL_START, urls)

    tasks = []
    url_map = {}

    for url in urls:
        task = asyncio.create_task(
            _retrieve_chunks_single_url(url, client, settings, limit)
        )
        tasks.append(task)
        url_map[task] = url

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_documents: List[Document] = []
    primary_found = False

    for task, result in zip(tasks, results):
        url = url_map[task]

        if isinstance(result, Exception):
            if url == primary_url:
                raise result
            else:
                logger.warning(RETRIEVE_MULTI_URL_SKIP_URL, url, str(result))
                continue

        for doc in result:
            is_primary = url == primary_url
            doc.metadata["is_primary"] = is_primary

            if is_primary:
                primary_found = True

            all_documents.append(doc)

    if not primary_found:
        raise NoContentFoundError(
            NO_CONTENT_FOUND_PRIMARY.format(primary_url=primary_url)
        )

    if not all_documents:
        raise NoContentFoundError(NO_CONTENT_FOUND_ALL)

    logger.info(RETRIEVE_MULTI_URL_SUCCESS, len(all_documents))
    return all_documents
