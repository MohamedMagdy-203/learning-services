from fastapi import FastAPI
from .routers import base, data, summarization_router
from src.ai_engine.summarization_engine.openai_client_dependency import (
    init_openai_client,
    close_openai_client,
)

from src.ai_engine.data_fetchers.qdrant_client_dependency import (
    init_qdrant_client,
    close_qdrant_client,
)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await init_openai_client()
    try:
        await init_qdrant_client()
    except Exception:
        await close_openai_client()
        raise


@app.on_event("shutdown")
async def shutdown_event():
    try:
        await close_openai_client()
    finally:
        await close_qdrant_client()


app.include_router(base.base_router)
app.include_router(data.data_router)

app.include_router(summarization_router.summ_router)
