# Copyright (c) 2026 Abdul Samad Gilal
# All rights reserved.

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes.video import router as video_router
import os

app = FastAPI(
    title="Magic AI Captions",
    description="A powerful API for generating captions for videos using AI.",
    version="1.0.0",
)

app.include_router(video_router, prefix="/api/v1")

_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=_static_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(_static_dir, "index.html"))