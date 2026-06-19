import os
import subprocess

def burn_captions(video_path: str, ass_content: str) -> str:
    ass_path = "/tmp/captions.ass"
    output_path = "/tmp/output.mp4"

    # Write ASS caption file
    with open(ass_path, "w") as f:
        f.write(ass_content)

    # Remove old output if exists
    if os.path.exists(output_path):
        os.unlink(output_path)

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"ass={ass_path}",   # use ass filter
        "-c:v", "libx264",
        "-c:a", "aac",
        "-y",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("FFmpeg error:", result.stderr)
        raise Exception(f"FFmpeg failed: {result.stderr}")

    return output_path