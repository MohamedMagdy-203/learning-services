from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams  # type: ignore

QDRANT_URL: str = "http://localhost:6333"
COLLECTION_NAME: str = "learning_materials"
VECTOR_SIZE: int = 768  # paraphrase-multilingual-mpnet-base-v2 dimensions


def get_qdrant_client() -> QdrantClient:  # type: ignore
    return QdrantClient(url=QDRANT_URL)  # type: ignore


def ensure_collection_exists() -> None:
    """Create the collection if it doesn't exist yet."""
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]  # type: ignore
    if COLLECTION_NAME not in existing:
        client.create_collection(  # type: ignore
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,  # type: ignore
            ),
        )
