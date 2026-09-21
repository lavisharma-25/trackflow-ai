import os
from src.tools.tracker_tools._shared import (
    get_registry,
    save_registry,
    get_schema_registry,
    save_schema_registry,
    get_tracker_path
)


def delete_tracker(
    name: str,
    password: str | None = None,
    confirmed: bool = False,
):
    """
    Delete a tracker permanently after password validation.

    Returns:
        dict: Status message
    """

    if confirmed is not True:
        return {"error": "Deletion requires confirmed=true"}

    registry = get_registry()
    schema_registry = get_schema_registry()

    if name not in registry:
        return {"error": "Tracker not found"}

    # remove file
    path = get_tracker_path(name)
    if path.exists():
        os.remove(path)

    # remove registry entries
    registry.pop(name, None)
    schema_registry.pop(name, None)

    save_registry(registry)
    save_schema_registry(schema_registry)

    return {
        "status": "success",
        "message": f"Tracker '{name}' deleted"
    }
