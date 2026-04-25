# pytest tests/quiz/unit/test_bank_questions.py

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.documents import Document
import itertools

from src.ai_engine.quiz_feature.BankQuestions_engine.BankQuestions_generator import (
    BankQuestionsGenerator,
)

from src.ai_engine.quiz_feature.question_retrieval import QuestionRetrieval
from src.ai_engine.quiz_feature.session_manager import SessionManager
from src.ai_engine.quiz_feature.qdrant_question_store import QdrantQuestionStore

from src.models.quiz_schemas import Question
from src.core.exceptions import NoContentFoundError


# HELPERS


def make_doc(url="http://test.com", is_primary=True):
    return Document(
        page_content="test content",
        metadata={
            "url": url,
            "is_primary": is_primary,
        },
    )


def make_question(i=0, bank_id="bank_123", source_url="http://test.com"):
    return Question(
        question_id=str(uuid.uuid4()),
        subtopic_id="sub_1",
        bank_id=bank_id,
        source_url=source_url,
        content=f"Q{i}",
        options=["A", "B"],
        correct_answer="A",
        difficulty="easy",
        explanations={"A": "Correct", "B": "Wrong"},
        metadata={},
    )


def make_docs():
    return [
        make_doc("http://primary.com", True),
        make_doc("http://secondary1.com", False),
        make_doc("http://secondary2.com", False),
    ]


# 1) GENERATOR TESTS


@pytest.mark.asyncio
async def test_generator_100_questions():
    generator = BankQuestionsGenerator(client=AsyncMock())
    docs = make_docs()

    counter = itertools.count()

    async def fake_generate(*args, **kwargs):
        return [make_question(i=next(counter)) for _ in range(10)]

    with patch.object(generator, "_generate_for_source", side_effect=fake_generate):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="sub_1",
            primary_url="http://primary.com",
            bank_id="bank_123",
        )

    assert len(result.questions) <= 100


@pytest.mark.asyncio
async def test_generator_primary_missing():
    generator = BankQuestionsGenerator(client=AsyncMock())

    docs = [make_doc(is_primary=False)]

    with pytest.raises(NoContentFoundError):
        await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="sub_1",
            primary_url="http://x.com",
            bank_id="bank_123",
        )


@pytest.mark.asyncio
async def test_generator_deduplication():
    generator = BankQuestionsGenerator(client=AsyncMock())
    docs = make_docs()

    async def fake_generate(*args, **kwargs):
        q = make_question()
        return [q, q]

    with patch.object(generator, "_generate_for_source", side_effect=fake_generate):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="sub_1",
            primary_url="http://primary.com",
            bank_id="bank_123",
        )

    contents = [q.content for q in result.questions]

    assert len(contents) == len(set(contents))


@pytest.mark.asyncio
async def test_generator_fallback_logic():
    generator = BankQuestionsGenerator(client=AsyncMock())
    docs = make_docs()

    async def fake_generate(*args, **kwargs):
        return [make_question()]

    with patch.object(generator, "_generate_for_source", side_effect=fake_generate):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="sub_1",
            primary_url="http://primary.com",
            bank_id="bank_123",
        )

    assert len(result.questions) > 0


# 2) QDRANT STORE TESTS


@pytest.mark.asyncio
async def test_qdrant_store_upsert_called():
    client = AsyncMock()

    store = QdrantQuestionStore(client=client, collection_name="test_collection")

    await store.store_questions(
        questions=[make_question()],
        bank_id="bank_123",
    )

    client.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_qdrant_store_payload_structure():
    client = AsyncMock()

    store = QdrantQuestionStore(client=client, collection_name="test_collection")

    await store.store_questions(
        questions=[make_question()],
        bank_id="bank_123",
    )

    points = client.upsert.call_args[1]["points"]

    assert points[0].payload["bank_id"] == "bank_123"
    assert "explanations" in points[0].payload


# 3) RETRIEVAL TESTS


@pytest.mark.asyncio
async def test_retrieval_by_bank():
    client = AsyncMock()

    client.scroll.return_value = (
        [
            MagicMock(
                payload={
                    "question_id": "1",
                    "subtopic_id": "sub_1",
                    "bank_id": "bank_123",
                    "source_url": "http://test.com",
                    "content": "Q1",
                    "options": ["A", "B"],
                    "correct_answer": "A",
                    "difficulty": "easy",
                    "explanations": {},
                    "metadata": {},
                }
            )
        ],
        None,
    )

    retrieval = QuestionRetrieval(client, "collection")

    result = await retrieval.get_question_by_bank("bank_123")

    assert result is not None
    assert result.bank_id == "bank_123"


@pytest.mark.asyncio
async def test_retrieval_with_difficulty():
    client = AsyncMock()

    client.scroll.return_value = (
        [
            MagicMock(
                payload={
                    "question_id": "1",
                    "subtopic_id": "sub_1",
                    "bank_id": "bank_123",
                    "source_url": "http://test.com",
                    "content": "Q1",
                    "options": ["A", "B"],
                    "correct_answer": "A",
                    "difficulty": "hard",
                    "explanations": {},
                    "metadata": {},
                }
            )
        ],
        None,
    )

    retrieval = QuestionRetrieval(client, "collection")

    result = await retrieval.get_question_by_bank(bank_id="bank_123", difficulty="hard")

    assert result is not None
    assert result.difficulty == "hard"


@pytest.mark.asyncio
async def test_retrieval_empty():
    client = AsyncMock()
    client.scroll.return_value = ([], None)

    retrieval = QuestionRetrieval(client, "collection")

    result = await retrieval.get_question_by_bank("bank_123")

    assert result is None


# 4) SESSION MANAGER TESTS


def test_session_creation():
    manager = SessionManager()

    session = manager.create_session("bank_123", "user_1")

    assert session.bank_id == "bank_123"
    assert session.current_index == 0


def test_session_not_found():
    manager = SessionManager()

    assert manager.get_session("invalid") is None


def test_session_asked_questions_tracking():
    manager = SessionManager()
    session = manager.create_session("bank_123", "user_1")

    session.asked_questions.add("q1")

    assert "q1" in session.asked_questions


# 5) INTEGRATION LOGIC TEST


def test_session_bank_linking():
    manager = SessionManager()

    session = manager.create_session("bank_123", "user_1")

    assert session.bank_id == "bank_123"
