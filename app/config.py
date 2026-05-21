import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

port = int(os.getenv("PORT", 8000))

file_path = BASE_DIR / "app" / "storage" / "data.json"
