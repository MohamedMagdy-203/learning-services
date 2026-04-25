import logging
from src.ai_engine.quiz_feature.question_retrieval import QuestionRetrieval

logger = logging.getLogger(__name__)


class AdaptiveQuizEngine:
    MIN_QUESTIONS = 5
    MAX_QUESTIONS = 15
    DIFFICULTIES = ["easy", "medium", "hard"]

    def __init__(self, retriever: QuestionRetrieval):
        self.retriever = retriever

    async def get_initial_question(self, bank_id: str):
        first_q = await self.retriever.get_question_by_bank(
            bank_id, difficulty="medium"
        )
        if not first_q:
            raise Exception("No question found")
        return first_q
