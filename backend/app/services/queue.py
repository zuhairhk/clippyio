import boto3
import os
import json
from dotenv import load_dotenv

def push_job(message: dict):
    load_dotenv()  # ensure env is loaded at runtime

    queue_url = os.getenv("SQS_QUEUE_URL")
    if not queue_url:
        raise RuntimeError("SQS_QUEUE_URL is not set")

    sqs = boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )
