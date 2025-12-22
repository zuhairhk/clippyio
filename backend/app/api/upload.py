import uuid
from fastapi import APIRouter, UploadFile, File, Form
from app.services.s3 import upload_file
from app.services.queue import push_job

router = APIRouter()

@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    captions: bool = Form(True),
):
    s3_key = upload_file(file.file, file.filename)

    job_id = str(uuid.uuid4())

    push_job({
        "job_id": job_id,
        "s3_key": s3_key,
        "captions": captions,
    })

    return {
        "job_id": job_id,
        "status": "queued",
    }
