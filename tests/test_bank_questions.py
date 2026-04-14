import pytest
import json
from unittest.mock import AsyncMock, patch

from src.ai_engine.BankQuestions_engine.BankQuestions_generator import (
    BankQuestionsGenerator,
)
from src.core.exceptions import EmptyContentError, LLMGenerationError

from src.models.distillation_schemas import SingleDistilledItem, DistilledContent


# 1) STRUCTURE TEST


@pytest.mark.asyncio
async def test_generate_for_source_structure():
    generator = BankQuestionsGenerator()

    fake_response = {
        "questions": [
            {
                "content": "What is Python?",
                "difficulty": "easy",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Because...",
            }
        ]
    }

    mock_llm = AsyncMock()
    mock_llm.chat.completions.create.return_value = AsyncMock(
        choices=[AsyncMock(message=AsyncMock(content=json.dumps(fake_response)))]
    )

    with patch.object(generator, "client", mock_llm):
        result = await generator._generate_for_source(
            distilled_content=DistilledContent(
                key_terms=[], main_points=["dummy"], examples=[]
            ),
            source_url="http://test.com",
            subtopic_id="123",
            num_questions=1,
            difficulty="easy",
        )

    assert len(result) == 1
    assert result[0].content == "What is Python?"


# 2) DEDUPLICATION TEST


@pytest.mark.asyncio
async def test_deduplication():
    generator = BankQuestionsGenerator()

    MockQ = type("MockQ", (), {})

    q1 = MockQ()
    q1.question_id = "1"
    q1.subtopic_id = "123"
    q1.source_url = "http://test.com"
    q1.difficulty = "easy"
    q1.content = "Same Question"
    q1.options = ["A", "B"]
    q1.correct_answer = "A"
    q1.explanation = ""

    q2 = MockQ()
    q2.question_id = "2"
    q2.subtopic_id = "123"
    q2.source_url = "http://test.com"
    q2.difficulty = "easy"
    q2.content = "Same Question"
    q2.options = ["A", "B"]
    q2.correct_answer = "A"
    q2.explanation = ""

    fake_item = SingleDistilledItem(
        url="http://test.com",
        distilled_content=DistilledContent(
            key_terms=[], main_points=["dummy"], examples=[]
        ),
        is_primary=True,
    )

    with patch.object(
        generator, "_generate_for_source", new=AsyncMock(return_value=[q1, q2])
    ):
        result = await generator.generate_bank_questions(
            distilled_results=[fake_item],
            subtopic_id="123",
            primary_url="http://test.com",
            total_questions=2,
        )

    assert len(result["questions"]) == 1


# 3) EMPTY CONTENT TEST


@pytest.mark.asyncio
async def test_empty_content_raises():
    generator = BankQuestionsGenerator()

    with pytest.raises(EmptyContentError):
        await generator._generate_for_source(
            distilled_content=DistilledContent(
                key_terms=[], main_points=[], examples=[]
            ),
            source_url="http://test.com",
            subtopic_id="123",
            num_questions=1,
            difficulty="easy",
        )


# 4) TOTAL QUESTIONS TEST


@pytest.mark.asyncio
async def test_total_questions_distribution():
    generator = BankQuestionsGenerator()

    fake_item = SingleDistilledItem(
        url="http://test.com",
        distilled_content=DistilledContent(
            key_terms=[], main_points=["dummy"], examples=[]
        ),
        is_primary=True,
    )

    mock_question = type(
        "MockQ",
        (),
        {
            "question_id": "1",
            "subtopic_id": "123",
            "source_url": "http://test.com",
            "difficulty": "easy",
            "content": "Q1",
            "options": ["A", "B"],
            "correct_answer": "A",
            "explanation": "",
        },
    )()

    with patch.object(
        generator, "_generate_for_source", new=AsyncMock(return_value=[mock_question])
    ):
        result = await generator.generate_bank_questions(
            distilled_results=[fake_item],
            subtopic_id="123",
            primary_url="http://test.com",
            total_questions=10,
        )

    assert len(result["questions"]) > 0


# 5) PRIMARY SOURCE MISSING TEST


@pytest.mark.asyncio
async def test_primary_source_missing():
    generator = BankQuestionsGenerator()

    with pytest.raises(LLMGenerationError):
        await generator.generate_bank_questions(
            distilled_results=[],
            subtopic_id="123",
            primary_url="http://missing.com",
            total_questions=5,
        )
        # pytest tests/test_bank_questions.py -v
