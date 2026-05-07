"""
ValoSarthi — Phase 2: OCR Text Extraction Test
===============================================
Purpose : Verify Tesseract reads text accurately from captured.png.
Input   : ocr-experiments/captured.png (produced by capture_test.py)

Usage
-----
    python ocr-experiments/ocr_test.py

Pass Criteria
-------------
  'Mid Market' → prints 'Mid Market'
  'Hookah'     → prints 'Hookah'
  'Heaven'     → prints 'Heaven'
  Accuracy acceptable if common positions are read correctly.

Common Issues
-------------
  Extra chars  → normalise() strips them (see engine/ocr_engine.py)
  Wrong chars  → Try adjusting contrast in _preprocess()
  Empty output → Region coordinates are wrong — revisit Phase 1
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

try:
    import pytesseract
except ImportError:
    print("ERROR: pytesseract not installed. Run: pip install pytesseract")
    sys.exit(1)

from engine.ocr_engine import _preprocess, normalise, TESS_CONFIG

IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captured.png")


def main():
    print("Phase 2 — OCR Text Extraction Test")
    print(f"Loading: {IMG_PATH}\n")

    if not os.path.isfile(IMG_PATH):
        print(f"ERROR: {IMG_PATH} not found.")
        print("Run capture_test.py first to generate captured.png.")
        sys.exit(1)

    img = Image.open(IMG_PATH)
    print(f"Image size: {img.size}")

    # Pre-process
    processed = _preprocess(img)
    processed.save(
        os.path.join(os.path.dirname(IMG_PATH), "captured_processed.png")
    )
    print("Saved pre-processed image → captured_processed.png")

    # OCR
    raw = pytesseract.image_to_string(processed, config=TESS_CONFIG)
    print(f"\nRaw OCR output : {repr(raw)}")
    print(f"Normalised     : {repr(normalise(raw))}")


if __name__ == "__main__":
    main()
