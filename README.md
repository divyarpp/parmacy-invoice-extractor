# Pharmacy Invoice Extractor

A local, offline web app that reads pharmacy purchase invoices and, in later stages, turns them into structured data a person can review and approve.

Built for hospital Windows PCs: CPU-only, no cloud services, no data leaving the machine. The app listens on `127.0.0.1` only.

## Status

Work in progress, built in stages.

| Stage | Scope | State |
|---|---|---|
| 1 | Environment and standalone PaddleOCR test | Done |
| 2 | Upload, validation, preview, duplicate detection | Done |
| 3 | Background OCR, text boxes over the invoice, linked text list | Done |
| 4 | Manual layout templates and column-by-column extraction | Next |
| 5–9 | Review and correction, template editor, validation, CSV export, automatic template suggestions, packaging | Planned |

## What works today

- Upload JPG or PNG invoices. The app checks file content, not just the extension.
- Identical files are detected by SHA-256 fingerprint, so nothing is stored twice.
- Originals are kept untouched. A preview is generated with EXIF rotation applied.
- OCR runs in a background worker with the models loaded once. Results are cached against the file and model settings.
- The viewer draws a box for every piece of text, with its confidence score. Lower-scoring text is dashed amber, and clicking a box or a list line highlights its counterpart.

## Design principles

- **Local only.** Offline models, localhost binding, no CDN, no external AI service.
- **Human in the loop.** OCR scores are not proof of correctness, and unreadable values are never invented or silently corrected.
- **Raw beside parsed.** Original text is stored with every parsed value.
- **Money as Decimal.** Missing values are null, never zero.

## Stack

Python 3.12, PaddleOCR 3.4.1 (PP-OCRv5 mobile models), PaddlePaddle 3.2.0 (CPU), Flask, Pillow, OpenCV, plain HTML and JavaScript.

## Known OCR limits

Fused table cells, ruled lines misread as digits, handwriting read as text, and faint scans can all produce wrong readings. The template, validation and review stages exist to catch these. The tool does not promise perfect accuracy.

## Scope

In scope: purchase invoices, both cash and credit. Out of scope: payment receipts, ledgers and statements, delivery challans, credit notes, accounting integration, GST filing.
