import base64
import json
import time
from google import genai
from google.genai import types
from app.config import settings

# =====================================================================
# TODO 1: Initialize the Google GenAI Client for Gemini Platform
# Use genai.Client() with enterprise=True, project, and location from settings.
# =====================================================================
client = genai.Client(
    enterprise=True,
    project=settings.project_id,
    location=settings.location,
    
    
)  # REPLACE THIS WITH YOUR CODE

def generate_driver_prompt(image_bytes: bytes, scene_option: str) -> str:
    """Uses Gemini 3.8 Flash via Interactions API to craft a detailed prompt from the driver photo."""
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    # =====================================================================
    # TODO 2: Call client.interactions.create()
    # Model: "gemini-3.8-flash"
    # Input: list of dicts [{"type": "text", ...}, {"type": "image", "bytes": ..., "mime_type": "image/jpeg"}]
    # Generation Config: {"thinking_level": "high", "temperature": 0.2}
    # =====================================================================
    interaction =     interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=[
            {"type": "text", "text": f"Analyze this photo and write a prompt describing this person as a Formula E race driver in a high-tech suit for a {scene_option} scene beside a Gen4 formula E car in night with flash on the driver."},
            {"type": "image", "bytes": base64_image, "mime_type": "image/jpeg"}
        ],
        generation_config={
            "thinking_level": "high",
            "temperature": 0.2
        }
    ) # REPLACE THIS WITH YOUR CODE
    
    return interaction.output_text

def generate_driver_avatar(driver_prompt: str, image_bytes: bytes) -> bytes:
    # """Uses Nano Banana 2 (gemini-3.1-flash-image) to generate stylized driver avatar."""

    text_parts = types.Part.from_text(text=f"Generate a stylized Formula E driver portrait: {driver_prompt}")

    image_parts = types.Part.from_bytes(data=image_bytes,
            mime_type='image/jpeg',)

    gen4_image_parts = types.Part.from_uri(file_uri="https://coffeecornermotorsport.com/wp-content/uploads/2026/04/m37258_GEN4-HERO3.webp", mime_type="image/webp")
    
    # =====================================================================
    # TODO 3: Call client.models.generate_content() for image generation
    # Model: "gemini-3.1-flash-image" or "gemini-nano-banana-2.1"
    # Content: A list with the parts
    # Generation Config: Image Response Modality and 16:9 Aspect ratio
    # =====================================================================
        
    response = client.models.generate_content(
    model="gemini-nano-banana-2.1", # Or "gemini-nano-banana-2.1"
    content=[text_parts, image_parts, gen4_image_parts],
    config=types.GenerateContentConfig(   
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9"),
        )
    )  # REPLACE THIS WITH YOUR CODE
    
    generated_bytes = None
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                generated_bytes = part.inline_data.data
                break

return base64.b64encode(generated_bytes).decode('utf-8')


def generate_formula_e_video(driver_prompt: str, avatar_bytes: bytes) -> bytes:
    """Uses Gemini Omni 1.1 Flash to generate an 8-second cinematic Formula E video."""
    base64_avatar = base64.b64encode(avatar_bytes).decode("utf-8")
    
    # =====================================================================
    # TODO 4a: Start async video generation with 'gemini-omni-1.1-flash-preview'
    # Input: list of dicts with avatar image and prompt text. Set background=True!
    # =====================================================================
    interaction = client.interactions.create(
        model="gemini-omni-1.1-flash-preview",
        input=[
            {"type": "text", "text": f"Generate an 8-second 60fps cinematic video: {driver_prompt}. Formula E racing atmosphere with crowd cd ~/fe-genmedia-kiosk."},
            {"type": "image", "bytes": base64_avatar, "mime_type": "image/png"}
        ],
        background=True
    )  # REPLACE THIS WITH YOUR CODE
    
    # =====================================================================
    # TODO 4b: Write polling loop with client.interactions.get(interaction.id)
    # Loop every 5 seconds until status == "completed" or "failed".
    # Return base64.b64decode(status_check.output_video.data)
    # =====================================================================
    while True:
        # REPLACE THIS LOOP BODY WITH YOUR CODE
        status_check = client.interactions.get(interaction.id)
        if status_check.status == "completed":
            return base64.b64decode(status_check.output_video.data)
        elif status_check.status in ["failed", "cancelled"]:
            raise RuntimeError(f"Video generation failed: {status_check.status}")
        time.sleep(5)