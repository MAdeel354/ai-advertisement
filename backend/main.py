"""
FastAPI backend for Ad Generator.

Async job processing with real-time notifications.
"""

import os
import sys
import time
import asyncio
import json
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from loguru import logger
import uvicorn

# Import services and models
from app.services.job_service import job_manager
from app.models import get_user_jobs as get_jobs_from_db, get_job, JobStatus

load_dotenv()

# Configuration
if not os.getenv("GOOGLE_API_KEY"):
    logger.error("GOOGLE_API_KEY not found in environment")
    sys.exit(1)

logger.info("Ad Generator API starting up with Google Gemini AI...")

# Initialize FastAPI
app = FastAPI(title="Ad Generator API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Simple request logger (less intrusive)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Only log basic info to avoid interfering with requests
    logger.info(f"📥 {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    if process_time > 1.0:  # Only log slow requests
        logger.info(f"📤 {response.status_code} - {process_time:.3f}s")

    return response

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Pydantic models for async workflow
class AsyncGenerationRequest(BaseModel):
    prompt: str
    generate_video: bool = False
    user_id: Optional[str] = "default"

class AsyncGenerationResponse(BaseModel):
    success: bool
    job_id: str
    message: str
    prompt: str

class JobStatusResponse(BaseModel):
    success: bool
    job_id: str
    status: str
    progress: int
    logo_url: Optional[str] = None
    video_url: Optional[str] = None
    error_message: Optional[str] = None

class JobsListResponse(BaseModel):
    success: bool
    jobs: List[dict]

# Static files
app.mount("/output", StaticFiles(directory="output"), name="output")

# Routes
@app.get("/")
async def root():
    return {"message": "Ad Generator API is running"}

@app.get("/api/health")
async def health_check():
    logger.info("🏥 Health check requested")
    return {
        "status": "healthy",
        "google_api_configured": True
    }

# NEW ENDPOINTS FOR ASYNC WORKFLOW

@app.post("/api/generate-ad-async", response_model=AsyncGenerationResponse)
async def generate_ad_async(request: AsyncGenerationRequest):
    """Start async generation job and return job ID immediately."""
    logger.info(f"🚀 Async generate endpoint called with prompt: '{request.prompt}'")
    try:
        # Start background job
        job_id = await job_manager.start_generation_job(
            request.prompt,
            request.generate_video,
            request.user_id or "default"
        )

        # Broadcast job started notification
        await manager.broadcast(json.dumps({
            "type": "job_started",
            "job_id": job_id,
            "prompt": request.prompt,
            "generate_video": request.generate_video
        }))

        return AsyncGenerationResponse(
            success=True,
            job_id=job_id,
            message="Generation job started. Use job ID to track progress.",
            prompt=request.prompt
        )

    except Exception as e:
        logger.error(f"Failed to start generation job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start job: {str(e)}")

@app.get("/api/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get status of a specific job."""
    logger.info(f"📊 Job status requested for: {job_id}")
    try:
        job = job_manager.get_job_status(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobStatusResponse(
            success=True,
            job_id=job_id,
            status=job["status"],
            progress=job.get("progress", 0),
            logo_url=job.get("logo_url"),
            video_url=job.get("video_url"),
            error_message=job.get("error_message")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@app.get("/api/jobs", response_model=JobsListResponse)
async def get_user_jobs_endpoint(user_id: str = "default", limit: int = 50):
    """Get all jobs for a user."""
    logger.info(f"📋 Jobs list requested for user: {user_id}")
    try:
        jobs = get_jobs_from_db(user_id, limit)

        return JobsListResponse(
            success=True,
            jobs=jobs
        )

    except Exception as e:
        logger.error(f"Failed to get jobs list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get jobs: {str(e)}")

@app.get("/api/dashboard")
async def get_dashboard_data(user_id: str = "default"):
    """Get dashboard data - serves jobs.json directly for frontend consumption."""
    logger.info(f"📊 Dashboard data requested for user: {user_id}")
    try:
        jobs = get_jobs_from_db(user_id)

        # Calculate summary stats
        total_jobs = len(jobs)
        completed_jobs = len([j for j in jobs if j["status"] == "completed"])
        pending_jobs = len([j for j in jobs if j["status"] == "pending"])
        processing_jobs = len([j for j in jobs if j["status"] == "processing"])
        failed_jobs = len([j for j in jobs if j["status"] == "failed"])

        dashboard_data = {
            "summary": {
                "total": total_jobs,
                "completed": completed_jobs,
                "pending": pending_jobs,
                "processing": processing_jobs,
                "failed": failed_jobs
            },
            "jobs": jobs  # Frontend can use this directly
        }

        return dashboard_data

    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@app.delete("/api/job/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job."""
    logger.info(f"❌ Job cancellation requested for: {job_id}")
    try:
        success = job_manager.cancel_job(job_id)

        if success:
            # Broadcast job cancelled notification
            await manager.broadcast(json.dumps({
                "type": "job_cancelled",
                "job_id": job_id
            }))

            return {"success": True, "message": "Job cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

# NOTE: Synchronous endpoint removed - use async workflow instead

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time job updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await manager.send_personal_message(f"Received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)