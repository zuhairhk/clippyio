import subprocess
from pathlib import Path

def extract_audio(video_path: Path) -> Path:
    audio_path = video_path.with_suffix(".wav")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-ac", "1",
            "-ar", "16000",
            str(audio_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    return audio_path
