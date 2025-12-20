import boto3
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from processors.audio import extract_audio
from processors.transcribe import transcribe_audio
from utils.transcript import save_transcript
from processors.summary import generate_summary
from processors.caption import generate_caption
from processors.clips import detect_clips
from processors.cut import cut_clip

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
QUEUE_URL = os.getenv("SQS_QUEUE_URL")
BUCKET = os.getenv("S3_BUCKET_NAME")

sqs = boto3.client(
    "sqs",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

TMP_DIR = Path("/tmp/clippyio")
TMP_DIR.mkdir(parents=True, exist_ok=True)


def poll_queue():
    resp = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    if "Messages" not in resp:
        return None

    msg = resp["Messages"][0]
    body = json.loads(msg["Body"])
    receipt = msg["ReceiptHandle"]

    return body, receipt


def delete_message(receipt_handle):
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )


def download_video(s3_key: str) -> Path:
    local_path = TMP_DIR / s3_key.split("/")[-1]
    s3.download_file(BUCKET, s3_key, str(local_path))
    return local_path


def main():
    print("Worker started. Waiting for jobs...")

    while True:
        result = poll_queue()
        if not result:
            continue

        job, receipt = result
        print("Got job:", job)
        
        # DOWNLOAD VIDEO
        video_path = download_video(job["s3_key"])
        print("Downloaded to:", video_path)
        # EXTRACT AUDIO + TRANSCRIBE & SAVE TRANSCRIPT
        audio_path = extract_audio(video_path)
        print("Audio extracted:", audio_path)
        transcript = transcribe_audio(audio_path)
        print("Transcription done.")
        transcript_path = save_transcript(transcript, job["job_id"])
        print("Transcript saved to:", transcript_path)
        
        # PRINT TRANSCRIPT PREVIEW
        segments = transcript.get("segments", [])
        print(f"Total segments: {len(segments)}")
        for seg in segments[:5]:
            print(
                f"[{seg['start']:.2f}s → {seg['end']:.2f}s] {seg['text']}"
            )

        # CLIP DETECTION
        clips = detect_clips(segments)
        print(f"Detected {len(clips)} clips")
        for c in clips:
            print(f"[{c['start']}s → {c['end']}s] ({c['duration']}s)")

        # CUT CLIPS
        clip_paths = []
        for idx, clip in enumerate(clips):
            path = cut_clip(
                video_path=video_path,
                start=clip["start"],
                end=clip["end"],
                index=idx,
                job_id=job["job_id"],
            )
            clip_paths.append(path)
            print("Clip created:", path)

        # SUMMARY + CAPTION GENERATION
        try:
            summary = generate_summary(transcript["text"])
            print("Summary:", summary)
        except Exception as e:
            print("Summary failed:", e)
            summary = None
        try:
            caption = generate_caption(transcript["text"])
            print("Caption:", caption)
        except Exception as e:
            print("Caption failed:", e)
            caption = None

        delete_message(receipt)
        print("Job done\n")


if __name__ == "__main__":
    main()
