import boto3
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

BUCKET = os.getenv("S3_BUCKET_NAME")

def upload_file(local_path: Path, s3_key: str) -> str:
    s3.upload_file(str(local_path), BUCKET, s3_key)
    return f"s3://{BUCKET}/{s3_key}"
