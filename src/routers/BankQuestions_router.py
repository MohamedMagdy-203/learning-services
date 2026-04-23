from fastapi import APIRouter, HTTPException, Depends
import logging
from src.ai_engine.BankQuestions_engine.BankQuestions_generator import (
    BankQuestionsGenerator,
)
from src.models.BankQuestions_schemas import (
    QuestionGenerationRequest,
    QuizBank,
)

from src.ai_engine.data_fetchers.ChunksRetrieval import retrieve_chunks_multi_urls
from src.ai_engine.data_fetchers.qdrant_client_dependency import (
    get_qdrant_client_dependency,
)
from src.ai_engine.BankQuestions_engine.openai_client_dependency import (
    get_openai_client,
)

from src.core.config import get_settings
from src.core.messages import (
    QUIZ_GENERATED_SUCCESSFULLY,
    BANK_GENERATION_FAILED,
    GENERATION_STARTED,
    EMPTY_SOURCE_CONTENT,
)
from src.core.exceptions import (
    NoContentFoundError,
    LLMGenerationError,
    InvalidLLMResponseError,
)

logger = logging.getLogger(__name__)

gen_router = APIRouter(prefix="/api/v1/quiz-bank", tags=["Quiz Bank"])


def get_generator(
    client=Depends(get_openai_client),
):
    return BankQuestionsGenerator(client)


@gen_router.post("/generate", response_model=QuizBank)
async def generate_quiz_bank(
    request: QuestionGenerationRequest,
    generator: BankQuestionsGenerator = Depends(get_generator),
    qdrant_client=Depends(get_qdrant_client_dependency),
):
    logger.info(GENERATION_STARTED.format(subtopic_id=request.subtopic_id))

    try:
        settings = get_settings()

        documents = await retrieve_chunks_multi_urls(
            urls=[str(u) for u in request.urls],
            primary_url=str(request.primary_url),
            client=qdrant_client,
            settings=settings,
        )

        quiz_bank = await generator.generate_bank_questions(
            documents=documents,
            subtopic_id=request.subtopic_id,
            primary_url=str(request.primary_url),
        )

        logger.info(QUIZ_GENERATED_SUCCESSFULLY.format(count=len(quiz_bank.questions)))

        return quiz_bank

    except NoContentFoundError:
        logger.error(EMPTY_SOURCE_CONTENT)
        raise HTTPException(
            status_code=400,
            detail="The provided URLs do not contain enough content to generate questions.",
        )

    except (LLMGenerationError, InvalidLLMResponseError) as e:
        logger.error(f"LLM generation error: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="Failed to generate questions from AI engine. Please try again.",
        )

    except Exception as e:
        logger.error(
            BANK_GENERATION_FAILED.format(subtopic_id=request.subtopic_id, error=str(e))
        )
        raise HTTPException(status_code=500, detail="Failed to generate quiz")
