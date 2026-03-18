from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams  # type: ignore

from src.core.config import get_settings

VECTOR_SIZE: int = 768


def get_qdrant_client() -> QdrantClient:  # type: ignore
    return QdrantClient(url=get_settings().QDRANT_URL)  # type: ignore


def ensure_collection_exists() -> None:
    settings = get_settings()
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]  # type: ignore
    if settings.QDRANT_COLLECTION_NAME not in existing:
        client.create_collection(  # type: ignore
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),  # type: ignore
        )
