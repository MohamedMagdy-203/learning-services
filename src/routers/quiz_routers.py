from fastapi import APIRouter, HTTPException, Depends
import logging
import uuid

from src.ai_engine.quiz_feature.adaptive_engine import AdaptiveQuizEngine
from src.ai_engine.quiz_feature.session_manager import session_manager
from src.ai_engine.quiz_feature.question_retrieval import QuestionRetrieval
from src.ai_engine.data_fetchers.qdrant_client_dependency import (
    get_qdrant_client_dependency,
)

from src.ai_engine.quiz_feature.BankQuestions_engine.BankQuestions_generator import (
    BankQuestionsGenerator,
)
from src.models.quiz_schemas import (
    QuestionGenerationRequest,
    SubmitAnswerRequest,
    StartQuizRequest,
)
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

        if not quiz_bank.questions:
            raise HTTPException(status_code=500, detail=AI_QUESTION_GENERATION_FAILED)

        store = QdrantQuestionStore(
            client=qdrant_client,
            collection_name=settings.QUIZ_COLLECTION_NAME,
        )

        await store.store_questions(questions=quiz_bank.questions)

        logger.info(QUIZ_GENERATED_SUCCESSFULLY.format(count=len(quiz_bank.questions)))

        return {
            "bank_id": bank_id,
            "subtopic_id": request.subtopic_id,
            "questions_count": len(quiz_bank.questions),
            "message": "Question bank generated and stored successfully.",
        }

    except NoContentFoundError as e:
        logger.error(EMPTY_SOURCE_CONTENT)
        raise HTTPException(status_code=400, detail=AI_INSUFFICIENT_URL_CONTENT) from e

    except (LLMGenerationError, InvalidLLMResponseError) as e:
        logger.error(f"LLM generation error: {e}")
        raise HTTPException(
            status_code=502, detail=AI_QUESTION_GENERATION_FAILED
        ) from e

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
        ) from e


quiz_router = APIRouter(prefix="/api/v1/quiz", tags=["Quiz Execution"])


async def get_engine(qdrant_client=Depends(get_qdrant_client_dependency)):
    settings = get_settings()
    retriever = QuestionRetrieval(
        client=qdrant_client, collection_name=settings.QUIZ_COLLECTION_NAME
    )
    return AdaptiveQuizEngine(retriever)


@quiz_router.post("/start")
async def start_quiz(
    request: StartQuizRequest,
    engine: AdaptiveQuizEngine = Depends(get_engine),
):
    bank_id = request.bank_id
    user_id = request.user_id

    try:
        first_question = await engine.get_initial_question(bank_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=NO_QUESTIONS_AVAILABLE) from e

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
    request: SubmitAnswerRequest, engine: AdaptiveQuizEngine = Depends(get_engine)
):
    session_id = request.session_id
    question_id = request.question_id
    is_correct = request.is_correct
    response_time = request.response_time

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
    if hasattr(next_q, "model_dump"):
        next_q = next_q.model_dump()

    return {
        "session_id": session_id,
        "status": "ongoing",
        "next_question": next_q,
    }
