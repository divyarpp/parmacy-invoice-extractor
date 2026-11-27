"""Stage 1: standalone PaddleOCR test.

Run from the project folder:
    python ocr_test.py samples\\Scanned_20261014-1927-01.jpg

Reads one image and saves, under outputs\\<image name>\\ :
    raw\\                  PaddleOCR's own JSON and preview image
    ocr_result.json       one record per detected text line (our format)
    ocr_text.txt          recognised text, one line per segment
    run_info.json         software versions, models, settings, timings
"""

import argparse
import hashlib
import json
import os
import time
from datetime import datetime
from importlib import metadata
from pathlib import Path

from PIL import Image

# Skip PaddleX's online check of model hosts.
# This must be set BEFORE paddleocr is imported.
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from paddleocr import PaddleOCR  # noqa: E402

# We name the models ourselves. With lang="en" PaddleOCR would pick the large
# "server" detector, which is heavy for an 8 GB laptop.
DET_MODEL = "PP-OCRv5_mobile_det"
REC_MODEL = "en_PP-OCRv5_mobile_rec"

# The models live inside the project, so nothing is downloaded at run time.
MODELS_DIR = Path("models")
DET_DIR = MODELS_DIR / DET_MODEL
REC_DIR = MODELS_DIR / REC_MODEL

PACKAGES = [
    "paddlepaddle",
    "paddleocr",
    "paddlex",
    "numpy",
    "opencv-contrib-python",
    "Pillow",
]


def package_versions():
    """Return {package name: installed version}."""
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def file_sha256(path):
    """Fingerprint of the source file, so we can tell identical files apart."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def polygon_to_box(polygon):
    """Turn a polygon [[x, y], ...] into a rectangle [x_min, y_min, x_max, y_max]."""
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    return [min(xs), min(ys), max(xs), max(ys)]


def main():
    parser = argparse.ArgumentParser(description="Run PaddleOCR on one image.")
    parser.add_argument("image", help="Path to a JPG or PNG file")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        raise SystemExit(f"File not found: {image_path}")

    out_dir = Path("outputs") / image_path.stem
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    for model_dir in (DET_DIR, REC_DIR):
        if not model_dir.is_dir():
            raise SystemExit(f"Model folder missing: {model_dir}")

    with Image.open(image_path) as img:
        file_width, file_height = img.size

    # Load the models once. This is the slow part (and downloads on first run).
    t0 = time.perf_counter()
    ocr = PaddleOCR(
        text_detection_model_name=DET_MODEL,
        text_detection_model_dir=str(DET_DIR),
        text_recognition_model_name=REC_MODEL,
        text_recognition_model_dir=str(REC_DIR),
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    load_seconds = time.perf_counter() - t0

    # Read the image.
    t1 = time.perf_counter()
    results = ocr.predict(str(image_path))
    predict_seconds = time.perf_counter() - t1

    res = results[0]  # one image in, one result out

    # PaddleOCR's own saved files, kept untouched as the raw record.
    res.save_to_json(str(raw_dir))
    res.save_to_img(str(raw_dir))

    # The size of the image the OCR actually read. Our 0-1 coordinates divide by this.
    ocr_height, ocr_width = res["doc_preprocessor_res"]["output_img"].shape[:2]

    texts = res["rec_texts"]
    scores = res["rec_scores"]
    polygons = res["rec_polys"]

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
                    round(x0 / ocr_width, 6),
                    round(y0 / ocr_height, 6),
                    round(x1 / ocr_width, 6),
                    round(y1 / ocr_height, 6),
                ],
            }
        )

    with open(out_dir / "ocr_result.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "source_file": image_path.name,
                "image_width_px": ocr_width,
                "image_height_px": ocr_height,
                "box_note": "box_norm = [x_min, y_min, x_max, y_max], 0-1, origin top-left",
                "segments": segments,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    with open(out_dir / "ocr_text.txt", "w", encoding="utf-8") as f:
        for segment in segments:
            f.write(segment["text"] + "\n")

    with open(out_dir / "run_info.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "run_at": datetime.now().isoformat(timespec="seconds"),
                "source_file": image_path.name,
                "source_sha256": file_sha256(image_path),
                "file_size_px": [file_width, file_height],
                "ocr_size_px": [ocr_width, ocr_height],
                "detection_model": DET_MODEL,
                "recognition_model": REC_MODEL,
                "settings": {
                    "use_doc_orientation_classify": False,
                    "use_doc_unwarping": False,
                    "use_textline_orientation": False,
                },
                "seconds_load_models": round(load_seconds, 2),
                "seconds_read_image": round(predict_seconds, 2),
                "packages": package_versions(),
            },
            f,
            indent=2,
        )

    # Short report on screen.
    print()
    print(f"File:             {image_path.name}")
    print(f"Image size:       {ocr_width} x {ocr_height} px")
    if (ocr_width, ocr_height) != (file_width, file_height):
        print(f"  note: the file header says {file_width} x {file_height}")
    print(f"Text segments:    {len(segments)}")
    if segments:
        all_scores = [s["score"] for s in segments]
        print(f"Score min / avg:  {min(all_scores):.3f} / {sum(all_scores) / len(all_scores):.3f}")
    print(f"Load models:      {load_seconds:.1f} s")
    print(f"Read image:       {predict_seconds:.1f} s")
    print(f"Saved to:         {out_dir}")
    print()
    print("First 15 segments:")
    for segment in segments[:15]:
        print(f"  {segment['score']:.2f}  {segment['text']}")


if __name__ == "__main__":
    main()