import logging
from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore

logger = logging.getLogger(__name__)

EMBEDDING_MODEL: str = "paraphrase-multilingual-mpnet-base-v2"

_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:  # type: ignore
    global _embeddings
    if _embeddings is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)  # type: ignore
    return _embeddings  # type: ignore
