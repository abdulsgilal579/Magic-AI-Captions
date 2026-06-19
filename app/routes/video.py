from fastapi import APIRouter, UploadFile, File
from app.services.s3 import upload_video
from app.services.transcribe import transcribe_video
from app.services.captions import burn_captions
import uuid
import tempfile
import os

router = APIRouter()

@router.post("/upload")
async def upload_video_route(file: UploadFile = File(...)):
    """
    Full flow:
    1 — Save video temporarily
    2 — Transcribe with Whisper
    3 — Burn captions with FFmpeg
    4 — Upload final video to S3
    5 — Return download link
    """
    job_id = str(uuid.uuid4())
    filename = f"{job_id}-{file.filename}"

    # Step 1 — Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Step 2 — Transcribe with Whisper
    print("🎤 Transcribing video...")
    srt_content = transcribe_video(tmp_path)

    # Step 3 — Burn captions into video
    print("🔥 Burning captions into video...")
    captioned_video_path = burn_captions(tmp_path, srt_content)

    # Step 4 — Upload final captioned video to S3
    print("☁️ Uploading to S3...")
    final_filename = f"captioned/{filename}"
    video_url = upload_video(open(captioned_video_path, "rb"), final_filename)

    # Step 5 — Clean up temp files
    os.unlink(tmp_path)
    os.unlink(captioned_video_path)

    return {
        "job_id": job_id,
        "message": "Captions burned successfully! 🎬",
        "download_url": video_url,
        "captions": srt_content
    }