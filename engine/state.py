"""
Shared application state and constants.
Both main.py and manager.py import from here.
"""

import os

# ── Paths ─────────────────────────────────────────────────────
ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINEUPS_DIR = os.path.join(ROOT_DIR, "lineups")

# ── Maps (12) ────────────────────────────────────────────────
MAPS = [
    "Ascent", "Bind", "Haven", "Split", "Fracture",
    "Breeze", "Icebox", "Pearl", "Lotus", "Sunset",
    "Abyss", "Drift"
]

# ── Agents (24) ──────────────────────────────────────────────
AGENTS = [
    "Brimstone", "Viper", "Omen", "Killjoy", "Cypher",
    "Sova", "Sage", "Phoenix", "Jett", "Reyna",
    "Raze", "Breach", "Skye", "Yoru", "Astra",
    "KAY/O", "Chamber", "Neon", "Fade", "Harbor",
    "Gekko", "Deadlock", "Iso", "Clove"
]

# ── Spike Sites ───────────────────────────────────────────────
SPIKE_SITES = [
    "A Default", "A Open",
    "B Default", "B Open",
    "C Default", "C Open",
]

# Key → site index mapping (keys 9,8,7,6,5,4)
SITE_KEYS = {
    "9": "A Default",
    "8": "A Open",
    "7": "B Default",
    "6": "B Open",
    "5": "C Default",
    "4": "C Open",
}

# ── Agent Positions ───────────────────────────────────────────
# Derived at runtime from spike site letter
# Main → prefixed with site letter  e.g. "B Default" → "B Main"
# Mid  → always "Mid", no prefix

POSITION_KEYS = {
    "9": "main",   # [X] Main
    "8": "mid",    # Mid
}

def get_position_label(spike_site: str, pos_key: str) -> str:
    """
    Returns display label for a position.
    spike_site e.g. "B Default", pos_key "9" or "8"
    """
    if pos_key == "8":
        return "Mid"
    letter = spike_site[0].upper()   # "A", "B", or "C"
    return f"{letter} Main"

def get_position_folder(spike_site: str, pos_key: str) -> str:
    """
    Returns the folder name used on disk.
    e.g. "b_main", "mid"
    """
    if pos_key == "8":
        return "mid"
    letter = spike_site[0].lower()
    return f"{letter}_main"

def site_to_folder(site: str) -> str:
    """'B Default' → 'b_default'"""
    return site.lower().replace(" ", "_")

def folder_to_site(folder: str) -> str:
    """'b_default' → 'B Default'"""
    return folder.replace("_", " ").title()

# ── Throw Types ───────────────────────────────────────────────
THROW_TYPES = ["Normal", "Jump"]

THROW_DISPLAY = {
    "normal": "NORMAL THROW",
    "jump":   "JUMP THROW",
}

# ── Runtime State (held in memory by main.py) ─────────────────
class AppState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.map_name:        str   = ""
        self.agent:           str   = ""
        self.spike_site:      str   = ""   # e.g. "B Default"
        self.agent_position:  str   = ""   # e.g. "b_main" or "mid"
        self.t1_set:          bool  = False
        self.t2_set:          bool  = False

    def set_t1(self, map_name: str, agent: str):
        self.map_name   = map_name
        self.agent      = agent
        self.t1_set     = True
        # Invalidate T2
        self.spike_site     = ""
        self.agent_position = ""
        self.t2_set         = False

    def set_t2(self, spike_site: str, agent_position: str):
        self.spike_site     = spike_site
        self.agent_position = agent_position
        self.t2_set         = True

    @property
    def ready(self) -> bool:
        return self.t1_set and self.t2_set
