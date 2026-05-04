# Valorant Lineup Assistant — MVP v1.0

Two programs. One shared lineup database.

---

## Setup

```bash
pip install PyQt5 keyboard
```

> **Windows:** Run both programs as Administrator for global hotkeys to work.

---

## Game Tool  (`main.py`)

Run during matches.

```bash
python main.py
```

### Hotkeys

| Key | Action |
|-----|--------|
| F5  | Setup — pick Map + Agent (run once before match) |
| F6  | Spike site → Agent position → lineup fires |
| F7  | Repeat — show same lineup again, resets 7s timer |

### F6 Selection Keys

**Step 1 — Spike Site:**

| Key | Site |
|-----|------|
| 9 | A Default |
| 8 | A Open |
| 7 | B Default |
| 6 | B Open |
| 5 | C Default |
| 4 | C Open |

**Step 2 — Agent Position:**

| Key | Position |
|-----|----------|
| 9 | [X] Main (prefixed with site letter) |
| 8 | Mid |

### State Rules

- T1 (F5) must be set before F6 or F7 work
- Changing T1 wipes T2 — must re-enter spike + position
- F7 does nothing if T2 not yet set
- No lineup found → overlay shows "No Lineup in Database"
- Overlay auto-closes after 7 seconds
- F7 kills active overlay and restarts 7s countdown immediately

---

## Lineup Manager  (`manager.py`)

Run before/after matches to manage your lineup database.

```bash
python manager.py
```

### Add Lineup

1. Select Map, Agent, Spike Site, Agent Position, Throw Type
2. Upload `stand.png` — screenshot of where to stand
3. Upload `aim.gif` — screen recording of aim + throw
4. Click Save

### View / Delete

Browse all saved lineups with image status indicators. Delete any lineup.

---

## Database Structure

```
lineups/
└── {map}/
    └── {agent}/
        └── {spike_site}/          e.g. b_default
            └── {agent_position}/  e.g. b_main  or  mid
                ├── stand.png
                ├── aim.gif
                └── meta.json      {"throw": "normal"} or {"throw": "jump"}
```

---

## Project Structure

```
valorant-lineup-assistant/
├── main.py          ← Game tool
├── manager.py       ← Lineup manager
├── requirements.txt
├── README.md
├── engine/
│   ├── __init__.py
│   ├── state.py     ← Shared constants + AppState
│   └── matcher.py   ← Lineup matching logic
└── lineups/         ← Your lineup database (add via manager.py)
```
