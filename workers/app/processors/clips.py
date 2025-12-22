from typing import List, Dict
import os
import json
from openai import OpenAI

# ---------------- Config ----------------
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"
OPENAI_MODEL = os.getenv("OPENAI_CLIP_MODEL", "gpt-4o-mini")
MAX_CLIPS = 5

client = OpenAI()


# -------------------------------------------------
# 1. Generate candidate clips (deterministic)
# -------------------------------------------------
def generate_candidate_clips(
    segments: List[Dict],
    min_duration: float = 20.0,
    max_duration: float = 45.0,
):
    candidates = []
    i = 0

    while i < len(segments):
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
            candidates.append({
                "id": len(candidates),
                "start": round(start, 2),
                "end": round(end, 2),
                "duration": round(end - start, 2),
                "text": text.strip(),
            })

        i = j

    return candidates


# -------------------------------------------------
# 2. Rank clips using OpenAI (AI selection)
# -------------------------------------------------
def rank_clips_with_llm(
    candidates: List[Dict],
    max_clips: int = MAX_CLIPS,
):
    if not candidates:
        return []

    prompt = f"""
            You are a short-form video editor.

            TASK:
            Select the {max_clips} MOST CLIPPABLE moments for TikTok/Reels/Shorts.

            RULES (IMPORTANT):
            - Return ONLY a valid JSON array of integers
            - Each integer MUST be a clip id
            - NO markdown
            - NO explanations
            - NO text
            - Example output: [3, 7, 1, 4, 2]

            CRITERIA:
            - Emotional moments
            - Strong dialogue
            - Turning points
            - Educational/relavent to subject moments
            - Insightful or quotable lines
            - Avoid slow exposition

            CLIPS:
            {json.dumps([
                {
                    "id": c["id"],
                    "start": c["start"],
                    "end": c["end"],
                    "text": c["text"][:500]
                }
                for c in candidates
            ], indent=2)}
            """

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional viral video editor."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()

    # ---- HARDENED PARSING ----
    try:
        # Strip markdown if model ignores instructions
        if raw.startswith("```"):
            raw = raw.split("```")[1].strip()

        selected_ids = json.loads(raw)

        if not isinstance(selected_ids, list):
            raise ValueError("LLM output is not a list")

        # Validate IDs
        valid_ids = {c["id"] for c in candidates}
        selected_ids = [i for i in selected_ids if i in valid_ids]

        # Map IDs → clips (preserve ranking order)
        ranked = [next(c for c in candidates if c["id"] == i) for i in selected_ids]

        return ranked[:max_clips]

    except Exception as e:
        print("Failed to parse LLM response:", raw)
        raise e


# -------------------------------------------------
# 3. Public API (used by worker)
# -------------------------------------------------
def detect_clips(
    segments: List[Dict],
    min_duration: float = 20.0,
    max_duration: float = 45.0,
    max_clips: int = MAX_CLIPS,
):
    candidates = generate_candidate_clips(
        segments,
        min_duration=min_duration,
        max_duration=max_duration,
    )

    if not candidates:
        return []

    if USE_LLM:
        try:
            ranked = rank_clips_with_llm(candidates, max_clips)

            for i, c in enumerate(ranked):
                print(
                    f"AI Clip {i+1}: "
                    f"{c['start']}–{c['end']} ({c['duration']}s)"
                )

            return ranked

        except Exception as e:
            print("LLM clip ranking failed, falling back:", e)

    # Fallback: deterministic first-N
    return candidates[:max_clips]
