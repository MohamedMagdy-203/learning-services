from fastapi import FastAPI
from src.routers import base
from src.routers.quiz_routers import gen_router, quiz_router
from src.ai_engine.quiz_feature.BankQuestions_engine.openai_client_dependency import (
    init_openai_client,
    close_openai_client,
)
from .routers import roadmap, mindmap, summarization_router

from src.ai_engine.data_fetchers.qdrant_client_dependency import (
    init_qdrant_client,
    close_qdrant_client,
)
from src.ai_engine.quiz_feature.quiz_qdrant_client import ensure_quiz_collection_exists

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await init_openai_client()
    try:
        await init_qdrant_client()
        await ensure_quiz_collection_exists()
    except Exception:
        await close_openai_client()
        await close_qdrant_client()
        raise


@app.on_event("shutdown")
async def shutdown_event():
    try:
        await close_openai_client()
    finally:
        await close_qdrant_client()


app.include_router(base.base_router)


app.include_router(gen_router)
app.include_router(quiz_router)

app.include_router(summarization_router.summ_router)
app.include_router(roadmap.roadmap_router)
app.include_router(mindmap.mindmap_router)
