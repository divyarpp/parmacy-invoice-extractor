"""Shared storage helpers: the data folders, JSON files, and invoice records.

Both app.py and ocr_jobs.py use this file, so the rules for where things
live are written in exactly one place.
"""

import json
import re
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ORIGINALS_DIR = DATA_DIR / "originals"
PREVIEWS_DIR = DATA_DIR / "previews"
MANIFESTS_DIR = DATA_DIR / "manifests"
OCR_DIR = DATA_DIR / "ocr"

# The portable storage layout.
for folder_name in (
    "originals",
    "previews",
    "manifests",
    "ocr",
    "extracted",
    "approved",
    "templates",
):
    (DATA_DIR / folder_name).mkdir(parents=True, exist_ok=True)

DOCUMENT_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")

# Only one thread at a time may rewrite an invoice record.
_manifest_lock = threading.Lock()


def save_json(path, content):
    """Write JSON safely: write a temporary file, then swap it into place."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    with open(temporary, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    temporary.replace(path)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def all_manifests():
    """Every saved invoice record, newest first."""
    records = [load_json(path) for path in MANIFESTS_DIR.glob("*.json")]
    records.sort(key=lambda record: record["uploaded_at"], reverse=True)
    return records


def load_manifest(document_id):
    """Load one record, or None. The id must look like 32 hex characters,
    so a web request can never point us at some other file."""
    if not DOCUMENT_ID_PATTERN.match(document_id):
        return None
    path = MANIFESTS_DIR / f"{document_id}.json"
    if not path.is_file():
        return None
    return load_json(path)


def update_manifest(document_id, **changes):
    """Change some fields of one invoice record and save it."""
    with _manifest_lock:
        record = load_manifest(document_id)
        if record is None:
            return None
        record.update(changes)
        save_json(MANIFESTS_DIR / f"{document_id}.json", record)
        return record


def summary(record):
    """The few fields the web page needs for its list."""
    return {
        "document_id": record["document_id"],
        "original_filename": record["original_filename"],
        "uploaded_at": record["uploaded_at"],
        "status": record["status"],
        "width_px": record["width_px"],
        "height_px": record["height_px"],
        "size_bytes": record["size_bytes"],
        "sha256": record["sha256"],
    }