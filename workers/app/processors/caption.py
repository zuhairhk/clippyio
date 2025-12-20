from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_caption(transcript_text: str) -> str:
    prompt = f"""
            Create a short, engaging social media caption for this video.
            Keep it under 2 lines.
            Casual, emotional, scroll-stopping.
            No hashtags. No em-dashes.

            Transcript:
            {transcript_text}
            """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
