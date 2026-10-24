from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
from app.services.gemini_service import (
    generate_driver_prompt,
    generate_driver_avatar,
    generate_formula_e_video,
    upload_to_gcs
)

app = FastAPI(title="Formula E AI Kiosk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs_db = {}

class JobStatus(BaseModel):
    job_id: str
    status: str
    stage: str
    result_url: str | None = None

@app.get("/api/health")
def health_check():
    return {"status": "ok", "experience": "Formula E Gen4 AI Kiosk"}

@app.post("/api/process-driver")
async def process_driver(
    file: UploadFile = File(...),
    option: str = Form("podium_celebration")
):
    job_id = str(uuid.uuid4())
    image_bytes = await file.read()
    
    jobs_db[job_id] = {
        "status": "processing",
        "stage": "generating_prompt",
        "result_url": None
    }
    
    asyncio.create_task(run_kiosk_pipeline(job_id, image_bytes, option))
    return {"job_id": job_id, "status": "queued"}

async def run_kiosk_pipeline(job_id: str, image_bytes: bytes, option: str):
    try:
        jobs_db[job_id]["stage"] = "Writing driver prompt with Gemini 3.8 Flash..."
        driver_prompt = generate_driver_prompt(image_bytes, option)
        
        jobs_db[job_id]["stage"] = "Rendering Nano Banana 2 avatar..."
        avatar_bytes = generate_driver_avatar(driver_prompt, image_bytes)
        
        jobs_db[job_id]["stage"] = "Generating Gemini Omni Flash video..."
        video_bytes = generate_formula_e_video(driver_prompt, avatar_bytes)
        
        jobs_db[job_id]["stage"] = "Publishing generated video to Cloud Storage..."
        result_url = upload_to_gcs(video_bytes, f"videos/{job_id}.mp4", "video/mp4")
        
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["stage"] = "Done"
        jobs_db[job_id]["result_url"] = result_url
    except Exception as e:
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["stage"] = str(e)

@app.get("/api/job/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    data = jobs_db[job_id]
    return JobStatus(
        job_id=job_id,
        status=data["status"],
        stage=data["stage"],
        result_url=data.get("result_url")
    )

