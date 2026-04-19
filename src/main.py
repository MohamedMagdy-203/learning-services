from fastapi import FastAPI
from .routers import base, roadmap, mindmap

app = FastAPI()

app.include_router(base.base_router)
app.include_router(roadmap.roadmap_router)
app.include_router(mindmap.mindmap_router)
