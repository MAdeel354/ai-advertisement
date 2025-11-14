"""
Image generation service using Replicate SDXL models.

Handles logo generation with SDXL models.
"""

import os
import uuid
import requests
from PIL import Image
from io import BytesIO
import replicate
from fastapi import HTTPException
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Configuration
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
OUTPUT_DIR = "output"
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_logo(prompt: str) -> str:
    """
    Generate a logo using SDXL via Replicate.

    Args:
        prompt (str): Text prompt for logo generation

    Returns:
        str: Relative URL to the generated logo image

    Raises:
        HTTPException: If image generation fails
    """
    logger.info(f"Generating logo with SDXL for prompt: {prompt}")

    try:
        # Try the primary SDXL model first
        model = client.models.get("stability-ai/stable-diffusion-xl")
        version = model.versions.get("7762fd07cf82c948538e41f63f77d2b5")
    except Exception as e:
        logger.warning(f"Primary SDXL model not found, trying fallback... Error: {e}")
        try:
            # Fallback to sdxl-turbo
            model = client.models.get("stability-ai/sdxl-turbo")
            version = model.versions.get("d33fb258a3c9d7c52cb51e35a5d38d8b")
        except Exception as e2:
            logger.error(f"Fallback model also not found: {e2}")
            raise HTTPException(status_code=404, detail="No available SDXL model found on Replicate")

    input_prompt = (
        f"minimalist flat logo for {prompt}, vector style, "
        "white background, brand identity, simple icon"
    )

    try:
        output = version.predict(
            prompt=input_prompt,
            width=1024,
            height=1024,
            refine="expert_ensemble_refiner",
            scheduler="K_EULER",
            num_outputs=1,
            guidance_scale=7.5,
            apply_watermark=False,
        )

        logo_url = output[0]

        # Generate unique filename
        logo_filename = f"logo_{uuid.uuid4().hex[:8]}.png"
        logo_path = os.path.join(OUTPUT_DIR, logo_filename)

        # Download and save image
        img_data = requests.get(logo_url).content
        with open(logo_path, "wb") as f:
            f.write(img_data)

        # Resize to 720×720 for consistency
        img = Image.open(BytesIO(img_data)).convert("RGBA")
        img = img.resize((720, 720), Image.LANCZOS)
        img.save(logo_path)

        logger.info(f"Logo saved to {logo_path}")

        # Return relative path for frontend access
        return f"/{OUTPUT_DIR}/{logo_filename}"

    except Exception as e:
        logger.error(f"Error generating logo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate logo: {str(e)}")