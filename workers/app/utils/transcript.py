import json
from pathlib import Path

def save_transcript(transcript: dict, job_id: str, output_dir: Path | None = None) -> Path:
    if output_dir is None:
        out_dir = Path("/tmp/clippyio/transcripts")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{job_id}.json"
    else:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "transcript.json"

    with open(path, "w") as f:
        json.dump(transcript, f, indent=2)

    return path
