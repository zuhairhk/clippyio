import boto3
import os
import json
from dotenv import load_dotenv
from pathlib import Path
import shutil
from app.processors.audio import extract_audio
from app.processors.transcribe import transcribe_audio
from app.utils.transcript import save_transcript
from app.processors.summary import generate_summary
from app.processors.caption import generate_caption
from app.processors.clips import detect_clips
from app.processors.cut import cut_clip
from app.utils.s3_upload import upload_file
import torch

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

        # per-job temp dir
        job_dir = TMP_DIR / job["job_id"]
        job_dir.mkdir(parents=True, exist_ok=True)

        # INITIAL STATUS UPLOAD (write a temp file then upload)
        status_path = job_dir / "status.json"
        with open(status_path, "w") as f:
            json.dump({"status": "processing"}, f)
        upload_file(status_path, f"results/{job['job_id']}/status.json")

        try:
            # DOWNLOAD VIDEO
            video_path = download_video(job["s3_key"], job_dir)
            print("Downloaded to:", video_path)
            # EXTRACT AUDIO + TRANSCRIBE & SAVE TRANSCRIPT
            audio_path = extract_audio(video_path)
            print("Audio extracted:", audio_path)
            transcript = transcribe_audio(audio_path, device=DEVICE)
            print("Transcription done.")
            transcript_path = save_transcript(transcript, job["job_id"], output_dir=job_dir)
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
                clip_out_dir = job_dir / "clips"
                path = cut_clip(
                    video_path=video_path,
                    start=clip["start"],
                    end=clip["end"],
                    index=idx,
                    job_id=job["job_id"],
                    out_dir=clip_out_dir,
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

            # UPLOAD RESULTS TO S3 AND CREATE RESULTS JSON LOG
            uploaded_clips = []
            for idx, path in enumerate(clip_paths):
                s3_key = f"results/{job['job_id']}/clip_{idx}.mp4"
                upload_file(path, s3_key)
                uploaded_clips.append(s3_key)
                print("Uploaded clip:", s3_key)

            results_dir = job_dir
            results_dir.mkdir(parents=True, exist_ok=True)

            results = {
                "job_id": job["job_id"],
                "summary": summary,
                "caption": caption,
                "clips": [
                    {
                        **clip,
                        "s3_key": uploaded_clips[i]
                    }
                    for i, clip in enumerate(clips)
                ],
            }

            results_path = results_dir / "results.json"
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)

            print("Results JSON created:", results_path)
            results_s3_key = f"results/{job['job_id']}/results.json"
            upload_file(results_path, results_s3_key)
            print("Uploaded results JSON:", results_s3_key)

            # mark success status
            success_status_path = job_dir / "status.json"
            with open(success_status_path, "w") as f:
                json.dump({"status": "done"}, f)
            upload_file(success_status_path, f"results/{job['job_id']}/status.json")
            print("Uploaded status 'done'")

            delete_message(receipt)

            # cleanup job dir
            shutil.rmtree(job_dir, ignore_errors=True)

            print("Job done\n")

        except Exception as e:
            print("Job failed:", e)
            # upload failed status
            failed_status_path = job_dir / "status.json"
            with open(failed_status_path, "w") as f:
                json.dump({"status": "failed"}, f)
            try:
                upload_file(failed_status_path, f"results/{job['job_id']}/status.json")
                print("Uploaded failed status")
            except Exception as uerr:
                print("Failed to upload failed status:", uerr)
            delete_message(receipt)

            # cleanup job dir even on failure
            shutil.rmtree(job_dir, ignore_errors=True)

            print("Job marked failed and message deleted\n")
            continue


if __name__ == "__main__":
    main()
