import os
from dotenv import load_dotenv
from pathlib import Path

# Get project root (one level above utils/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root (safe to call multiple times)
load_dotenv(BASE_DIR / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DIR_NOTES_PATH = os.getenv("DIR_NOTES_PATH", "data/notes")
DIR_AUDIO_PATH = os.getenv("DIR_AUDIO_PATH", "data/audio")
DIR_TRANSCRIPTS = os.getenv("DIR_TRANSCRIPTS", "data/transcripts")

# Chunk size (characters) for naive transcript chunking. Tune as needed.
try:
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "25000"))
except Exception:
    CHUNK_SIZE = 25000

# Do not raise at import time if the API key is missing; allow the app UI
# to handle missing keys gracefully.
