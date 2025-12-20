import whisper
from pathlib import Path

model = whisper.load_model("base")

def transcribe_audio(audio_path: Path) -> dict:
    result = model.transcribe(
        str(audio_path),
        word_timestamps=True
    )
    return result
