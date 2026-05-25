import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data" / "trackers"
DATA_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "TrackFlow AI"
APP_VERSION = "0.1.0"

PORT = int(os.getenv("PORT", 8000))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
TRACKFLOW_DATA_PATH = Path(
    os.getenv("TRACKFLOW_DATA_PATH", BASE_DIR / "app" / "storage" / "data.json")
)

# Backward-compatible aliases for the original scaffold.
port = PORT
file_path = TRACKFLOW_DATA_PATH
