import logging
from qdrant_client.models import Filter, FieldCondition, MatchValue  # type: ignore
from .qdrant_client import get_qdrant_client
from src.core.config import get_settings

logger = logging.getLogger(__name__)


def is_url_already_stored(url: str) -> bool:
    client = get_qdrant_client()

    try:
        response, _ = client.scroll(  # type: ignore
            collection_name=get_settings().QDRANT_COLLECTION_NAME,
            scroll_filter=Filter(
                must=[FieldCondition(key="metadata.url", match=MatchValue(value=url))]
            ),
            limit=1,
            with_payload=False,
            with_vectors=False,
        )
        return len(response) > 0  # type: ignore

    except Exception as e:
        logger.warning(
            "Could not filter URL (Collection might not exist yet): %s", str(e)
        )
        return False
