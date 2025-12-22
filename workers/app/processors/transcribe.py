import whisper
from pathlib import Path

model = whisper.load_model("base")

def transcribe_audio(audio_path, device="cpu"):
    model = whisper.load_model("base", device=device)
    return model.transcribe(
        str(audio_path),
        word_timestamps=False
    )