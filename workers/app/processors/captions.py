from pathlib import Path
import subprocess

def format_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def build_srt(segments, start, end, out_path: Path):
    lines = []
    idx = 1

    for seg in segments:
        if seg["end"] < start or seg["start"] > end:
            continue

        seg_start = max(seg["start"], start) - start
        seg_end = min(seg["end"], end) - start

        lines.append(str(idx))
        lines.append(
            f"{format_ts(seg_start)} --> {format_ts(seg_end)}"
        )
        lines.append(seg["text"].strip())
        lines.append("")
        idx += 1

    out_path.write_text("\n".join(lines))


def burn_captions(video_path: Path, srt_path: Path, out_path: Path):
    if video_path.resolve() == out_path.resolve():
        raise ValueError("Output path must be different from input path")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf",
            (
                "subtitles="
                f"{srt_path}:force_style="
                "'PlayResY=1920,"
                "Fontname=Arial,"
                "Fontsize=40,"
                "PrimaryColour=&HFFFFFF&,"
                "OutlineColour=&H000000&,"
                "Outline=3,"
                "Shadow=0,"
                "Alignment=2,"
                "MarginV=120'"
            ),
            "-c:a", "copy",
            str(out_path),
        ],
        check=True,
    )
