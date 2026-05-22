import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.config import file_path
from app.core.trackers import SUPPORTED_TRACKERS

DEFAULT_DATA = {
    "watchlist": [],
    "conversations": {},
    "trackers": SUPPORTED_TRACKERS,
}


class JsonStore:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path or file_path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return deepcopy(DEFAULT_DATA)
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = {}
        return self._with_defaults(data)

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        normalized = self._with_defaults(data)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(normalized, file, indent=2)

    def get_collection(self, name: str) -> list[dict[str, Any]]:
        data = self.load()
        return list(data.get(name, []))

    def replace_collection(self, name: str, items: list[dict[str, Any]]) -> None:
        data = self.load()
        data[name] = items
        self.save(data)

    def get_conversation(self, conversation_id: str) -> dict[str, Any] | None:
        return self.load().get("conversations", {}).get(conversation_id)

    def set_conversation(self, conversation_id: str, value: dict[str, Any]) -> None:
        data = self.load()
        data["conversations"][conversation_id] = value
        self.save(data)

    def clear_conversation(self, conversation_id: str) -> None:
        data = self.load()
        data.get("conversations", {}).pop(conversation_id, None)
        self.save(data)

    def _with_defaults(self, data: dict[str, Any]) -> dict[str, Any]:
        normalized = deepcopy(DEFAULT_DATA)
        if isinstance(data, dict):
            normalized.update(data)
        if not isinstance(normalized.get("watchlist"), list):
            normalized["watchlist"] = []
        if not isinstance(normalized.get("conversations"), dict):
            normalized["conversations"] = {}
        if not normalized.get("trackers"):
            normalized["trackers"] = SUPPORTED_TRACKERS
        return normalized

def load_data():
    return JsonStore().load()

def save_data(data):
    JsonStore().save(data)
