from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams  # type: ignore
import threading
from src.core.config import get_settings

# Must match the embedding model dimension in embedder.py
# Current model: paraphrase-multilingual-mpnet-base-v2 → 768 dims
# If you change the model, delete the Qdrant collection and recreate it
VECTOR_SIZE: int = 768

# Cached singleton client
_client: QdrantClient | None = None
_client_lock = threading.Lock()


def get_qdrant_client() -> QdrantClient:  # type: ignore
    """
    Returns a shared Qdrant client instance.

    Creating a new client for every call can lead to many open
    connections under concurrency. This function caches a single
    client instance and reuses it across the application.
    """
    global _client

    if _client is None:
        with _client_lock:
            if _client is None:
                settings = get_settings()
                _client = QdrantClient(url=settings.QDRANT_URL)
    return _client


def ensure_collection_exists() -> None:
    settings = get_settings()
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]  # type: ignore
    if settings.QDRANT_COLLECTION_NAME not in existing:
        client.create_collection(  # type: ignore
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),  # type: ignore
        )
