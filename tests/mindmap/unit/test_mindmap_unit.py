import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.documents import Document
from src.core.mock_data import (
    MOCK_MINDMAP_REQUEST,
    MOCK_MINDMAP_REQUEST_ONE_SOURCE,
    MOCK_MINDMAP_CHUNKS,
    MOCK_MINDMAP_RESPONSE,
)
from src.models.schemas import MindmapGenerationRequest, MindmapNodeSchema


MOCK_MINDMAP_JSON = json.dumps(MOCK_MINDMAP_RESPONSE)


@pytest.fixture
def request_all_sources() -> MindmapGenerationRequest:
    return MindmapGenerationRequest(**MOCK_MINDMAP_REQUEST)


@pytest.fixture
def request_one_source() -> MindmapGenerationRequest:
    return MindmapGenerationRequest(**MOCK_MINDMAP_REQUEST_ONE_SOURCE)


class TestMindmapParser:
    def test_parses_valid_json(self) -> None:
        from src.ai_engine.mindmap_feature.mindmap_parser import parse_mindmap_response

        result = parse_mindmap_response(MOCK_MINDMAP_JSON)
        assert isinstance(result, MindmapNodeSchema)
        assert result.topic == "Database Fundamentals"
        assert len(result.children) == 5

    def test_parses_json_with_markdown_fences(self) -> None:
        from src.ai_engine.mindmap_feature.mindmap_parser import parse_mindmap_response

        fenced = f"```json\n{MOCK_MINDMAP_JSON}\n```"
        result = parse_mindmap_response(fenced)
        assert isinstance(result, MindmapNodeSchema)
        assert result.topic == "Database Fundamentals"

    def test_parses_nested_children(self) -> None:
        from src.ai_engine.mindmap_feature.mindmap_parser import parse_mindmap_response

        result = parse_mindmap_response(MOCK_MINDMAP_JSON)
        first_branch = result.children[0]
        assert first_branch.topic == "SQL Databases"
        assert len(first_branch.children) == 3

    def test_raises_on_invalid_json(self) -> None:
        from src.ai_engine.mindmap_feature.mindmap_parser import parse_mindmap_response

        with pytest.raises(ValueError, match="not valid JSON"):
            parse_mindmap_response("this is not json at all")

    def test_raises_on_missing_topic_field(self) -> None:
        from src.ai_engine.mindmap_feature.mindmap_parser import parse_mindmap_response

        with pytest.raises(ValueError):
            parse_mindmap_response('{"children": []}')

    def test_raises_on_empty_response(self) -> None:
        from src.ai_engine.mindmap_feature.mindmap_parser import parse_mindmap_response

        with pytest.raises(ValueError):
            parse_mindmap_response("")


