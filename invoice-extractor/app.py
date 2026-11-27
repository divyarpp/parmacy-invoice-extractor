"""Local app: upload an invoice image, preview it, and read it with OCR.

Start it from the project folder:
    python app.py
then open http://127.0.0.1:8765 in your browser.
"""

import hashlib
import io
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from PIL import Image, ImageOps, UnidentifiedImageError

import ocr_jobs
from storage import (
    DATA_DIR,
    MANIFESTS_DIR,
    ORIGINALS_DIR,
    PREVIEWS_DIR,
    all_manifests,
    load_manifest,
    save_json,
    summary,
)

ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB
PREVIEW_MAX_SIDE = 1600  # pixels, longest side of the preview

# Refuse absurdly large images (a "decompression bomb").
Image.MAX_IMAGE_PIXELS = 100_000_000

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


def error_response(message, status):
    """A JSON error the web page can show to the user."""
    return jsonify({"error": message}), status


# ----------------------------------------------------------------- routes


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.errorhandler(413)
def file_too_large(_error):
    limit_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
    return error_response(f"The file is larger than {limit_mb} MB.", 413)


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/documents")
def list_documents():
    return jsonify([summary(record) for record in all_manifests()])


@app.get("/api/documents/<document_id>")
def get_document(document_id):
    record = load_manifest(document_id)
    if record is None:
        return error_response("Document not found.", 404)
    return jsonify(record)


@app.get("/api/documents/<document_id>/preview")
def get_preview(document_id):
    record = load_manifest(document_id)
    if record is None:
        return error_response("Document not found.", 404)
    return send_from_directory(DATA_DIR, record["preview_path"])


@app.post("/api/documents")
def upload_document():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return error_response("No file was chosen.", 400)

    # Keep only the file name, never any folder part the browser sent.
    original_name = Path(uploaded.filename.replace("\\", "/")).name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        shown = extension if extension else "(no extension)"
        return error_response(
            f"File type {shown} is not supported yet. Please use JPG or PNG.", 400
        )

    data = uploaded.read()
    if not data:
        return error_response("The file is empty.", 400)

    # An identical file we already hold? Do not store it twice.
    sha256 = hashlib.sha256(data).hexdigest()
    for record in all_manifests():
        if record["sha256"] == sha256:
            return jsonify({"duplicate": True, "document": summary(record)})

    # Is it really an image? Check the content, not just the file name.
    try:
        with Image.open(io.BytesIO(data)) as probe:
            probe.verify()
        with Image.open(io.BytesIO(data)) as image:
            image_format = image.format
            if image_format not in ALLOWED_FORMATS:
                return error_response(
                    f"This file is {image_format}, not a JPG or PNG image.", 400
                )
            exif_orientation = image.getexif().get(274, 1)
            upright = ImageOps.exif_transpose(image).convert("RGB")
    except (
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        ValueError,
        Image.DecompressionBombError,
    ):
        return error_response("This file could not be read as an image.", 400)

    width, height = upright.size
    preview = upright.copy()
    preview.thumbnail((PREVIEW_MAX_SIDE, PREVIEW_MAX_SIDE))

    document_id = uuid.uuid4().hex
    stored_name = document_id + ALLOWED_FORMATS[image_format]
    preview_name = document_id + ".jpg"

    # The original is saved exactly as received.
    (ORIGINALS_DIR / stored_name).write_bytes(data)
    preview.save(PREVIEWS_DIR / preview_name, "JPEG", quality=85)

    record = {
        "schema_version": 1,
        "document_id": document_id,
        "original_filename": original_name,
        "original_path": f"originals/{stored_name}",
        "preview_path": f"previews/{preview_name}",
        "sha256": sha256,
        "size_bytes": len(data),
        "format": image_format,
        "exif_orientation": exif_orientation,
        "width_px": width,
        "height_px": height,
        "preview_width_px": preview.size[0],
        "preview_height_px": preview.size[1],
        "uploaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "uploaded",
    }
    save_json(MANIFESTS_DIR / f"{document_id}.json", record)

    return jsonify({"duplicate": False, "document": summary(record)}), 201


# ------------------------------------------------------------ OCR routes


@app.post("/api/documents/<document_id>/ocr")
def start_ocr(document_id):
    """Ask for the invoice to be read. Returns at once with its status."""
    manifest = load_manifest(document_id)
    if manifest is None:
        return error_response("Document not found.", 404)
    ocr_jobs.submit(manifest)
    status = ocr_jobs.get_status(manifest)
    return jsonify(status), (200 if status["state"] == "done" else 202)


@app.get("/api/documents/<document_id>/ocr/status")
def ocr_status(document_id):
    manifest = load_manifest(document_id)
    if manifest is None:
        return error_response("Document not found.", 404)
    return jsonify(ocr_jobs.get_status(manifest))


@app.get("/api/documents/<document_id>/ocr")
def ocr_result(document_id):
    manifest = load_manifest(document_id)
    if manifest is None:
        return error_response("Document not found.", 404)
    result = ocr_jobs.cached_result(manifest)
    if result is None:
        return error_response("This invoice has not been read yet.", 404)
    return jsonify(result)


if __name__ == "__main__":
    # 127.0.0.1 means: only this computer can open the app.
    app.run(host="127.0.0.1", port=8765, debug=False)