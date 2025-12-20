import boto3
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from processors.audio import extract_audio
from processors.transcribe import transcribe_audio

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
        
        video_path = download_video(job["s3_key"])
        print("Downloaded to:", video_path)
        audio_path = extract_audio(video_path)
        print("Audio extracted:", audio_path)
        transcript = transcribe_audio(audio_path)
        print("Transcript text:", transcript["text"][:200])

        delete_message(receipt)
        print("Job done\n")


if __name__ == "__main__":
    main()
