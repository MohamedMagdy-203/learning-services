import logging
from typing import Dict, Any
from src.ai_engine.quiz_feature.session_analytics import SessionAnalytics
from src.ai_engine.quiz_feature.question_retrieval import QuestionRetrieval
from src.ai_engine.quiz_feature.session_manager import QuizSession
from src.core.messages import STOPPING_QUIZ, NO_MORE_QUESTIONS

logger = logging.getLogger(__name__)


class AdaptiveQuizEngine:
    MIN_QUESTIONS = 5
    MAX_QUESTIONS = 15
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    DIFFICULTIES = ["easy", "medium", "hard"]

    def __init__(self, retriever: QuestionRetrieval):
        self.retriever = retriever

    async def get_initial_question(self, bank_id: str):
        first_q = await self.retriever.get_question_by_bank(
            bank_id, difficulty="medium"
        )
        if not first_q:
            raise Exception("No medium difficulty question found")
        return first_q

    async def process_answer(
        self,
        session: QuizSession,
        is_correct: bool,
        response_time: float,
        question_id: str,
    ) -> Dict[str, Any]:
        current_difficulty = session.last_difficulty or "medium"

        session.history.append(
            {
                "question_id": question_id,
                "is_correct": is_correct,
                "response_time": response_time,
                "difficulty": current_difficulty,
            }
        )

        history = session.history

        should_cont, reason = self._should_continue(history, current_difficulty)

        if not should_cont:
            logger.info(STOPPING_QUIZ.format(reason=reason))
            return {"status": "finished", "summary": self._calculate_summary(history)}

        next_q = await self.retriever.get_question_by_bank(
            bank_id=session.bank_id, exclude_ids=session.asked_questions
        )

        if not next_q:
            logger.warning(NO_MORE_QUESTIONS)
            return {"status": "finished", "summary": self._calculate_summary(history)}

        next_diff = self._get_next_difficulty(
            current_difficulty, is_correct, response_time, history
        )

        session.asked_questions.add(next_q.question_id)
        session.last_difficulty = next_diff

        return {"status": "ongoing", "next_question": next_q.model_dump()}

    def _get_next_difficulty(
        self, current_difficulty, is_correct, response_time, history
    ):
        if current_difficulty not in self.DIFFICULTIES:
            current_difficulty = "medium"

        index = self.DIFFICULTIES.index(current_difficulty)

        expected_time = {"easy": 20, "medium": 30, "hard": 45}.get(
            current_difficulty, 30
        )

        time_ratio = response_time / expected_time

        is_fast = time_ratio <= 0.8
        is_slow = time_ratio >= 1.2

        correct_streak = SessionAnalytics.consecutive_correct(history)
        wrong_streak = SessionAnalytics.consecutive_wrong(history)

        if is_correct:
            if index < 2 and (is_fast or correct_streak >= 2):
                return self.DIFFICULTIES[index + 1]
            return current_difficulty

        if wrong_streak >= 2 and index > 0:
            return self.DIFFICULTIES[index - 1]

        if is_slow and index > 0:
            return self.DIFFICULTIES[index - 1]

        return current_difficulty
