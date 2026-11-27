"""Stage 3: the OCR engine. Loads the models once and reuses them.

Quick test from the project folder:
    python ocr_engine.py samples\\Scanned_20261014-1927-01.jpg
"""

import argparse
import hashlib
import json
import os
import threading
import time
from importlib import metadata
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

# Skip PaddleX's online check of model hosts.
# This must be set BEFORE paddleocr is imported (which happens in get_engine).
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

BASE_DIR = Path(__file__).resolve().parent

DET_MODEL = "PP-OCRv5_mobile_det"
REC_MODEL = "en_PP-OCRv5_mobile_rec"
DET_DIR = BASE_DIR / "models" / DET_MODEL
REC_DIR = BASE_DIR / "models" / REC_MODEL

SETTINGS = {
    "use_doc_orientation_classify": False,
    "use_doc_unwarping": False,
    "use_textline_orientation": False,
}

# Change this number whenever the shape of our result record changes.
RESULT_SCHEMA_VERSION = 1

PACKAGES = [
    "paddlepaddle",
    "paddleocr",
    "paddlex",
    "numpy",
    "opencv-contrib-python",
    "Pillow",
]

_engine = None
_engine_lock = threading.Lock()  # protects loading
_run_lock = threading.Lock()  # one image at a time
_load_seconds = 0.0


class ModelsMissingError(Exception):
    """A model folder is not where we expect it."""


# ---------------------------------------------------------------- helpers


def package_versions():
    """Return {package name: installed version}."""
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def engine_description():
    """Everything that changes what the OCR would produce."""
    return {
        "detection_model": DET_MODEL,
        "recognition_model": REC_MODEL,
        "settings": SETTINGS,
        "result_schema_version": RESULT_SCHEMA_VERSION,
    }


def cache_key(source_sha256):
    """A fingerprint of: this exact file + these models and settings.
    If either changes, the key changes, and old results are not reused."""
    text = json.dumps(
        {"source": source_sha256, "engine": engine_description()}, sort_keys=True
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def polygon_to_box(polygon):
    """Turn a polygon [[x, y], ...] into [x_min, y_min, x_max, y_max]."""
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    return [min(xs), min(ys), max(xs), max(ys)]


def build_segments(texts, scores, polygons, width, height):
    """One record per detected text line, in our own format."""
    segments = []
    for index, (text, score, polygon) in enumerate(zip(texts, scores, polygons)):
        polygon_px = [[float(x), float(y)] for x, y in polygon]
        x0, y0, x1, y1 = polygon_to_box(polygon_px)
        segments.append(
            {
                "id": index,
                "text": text,
                "score": round(float(score), 4),
                "polygon_px": polygon_px,
                "box_px": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
                "box_norm": [
                    round(x0 / width, 6),
                    round(y0 / height, 6),
                    round(x1 / width, 6),
                    round(y1 / height, 6),
                ],
            }
        )
    return segments


def load_upright(image_path):
    """Open an image and turn it upright, exactly as the preview does."""
    with Image.open(image_path) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


# ----------------------------------------------------------------- engine


def get_engine():
    """Load the models on first use, then keep them in memory."""
    global _engine, _load_seconds
    with _engine_lock:
        if _engine is None:
            for model_dir in (DET_DIR, REC_DIR):
                if not model_dir.is_dir():
                    raise ModelsMissingError(f"Model folder missing: {model_dir}")

            started = time.perf_counter()
            from paddleocr import PaddleOCR  # the slow import happens here

            _engine = PaddleOCR(
                text_detection_model_name=DET_MODEL,
                text_detection_model_dir=str(DET_DIR),
                text_recognition_model_name=REC_MODEL,
                text_recognition_model_dir=str(REC_DIR),
                **SETTINGS,
            )
            _load_seconds = time.perf_counter() - started
        return _engine


def is_loaded():
    return _engine is not None


def read_image(image_path):
    """Run OCR on one image file.

    Returns (result, raw):
      result  our record: image size, timings, and the list of segments
      raw     PaddleOCR's own result object, for saving the untouched output
    """
    upright = load_upright(image_path)
    width, height = upright.size

    # PaddleOCR expects colour channels in Blue-Green-Red order.
    pixels = np.ascontiguousarray(np.asarray(upright)[:, :, ::-1])

    engine = get_engine()
    with _run_lock:
        started = time.perf_counter()
        results = engine.predict(pixels)
        read_seconds = time.perf_counter() - started

    raw = results[0]
    segments = build_segments(
        raw["rec_texts"], raw["rec_scores"], raw["rec_polys"], width, height
    )

    result = {
        "image_width_px": width,
        "image_height_px": height,
        "box_note": "box_norm = [x_min, y_min, x_max, y_max], 0-1, origin top-left",
        "seconds_load_models": round(_load_seconds, 2),
        "seconds_read_image": round(read_seconds, 2),
        "segments": segments,
    }
    return result, raw


# ------------------------------------------------------------- quick test


def main():
    parser = argparse.ArgumentParser(description="Test the OCR engine on one image.")
    parser.add_argument("image", help="Path to a JPG or PNG file")
    args = parser.parse_args()

    try:
        result, _raw = read_image(args.image)
    except ModelsMissingError as problem:
        raise SystemExit(str(problem))

    segments = result["segments"]
    print()
    print(f"Image size:       {result['image_width_px']} x {result['image_height_px']} px")
    print(f"Text segments:    {len(segments)}")
    print(f"Load models:      {result['seconds_load_models']} s")
    print(f"Read image:       {result['seconds_read_image']} s")
    print()
    print("First 10 segments (text, score, box_norm):")
    for segment in segments[:10]:
        print(f"  {segment['text']!r:40} {segment['score']:.2f}  {segment['box_norm']}")


if __name__ == "__main__":
    main()