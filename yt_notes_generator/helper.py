import os
import sys
from os.path import dirname as up

sys.path.append(os.path.abspath(os.path.join(up(__file__), os.pardir)))

from google import genai
from utils import GOOGLE_API_KEY, get_youtube_transcript
from utils.constants import CHUNK_SIZE
from custom_logger import logger


def generate_notes_audio(
    youtube_url: str,
    model_name: str,
    system_prompt: str,
    user_prompt: str,
):
    """
    Extract YouTube transcript and generate notes using Gemini.

    This uses text-only processing (no audio download or file upload) for
    faster, cheaper inference while keeping the behavior of the app unchanged.
    """

    if not GOOGLE_API_KEY:
        logger.error("Missing GOOGLE_API_KEY; cannot generate notes with Gemini.")
        return None

    # Create Gemini client lazily so missing keys fail here instead of at import time
    client = genai.Client(api_key=GOOGLE_API_KEY)

    # ---------------- Get Transcript ----------------
    transcript = get_youtube_transcript(youtube_url)

    if not transcript:
        logger.error("Transcript not available.")
        return None

    logger.info("Transcript extracted successfully.")
    logger.info("Generating notes with Gemini...")
    logger.info(f"Model used: {model_name}")

    try:
        # If transcript is short enough, send directly
        if len(transcript) <= CHUNK_SIZE:
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

        # Otherwise, chunk the transcript and generate per-chunk notes
        logger.info("Transcript exceeds chunk size; splitting into chunks.")
        chunks = [transcript[i : i + CHUNK_SIZE] for i in range(0, len(transcript), CHUNK_SIZE)]
        partial_notes = []

        for idx, chunk in enumerate(chunks, start=1):
            logger.info(f"Generating notes for chunk {idx}/{len(chunks)}")
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=[
                        {
                            "role": "user",
                            "parts": [
                                {"text": system_prompt},
                                {"text": f"{user_prompt}\n\n[Chunk {idx}/{len(chunks)}]"},
                                {"text": chunk},
                            ],
                        }
                    ],
                )

                partial_text = getattr(resp, "text", "")
                if partial_text:
                    partial_notes.append(partial_text)
                else:
                    logger.warning(f"Empty response for chunk {idx}")
            except Exception as e:
                logger.error(f"Chunk generation failed for chunk {idx}: {str(e)}")
                return None

        # Stitch partial notes together by asking the model to merge them
        merge_prompt = (
            "Merge the following partial notes into a single, clean, deduplicated set of notes. "
            "Preserve logical order, headings, and important details. Remove duplicates and keep the result concise.\n\n"
            "Partial notes:\n\n"
            + "\n\n---\n\n".join(partial_notes)
        )

        logger.info("Merging partial notes into final document.")

        final_response = client.models.generate_content(
            model=model_name,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": system_prompt},
                        {"text": merge_prompt},
                    ],
                }
            ],
        )

        return final_response

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
