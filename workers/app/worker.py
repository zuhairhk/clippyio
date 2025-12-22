import boto3
import os
import json
from dotenv import load_dotenv
from pathlib import Path
import shutil
import torch

from app.processors.audio import extract_audio
from app.processors.transcribe import transcribe_audio
from app.utils.transcript import save_transcript
from app.processors.summary import generate_summary
from app.processors.caption import generate_caption
from app.processors.clips import detect_clips
from app.processors.cut import cut_clip
from app.processors.captions import build_srt, burn_captions
from app.utils.s3_upload import upload_file

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


def download_video(s3_key: str, job_dir: Path) -> Path:
    job_dir.mkdir(parents=True, exist_ok=True)
    local_path = job_dir / "input.mp4"
    s3.download_file(BUCKET, s3_key, str(local_path))
    return local_path


def main():
    print("Worker started. Waiting for jobs...")

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {DEVICE}")

    while True:
        result = poll_queue()
        if not result:
            continue

        job, receipt = result
        print("Got job:", job)

        WITH_SUMMARY = job.get("summary", True)
        WITH_VIDEO_CAPTION = job.get("video_caption", True)
        WITH_CAPTIONS = job.get("captions", True)

        print(
            f"Options → summary={WITH_SUMMARY}, "
            f"video_caption={WITH_VIDEO_CAPTION}, "
            f"captions={WITH_CAPTIONS}"
        )

        job_dir = TMP_DIR / job["job_id"]
        job_dir.mkdir(parents=True, exist_ok=True)

        status_path = job_dir / "status.json"
        status_path.write_text(json.dumps({"status": "processing"}))
        upload_file(status_path, f"results/{job['job_id']}/status.json")

        try:
            video_path = download_video(job["s3_key"], job_dir)
            audio_path = extract_audio(video_path)
            transcript = transcribe_audio(audio_path, device=DEVICE)
            save_transcript(transcript, job["job_id"], output_dir=job_dir)

            segments = transcript.get("segments", [])

            clips = detect_clips(segments)
            clip_paths = []
            clip_out_dir = job_dir / "clips"

            for idx, clip in enumerate(clips):
                raw_clip = cut_clip(
                    video_path=video_path,
                    start=clip["start"],
                    end=clip["end"],
                    index=idx,
                    job_id=job["job_id"],
                    out_dir=clip_out_dir,
                )

                if WITH_CAPTIONS:
                    srt_path = clip_out_dir / f"clip_{idx}.srt"
                    build_srt(
                        segments=segments,
                        start=clip["start"],
                        end=clip["end"],
                        out_path=srt_path,
                    )

                    captioned = clip_out_dir / f"clip_{idx}.mp4"
                    burn_captions(
                        video_path=raw_clip,
                        srt_path=srt_path,
                        out_path=captioned,
                    )
                    clip_paths.append(captioned)
                else:
                    clip_paths.append(raw_clip)

            summary = None
            if WITH_SUMMARY:
                summary = generate_summary(transcript["text"])

            caption = None
            if WITH_VIDEO_CAPTION:
                caption = generate_caption(transcript["text"])

            uploaded_clips = []
            for idx, path in enumerate(clip_paths):
                s3_key = f"results/{job['job_id']}/clip_{idx}.mp4"
                upload_file(path, s3_key)
                uploaded_clips.append(s3_key)

            results = {
                "job_id": job["job_id"],
                "summary": summary,
                "caption": caption,
                "clips": [
                    {**clip, "s3_key": uploaded_clips[i]}
                    for i, clip in enumerate(clips)
                ],
            }

            results_path = job_dir / "results.json"
            results_path.write_text(json.dumps(results, indent=2))
            upload_file(results_path, f"results/{job['job_id']}/results.json")

            status_path.write_text(json.dumps({"status": "done"}))
            upload_file(status_path, f"results/{job['job_id']}/status.json")

            delete_message(receipt)
            shutil.rmtree(job_dir, ignore_errors=True)

            print("Job done\n")

        except Exception as e:
            print("Job failed:", e)

            status_path.write_text(json.dumps({"status": "failed"}))
            upload_file(status_path, f"results/{job['job_id']}/status.json")

            delete_message(receipt)
            shutil.rmtree(job_dir, ignore_errors=True)

            print("Job marked failed\n")


if __name__ == "__main__":
    main()
