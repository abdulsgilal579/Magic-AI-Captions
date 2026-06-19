# Magic AI Captions

A FastAPI service that transcribes a video with OpenAI Whisper, burns word-by-word highlighted captions into it using FFmpeg, and uploads the result to S3.

## Preview

<video src="preview_video/Linkedin.mp4" controls width="100%"></video>

## How it works

1. `POST /api/v1/upload` — upload your video; Whisper transcribes it and returns the raw ASS caption content
2. Edit the captions however you like (fix words, adjust timing, change styling)
3. `POST /api/v1/burn` — send the job ID and your edited captions; FFmpeg burns them into the video and uploads the result to S3

## Requirements

- Python 3.9+
- FFmpeg installed and available on your PATH
- An AWS account with an S3 bucket

## Setup

```bash
git clone https://github.com/your-username/Magic-AI-Captions.git
cd Magic-AI-Captions

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your AWS credentials:

```bash
cp .env.example .env
```

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_aws_region
AWS_S3_BUCKET_NAME=your_s3_bucket_name
```

## Running

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

## API

### `POST /api/v1/upload`

Upload a video. Transcribes it and returns the ASS caption content for review.

**Request:** `multipart/form-data` with a `file` field containing the video.

**Response:**

```json
{
  "job_id": "uuid",
  "captions": "... ASS subtitle content ...",
  "message": "Transcription done. Edit the captions if needed, then call /burn."
}
```

---

### `POST /api/v1/burn`

Burn the captions into the video and upload to S3.

**Request:** JSON body

```json
{
  "job_id": "uuid",
  "captions": "... ASS subtitle content, edited or unchanged ..."
}
```

**Response:**

```json
{
  "job_id": "uuid",
  "message": "Captions burned successfully.",
  "download_url": "https://your-bucket.s3.region.amazonaws.com/captioned/..."
}
```

## Project structure

```
app/
  main.py              # FastAPI app and router registration
  config.py            # Loads env vars
  routes/
    video.py           # Upload endpoint
  services/
    transcribe.py      # Whisper transcription and ASS generation
    captions.py        # FFmpeg caption burning
    s3.py              # S3 upload
```

## Dependencies

| Package | Purpose |
|---|---|
| fastapi | API framework |
| uvicorn | ASGI server |
| openai-whisper | Speech-to-text transcription |
| boto3 | AWS S3 upload |
| python-multipart | File upload parsing |
| python-dotenv | `.env` file loading |
| ffmpeg-python | FFmpeg subprocess wrapper |
