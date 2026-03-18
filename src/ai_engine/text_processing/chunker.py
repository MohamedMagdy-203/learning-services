import logging
from langchain_experimental.text_splitter import SemanticChunker  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
from src.ai_engine.vector_store.embedder import get_embeddings  # type: ignore

logger = logging.getLogger(__name__)

MAX_CHAR_LIMIT = 1500

_fallback_splitter = RecursiveCharacterTextSplitter(  # type: ignore
    chunk_size=MAX_CHAR_LIMIT,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", "،", " ", ""],
)


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

    semantic_chunks = splitter.split_text(raw_content)  # type: ignore
    final_chunks = []

    for chunk in semantic_chunks:  # type: ignore
        if len(chunk) > MAX_CHAR_LIMIT:  # type: ignore
            sub_chunks = _fallback_splitter.split_text(chunk)  # type: ignore
            final_chunks.extend(sub_chunks)  # type: ignore
        else:
            final_chunks.append(chunk)  # type: ignore

    logger.info("Chunking done | chunks produced: %d", len(final_chunks))  # type: ignore
    return final_chunks  # type: ignore
