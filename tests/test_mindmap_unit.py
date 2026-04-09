import json
import pytest
from unittest.mock import patch

from src.core.mock_data import (
    MOCK_MINDMAP_REQUEST,
    MOCK_MINDMAP_REQUEST_ONE_SOURCE,
    MOCK_MINDMAP_REQUEST_NO_SOURCES,
    MOCK_MINDMAP_CHUNKS,
    MOCK_MINDMAP_RESPONSE,
)
from src.models.schemas import MindmapGenerationRequest

MOCK_MINDMAP_JSON = json.dumps(MOCK_MINDMAP_RESPONSE)


@pytest.fixture
def request_all_sources() -> MindmapGenerationRequest:
    return MindmapGenerationRequest(**MOCK_MINDMAP_REQUEST)


@pytest.fixture
def request_one_source() -> MindmapGenerationRequest:
    return MindmapGenerationRequest(**MOCK_MINDMAP_REQUEST_ONE_SOURCE)


@pytest.fixture
def request_no_sources() -> MindmapGenerationRequest:
    return MindmapGenerationRequest(**MOCK_MINDMAP_REQUEST_NO_SOURCES)


class TestMindmapRetriever:
    @pytest.mark.asyncio
    async def test_skips_none_urls(
        self, request_one_source: MindmapGenerationRequest
    ) -> None:
        from src.mindmap_feature.retriever import retrieve_all_chunks_for_mindmap

        with patch(
            "src.mindmap_feature.retriever._scroll_chunks_by_url",
            return_value=MOCK_MINDMAP_CHUNKS,
        ):
            chunks = await retrieve_all_chunks_for_mindmap(request_one_source)

        assert len(chunks) == len(MOCK_MINDMAP_CHUNKS)

    @pytest.mark.asyncio
    async def test_raises_when_no_sources(
        self, request_no_sources: MindmapGenerationRequest
    ) -> None:
        from src.mindmap_feature.retriever import retrieve_all_chunks_for_mindmap
        from src.core.exceptions import MindmapContentNotFoundError

        with pytest.raises(MindmapContentNotFoundError):
            await retrieve_all_chunks_for_mindmap(request_no_sources)

    @pytest.mark.asyncio
    async def test_raises_when_all_urls_return_empty(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.mindmap_feature.retriever import retrieve_all_chunks_for_mindmap
        from src.core.exceptions import MindmapContentNotFoundError

        with patch(
            "src.mindmap_feature.retriever._scroll_chunks_by_url",
            return_value=[],
        ):
            with pytest.raises(MindmapContentNotFoundError):
                await retrieve_all_chunks_for_mindmap(request_all_sources)

    @pytest.mark.asyncio
    async def test_combines_chunks_from_all_sources(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.mindmap_feature.retriever import retrieve_all_chunks_for_mindmap

        with patch(
            "src.mindmap_feature.retriever._scroll_chunks_by_url",
            return_value=MOCK_MINDMAP_CHUNKS,
        ):
            chunks = await retrieve_all_chunks_for_mindmap(request_all_sources)

        assert len(chunks) == len(MOCK_MINDMAP_CHUNKS) * 3
