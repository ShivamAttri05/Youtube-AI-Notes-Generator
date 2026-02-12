import os
import sys
from os.path import dirname as up

sys.path.append(os.path.abspath(os.path.join(up(__file__), os.pardir)))

from google import genai
from utils import GOOGLE_API_KEY, get_youtube_transcript
from custom_logger import logger

# Create Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)


def generate_notes_audio(
    youtube_url: str,
    model_name: str,
    system_prompt: str,
    user_prompt: str,
):
    """
    Extracts YouTube transcript and generates notes using Gemini.
    No audio download. No file upload. Faster and cleaner.
    """

    # ---------------- Get Transcript ----------------
    transcript = get_youtube_transcript(youtube_url)

    if not transcript:
        logger.error("Transcript not available.")
        return None

    logger.info("Transcript extracted successfully.")
    logger.info("Generating notes with Gemini...")
    logger.info(f"Model used: {model_name}")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": system_prompt},
                        {"text": user_prompt},
                        {"text": transcript},
                    ],
                }
            ],
        )

        return response

    except Exception as e:
        logger.error(f"Gemini generation failed: {str(e)}")
        return None


# ---------------- Local Test ----------------
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=nbicUrB7Mcc"

    response = generate_notes_audio(
        youtube_url=test_url,
        model_name="gemini-3-flash-preview",
        system_prompt="You are an expert educator creating structured notes.",
        user_prompt="Generate structured notes from this transcript.",
    )

    if response:
        print(response.text)
    else:
        print("Failed to generate notes.")
