import logging
from typing import List

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from langchain_core.documents import Document

from src.core.config import Settings
from src.core.exceptions import NoContentFoundError
from src.core.messages import (
    RETRIEVE_CHUNKS_START,
    RETRIEVE_CHUNKS_SUCCESS,
    RETRIEVE_CHUNKS_ERROR,
    NO_CONTENT_FOUND,
    QDRANT_RETRIEVE_FAILED,
)

logger = logging.getLogger(__name__)


def build_metadata(payload: dict) -> dict:
    """
    Extracts and standardizes metadata fields from Qdrant payload
    to ensure consistent structure for downstream processing.
    """
    raw_meta = payload.get("metadata", {})

    return {
        "source_type": raw_meta.get("source_type", payload.get("source_type")),
        "title": raw_meta.get("title", payload.get("title")),
        "url": raw_meta.get("url", payload.get("url")),
    }


async def retrieve_chunks_by_url(
    primary_url: str,
    client: AsyncQdrantClient,
    settings: Settings,
    limit: int = 100,
) -> List[Document]:
    logger.info(RETRIEVE_CHUNKS_START, primary_url)

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
                            match=MatchValue(value=primary_url),
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
            raise NoContentFoundError(NO_CONTENT_FOUND.format(url=primary_url))

        logger.info(RETRIEVE_CHUNKS_SUCCESS, len(all_documents), primary_url)
        return all_documents

    except NoContentFoundError:
        raise

    except Exception as e:
        logger.error(RETRIEVE_CHUNKS_ERROR, primary_url, e)
        raise RuntimeError(QDRANT_RETRIEVE_FAILED.format(error=str(e))) from e
