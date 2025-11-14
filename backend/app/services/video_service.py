"""
Video generation service using Replicate video models.

Handles advertisement video generation with video processing.
"""

import os
import uuid
import requests
import ffmpeg
import replicate
from fastapi import HTTPException
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Configuration
OUTPUT_DIR = "output"

def generate_ad_video(prompt: str) -> str:
    """
    Generate an advertisement video using Wan 2.1 via Replicate.

    Args:
        prompt (str): Text prompt for video generation

    Returns:
        str: Relative URL to the generated video

    Raises:
        HTTPException: If video generation fails
    """
    logger.info(f"Generating video with Wan 2.1 for prompt: {prompt}")

    try:
        client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))
        model = client.models.get("wavespeedai/wan-2.1-t2v-480p")
    except Exception as e:
        logger.error(f"Wan 2.1 model not found: {e}")
        raise HTTPException(status_code=404, detail="Wan 2.1 model not found on Replicate")

    input_prompt = (
        f"cinematic product ad for {prompt}, luxury feel, "
        "smooth camera pan, vibrant colors, high energy, 5 seconds"
    )

    try:
        output = model.predict(
            prompt=input_prompt,
            num_frames=120,      # 120 frames @ 24 fps = 5 s
            width=854,           # 480p landscape
            height=480,
            num_inference_steps=50,
            guidance_scale=7.5,
            shift=2.0,
            seed=-1,
        )

        video_url = output[0]

        # Generate unique filename
        video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        raw_path = os.path.join(OUTPUT_DIR, f"raw_{video_filename}")
        final_path = os.path.join(OUTPUT_DIR, video_filename)

        # Download video
        with open(raw_path, "wb") as f:
            f.write(requests.get(video_url).content)

        # Trim video to exactly 4 seconds (logo takes first second)
        try:
            ffmpeg.input(raw_path).trim(start=0, end=4).output(
                final_path, c="copy"
            ).overwrite_output().run(quiet=True, overwrite_output=True)

            # Remove raw file
            os.remove(raw_path)

        except ffmpeg.Error as e:
            logger.warning(f"FFmpeg error: {e}")
            # If trimming fails, just rename the original
            os.rename(raw_path, final_path)

        logger.info(f"Video saved to {final_path}")

        # Return relative path for frontend access
        return f"/{OUTPUT_DIR}/{video_filename}"

    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")