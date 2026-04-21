import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.documents import Document
from src.ai_engine.BankQuestions_engine.BankQuestions_generator import (
    BankQuestionsGenerator,
)
from src.models.BankQuestions_schemas import Question
from src.core.exceptions import EmptyContentError


# Helpers


def make_doc(is_primary=True):
    return Document(
        page_content="test content",
        metadata={
            "url": "http://test.com",
            "is_primary": is_primary,
        },
    )


def make_question(i):
    return Question(
        question_id=str(i),
        subtopic_id="123",
        source_url="http://test.com",
        difficulty="easy",
        content=f"Q{i}",
        options=[f"A{i}", f"B{i}"],
        correct_answer=f"A{i}",
        explanation="exp",
    )


# Tests


@pytest.mark.asyncio
async def test_generate_for_source_structure():
    generator = BankQuestionsGenerator(client=AsyncMock())

    docs = [make_doc(is_primary=True)]

    fake_questions = [make_question(1)]

    with patch.object(
        generator,
        "_generate_for_source",
        new=AsyncMock(return_value=fake_questions),
    ):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://test.com",
        )

    assert result.questions
    assert isinstance(result.questions[0], Question)


@pytest.mark.asyncio
async def test_empty_documents_raises():
    generator = BankQuestionsGenerator(client=AsyncMock())

    with pytest.raises(EmptyContentError):
        await generator.generate_bank_questions(
            documents=[],
            subtopic_id="123",
            primary_url="http://test.com",
        )


@pytest.mark.asyncio
async def test_primary_missing():
    generator = BankQuestionsGenerator(client=AsyncMock())

    docs = [make_doc(is_primary=False)]

    with pytest.raises(EmptyContentError):
        await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://test.com",
        )


@pytest.mark.asyncio
async def test_deduplication():
    generator = BankQuestionsGenerator(client=AsyncMock())

    docs = [
        make_doc(is_primary=True),
        make_doc(is_primary=False),
        make_doc(is_primary=False),
    ]

    q = make_question(1)

    with patch.object(
        generator,
        "_generate_for_source",
        new=AsyncMock(return_value=[q, q, q]),
    ):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://test.com",
        )

    contents = [q.content for q in result.questions]

    assert len(set(contents)) == 1


@pytest.mark.asyncio
async def test_total_questions_always_30():
    generator = BankQuestionsGenerator(client=AsyncMock())

    docs = [
        make_doc(is_primary=True),
        make_doc(is_primary=False),
        make_doc(is_primary=False),
    ]

    with patch.object(
        generator,
        "_generate_for_source",
        new=AsyncMock(return_value=[make_question(i) for i in range(10)]),
    ):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://test.com",
        )

    assert len(result.questions) == 30


@pytest.mark.asyncio
async def test_secondary_failure_still_30():
    generator = BankQuestionsGenerator(client=AsyncMock())

    docs = [
        make_doc(is_primary=True),
        make_doc(is_primary=False),
        make_doc(is_primary=False),
    ]

    async def side_effect(*args, **kwargs):
        num_questions = args[3]

        if num_questions == 21:
            return [make_question(i) for i in range(21)]

        raise Exception("secondary failed")

    with patch.object(
        generator,
        "_generate_for_source",
        new=AsyncMock(side_effect=side_effect),
    ):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://test.com",
        )

    assert len(result.questions) == 30
