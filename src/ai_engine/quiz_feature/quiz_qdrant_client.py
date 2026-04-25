from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams  # type: ignore
import threading
from src.core.config import get_settings

VECTOR_SIZE: int = 1

_client: AsyncQdrantClient | None = None
_client_lock = threading.Lock()


def get_quiz_qdrant_client() -> AsyncQdrantClient:  # type: ignore
    global _client

    if _client is None:
        with _client_lock:
            if _client is None:
                settings = get_settings()
                _client = AsyncQdrantClient(url=settings.QDRANT_URL)
    return _client


async def ensure_quiz_collection_exists() -> None:
    settings = get_settings()
    client = get_quiz_qdrant_client()

    existing = await client.get_collections()
    names = [c.name for c in existing.collections]

    if settings.QUIZ_COLLECTION_NAME not in names:
        await client.create_collection(
            collection_name=settings.QUIZ_COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
