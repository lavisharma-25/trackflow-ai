SUPPORTED_TRACKERS = [
    {"key": "watchlist", "name": "Watchlist Tracker", "implemented": True},
    {"key": "games", "name": "Games Tracker", "implemented": False},
    {"key": "finance", "name": "Finance Tracker", "implemented": False},
    {"key": "project", "name": "Project Tracker", "implemented": False},
]

TRACKER_KEYS = {tracker["key"] for tracker in SUPPORTED_TRACKERS}


def normalize_tracker(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def get_tracker(key: str) -> dict | None:
    normalized = normalize_tracker(key)
    if normalized == "projects":
        normalized = "project"
    for tracker in SUPPORTED_TRACKERS:
        if tracker["key"] == normalized:
            return tracker
    return None
