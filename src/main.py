from fastapi import FastAPI
from src.routers import base, data
from src.routers.distillation_router import dist_router

app = FastAPI()

app.include_router(base.base_router)
app.include_router(data.data_router)


app.include_router(dist_router)

