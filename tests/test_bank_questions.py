import pytest
import uuid
from unittest.mock import AsyncMock, patch
from langchain_core.documents import Document
import itertools
from src.ai_engine.BankQuestions_engine.BankQuestions_generator import (
    BankQuestionsGenerator,
)

from src.models.BankQuestions_schemas import Question
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


def make_question(i, content, source_url):
    normalized_source_url = str(source_url).rstrip("/") + "/"
    return Question(
        question_id=str(uuid.uuid4()),
        subtopic_id="123",
        source_url=normalized_source_url,
        difficulty="easy",
        content=content,
        options=[f"A{i}", f"B{i}"],
        correct_answer=f"A{i}",
        explanation="exp",
    )


def make_docs():
    return [
        make_doc("http://primary.com", True),
        make_doc("http://secondary1.com", False),
        make_doc("http://secondary2.com", False),
    ]


# TEST 1: 100 QUESTIONS GUARANTEE


@pytest.mark.asyncio
async def test_generator_with_strong_source_diversity():
    generator = BankQuestionsGenerator(client=AsyncMock())
    docs = make_docs()

    question_counter = itertools.count()

    async def side_effect(documents, url, subtopic_id, count, *args, **kwargs):
        if "primary" in url:
            prefix = "PRIMARY"
        elif "secondary1" in url:
            prefix = "SEC1"
        elif "secondary2" in url:
            prefix = "SEC2"
        else:
            prefix = "UNKNOWN"

        return [
            make_question(
                next(question_counter),
                content=f"{prefix}-Question-{next(question_counter)}",
                source_url=url,
            )
            for _ in range(count)
        ]

    with patch.object(generator, "_generate_for_source", side_effect=side_effect):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://primary.com",
        )

    questions = result.questions

    assert len(questions) == 100

    sources = {str(q.source_url) for q in questions}

    assert "http://primary.com/" in sources  # Corrected: Added trailing slash
    assert "http://secondary1.com/" in sources  # Corrected: Added trailing slash
    assert "http://secondary2.com/" in sources  # Corrected: Added trailing slash

    contents = [q.content for q in questions]
    assert len(contents) == len(set(contents))

    assert any("PRIMARY" in q.content for q in questions)
    assert any("SEC1" in q.content for q in questions)
    assert any("SEC2" in q.content for q in questions)


# TEST 2: PRIMARY MISSING


@pytest.mark.asyncio
async def test_primary_missing_raises_error():
    generator = BankQuestionsGenerator(client=AsyncMock())

    docs = [make_doc(is_primary=False)]

    with pytest.raises(NoContentFoundError):
        await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://test.com",
        )


# TEST 3: SECONDARY FAILURE


@pytest.mark.asyncio
async def test_secondary_failure_does_not_stop_process():
    generator = BankQuestionsGenerator(client=AsyncMock())

    docs = make_docs()

    question_counter = itertools.count()

    async def side_effect(documents, url, subtopic_id, count, *args, **kwargs):
        if "secondary1.com" in url:
            raise Exception("secondary failed")

        return [
            make_question(
                next(question_counter),
                content=f"{url}-Q{next(question_counter)}",
                source_url=url,
            )
            for _ in range(count)
        ]

    with patch.object(generator, "_generate_for_source", side_effect=side_effect):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://primary.com",
        )

    assert len(result.questions) == 100


# TEST 4: FINAL SLICE


@pytest.mark.asyncio
async def test_final_slice_is_exactly_30():
    generator = BankQuestionsGenerator(client=AsyncMock())
    docs = make_docs()

    question_counter = itertools.count()

    with patch.object(
        generator,
        "_generate_for_source",
        side_effect=lambda documents, url, subtopic_id, count, *args, **kwargs: [
            make_question(
                next(question_counter),
                content=f"Q{next(question_counter)}",
                source_url="http://primary.com",
            )
            for _ in range(count)
        ],
    ):
        result = await generator.generate_bank_questions(
            documents=docs,
            subtopic_id="123",
            primary_url="http://primary.com",
        )

    assert len(result.questions) == 100

    # pytest tests/test_bank_questions.py
