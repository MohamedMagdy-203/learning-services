from fastapi import FastAPI
from .routers import base, data,summarization

app = FastAPI()

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(summarization.summarization_router)


