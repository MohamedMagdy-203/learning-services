import pytest
import logging

from src.core.mock_data import (
    MOCK_MINDMAP_REQUEST,
    MOCK_MINDMAP_REQUEST_ONE_SOURCE,
    # MOCK_MINDMAP_CHUNKS,
)
from src.models.schemas import MindmapGenerationRequest, MindmapNodeSchema

logger = logging.getLogger(__name__)

COURSE_URL = "https://www.udemy.com/course/the-complete-sql-bootcamp/"
VIDEO_URL = "https://www.youtube.com/watch?v=wR0jg0eQsZA"
BLOG_URL = "https://www.mongodb.com/nosql-explained/nosql-vs-sql"


@pytest.fixture
def request_all_sources() -> MindmapGenerationRequest:
    return MindmapGenerationRequest(**MOCK_MINDMAP_REQUEST)


@pytest.fixture
def request_one_source() -> MindmapGenerationRequest:
    return MindmapGenerationRequest(**MOCK_MINDMAP_REQUEST_ONE_SOURCE)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_retrieval_all_sources(
    request_all_sources: MindmapGenerationRequest,
) -> None:
    """Ensure the number of chunks per source does not exceed the limit."""
    from src.ai_engine.mindmap_feature.retriever import retrieve_all_chunks_for_mindmap

    chunks = await retrieve_all_chunks_for_mindmap(request_all_sources)

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) > 0 for chunk in chunks)

    logger.info("\n" + "=" * 60)
    logger.info("RETRIEVAL — ALL SOURCES")
    logger.info("=" * 60)
    logger.info("Total chunks: %d", len(chunks))
    for i, chunk in enumerate(chunks, 1):
        logger.info("\n--- [ Chunk %d ] ---", i)
        logger.info("Length : %d chars", len(chunk))
        logger.info("Preview: %s", chunk[:200])
    logger.info("=" * 60)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_retrieval_one_source(
    request_one_source: MindmapGenerationRequest,
) -> None:
    """Ensure the retriever works correctly when only one source is provided."""
    from src.ai_engine.mindmap_feature.retriever import retrieve_all_chunks_for_mindmap

    chunks = await retrieve_all_chunks_for_mindmap(request_one_source)

    assert isinstance(chunks, list)
    assert len(chunks) > 0

    logger.info("\n" + "=" * 60)
    logger.info("RETRIEVAL — ONE SOURCE")
    logger.info("=" * 60)
    logger.info("Total chunks: %d", len(chunks))
    logger.info("=" * 60)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_chunks_per_source_limits(
    request_all_sources: MindmapGenerationRequest,
) -> None:
    from src.ai_engine.mindmap_feature.retriever import (
        retrieve_all_chunks_for_mindmap,
        CHUNKS_PER_PRIMARY_URL,
    )

    chunks = await retrieve_all_chunks_for_mindmap(request_all_sources)

    max_total = CHUNKS_PER_PRIMARY_URL
    assert (
        len(chunks) <= max_total
    ), f"Expected at most {max_total} chunks, got {len(chunks)}"

    logger.info("\n" + "=" * 60)
    logger.info("CHUNKS LIMIT CHECK")
    logger.info("=" * 60)
    logger.info("Max allowed : %d", max_total)
    logger.info("Chunks got  : %d", len(chunks))
    logger.info("=" * 60)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_generation_pipeline(
    request_all_sources: MindmapGenerationRequest,
) -> None:
    from src.ai_engine.mindmap_feature.retriever import retrieve_all_chunks_for_mindmap
    from src.ai_engine.mindmap_feature.mindmap_generator import generate_mindmap

    chunks = await retrieve_all_chunks_for_mindmap(request_all_sources)

    assert len(chunks) > 0, "No chunks found — check Qdrant URLs"

    mindmap = await generate_mindmap(
        request=request_all_sources,
        chunks=chunks,
    )

    assert isinstance(mindmap, MindmapNodeSchema)
    assert mindmap.topic == request_all_sources.subtopic_name

    assert len(mindmap.children) >= 2, "Mindmap should have at least 2 main branches"
    assert len(mindmap.children) <= 15, "Mindmap has too many branches, might break UI"

    assert all(isinstance(branch.topic, str) for branch in mindmap.children)

    assert isinstance(mindmap.children[0].children, list)

    logger.info("\n" + "=" * 60)
    logger.info("FULL GENERATION PIPELINE")
    logger.info("=" * 60)
    logger.info("Root topic : %s", mindmap.topic)
    logger.info("Branches   : %d", len(mindmap.children))
    for branch in mindmap.children:
        logger.info("\n  Branch: %s", branch.topic)
        for child in branch.children:
            logger.info("    - %s", child.topic)
    logger.info("=" * 60)
