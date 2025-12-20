import boto3
import os
import uuid
from dotenv import load_dotenv

def upload_file(file_obj, filename: str) -> str:
    load_dotenv()

    bucket = os.getenv("S3_BUCKET_NAME")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    key = f"uploads/{uuid.uuid4()}-{filename}"
    s3.upload_fileobj(file_obj, bucket, key)
    return key
