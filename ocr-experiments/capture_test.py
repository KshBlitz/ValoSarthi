"""
ValoSarthi — Phase 1: Capture Region Test
==========================================
Purpose : Verify the screen crop contains only the HUD location text.
Hotkey  : F8
Output  : Saves captured.png next to this script.

Usage
-----
    python ocr-experiments/capture_test.py

Press F8 while Valorant is visible on screen. Check captured.png to confirm
the crop shows only the location label (e.g. "Mid Market") with no other HUD
elements. Adjust OCR_REGION in engine/ocr_engine.py if needed.

Pass Criteria
-------------
  - captured.png contains ONLY the location text area.
  - No minimap, health bar, or other HUD elements are visible.
  - Text is clearly legible in the saved image.
"""

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import keyboard
except ImportError:
    print("ERROR: 'keyboard' not installed. Run: pip install keyboard")
    sys.exit(1)

try:
    from engine.ocr_engine import capture_location_region, OCR_REGION
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captured.png")


def on_f8():
    print("F8 pressed — capturing screen region …")
    try:
        img = capture_location_region()
        img.save(OUT_PATH)
        print(f"Captured: saved to {OUT_PATH}")
        print(f"  Region: left={OCR_REGION['left']}, top={OCR_REGION['top']}, "
              f"width={OCR_REGION['width']}, height={OCR_REGION['height']}")
        print("  → Open captured.png and verify the crop.")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    print("Phase 1 — Capture Region Test")
    print(f"Current OCR_REGION: {OCR_REGION}")
    print("Press F8 while Valorant is on screen to capture.")
    print("Press Ctrl+C to quit.\n")

    keyboard.add_hotkey("F8", on_f8)
    keyboard.wait()


if __name__ == "__main__":
    main()
