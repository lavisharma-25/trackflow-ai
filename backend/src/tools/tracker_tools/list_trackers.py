from src.tools.tracker_tools._shared import get_registry


def list_trackers():
    """
    Fetch all existing trackers.

    Returns:
        dict: List of trackers
    """
    registry = get_registry()

    if not registry:
        return {"message": "No trackers found"}

    return {
        "trackers": list(registry.keys()),
        "count": len(registry)
    }