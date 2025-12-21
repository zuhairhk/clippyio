from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.upload import router as upload_router
from app.api.jobs import router as jobs_router

load_dotenv()

app = FastAPI(title="ClippyIO API")

app.include_router(upload_router)
app.include_router(jobs_router)

@app.get("/")
def health_check():
    return {"status": "ok"}
