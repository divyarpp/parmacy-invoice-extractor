"""Stage 3: the back room. Reads invoices one at a time, in a background thread.

The web app hands over a job and gets an answer straight away. The worker
thread does the slow reading and saves the result in data/ocr/.
"""

import queue
import threading
import traceback
from datetime import datetime, timezone

import ocr_engine
import storage

# What the worker is doing with each invoice right now.
# States: queued, loading_models, running, failed.
# (A finished job is not kept here. The saved result file is the proof.)
_jobs = {}
_jobs_lock = threading.Lock()

_queue = queue.Queue()
_worker = None
_worker_lock = threading.Lock()

BUSY_STATES = ("queued", "loading_models", "running")


def result_path(document_id):
    return storage.OCR_DIR / f"{document_id}.json"


def raw_path(document_id):
    return storage.OCR_DIR / f"{document_id}_raw.json"


def cached_result(manifest):
    """The saved result, but only if it was made from this exact file
    with these exact models and settings. Otherwise None."""
    path = result_path(manifest["document_id"])
    if not path.is_file():
        return None
    result = storage.load_json(path)
    if result.get("cache_key") == ocr_engine.cache_key(manifest["sha256"]):
        return result
    return None


def get_status(manifest):
    """Where is this invoice in the reading process?"""
    document_id = manifest["document_id"]
    with _jobs_lock:
        job = _jobs.get(document_id)
        if job is not None:
            state, error = job["state"], job["error"]
        else:
            state, error = None, None

    if state is None:
        state = "done" if cached_result(manifest) is not None else "not_read"

    return {
        "document_id": document_id,
        "state": state,
        "error": error,
        "models_loaded": ocr_engine.is_loaded(),
    }


def submit(manifest):
    """Ask for an invoice to be read. Returns at once, never waits."""
    document_id = manifest["document_id"]

    # Already read with the same file and settings? Nothing to do.
    if cached_result(manifest) is not None:
        return

    with _jobs_lock:
        job = _jobs.get(document_id)
        if job is not None and job["state"] in BUSY_STATES:
            return  # already waiting or being read
        _jobs[document_id] = {"state": "queued", "error": None}

    _ensure_worker()
    _queue.put(document_id)


# ---------------------------------------------------------------- worker


def _set_state(document_id, state, error=None):
    with _jobs_lock:
        _jobs[document_id] = {"state": state, "error": error}


def _ensure_worker():
    """Start the background worker the first time it is needed."""
    global _worker
    with _worker_lock:
        if _worker is None:
            _worker = threading.Thread(target=_worker_loop, daemon=True)
            _worker.start()


def _worker_loop():
    while True:
        document_id = _queue.get()
        try:
            _process(document_id)
        except ocr_engine.ModelsMissingError as problem:
            _set_state(document_id, "failed", str(problem))
        except Exception as problem:  # keep the worker alive whatever happens
            traceback.print_exc()
            _set_state(
                document_id, "failed", f"Reading failed: {type(problem).__name__}: {problem}"
            )
        finally:
            _queue.task_done()


def _process(document_id):
    manifest = storage.load_manifest(document_id)
    if manifest is None:
        raise RuntimeError("The invoice record disappeared.")

    if not ocr_engine.is_loaded():
        _set_state(document_id, "loading_models")
        ocr_engine.get_engine()  # slow the first time; then stays in memory
    _set_state(document_id, "running")

    image_path = storage.DATA_DIR / manifest["original_path"]
    result, raw = ocr_engine.read_image(image_path)

    # PaddleOCR's own output, kept untouched next to our tidy record.
    raw_file = None
    try:
        raw.save_to_json(str(raw_path(document_id)))
        raw_file = raw_path(document_id).name
    except Exception:
        traceback.print_exc()  # the tidy record is still worth saving

    record = {
        "schema_version": 1,
        "document_id": document_id,
        "source_sha256": manifest["sha256"],
        "cache_key": ocr_engine.cache_key(manifest["sha256"]),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine": {
            **ocr_engine.engine_description(),
            "packages": ocr_engine.package_versions(),
        },
        "raw_file": raw_file,
        **result,
    }
    storage.save_json(result_path(document_id), record)
    storage.update_manifest(document_id, status="ocr_done")

    with _jobs_lock:
        _jobs.pop(document_id, None)  # finished: the saved file now tells the story