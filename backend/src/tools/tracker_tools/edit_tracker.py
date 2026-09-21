import pandas as pd

from src.tools.tracker_tools._shared import (
    get_registry,
    save_registry,
    get_schema_registry,
    save_schema_registry,
    get_tracker_path
)


def edit_tracker(name: str, action: str, payload: dict):
    """
    Edit tracker schema.

    Actions:
        - add_column
        - remove_column
        - rename_column
        - change_type

    Returns:
        dict: Operation result
    """

    registry = get_registry()
    schema_registry = get_schema_registry()

    if name not in registry:
        return {"error": "Tracker not found"}

    schema = schema_registry.get(name, [])
    df_path = get_tracker_path(name)

    if action == "add_column":
        new_col = payload["column"]
        schema.append(new_col)

        df = pd.read_excel(df_path)
        df[new_col["name"]] = None
        df.to_excel(df_path, index=False)

    elif action == "remove_column":
        col_name = payload["column_name"]
        schema = [c for c in schema if c["name"] != col_name]

        df = pd.read_excel(df_path)
        df = df.drop(columns=[col_name], errors="ignore")
        df.to_excel(df_path, index=False)

    elif action == "rename_column":
        old = payload["old_name"]
        new = payload["new_name"]

        for c in schema:
            if c["name"] == old:
                c["name"] = new

        df = pd.read_excel(df_path)
        df = df.rename(columns={old: new})
        df.to_excel(df_path, index=False)

    elif action == "change_type":
        # metadata only (no strict enforcement in Excel layer)
        col = payload["column_name"]
        new_type = payload["new_type"]

        for c in schema:
            if c["name"] == col:
                c["type"] = new_type

    else:
        return {"error": "Invalid action"}

    schema_registry[name] = schema
    save_schema_registry(schema_registry)

    registry[name]["columns"] = [column["name"] for column in schema]
    save_registry(registry)

    return {
        "status": "success",
        "message": f"Tracker '{name}' updated",
        "action": action
    }
