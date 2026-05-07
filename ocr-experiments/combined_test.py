"""
ValoSarthi — Phase 3: Combined Pipeline Test
=============================================
Purpose : Single hotkey runs the full capture → OCR → normalise pipeline
          and prints the result. Measures latency.
Hotkey  : F8

Usage
-----
    python ocr-experiments/combined_test.py

Pass Criteria
-------------
  - Prints detected position string (e.g. 'mid_market') on F8.
  - Latency from F8 press to printed result < 300 ms.
  - Stable across 5+ different in-game positions.
  - Returns '' (not a crash) when standing in an unnamed area.

Once this is consistently accurate, proceed to Phase 4 integration.
Do NOT integrate early — stability first.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import keyboard
except ImportError:
    print("ERROR: 'keyboard' not installed. Run: pip install keyboard")
    sys.exit(1)

from engine.ocr_engine import detect_player_position


def on_f8():
    t0 = time.time()
    pos = detect_player_position()
    elapsed_ms = (time.time() - t0) * 1000

    if pos:
        print(f"Detected Position : {pos}   ({elapsed_ms:.0f} ms)")
    else:
        print(f"No position detected (empty string)   ({elapsed_ms:.0f} ms)")

    if elapsed_ms > 300:
        print(f"  ⚠  Latency exceeds 300 ms target ({elapsed_ms:.0f} ms)")


def main():
    print("Phase 3 — Combined Pipeline Test")
    print("Press F8 while Valorant is on screen.")
    print("Press Ctrl+C to quit.\n")
    keyboard.add_hotkey("F8", on_f8)
    keyboard.wait()


if __name__ == "__main__":
    main()
