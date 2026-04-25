from fastapi import APIRouter, HTTPException, Depends
import logging
import uuid
from typing import Dict, Any

from src.ai_engine.quiz_feature.adaptive_engine import AdaptiveQuizEngine
from src.ai_engine.quiz_feature.session_manager import session_manager
from src.ai_engine.quiz_feature.question_retrieval import QuestionRetrieval
from src.ai_engine.data_fetchers.qdrant_client_dependency import (
    get_qdrant_client_dependency,
)

from src.ai_engine.quiz_feature.BankQuestions_engine.BankQuestions_generator import (
    BankQuestionsGenerator,
)
from src.models.quiz_schemas import QuestionGenerationRequest
from src.ai_engine.quiz_feature.ChunksRetrieval import retrieve_chunks_multi_urls
from src.ai_engine.quiz_feature.BankQuestions_engine.openai_client_dependency import (
    get_openai_client,
)
from src.ai_engine.quiz_feature.qdrant_question_store import QdrantQuestionStore
from src.core.config import get_settings

from src.core.messages import (
    QUIZ_GENERATED_SUCCESSFULLY,
    BANK_GENERATION_FAILED,
    GENERATION_STARTED,
    EMPTY_SOURCE_CONTENT,
    AI_QUESTION_GENERATION_FAILED,
    AI_INSUFFICIENT_URL_CONTENT,
    NO_QUESTIONS_AVAILABLE,
    REQUIRED_IDS,
)
from src.core.exceptions import (
    NoContentFoundError,
    LLMGenerationError,
    InvalidLLMResponseError,
)

logger = logging.getLogger(__name__)

gen_router = APIRouter(prefix="/api/v1/question-bank", tags=["Question Bank"])


def get_generator(
    client=Depends(get_openai_client),
):
    return BankQuestionsGenerator(client)


@gen_router.post("/generate")
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

        if not documents:
            raise NoContentFoundError(EMPTY_SOURCE_CONTENT)

        bank_id = str(uuid.uuid4())

        quiz_bank = await generator.generate_bank_questions(
            documents=documents,
            subtopic_id=request.subtopic_id,
            primary_url=str(request.primary_url),
            bank_id=bank_id,
        )

        store = QdrantQuestionStore(
            client=qdrant_client,
            collection_name=settings.QUIZ_COLLECTION_NAME,
        )

        await store.store_questions(
            questions=quiz_bank.questions,
            bank_id=bank_id,
        )

        logger.info(QUIZ_GENERATED_SUCCESSFULLY.format(count=len(quiz_bank.questions)))

        return {
            "bank_id": bank_id,
            "subtopic_id": request.subtopic_id,
            "questions_count": len(quiz_bank.questions),
            "message": "Question bank generated and stored successfully.",
        }

    except NoContentFoundError:
        logger.error(EMPTY_SOURCE_CONTENT)
        raise HTTPException(status_code=400, detail=AI_INSUFFICIENT_URL_CONTENT)

    except (LLMGenerationError, InvalidLLMResponseError) as e:
        logger.error(f"LLM generation error: {str(e)}")
        raise HTTPException(status_code=502, detail=AI_QUESTION_GENERATION_FAILED)

    except Exception as e:
        logger.error(
            BANK_GENERATION_FAILED.format(
                subtopic_id=request.subtopic_id,
                error=str(e),
            )
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate quiz",
        )


quiz_router = APIRouter(prefix="/api/v1/quiz", tags=["Quiz Execution"])


async def get_engine(qdrant_client=Depends(get_qdrant_client_dependency)):
    settings = get_settings()
    retriever = QuestionRetrieval(
        client=qdrant_client, collection_name=settings.QUIZ_COLLECTION_NAME
    )
    return AdaptiveQuizEngine(retriever)


@quiz_router.post("/start")
async def start_quiz(
    request: Dict[str, str], engine: AdaptiveQuizEngine = Depends(get_engine)
):
    bank_id = request.get("bank_id")
    user_id = request.get("user_id")

    if not bank_id or not user_id:
        raise HTTPException(status_code=400, detail=REQUIRED_IDS)

    first_question = await engine.get_initial_question(bank_id)
    if not first_question:
        raise HTTPException(status_code=404, detail=NO_QUESTIONS_AVAILABLE)

    session = session_manager.create_session(bank_id, user_id)
    session.asked_questions.add(first_question.question_id)
    session.last_difficulty = first_question.difficulty

    return {
        "session_id": session.session_id,
        "status": "ongoing",
        "question": first_question.model_dump(),
    }


@quiz_router.post("/answer")
async def submit_answer(
    request: Dict[str, Any], engine: AdaptiveQuizEngine = Depends(get_engine)
):
    session_id = request.get("session_id")
    question_id = request.get("question_id")
    is_correct = request.get("is_correct")
    response_time = request.get("response_time")

    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await engine.process_answer(
        session, question_id, is_correct, response_time
    )

    if result["status"] == "finished":
        session_manager.delete_session(session_id)
        return {
            "session_id": session_id,
            "status": "finished",
            "summary": result["summary"],
        }

    next_q = result["next_question"]
    return {
        "session_id": session_id,
        "status": "ongoing",
        "next_question": next_q.model_dump(),
    }
