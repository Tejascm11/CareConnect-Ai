import json
import os

def load_json(path, default=None):
    """
    Safely load a JSON file.
    Returns `default` if file is missing or invalid.
    """
    if not os.path.exists(path):
        print(f"[ERROR] JSON file not found: {path}")
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON format in: {path}")
        return default
    except Exception as e:
        print(f"[ERROR] Failed to load JSON {path}: {e}")
        return default