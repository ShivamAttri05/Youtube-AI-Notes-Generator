import os
import sys
import re
import requests
from os.path import dirname as up
from yt_dlp import YoutubeDL
from custom_logger import logger

sys.path.append(os.path.abspath(os.path.join(up(__file__), os.pardir)))


# ---------------- Save Markdown ----------------
def save_as_md(file_path: str, content: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    logger.info(f"Saving content to {file_path}")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------- Sanitize Filename ----------------
def sanitize_filename(filename: str) -> str:
    filename = os.path.splitext(filename)[0]
    sanitized = re.sub(r"[^a-z0-9-]", "-", filename.lower())
    sanitized = sanitized.strip("-")
    sanitized = re.sub(r"-+", "-", sanitized)
    return sanitized


# ---------------- Extract Filename ----------------
def extract_filename(filepath: str):
    base_name = os.path.basename(filepath)
    file_name = os.path.splitext(base_name)[0]
    return base_name, file_name


# ---------------- Get YouTube Title ----------------
def get_youtube_title(url: str):
    ydl_opts = {"quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("title", None)


# ---------------- Clean VTT Subtitles ----------------
def clean_vtt_content(vtt_text: str) -> str:
    """
    Removes timestamps and VTT formatting.
    """
    lines = vtt_text.splitlines()
    cleaned_lines = []

    for line in lines:
        if not line.strip():
            continue
        if "-->" in line:
            continue
        if line.startswith("WEBVTT"):
            continue
        if re.match(r"^\d+$", line.strip()):
            continue
        cleaned_lines.append(line.strip())

    return " ".join(cleaned_lines)


# ---------------- Get YouTube Transcript ----------------
def get_youtube_transcript(url: str):
    """
    Extract English subtitles from YouTube without downloading audio.
    """
    try:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "vtt",
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            subtitles = info.get("subtitles") or info.get("automatic_captions")

            if not subtitles:
                logger.error("No subtitles available.")
                return None

            if "en" not in subtitles:
                logger.error("No English subtitles available.")
                return None

            subtitle_url = subtitles["en"][0]["url"]

            response = requests.get(subtitle_url)
            if response.status_code != 200:
                logger.error("Failed to download subtitles.")
                return None

            cleaned_text = clean_vtt_content(response.text)

            logger.info("Transcript extracted successfully.")
            return cleaned_text

    except Exception as e:
        logger.error(f"Transcript extraction failed: {str(e)}")
        return None


# ---------------- Local Test ----------------
if __name__ == "__main__":
    test_url = "https://www.youtube.com/shorts/vJNkqS08D2M"

    transcript = get_youtube_transcript(test_url)

    if transcript:
        print("Transcript extracted successfully.")
        print(transcript[:1000])  # preview first 1000 characters
    else:
        print("Transcript not available.")
