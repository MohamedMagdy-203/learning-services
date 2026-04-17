from fastapi import FastAPI
from .routers import base, data, mindmap

app = FastAPI()

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(mindmap.mindmap_router)
