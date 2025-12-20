import json
from pathlib import Path

def save_transcript(transcript: dict, job_id: str) -> Path:
    out_dir = Path("/tmp/clippyio/transcripts")
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"{job_id}.json"
    with open(path, "w") as f:
        json.dump(transcript, f, indent=2)

    return path
