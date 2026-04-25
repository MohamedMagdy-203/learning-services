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
        question_id: str,
        is_correct: bool,
        response_time: float,
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

        next_diff = self._get_next_difficulty(
            current_difficulty, is_correct, response_time, history
        )

        next_q = await self.retriever.get_question_by_bank(
            bank_id=session.bank_id,
            difficulty=next_diff,
            exclude_ids=session.asked_questions,
        )

        if not next_q:
            next_q = await self.retriever.get_question_by_bank(
                bank_id=session.bank_id, exclude_ids=session.asked_questions
            )

        if not next_q:
            logger.warning(NO_MORE_QUESTIONS)
            return {"status": "finished", "summary": self._calculate_summary(history)}

        session.asked_questions.add(next_q.question_id)
        session.last_difficulty = next_q.difficulty

        return {"status": "ongoing", "next_question": next_q.model_dump()}

    def _should_continue(self, history, current_difficulty):
        total_answered = SessionAnalytics.total_answered(history)

        if total_answered < self.MIN_QUESTIONS:
            return True, "minimum_not_reached"

        if total_answered >= self.MAX_QUESTIONS:
            return False, "max_questions_reached"

        confidence = self._calculate_confidence_score(history)

        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            return False, "high_confidence"

        if (
            SessionAnalytics.consecutive_correct(history) >= 3
            and current_difficulty == "hard"
        ):
            return False, "mastery_detected"

        if (
            SessionAnalytics.consecutive_wrong(history) >= 3
            and current_difficulty == "easy"
        ):
            return False, "struggling_detected"

        return True, "continue"

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
            if index < 2:
                if is_fast or correct_streak >= 2:
                    return self.DIFFICULTIES[index + 1]
            return current_difficulty

        if wrong_streak >= 2 and index > 0:
            return self.DIFFICULTIES[index - 1]

        if is_slow and index > 0:
            return self.DIFFICULTIES[index - 1]

        return current_difficulty

    def _calculate_confidence_score(self, history):
        total = SessionAnalytics.total_answered(history)
        if total == 0:
            return 0.0

        return round(
            min(
                1.0,
                (
                    SessionAnalytics.recent_accuracy(history, 5) * 0.35
                    + SessionAnalytics.consistency_score(history) * 0.25
                    + SessionAnalytics.question_count_score(total, self.MAX_QUESTIONS)
                    * 0.25
                    + SessionAnalytics.speed_score(history) * 0.15
                ),
            ),
            2,
        )

    def _calculate_summary(self, history):
        total = len(history)
        correct = sum(1 for h in history if h["is_correct"])
        avg_time = sum(h["response_time"] for h in history) / total if total else 0

        return {
            "total_questions_answered": total,
            "correct_answers": correct,
            "average_response_time": round(avg_time, 2),
            "final_confidence_score": self._calculate_confidence_score(history),
        }
