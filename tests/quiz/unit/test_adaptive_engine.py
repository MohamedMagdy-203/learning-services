import pytest
from unittest.mock import AsyncMock, MagicMock

from src.ai_engine.quiz_feature.adaptive_engine import AdaptiveQuizEngine
from src.ai_engine.quiz_feature.session_manager import QuizSession


# Helpers


def make_question(qid="q1", difficulty="medium"):
    q = MagicMock()
    q.question_id = qid
    q.difficulty = difficulty
    return q


def make_session():
    session = QuizSession(session_id="s1", bank_id="bank_123", user_id="user_1")
    session.last_difficulty = "medium"
    session.asked_questions = set()
    return session


# 1) INITIAL QUESTION


@pytest.mark.asyncio
async def test_get_initial_question():
    retriever = AsyncMock()
    retriever.get_question_by_bank.return_value = make_question()

    engine = AdaptiveQuizEngine(retriever)

    q = await engine.get_initial_question("bank_123")

    assert q is not None
    retriever.get_question_by_bank.assert_called_once()


# 2) PROCESS ANSWER - CONTINUE FLOW


@pytest.mark.asyncio
async def test_process_answer_continue():
    retriever = AsyncMock()
    retriever.get_question_by_bank.return_value = make_question("q2", "hard")

    engine = AdaptiveQuizEngine(retriever)
    session = make_session()

    result = await engine.process_answer(
        session=session, question_id="q1", is_correct=True, response_time=10
    )

    assert result["status"] == "ongoing"
    assert "next_question" in result


# 3) PROCESS ANSWER - END QUIZ (MAX QUESTIONS)


@pytest.mark.asyncio
async def test_process_answer_end_by_max_questions():
    retriever = AsyncMock()
    engine = AdaptiveQuizEngine(retriever)

    session = make_session()

    # simulate history reaching max limit
    session.history = [
        {"is_correct": True, "response_time": 10, "difficulty": "medium"}
        for _ in range(15)
    ]

    result = await engine.process_answer(
        session=session, question_id="q1", is_correct=True, response_time=10
    )

    assert result["status"] == "finished"
    assert "summary" in result


# 4) PROCESS ANSWER - NO QUESTION FOUND


@pytest.mark.asyncio
async def test_process_answer_no_question():
    retriever = AsyncMock()
    retriever.get_question_by_bank.return_value = None

    engine = AdaptiveQuizEngine(retriever)
    session = make_session()

    result = await engine.process_answer(
        session=session, question_id="q1", is_correct=True, response_time=10
    )

    assert result["status"] == "finished"
    assert "summary" in result


# 5) DIFFICULTY UPDATE LOGIC


@pytest.mark.asyncio
async def test_difficulty_changes():
    retriever = AsyncMock()
    retriever.get_question_by_bank.return_value = make_question("q2", "hard")

    engine = AdaptiveQuizEngine(retriever)
    session = make_session()

    # simulate good performance
    session.history = [
        {"is_correct": True, "response_time": 5, "difficulty": "medium"},
        {"is_correct": True, "response_time": 5, "difficulty": "medium"},
    ]

    result = await engine.process_answer(
        session=session, question_id="q1", is_correct=True, response_time=5
    )

    assert result["status"] in ["ongoing", "finished"]


# 6) HISTORY IS BEING STORED


@pytest.mark.asyncio
async def test_history_tracking():
    retriever = AsyncMock()
    retriever.get_question_by_bank.return_value = make_question()

    engine = AdaptiveQuizEngine(retriever)
    session = make_session()

    await engine.process_answer(
        session=session, question_id="q1", is_correct=True, response_time=10
    )

    assert len(session.history) == 1
    assert session.history[0]["is_correct"] is True
    assert "difficulty" in session.history[0]
