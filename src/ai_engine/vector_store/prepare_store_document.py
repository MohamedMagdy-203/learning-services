import logging
from typing import Dict, Any, List
from langchain_core.documents import Document  # type: ignore

from src.ai_engine.vector_store.filters import is_url_already_stored
from src.ai_engine.text_processing.chunker import chunk_text
import asyncio

logger = logging.getLogger(__name__)


async def prepare_documents(reranker_data: Dict[str, Any]) -> List[Document]:  # type: ignore
    user_id: str = reranker_data.get("user_id", "unknown_user")
    subtopic_id: str = reranker_data.get("subtopic_id", "unknown_subtopic")

    all_documents: List[Document] = []  # type: ignore
    sources: List[str] = ["best_course", "best_video", "best_blog"]

    for source_type in sources:
        source_data = reranker_data.get(source_type)
        if not source_data or not source_data.get("raw_content"):
            continue

        url: str = source_data.get("url", "Unknown URL")

        if url != "Unknown URL" and is_url_already_stored(url):
            logger.info("URL already exists in Qdrant, skipping: %s", url)
            continue

        title: str = source_data.get("title", "Unknown Title")
        raw_content: str = source_data["raw_content"]

        logger.info("Processing new content %s: '%s'", source_type, title)

        chunks: List[str] = await asyncio.to_thread(chunk_text, raw_content)

        for chunk in chunks:
            all_documents.append(  # type: ignore
                Document(
                    page_content=chunk,
                    metadata={
                        "user_id": user_id,
                        "subtopic_id": subtopic_id,
                        "source_type": source_type,
                        "title": title,
                        "url": url,
                    },
                )  # type: ignore
            )
    return all_documents  # type: ignore
