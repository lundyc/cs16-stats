"""
file_utils.py
-------------
Common file operations used across the project.
"""

import os
import json
import csv
from typing import Any, Dict, List


# ------------------------------
# JSON Helpers
# ------------------------------

def load_json(path: str, default: Any = None) -> Any:
    """
    Load a JSON file. Returns `default` if not found.
    """
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: str) -> None:
    """
    Save data to JSON file (with pretty-print).
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ------------------------------
# CSV Helpers
# ------------------------------

def load_csv(path: str) -> List[Dict[str, str]]:
    """
    Load a CSV into a list of dictionaries.
    Returns [] if file does not exist.
    """
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def save_csv(data: List[Dict[str, Any]], path: str, fieldnames: List[str]) -> None:
    """
    Save a list of dictionaries to CSV.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# ------------------------------
# Misc Helpers
# ------------------------------

def ensure_dir(path: str) -> None:
    """
    Ensure that a directory exists.
    """
    os.makedirs(path, exist_ok=True)


def list_files(directory: str, extension: str = None) -> List[str]:
    """
    List all files in a directory, optionally filtered by extension.
    """
    if not os.path.exists(directory):
        return []
    files = os.listdir(directory)
    if extension:
        return [f for f in files if f.endswith(extension)]
    return files
