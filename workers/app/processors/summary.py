from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(transcript_text: str) -> str:
    prompt = f"""
            Summarize the following video transcript in 3-5 concise sentences.
            Focus on the main idea and emotional tone.

            Transcript:
            {transcript_text}
            """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()