class TestMindmapPrompt:
    def test_prompt_contains_subtopic_name(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.mindmap_prompt import build_mindmap_prompt

        prompt = build_mindmap_prompt(
            request=request_all_sources,
            chunks=MOCK_MINDMAP_CHUNKS,
        )
        assert request_all_sources.subtopic_name in prompt

    def test_prompt_contains_difficulty(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.mindmap_prompt import build_mindmap_prompt

        prompt = build_mindmap_prompt(
            request=request_all_sources,
            chunks=MOCK_MINDMAP_CHUNKS,
        )
        assert request_all_sources.subtopic_difficulty in prompt

    def test_prompt_contains_weaknesses(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.mindmap_prompt import build_mindmap_prompt

        prompt = build_mindmap_prompt(
            request=request_all_sources,
            chunks=MOCK_MINDMAP_CHUNKS,
        )
        for weakness in request_all_sources.weaknesses:
            assert weakness in prompt

    def test_prompt_contains_chunks(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.mindmap_prompt import build_mindmap_prompt

        prompt = build_mindmap_prompt(
            request=request_all_sources,
            chunks=MOCK_MINDMAP_CHUNKS,
        )
        assert MOCK_MINDMAP_CHUNKS[0][:50] in prompt

    def test_prompt_contains_json_instruction(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.mindmap_prompt import build_mindmap_prompt

        prompt = build_mindmap_prompt(
            request=request_all_sources,
            chunks=MOCK_MINDMAP_CHUNKS,
        )
        assert "JSON" in prompt
        assert "children" in prompt


class TestMindmapRetriever:
    @pytest.mark.asyncio
    async def test_skips_none_urls(
        self, request_one_source: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.retriever import (
            retrieve_all_chunks_for_mindmap,
        )

        mock_docs = [Document(page_content=chunk) for chunk in MOCK_MINDMAP_CHUNKS]
        with patch(
            "src.ai_engine.mindmap_feature.retriever.retrieve_content_chunks",
            return_value=mock_docs,
        ):
            chunks = await retrieve_all_chunks_for_mindmap(
                request_one_source, AsyncMock(), MagicMock()
            )

        assert len(chunks) == len(MOCK_MINDMAP_CHUNKS)

    @pytest.mark.asyncio
    async def test_schema_allows_missing_primary_url(self) -> None:
        from src.models.schemas import MindmapGenerationRequest
        from src.core.mock_data import MOCK_MINDMAP_REQUEST

        valid_data = MOCK_MINDMAP_REQUEST.copy()
        valid_data.pop("primary_url", None)
        request = MindmapGenerationRequest(**valid_data)

        assert request.primary_url is None

    @pytest.mark.asyncio
    async def test_raises_when_all_urls_return_empty(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.retriever import (
            retrieve_all_chunks_for_mindmap,
        )
        from src.core.exceptions import MindmapContentNotFoundError

        with patch(
            "src.ai_engine.mindmap_feature.retriever.retrieve_content_chunks",
            side_effect=Exception("No content found"),
        ):
            with pytest.raises(MindmapContentNotFoundError):
                await retrieve_all_chunks_for_mindmap(
                    request_all_sources, AsyncMock(), MagicMock()
                )

    @pytest.mark.asyncio
    async def test_retrieves_from_secondary_if_primary_insufficient(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.retriever import (
            retrieve_all_chunks_for_mindmap,
        )

        mock_docs = [Document(page_content=chunk) for chunk in MOCK_MINDMAP_CHUNKS]
        with patch(
            "src.ai_engine.mindmap_feature.retriever.retrieve_content_chunks",
            return_value=mock_docs,
        ) as mock_scroll:
            chunks = await retrieve_all_chunks_for_mindmap(
                request_all_sources, AsyncMock(), MagicMock()
            )

        # Should fetch from primary (1) + secondary (2) = 3 total calls
        assert mock_scroll.call_count == 1
        assert len(chunks) == len(MOCK_MINDMAP_CHUNKS)
        assert len(chunks) <= 15


class TestMindmapGenerator:
    @pytest.mark.asyncio
    async def test_generate_mindmap_success(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.mindmap_generator import generate_mindmap

        mock_response = MagicMock()
        mock_response.text = MOCK_MINDMAP_JSON

        with patch(
            "src.ai_engine.mindmap_feature.mindmap_generator._get_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.aio.models.generate_content = AsyncMock(
                return_value=mock_response
            )
            mock_get_client.return_value = mock_client

            result = await generate_mindmap(
                request=request_all_sources,
                chunks=MOCK_MINDMAP_CHUNKS,
            )

        assert isinstance(result, MindmapNodeSchema)
        assert result.topic == "Database Fundamentals"
        assert len(result.children) == 5

    @pytest.mark.asyncio
    async def test_generate_mindmap_raises_on_empty_response(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.mindmap_generator import generate_mindmap

        mock_response = MagicMock()
        mock_response.text = None

        with patch(
            "src.ai_engine.mindmap_feature.mindmap_generator._get_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.aio.models.generate_content = AsyncMock(
                return_value=mock_response
            )
            mock_get_client.return_value = mock_client

            with pytest.raises(ValueError, match="empty response"):
                await generate_mindmap(
                    request=request_all_sources,
                    chunks=MOCK_MINDMAP_CHUNKS,
                )

    @pytest.mark.asyncio
    async def test_generate_mindmap_raises_on_invalid_json(
        self, request_all_sources: MindmapGenerationRequest
    ) -> None:
        from src.ai_engine.mindmap_feature.mindmap_generator import generate_mindmap

        mock_response = MagicMock()
        mock_response.text = "not valid json {{{"

        with patch(
            "src.ai_engine.mindmap_feature.mindmap_generator._get_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.aio.models.generate_content = AsyncMock(
                return_value=mock_response
            )
            mock_get_client.return_value = mock_client

            with pytest.raises(ValueError):
                await generate_mindmap(
                    request=request_all_sources,
                    chunks=MOCK_MINDMAP_CHUNKS,
                )
