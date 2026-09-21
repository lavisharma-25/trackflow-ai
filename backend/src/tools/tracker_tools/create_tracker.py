import pandas as pd

from src.models.tracker import CreateTrackerRequest
from src.tools.tracker_tools._shared import (
    get_registry,
    save_registry,
    get_schema_registry,
    save_schema_registry,
    get_tracker_path
)


def create_tracker(name: str, columns: list):
    """
    Create a new tracker with given schema.

    Args:
        name (str): Tracker name
        columns (list): List of column definitions

    Returns:
        dict: Status of creation
    """

    try:
        # Validate input using Pydantic
        req = CreateTrackerRequest(name=name, columns=columns)

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    registry = get_registry()
    schema_registry = get_schema_registry()

    if req.name in registry:
        return {"status": "error", "message": "Tracker already exists"}

    # Save schema
    schema_registry[req.name] = [c.model_dump() for c in req.columns]
    save_schema_registry(schema_registry)

    # Create Excel file
    col_names = [c.name for c in req.columns]
    df = pd.DataFrame(columns=col_names)

    path = get_tracker_path(req.name)
    df.to_excel(path, index=False)

    # Update registry
    registry[req.name] = {"columns": col_names}
    save_registry(registry)

    return {
        "status": "success",
        "message": f"Tracker '{req.name}' created successfully",
        "columns": schema_registry[req.name]
    }