import json
import re
import pandas as pd

from src.core.settings import settings

def load_json(file_path):
    if not file_path.exists():
        return {}
    with open(file_path, "r") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def get_registry():
    return load_json(settings.REGISTRY_FILE)


def save_registry(data):
    save_json(settings.REGISTRY_FILE, data)


def get_schema_registry():
    return load_json(settings.SCHEMA_FILE)


def save_schema_registry(data):
    save_json(settings.SCHEMA_FILE, data)


def get_tracker_path(name: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("Unsafe legacy tracker name")
    path = (settings.TRACKERS_DIR / f"{name}.xlsx").resolve()
    if path.parent != settings.TRACKERS_DIR.resolve():
        raise ValueError("Tracker path escaped the storage directory")
    return path


def load_tracker(name: str):
    path = get_tracker_path(name)
    if not path.exists():
        return None
    return pd.read_excel(path)


def save_tracker(name: str, df: pd.DataFrame):
    path = get_tracker_path(name)
    df.to_excel(path, index=False)
