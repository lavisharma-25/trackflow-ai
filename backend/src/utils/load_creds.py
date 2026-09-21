import os
import glob

def load_json_path(cred_folder):
    """
    Returns the first JSON file path from the given folder.
    Raises FileNotFoundError if none is found.
    """

    json_files = glob.glob(os.path.join(cred_folder, "*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON credentials found in {cred_folder}")
    cred_path = json_files[0]
    return cred_path