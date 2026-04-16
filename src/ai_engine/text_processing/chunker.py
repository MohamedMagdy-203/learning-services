import logging
from langchain_experimental.text_splitter import SemanticChunker  # type: ignore
from src.ai_engine.vector_store.embedder import get_embeddings  # type: ignore

logger = logging.getLogger(__name__)


def chunk_text(raw_content: str) -> list[str]:
    """
    Split raw_content into semantically coherent chunks.
    Uses a multilingual embedding model to detect topic boundaries,
    ensuring each chunk represents a single coherent idea.
    Works with both Arabic and English content.
    """
    logger.info("Chunking content | length: %d chars", len(raw_content))

    splitter = SemanticChunker(  # type: ignore
        embeddings=get_embeddings(),
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=85,
    )

    final_chunks = splitter.split_text(raw_content)  # type: ignore

    logger.info("Chunking done | chunks produced: %d", len(final_chunks))  # type: ignore
    return final_chunks  # type: ignore
