"""
Video generation service using Google Gemini AI.

Handles advertisement video generation with Veo models.
"""

import os
import uuid
import time
from fastapi import HTTPException
from dotenv import load_dotenv
from loguru import logger
from google import genai

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OUTPUT_DIR = "output"

# Don't raise HTTPException at module level - let it be raised in function
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_ad_video(prompt: str, logo_image_path: str = None) -> str:
    """
    Generate an advertisement video using Google Gemini AI's Veo.

    Args:
        prompt (str): Text prompt for video generation
        logo_image_path (str): Path to generated logo image for reference

    Returns:
        str: Relative URL to the generated video

    Raises:
        HTTPException: If video generation fails
    """
    logger.info(f"Generating video with Gemini Veo for prompt: {prompt}")

    if not client:
        raise HTTPException(status_code=500, detail="Google API key not configured")

    try:
        # Create video generation prompt
        video_prompt = (
            f"Create an animated advertisement for social media marketing campaign "
            f"for the given prompt: '{prompt}'. Make it engaging, professional, suitable for platforms "
            f"like Instagram Reels or TikTok. Keep it around 4 seconds."
        )

        # Start video generation (skip logo for now to avoid format issues)
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=video_prompt
        )
        logger.info("Started video generation (logo reference disabled temporarily)")

        # Poll the operation status until the video is ready
        start_time = time.time()

        while not operation.done:
            elapsed = time.time() - start_time

            logger.info(f"Waiting for video generation... ({elapsed:.0f}s elapsed)")
            time.sleep(10)
            operation = client.operations.get(operation)

        if not operation.done or operation.response is None:
            raise HTTPException(status_code=500, detail="Video generation failed")

        # Download the generated video
        if not operation.response.generated_videos:
            raise HTTPException(status_code=500, detail="No video generated in response")

        video = operation.response.generated_videos[0]
        video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        video_path = os.path.join(OUTPUT_DIR, video_filename)

        # Save the video file
        client.files.download(file=video.video)
        video.video.save(video_path)

        logger.info(f"Video saved to {video_path}")

        # Return relative path for frontend access
        return f"/{OUTPUT_DIR}/{video_filename}"

    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")


def generate_ad_video_without_logo(prompt: str) -> str:
    """
    Generate an advertisement video without logo reference.

    Args:
        prompt (str): Text prompt for video generation

    Returns:
        str: Relative URL to the generated video

    Raises:
        HTTPException: If video generation fails
    """
    return generate_ad_video(prompt, logo_image_path=None)