import uuid
from fastapi import APIRouter, UploadFile, File
from app.services.s3 import upload_file
from app.services.queue import push_job

router = APIRouter()

JOBS = {}  # temp for memory storage

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    s3_key = upload_file(file.file, file.filename)

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "status": "queued",
        "s3_key": s3_key
    }

    push_job({
        "job_id": job_id,
        "s3_key": s3_key
    })

    return {
        "job_id": job_id,
        "status": "queued"
    }
