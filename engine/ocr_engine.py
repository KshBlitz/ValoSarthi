"""
ValoSarthi — OCR Engine  (Sprint 2)
=====================================
Captures the Valorant HUD location text region and returns a
normalised position string ready to use as a lineup folder name.

Public API
----------
    capture_location_region() -> PIL.Image
    detect_player_position()  -> str          # e.g. "mid_market", "" on failure
"""

import re
import os

# ── Optional dependency guards ────────────────────────────────
try:
    import mss
    MSS_OK = True
except ImportError:
    MSS_OK = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import pytesseract
    TESS_OK = True
except ImportError:
    TESS_OK = False


# ── Tesseract binary path (Windows only) ─────────────────────
# If Tesseract is not on PATH, set the path via environment variable
# TESSERACT_CMD or edit this fallback directly.
_TESS_CMD = os.environ.get(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)
if TESS_OK and os.path.isfile(_TESS_CMD):
    pytesseract.pytesseract.tesseract_cmd = _TESS_CMD

# ── Tesseract config ──────────────────────────────────────────
# psm 7  = single line of text (best for short HUD labels)
# oem 3  = LSTM neural engine (most accurate)
TESS_CONFIG = "--psm 7 --oem 3"

# ── Capture region (1920×1080 baseline) ───────────────────────
# Valorant renders the current map zone (e.g. "Mid Market") as
# fixed HUD text in the upper-left area of the screen.
# Adjust these values for your display resolution using the
# Phase-1 calibration script (ocr-experiments/capture_test.py).
# You can also override via environment variables:
#   VLA_OCR_LEFT, VLA_OCR_TOP, VLA_OCR_WIDTH, VLA_OCR_HEIGHT
OCR_REGION = {
    "left":   int(os.environ.get("VLA_OCR_LEFT",   50)),
    "top":    int(os.environ.get("VLA_OCR_TOP",    10)),
    "width":  int(os.environ.get("VLA_OCR_WIDTH",  300)),
    "height": int(os.environ.get("VLA_OCR_HEIGHT", 35)),
}


# ══════════════════════════════════════════════════════════════
# Public functions
# ══════════════════════════════════════════════════════════════

def capture_location_region():
    """
    Capture the HUD location text area from the primary screen.

    Returns a PIL.Image ready for OCR processing.
    Raises RuntimeError if mss or Pillow are not installed.
    """
    if not MSS_OK:
        raise RuntimeError(
            "mss is not installed. Run: pip install mss"
        )
    if not PIL_OK:
        raise RuntimeError(
            "Pillow is not installed. Run: pip install Pillow"
        )

    with mss.mss() as sct:
        monitor = {
            "left":   OCR_REGION["left"],
            "top":    OCR_REGION["top"],
            "width":  OCR_REGION["width"],
            "height": OCR_REGION["height"],
        }
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    return img


def detect_player_position() -> str:
    """
    Full pipeline: capture → pre-process → OCR → normalise.

    Returns normalised position string (e.g. 'mid_market').
    Returns empty string '' on any failure — the matcher will then
    show 'No Lineup in Database' without crashing.
    """
    try:
        img = capture_location_region()
        img = _preprocess(img)
        raw = pytesseract.image_to_string(img, config=TESS_CONFIG)
        return normalise(raw)
    except Exception as e:
        print(f"[OCR] Error: {e}")
        return ""


# ══════════════════════════════════════════════════════════════
# Internal helpers
# ══════════════════════════════════════════════════════════════

def _preprocess(img):
    """
    OCR preprocessing tuned for Valorant HUD text.
    """

    # Convert to grayscale
    img = img.convert("L")

    # Upscale 3× for better OCR accuracy
    w, h = img.size
    img = img.resize((w * 3, h * 3), Image.BILINEAR)

    # Moderate contrast boost
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    return img


def normalise(raw_text: str) -> str:
    """
    Normalise raw OCR output to a folder-safe string.

        'Mid Market'  →  'mid_market'
        'A Elbow '    →  'a_elbow'
        'Hookah'      →  'hookah'
        'B Link\\n'   →  'b_link'
        ''            →  ''
    """
    text = raw_text.strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)   # strip punctuation / special chars
    text = re.sub(r"\s+", "_", text)           # spaces → underscores
    text = text.strip("_")                     # trim leading/trailing underscores
    return text
