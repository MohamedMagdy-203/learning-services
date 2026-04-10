from typing import List
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from src.core.config import get_settings
from src.core.exceptions import NoContentFoundError


def get_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(url=get_settings().QDRANT_URL)


async def retrieve_chunks_by_url(url: str) -> List[str]:
    """
    Retrieves ALL text chunks from Qdrant based on a given URL using pagination (Asynchronously).
    """
    client = get_qdrant_client()
    settings = get_settings()

    chunks = []
    next_page_offset = None

    while True:
        search_result, next_page_offset = await client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            scroll_filter=Filter(
                must=[FieldCondition(key="metadata.url", match=MatchValue(value=url))]
            ),
            limit=100,
            with_payload=True,
            with_vectors=False,
            offset=next_page_offset,
        )

        for point in search_result:
            if point.payload and "page_content" in point.payload:
                chunks.append(point.payload["page_content"])

        if next_page_offset is None:
            break

    if not chunks:
        raise NoContentFoundError(f"No content found for URL: {url}")

    return chunks
