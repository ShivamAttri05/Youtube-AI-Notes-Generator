import os
from dotenv import load_dotenv
from pathlib import Path

# Get project root (one level above utils/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DIR_NOTES_PATH = os.getenv("DIR_NOTES_PATH", "data/notes")
DIR_AUDIO_PATH = os.getenv("DIR_AUDIO_PATH", "data/audio")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
