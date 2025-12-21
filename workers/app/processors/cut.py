import subprocess
from pathlib import Path

def cut_clip(
    video_path: Path,
    start: float,
    end: float,
    index: int,
    job_id: str,
    out_dir: Path | None = None,
) -> Path:
    # allow caller to provide a per-job clips dir; fall back to previous behavior
    if out_dir is None:
        out_dir = Path("/tmp/clippyio/clips") / job_id
    else:
        out_dir = Path(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"clip_{index}.mp4"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-ss", str(start),
            "-to", str(end),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "aac",
            "-c:v", "libx264",
            "-preset", "fast",
            str(out_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    return out_path
