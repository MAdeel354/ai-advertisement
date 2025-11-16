"""
Image generation service using Google Gemini AI.

Handles logo generation with Gemini AI models.
"""

import os
import uuid
from PIL import Image
from io import BytesIO
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


def generate_logo(prompt: str) -> str:
    """
    Generate a logo using Google Gemini AI.

    Args:
        prompt (str): Text prompt for logo generation

    Returns:
        str: Relative URL to the generated logo image

    Raises:
        HTTPException: If image generation fails
    """
    logger.info(f"Generating logo with Gemini AI for prompt: {prompt}")

    if not client:
        raise HTTPException(status_code=500, detail="Google API key not configured")

    try:
        # Create logo generation prompt
        input_prompt = (
            f"Create a logo for {prompt}. "
            "Make it minimalist, professional, suitable for brand identity. "
            "Use a clean vector style with transparent background if possible."
        )

        # Generate image using Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=input_prompt
        )

        # Extract and save the image
        logo_filename = f"logo_{uuid.uuid4().hex[:8]}.png"
        logo_path = os.path.join(OUTPUT_DIR, logo_filename)
        logger.info(f'logo name:{logo_filename}')
        # Process response parts to find image
        image_saved = False
        for part in response.parts:
            if part.inline_data is not None:
                # Convert inline data to PIL Image
                img_data = part.inline_data.data
                img = Image.open(BytesIO(img_data))

                # # Resize to 720×720 for consistency
                # if img.size != (720, 720):
                #     img = img.resize((720, 720), Image.LANCZOS)
                #
                # # Convert to RGBA for transparency support
                # if img.mode != 'RGBA':
                #     img = img.convert('RGBA')

                # Save the image
                img.save(logo_path, "PNG")
                image_saved = True
                break

        if not image_saved:
            raise HTTPException(status_code=500, detail="No image generated in response")

        logger.info(f"Logo saved to {logo_path}")

        # Return relative path for frontend access
        return f"/{OUTPUT_DIR}/{logo_filename}"

    except Exception as e:
        logger.error(f"Error generating logo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate logo: {str(e)}")