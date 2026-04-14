from fastapi import APIRouter, HTTPException, Depends
import logging

from src.ai_engine.BankQuestions_engine.BankQuestions_generator import (
    BankQuestionsGenerator,
)
from src.models.BankQuestions_schemas import QuestionGenerationRequest, QuizBank
from src.core.messages import QUIZ_GENERATED_SUCCESSFULLY, BANK_GENERATION_FAILED

logger = logging.getLogger(__name__)

gen_router = APIRouter(prefix="/api/v1/quiz-bank", tags=["Quiz Bank"])


def get_generator():
    return BankQuestionsGenerator()


@gen_router.post("/generate", response_model=QuizBank)
async def generate_quiz_bank(
    request: QuestionGenerationRequest,
    generator: BankQuestionsGenerator = Depends(get_generator),
):
    logger.info("Quiz bank generation started")

    try:
        quiz_bank = await generator.generate_bank_questions(
            distilled_results=request.distilled_results,
            subtopic_id=request.subtopic_id,
            primary_url=str(request.primary_url),
            total_questions=request.total_questions,
        )

        logger.info(QUIZ_GENERATED_SUCCESSFULLY.format(count=len(quiz_bank.questions)))
        return quiz_bank

    except Exception as e:
        logger.error(f"Quiz generation failed: {str(e)}")

        raise HTTPException(status_code=500, detail=BANK_GENERATION_FAILED)
