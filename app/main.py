# Copyright (c) 2026 Abdul Samad Gilal
# All rights reserved.

from fastapi import FastAPI
from app.routes.video import router as video_router

app = FastAPI(
    title="Magic AI Captions",
    description="A powerful API for generating captions for videos using AI.",
    version="1.0.0",
)

app.include_router(video_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Magic AI Captions API!"}