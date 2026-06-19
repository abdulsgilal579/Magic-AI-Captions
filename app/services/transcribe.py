import whisper

# Load the model once when app starts
model = whisper.load_model("base")

def transcribe_video(video_path: str) -> str:
    print(f"Transcribing video: {video_path}")

    # word_timestamps=True gives us timing per word!
    result = model.transcribe(video_path, word_timestamps=True)

    ass_content = generate_ass(result["segments"])
    return ass_content


def generate_ass(segments) -> str:
    """
    Generate ASS subtitle format with word-by-word highlighting
    """
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,65,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,1,0,0,0,100,100,2,0,1,4,0,2,10,10,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = []
    for segment in segments:
        if "words" not in segment:
            continue

        words = segment["words"]
        seg_start = format_ass_time(segment["start"])
        seg_end = format_ass_time(segment["end"])

        # Build karaoke line — yellow highlight on current word
        line_text = ""
        for word in words:
            duration = int((word["end"] - word["start"]) * 100)
            line_text += f"{{\\k{duration}}}{{\\1c&H0000FFFF&}}{word['word'].strip()} "

        lines.append(
            f"Dialogue: 0,{seg_start},{seg_end},Default,,0,0,0,,{line_text.strip()}"
        )

    return ass_header + "\n".join(lines)


def format_ass_time(seconds: float) -> str:
    """Convert seconds to ASS time format: H:MM:SS.cc"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02}:{secs:02}.{centiseconds:02}"