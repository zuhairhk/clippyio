from typing import List, Dict

def detect_clips(
    segments: List[Dict],
    min_duration: float = 20.0,
    max_duration: float = 45.0,
    max_clips: int = 5,
):
    clips = []
    i = 0

    while i < len(segments) and len(clips) < max_clips:
        start = segments[i]["start"]
        end = segments[i]["end"]
        text = segments[i]["text"]

        j = i + 1
        while j < len(segments):
            next_end = segments[j]["end"]
            if next_end - start > max_duration:
                break

            end = next_end
            text += " " + segments[j]["text"]

            if end - start >= min_duration:
                break

            j += 1

        if end - start >= min_duration:
            clips.append({
                "start": round(start, 2),
                "end": round(end, 2),
                "duration": round(end - start, 2),
                "text": text.strip()
            })

        i = j

    return clips
