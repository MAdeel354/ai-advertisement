"""
FastAPI backend for Ad Generator.

Simplified application for AI-powered advertisement generation.
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

# Import services
from app.services import generate_logo, generate_ad_video

load_dotenv()

# Configuration
if not os.getenv("REPLICATE_API_TOKEN"):
    logger.error("REPLICATE_API_TOKEN not found in environment")
    sys.exit(1)

logger.info("Ad Generator API starting up...")

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

# Pydantic models
class GenerationRequest(BaseModel):
    prompt: str
    generate_video: bool = False

class GenerationResponse(BaseModel):
    success: bool
    logo_url: Optional[str] = None
    video_url: Optional[str] = None
    message: str
    prompt: str

# Static files
app.mount("/output", StaticFiles(directory="output"), name="output")

# Routes
@app.get("/")
async def root():
    return {"message": "Ad Generator API is running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "replicate_token_configured": True
    }

@app.post("/api/generate-ad", response_model=GenerationResponse)
async def generate_ad(request: GenerationRequest):
    """Generate advertisement (logo and optionally video) from prompt."""
    try:
        logger.info(f"Starting generation for prompt: {request.prompt}")

        logo_url = None
        video_url = None

        # Generate logo
        try:
            logo_url = generate_logo(request.prompt)
        except Exception as e:
            logger.error(f"Logo generation failed: {e}")
            return GenerationResponse(
                success=False,
                message=f"Logo generation failed: {str(e)}",
                prompt=request.prompt
            )

        # Generate video if requested
        if request.generate_video:
            try:
                video_url = generate_ad_video(request.prompt)
            except Exception as e:
                logger.error(f"Video generation failed: {e}")
                return GenerationResponse(
                    success=True,
                    logo_url=logo_url,
                    message=f"Logo generated successfully, but video generation failed: {str(e)}",
                    prompt=request.prompt
                )

        return GenerationResponse(
            success=True,
            logo_url=logo_url,
            video_url=video_url,
            message="Advertisement generated successfully!",
            prompt=request.prompt
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)