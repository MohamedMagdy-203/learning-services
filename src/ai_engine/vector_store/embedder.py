import logging
from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore
from src.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings(model_name=settings.EMBEDDING_MODEL) -> HuggingFaceEmbeddings:  # type: ignore
    global _embeddings
    if _embeddings is None:
        logger.info("Loading embedding model: %s", model_name)
        _embeddings = HuggingFaceEmbeddings(model_name=model_name)  # type: ignore
    return _embeddings  # type: ignore
