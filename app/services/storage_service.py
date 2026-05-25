import json
from pathlib import Path
from app.config import DATA_DIR


class StorageService:

    @staticmethod
    def get_tracker_path(tracker_name: str) -> Path:
        return DATA_DIR / f"{tracker_name}.json"

    @staticmethod
    def read_tracker(tracker_name: str):
        path = StorageService.get_tracker_path(tracker_name)

        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def write_tracker(tracker_name: str, data: dict):
        path = StorageService.get_tracker_path(tracker_name)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)