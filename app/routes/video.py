from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.s3 import upload_video
from app.services.transcribe import transcribe_video
from app.services.captions import burn_captions
import uuid
import os

router = APIRouter()

# Holds video paths between upload and burn. Keyed by job_id.
# Fine for a single-process server; replace with Redis/DB for multi-worker deployments.
job_store: dict[str, dict] = {}


class BurnRequest(BaseModel):
    job_id: str
    captions: str  # ASS content, edited or unmodified from /upload response


@router.post("/upload")
async def upload_video_route(file: UploadFile = File(...)):
    """
    Step 1 — Upload and transcribe.

    Saves the video to a temp file, runs Whisper, and returns the generated
    ASS caption content. Edit the captions however you like, then pass them
    along with the job_id to POST /burn.
    """
    job_id = str(uuid.uuid4())
    tmp_path = f"/tmp/{job_id}-{file.filename}"

    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    print("Transcribing video...")
    captions = transcribe_video(tmp_path)

    job_store[job_id] = {
        "video_path": tmp_path,
        "original_filename": file.filename,
    }

    return {
        "job_id": job_id,
        "captions": captions,
        "message": "Transcription done. Edit the captions if needed, then call /burn.",
    }


@router.post("/burn")
async def burn_video_route(body: BurnRequest):
    """
    Step 2 — Burn and upload.

    Accepts the job_id from /upload and the ASS caption content (modified or
    as-is). Burns the captions into the video, uploads to S3, and cleans up.
    """
    job = job_store.pop(body.job_id, None)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found. It may have already been burned or never uploaded.")

    video_path = job["video_path"]
    original_filename = job["original_filename"]

    print("Burning captions into video...")
    captioned_video_path = burn_captions(video_path, body.captions)

    print("Uploading to S3...")
    final_filename = f"captioned/{body.job_id}-{original_filename}"
    video_url = upload_video(open(captioned_video_path, "rb"), final_filename)

    os.unlink(video_path)
    os.unlink(captioned_video_path)

    return {
        "job_id": body.job_id,
        "message": "Captions burned successfully.",
        "download_url": video_url,
    }
