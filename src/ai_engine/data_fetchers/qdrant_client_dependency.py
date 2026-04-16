from qdrant_client import AsyncQdrantClient
from src.core.config import get_settings

qdrant_client_dependency: AsyncQdrantClient | None = None


async def init_qdrant_client():
    """
    Initialize a single shared Qdrant client instance.
    Runs once at app startup.
    """
    global qdrant_client_dependency
    settings = get_settings()

    qdrant_client_dependency = AsyncQdrantClient(url=settings.QDRANT_URL)


async def close_qdrant_client():
    """
    Close Qdrant client on app shutdown.
    """
    global qdrant_client_dependency

    if qdrant_client_dependency:
        await qdrant_client_dependency.close()


def get_qdrant_client_dependency() -> AsyncQdrantClient:
    """
    Get initialized Qdrant client.
    """
    if qdrant_client_dependency is None:
        raise RuntimeError("Qdrant client is not initialized")

    return qdrant_client_dependency
