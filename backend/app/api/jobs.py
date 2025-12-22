from fastapi import APIRouter, HTTPException
from app.services.s3_reader import read_json, signed_url

router = APIRouter(prefix="/jobs")

@router.get("/{job_id}/status")
def get_status(job_id: str):
    try:
        return read_json(f"results/{job_id}/status.json")
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")


@router.get("/{job_id}/results")
def get_results(job_id: str):
    try:
        data = read_json(f"results/{job_id}/results.json")

        for clip in data["clips"]:
            clip["url"] = signed_url(clip["s3_key"])
            del clip["s3_key"]

        return data

    except Exception:
        raise HTTPException(status_code=404, detail="Results not ready")
