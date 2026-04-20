import logging
from typing import Dict, Any, List
from langchain_core.documents import Document  # type: ignore
import re
from src.ai_engine.vector_store.filters import is_url_already_stored
from src.ai_engine.text_processing.chunker import chunk_text
import asyncio

logger = logging.getLogger(__name__)


def _clean_video_transcript(raw_content: str) -> str:
    raw_content = raw_content.replace("\n", " ")
    raw_content = re.sub(
        r"(?<!\w)(um|uh|ah|you know)(?!\w)", "", raw_content, flags=re.IGNORECASE
    )
    return re.sub(r"[ \t]+", " ", raw_content).strip()


async def _process_single_source(
    source_type: str, source_data: Dict[str, Any]
) -> List[Document]:
    """Helper function to process a single source concurrently."""
    url: str = source_data.get("url", "Unknown URL")

    # Run the DB check in a thread so it doesn't block
    if url != "Unknown URL" and await asyncio.to_thread(is_url_already_stored, url):
        logger.info("URL already exists in Qdrant, skipping: %s", url)
        return []

    title: str = source_data.get("title", "Unknown Title")
    raw_content: str = source_data.get("raw_content", "")

    if not raw_content:
        return []

    logger.info("Processing new content %s: '%s'", source_type, title)
    if source_type == "best_video":
        raw_content = _clean_video_transcript(raw_content)

    # Chunking happens in a thread (Semantic Chunking is CPU-bound)
    chunks: List[str] = await asyncio.to_thread(chunk_text, raw_content)

    return [
        Document(
            page_content=chunk,
            metadata={
                "source_type": source_type,
                "title": title,
                "url": url,
            },
        )
        for chunk in chunks
    ]


async def prepare_documents(reranker_data: Dict[str, Any]) -> List[Document]:  # type: ignore
    sources: List[str] = ["best_course", "best_video", "best_blog"]
    tasks = []

    # Launch all sources concurrently instead of sequentially
    for source_type in sources:
        source_data = reranker_data.get(source_type)
        if source_data and source_data.get("raw_content"):
            tasks.append(_process_single_source(source_type, source_data))

    # Wait for all 3 tasks to finish at the same time
    results = await asyncio.gather(*tasks)

    # Flatten the list of lists into a single list of Documents
    all_documents = [doc for sublist in results for doc in sublist]

    return all_documents
