# ◈ ValoSarthi — AI-Powered Valorant Lineup Assistant

> **The first in-game lineup tool that reads where you're standing and pulls the right smoke or molly automatically — zero keypresses after the spike is planted.**

---

## What Is ValoSarthi?

Most lineup tools make you alt-tab to a website, remember a YouTube timestamp, or pause mid-round to click through menus. ValoSarthi lives as a background process that never touches your game window. You press **one hotkey**, pick the spike site, and it reads your on-screen position using OCR — then instantly shows you the correct stand position (screenshot) and aim animation (GIF) overlaid in the corner of your screen. No second keypress. No manual position selection. Just play.

### Why this changes things for the Valo community

Most agents have 10–20 useful lineups per map. Memorising all of them is genuinely hard, especially when you're on a new map or playing an off-agent. ValoSarthi turns lineup knowledge into a shared, community-built database that anyone can run locally. The more contributors add lineups, the more powerful it gets for everyone.

---

## Features (Sprint 2)

- **OCR-powered position detection** — uses Tesseract to read the HUD location text and auto-selects your agent position. No manual Step 2.
- **Single-keypress lineup trigger** — press F6, pick the spike site (6 options), and the lineup overlay appears.
- **Stand image + aim GIF** — shows exactly where to stand and the animated aim point side by side.
- **Throw type indicator** — displays NORMAL or JUMP THROW in the overlay so you don't have to remember.
- **7-second auto-close** — the overlay disappears on its own without breaking game flow.
- **F7 repeat** — re-shows the last lineup instantly if you missed it.
- **System tray** — runs silently in the background; right-click for all controls.
- **Lineup Manager** — a separate GUI (`manager.py`) to add, view, and delete lineups from the database with image previews.
- **Open lineup database** — the `lineups/` folder is just folders and files. Anyone can fork, add lineups, and submit a pull request.
- **Windowed Fullscreen compatible** — overlay renders on top of Valorant without alt-tabbing.

---

## Requirements

- **OS:** Windows 10 / 11 (64-bit)
- **Valorant:** set to Windowed Fullscreen (required for overlay and OCR)
- **Python:** 3.10 or higher
- **Tesseract OCR:** must be installed separately (see below)
- **Run as Administrator:** required for the `keyboard` library to intercept F-keys

---

## Installation — Step by Step

### 1. Install Python

Download Python 3.10+ from [python.org](https://www.python.org/downloads/) and install it. Make sure to check **"Add Python to PATH"** during installation.

### 2. Install Tesseract OCR

Tesseract is the OCR engine that reads your HUD position text.

1. Download the Windows installer from: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and note the install path (default: `C:\Program Files\Tesseract-OCR\`)
3. Make sure `tesseract.exe` is in that folder

ValoSarthi automatically looks for Tesseract at the default path. If you installed it somewhere else, set this environment variable before running:

```
set TESSERACT_CMD=C:\Your\Custom\Path\tesseract.exe
```

### 3. Clone the Repository

Open Command Prompt and run:

```cmd
git clone https://github.com/your-username/ValoSarthi.git
cd ValoSarthi
```

### 4. Install Python Dependencies

```cmd
pip install -r requirements.txt
```

This installs: `PyQt5`, `keyboard`, `pytesseract`, `Pillow`, and `mss`.

---

## Running ValoSarthi

**Important: You must run Command Prompt as Administrator**, otherwise the `keyboard` library cannot intercept global hotkeys like F5/F6/F7 while Valorant is in focus.

To open CMD as Administrator: press **Win**, type `cmd`, right-click **Command Prompt → Run as administrator**.

Then navigate to the project folder and run:

```cmd
python main.py
```

You'll see confirmation in the terminal:

```
Hotkeys active:
  F5 — Setup (map + agent)
  F6 — Spike site → lineup
  F7 — Repeat lineup
```

A tray icon will appear. ValoSarthi is now running.

---

## How to Use It In-Game

ValoSarthi requires Valorant to be in **Windowed Fullscreen** mode. Set this in Valorant: **Settings → Video → Window Mode → Windowed Fullscreen**.

### First Time — Setup

1. Press **F5** — the Setup window appears
2. Select your **Map** and **Agent**
3. Click **CONFIRM**

You only need to do this once per map, or when you switch agents.

### Each Round — Getting a Lineup

1. Find your position on the map (stand where you would throw from)
2. Press **F6** — an overlay appears in the top-right corner showing spike site options
3. Press the corresponding number key (4–9) for the site you want to smoke/molly

| Key | Site Option |
|-----|-------------|
| 9   | A Default   |
| 8   | A Open      |
| 7   | B Default   |
| 6   | B Open      |
| 5   | C Default   |
| 4   | C Open      |

ValoSarthi then reads your HUD position via OCR and shows the lineup automatically — the stand image and aim GIF appear in the corner with the throw type.

4. Line up, throw, and win the round.
5. The overlay closes after 7 seconds, or press **F7** to repeat it.

### Hotkey Summary

| Hotkey | Action |
|--------|--------|
| F5     | Open Setup (map + agent) |
| F6     | Start lineup sequence (spike site selection) |
| F7     | Repeat the last lineup |
| 4–9    | Select spike site during F6 overlay |

---

## Contributing Lineups

ValoSarthi's lineup database lives in the `lineups/` folder. The more people contribute, the better it gets for everyone. Here's how to add your lineups properly.

### Folder Structure

Every lineup is stored like this:

```
lineups/
└── {map}/
    └── {agent}/
        └── {site_folder}/
            └── {position_folder}/
                ├── stand.png       ← where to stand (screenshot)
                ├── aim.gif         ← where to aim (screen recording as GIF)
                └── meta.json       ← throw type
```

Example:
```
lineups/ascent/brimstone/a_default/mid_market/
```

### Using the Lineup Manager

The easiest way to add lineups is through the Lineup Manager GUI:

```cmd
python manager.py
```

Fill in the fields in the **Add Lineup** panel:

- **Map** — select from the dropdown
- **Agent** — select from the dropdown
- **Spike Site** — select the site (e.g. A Default, B Open)
- **Agent Position** — type the position name (see format rules below)
- **Throw Type** — Normal or Jump
- **stand.png** — upload a screenshot showing where to stand
- **aim.gif** — upload a GIF of the aim animation

Click **Save Lineup** and it's added to the database instantly.

---

### Agent Position — Format Rules

The position field is free-text, but it **must match the location name shown in the Valorant HUD** when you're standing in that spot. The game displays this as text in the top-left of the screen (e.g. "Mid Market", "A Lobby", "B Main").

**Rules:**

- Type it exactly as it appears in the Valorant HUD
- Use Title Case: first letter of each word capitalised
- Spaces are fine — they get converted to underscores internally
- Letters and numbers only — no special characters

| What you type | What gets saved | Valid? |
|---------------|-----------------|--------|
| `A Main`      | `a_main`        | ✅     |
| `Mid Market`  | `mid_market`    | ✅     |
| `B Lobby`     | `b_lobby`       | ✅     |
| `Hookah`      | `hookah`        | ✅     |
| `A Elbow`     | `a_elbow`       | ✅     |
| `amain`       | `amain`         | ❌ Won't match OCR |
| `a-main`      | `amain`         | ❌ Hyphens stripped |
| `A MAIN`      | `a_main`        | ✅ Works but use Title Case |

**The golden rule:** stand at the position in Valorant, look at what the HUD says in the top-left corner, and type that exactly.

---

### What to Record for stand.png and aim.gif

**stand.png** — a screenshot showing:
- Your character's feet / body position relative to a wall, ledge, or corner
- Enough context to identify the exact spot
- Taken in a custom game with no enemies

**aim.gif** — a short screen recording (converted to GIF) showing:
- Where to aim (crosshair position)
- The throw animation (for jump throws, include the jump)
- Ideally includes the smoke/molly landing on the target

Tools to create GIFs: ShareX, ScreenToGif, or OBS + EZGIF.

---

### How to Submit Your Lineups

Once you've tested your lineups and confirmed they work in ValoSarthi:

1. **Fork** the repository on GitHub
2. **Create a branch** with your name or agent/map:
   ```
   git checkout -b contributor-yourname
   ```
   or
   ```
   git checkout -b lineups-ascent-brimstone
   ```
3. Add your lineup folders under `lineups/`
4. **Push** your branch:
   ```
   git push origin contributor-yourname
   ```
5. Open a **Pull Request** to `main`

The maintainers will review the lineups for accuracy and merge good ones into main. Only tested, accurate lineups will be accepted — please verify each one works in a custom game before submitting.

---

## Project Structure

```
ValoSarthi/
├── main.py                    ← Game overlay tool (run this in-game)
├── manager.py                 ← Lineup Manager GUI (run separately)
├── requirements.txt           ← Python dependencies
├── engine/
│   ├── state.py               ← App state, maps, agents, constants
│   ├── matcher.py             ← Lineup lookup logic
│   └── ocr_engine.py          ← Screen capture + Tesseract OCR
├── lineups/
│   └── {map}/{agent}/{site}/{position}/
│       ├── stand.png
│       ├── aim.gif
│       └── meta.json
└── ocr-experiments/           ← OCR dev/calibration tools
    ├── capture_test.py        ← Test screen capture region (F8)
    ├── ocr_test.py            ← Test OCR text extraction
    └── combined_test.py       ← Full pipeline test (F8)
```

---

## Troubleshooting

**Overlay doesn't show / hotkeys don't work**
Run CMD as Administrator. The `keyboard` library requires admin rights to intercept system-wide keys.

**"No Lineup in Database" shows even though I'm in the right spot**
The OCR might be reading a slightly different position name. Run `ocr-experiments/combined_test.py` (press F8 while in-game) to see what text is being detected, then make sure your lineup folder name matches that output.

**Tesseract not found error**
Check that Tesseract is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`, or set the `TESSERACT_CMD` environment variable to the correct path.

**OCR region is wrong / reading garbage**
Run `ocr-experiments/capture_test.py` to save a screenshot of what the tool is capturing. Adjust the `OCR_REGION` values in `engine/ocr_engine.py` or via the environment variables `VLA_OCR_LEFT`, `VLA_OCR_TOP`, `VLA_OCR_WIDTH`, `VLA_OCR_HEIGHT`.

**Overlay appears behind Valorant**
Make sure Valorant is in Windowed Fullscreen, not Fullscreen (exclusive). Exclusive Fullscreen blocks overlays from other applications.

---

## License

MIT — free to use, fork, and build on. Lineup images and GIFs contributed by the community remain the property of their creators.

---

*ValoSarthi is an independent community project and is not affiliated with or endorsed by Riot Games.*# ◈ ValoSarthi — AI-Powered Valorant Lineup Assistant

> **The first in-game lineup tool that reads where you're standing and pulls the right smoke or molly automatically — zero keypresses after the spike is planted.**

---

## What Is ValoSarthi?

Most lineup tools make you alt-tab to a website, remember a YouTube timestamp, or pause mid-round to click through menus. ValoSarthi lives as a background process that never touches your game window. You press **one hotkey**, pick the spike site, and it reads your on-screen position using OCR — then instantly shows you the correct stand position (screenshot) and aim animation (GIF) overlaid in the corner of your screen. No second keypress. No manual position selection. Just play.

### Why this changes things for the Valo community

Most agents have 10–20 useful lineups per map. Memorising all of them is genuinely hard, especially when you're on a new map or playing an off-agent. ValoSarthi turns lineup knowledge into a shared, community-built database that anyone can run locally. The more contributors add lineups, the more powerful it gets for everyone.

---

## Features (Sprint 2)

* **OCR-powered position detection** — uses Tesseract to read the HUD location text and auto-selects your agent position. No manual Step 2.
* **Single-keypress lineup trigger** — press F6, pick the spike site (6 options), and the lineup overlay appears.
* **Stand image + aim GIF** — shows exactly where to stand and the animated aim point side by side.
* **Throw type indicator** — displays NORMAL or JUMP THROW in the overlay so you don't have to remember.
* **7-second auto-close** — the overlay disappears on its own without breaking game flow.
* **F7 repeat** — re-shows the last lineup instantly if you missed it.
* **System tray** — runs silently in the background; right-click for all controls.
* **Lineup Manager** — a separate GUI (`manager.py`) to add, view, and delete lineups from the database with image previews.
* **Open lineup database** — the `lineups/` folder is just folders and files. Anyone can fork, add lineups, and submit a pull request.
* **Windowed Fullscreen compatible** — overlay renders on top of Valorant without alt-tabbing.

---

## Requirements

* **OS:** Windows 10 / 11 (64-bit)
* **Valorant:** set to Windowed Fullscreen (required for overlay and OCR)
* **Python:** 3.10 or higher
* **Git:** required for cloning, pulling, and pushing changes
* **VS Code (recommended):** easier environment and project management
* **Tesseract OCR:** must be installed separately (see below)
* **Run as Administrator:** required for the `keyboard` library to intercept F-keys

---

## Installation — Full Fresh Windows Setup Guide

This section assumes you are setting up ValoSarthi on a completely fresh Windows machine.

---

### 1. Install Python

Download Python from:

```text
https://www.python.org/downloads/windows/
```

Recommended version:

* Python 3.11.x preferred
* Python 3.13 also works

During installation:

✅ IMPORTANT:

* Check **"Add Python to PATH"**
* Choose **"Install for all users"** if available

Recommended install location:

```text
C:\Program Files\Python313
```

Avoid installing into AppData/local user folders if possible.

---

### 2. Verify Python Installation

Open Command Prompt and run:

```cmd
python --version
```

Expected output:

```cmd
Python 3.x.x
```

Then verify PATH:

```cmd
where python
```

Expected:

```cmd
C:\Program Files\Python313\python.exe
```

If Python is not recognised:

* reinstall Python
* ensure "Add Python to PATH" was checked

---

### 3. Install Git

Download Git for Windows:

```text
https://git-scm.com/download/win
```

During installation, when prompted about PATH settings, choose:

```text
Git from the command line and also from 3rd-party software
```

After installation, restart Command Prompt and verify:

```cmd
git --version
```

Expected:

```cmd
git version x.x.x.windows.x
```

---

### 4. Install VS Code (Recommended)

Download:

```text
https://code.visualstudio.com/
```

Recommended during installation:

* Add to PATH
* Register Code as editor
* Enable shell integration

Install these VS Code extensions:

* Python (Microsoft)
* Pylance

---

### 5. Install Tesseract OCR

Tesseract is the OCR engine that reads your HUD position text.

1. Download the Windows installer from:

```text
https://github.com/UB-Mannheim/tesseract/wiki
```

2. Install it (default recommended path):

```text
C:\Program Files\Tesseract-OCR\
```

3. Verify this file exists:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If installed elsewhere, set:

```cmd
set TESSERACT_CMD=C:\Your\Custom\Path\tesseract.exe
```

before running the project.

---

### 6. Clone the Repository

Create a clean projects folder first:

```cmd
mkdir C:\Projects
cd C:\Projects
```

Clone the repository:

```cmd
git clone https://github.com/KshBlitz/ValoSarthi.git
cd ValoSarthi
```

---

### 7. Create a Python Virtual Environment

Inside the project folder:

```cmd
python -m venv venv
```

This creates an isolated Python environment for the project.

---

### 8. Activate the Virtual Environment

#### If using Command Prompt (CMD)

```cmd
venv\Scripts\activate
```

#### If using PowerShell

Fresh Windows installs often block script execution by default.

Run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate:

```powershell
.\venv\Scripts\Activate.ps1
```

Expected result:

```text
(venv)
```

appears before the terminal path.

---

### 9. Install Python Dependencies

Install all required packages:

```cmd
pip install -r requirements.txt
```

Core dependencies include:

* PyQt5
* keyboard
* Pillow
* pytesseract
* mss

If `requirements.txt` is missing or outdated, install manually:

```cmd
pip install PyQt5 keyboard pillow pytesseract mss
```

---

### 10. Verify Environment Setup

Run these commands:

```cmd
python -c "import PyQt5; print('PyQt OK')"
```

```cmd
python -c "import keyboard; print('keyboard OK')"
```

```cmd
python -c "from PIL import Image; print('Pillow OK')"
```

If all print successfully, the environment is configured correctly.

---

### 11. Optional — VS Code Python Interpreter Setup

If VS Code does not automatically detect the virtual environment:

1. Press:

```text
Ctrl + Shift + P
```

2. Search:

```text
Python: Select Interpreter
```

3. Select:

```text
./venv/Scripts/python.exe
```

If no interpreters appear:

* install the Python extension
* reload VS Code
* manually browse to:

```text
C:\Projects\ValoSarthi\venv\Scripts\python.exe
```

This step is optional if you already run the project successfully through the terminal.

---

### 12. Important — Run as Administrator

ValoSarthi uses the `keyboard` library for global hotkeys.

Because of this:

* VS Code
* PowerShell
* Command Prompt

should be launched as Administrator when testing overlays or using hotkeys in-game.

Without elevation:

* F5/F6/F7 may fail silently
* overlays may not trigger properly

---

## Daily Development Workflow

### Before Starting Work

Always pull the latest repository changes first:

```cmd
git pull
```

This is extremely important if you work across:

* multiple PCs
* laptop + desktop
* contributors/branches

Failing to pull first can cause:

* merge conflicts
* overwritten files
* outdated lineup data

---

### Activating the Environment

Before running the project each session:

#### CMD

```cmd
venv\Scripts\activate
```

#### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

---

### Running the Project

Run the in-game overlay tool:

```cmd
python main.py
```

Run the lineup manager:

```cmd
python manager.py
```

---

### Saving and Pushing Your Changes

After making changes:

```cmd
git add .
git commit -m "Describe your changes"
git push
```

Example:

```cmd
git commit -m "Added Ascent Brimstone lineups"
```

---

### Pulling Latest Changes on Another Machine

On your laptop or second PC:

```cmd
git pull
```

This syncs:

* latest code
* new lineups
* updated overlays
* manager changes
* OCR improvements

---

### Recommended Git Workflow

For larger features or experiments:

Create a branch:

```cmd
git checkout -b feature-name
```

Example:

```cmd
git checkout -b overlay-rework
```

Then later merge it into `main`.

This prevents unstable experimental code from breaking the main branch.

---

## Running ValoSarthi

**Important: You must run Command Prompt / PowerShell / VS Code as Administrator**, otherwise the `keyboard` library cannot intercept global hotkeys like F5/F6/F7 while Valorant is in focus.

To open CMD as Administrator:

* Press **Win**
* Type `cmd`
* Right-click **Command Prompt → Run as administrator**

Then navigate to the project folder and run:

```cmd
python main.py
```

You'll see confirmation in the terminal:

```text
Hotkeys active:
  F5 — Setup (map + agent)
  F6 — Spike site → lineup
  F7 — Repeat lineup
```

A tray icon will appear. ValoSarthi is now running.

---

## How to Use It In-Game

ValoSarthi requires Valorant to be in **Windowed Fullscreen** mode. Set this in Valorant:

```text
Settings → Video → Window Mode → Windowed Fullscreen
```

### First Time — Setup

1. Press **F5** — the Setup window appears
2. Select your **Map** and **Agent**
3. Click **CONFIRM**

You only need to do this once per map, or when you switch agents.

### Each Round — Getting a Lineup

1. Find your position on the map (stand where you would throw from)
2. Press **F6** — an overlay appears in the top-right corner showing spike site options
3. Press the corresponding number key (4–9) for the site you want to smoke/molly

| Key | Site Option |
| --- | ----------- |
| 9   | A Default   |
| 8   | A Open      |
| 7   | B Default   |
| 6   | B Open      |
| 5   | C Default   |
| 4   | C Open      |

ValoSarthi then reads your HUD position via OCR and shows the lineup automatically — the stand image and aim GIF appear in the corner with the throw type.

4. Line up, throw, and win the round.
5. The overlay closes after 7 seconds, or press **F7** to repeat it.

### Hotkey Summary

| Hotkey | Action                                       |
| ------ | -------------------------------------------- |
| F5     | Open Setup (map + agent)                     |
| F6     | Start lineup sequence (spike site selection) |
| F7     | Repeat the last lineup                       |
| 4–9    | Select spike site during F6 overlay          |

---

## Contributing Lineups

ValoSarthi's lineup database lives in the `lineups/` folder. The more people contribute, the better it gets for everyone. Here's how to add your lineups properly.

### Folder Structure

Every lineup is stored like this:

```text
lineups/
└── {map}/
    └── {agent}/
        └── {site_folder}/
            └── {position_folder}/
                ├── stand.png
                ├── aim.gif
                └── meta.json
```

Example:

```text
lineups/ascent/brimstone/a_default/mid_market/
```

### Using the Lineup Manager

The easiest way to add lineups is through the Lineup Manager GUI:

```cmd
python manager.py
```

Fill in the fields in the **Add Lineup** panel:

* **Map** — select from the dropdown
* **Agent** — select from the dropdown
* **Spike Site** — select the site (e.g. A Default, B Open)
* **Agent Position** — type the position name (see format rules below)
* **Throw Type** — Normal or Jump
* **stand.png** — upload a screenshot showing where to stand
* **aim.gif** — upload a GIF of the aim animation

Click **Save Lineup** and it's added to the database instantly.

---

### Agent Position — Format Rules

The position field is free-text, but it **must match the location name shown in the Valorant HUD** when you're standing in that spot. The game displays this as text in the top-left of the screen (e.g. "Mid Market", "A Lobby", "B Main").

### Rules

* Type it exactly as it appears in the Valorant HUD
* Use Title Case: first letter of each word capitalised
* Spaces are fine — they get converted to underscores internally
* Letters and numbers only — no special characters

| What you type | What gets saved | Valid?                     |
| ------------- | --------------- | -------------------------- |
| `A Main`      | `a_main`        | ✅                          |
| `Mid Market`  | `mid_market`    | ✅                          |
| `B Lobby`     | `b_lobby`       | ✅                          |
| `Hookah`      | `hookah`        | ✅                          |
| `A Elbow`     | `a_elbow`       | ✅                          |
| `amain`       | `amain`         | ❌ Won't match OCR          |
| `a-main`      | `amain`         | ❌ Hyphens stripped         |
| `A MAIN`      | `a_main`        | ✅ Works but use Title Case |

### Golden Rule

Stand at the position in Valorant, look at what the HUD says in the top-left corner, and type that exactly.

---

### What to Record for stand.png and aim.gif

#### stand.png

A screenshot showing:

* your character's feet/body position
* nearby wall or corner references
* enough visual context to identify the exact spot

#### aim.gif

A short GIF showing:

* crosshair placement
* throw animation
* jump timing (if applicable)
* ideally the smoke/molly landing correctly

Tools for GIF creation:

* ShareX
* ScreenToGif
* OBS + EZGIF

---

### How to Submit Your Lineups

1. Fork the repository on GitHub
2. Create a branch:

```cmd
git checkout -b contributor-yourname
```

or:

```cmd
git checkout -b lineups-ascent-brimstone
```

3. Add lineup folders under `lineups/`
4. Push your branch:

```cmd
git push origin contributor-yourname
```

5. Open a Pull Request to `main`

Please test all lineups in a custom game before submitting.

---

## Project Structure

```text
ValoSarthi/
├── main.py                    ← Game overlay tool (run this in-game)
├── manager.py                 ← Lineup Manager GUI (run separately)
├── requirements.txt           ← Python dependencies
├── engine/
│   ├── state.py               ← App state, maps, agents, constants
│   ├── matcher.py             ← Lineup lookup logic
│   └── ocr_engine.py          ← Screen capture + Tesseract OCR
├── lineups/
│   └── {map}/{agent}/{site}/{position}/
│       ├── stand.png
│       ├── aim.gif
│       └── meta.json
└── ocr-experiments/
    ├── capture_test.py
    ├── ocr_test.py
    └── combined_test.py
```

---

## Troubleshooting

### PowerShell says "running scripts is disabled"

Run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then:

```powershell
.\venv\Scripts\Activate.ps1
```

---

### 'git' is not recognised

Git either:

* is not installed
* OR was installed without PATH integration

Reinstall Git and ensure this option is selected:

```text
Git from the command line and also from 3rd-party software
```

---

### VS Code doesn't detect the virtual environment

Usually harmless.

You can still run the project manually from the activated terminal.

Optional fix:

* install Python extension
* reload VS Code
* manually select:

```text
./venv/Scripts/python.exe
```

as the interpreter.

---

### Overlay doesn't show / hotkeys don't work

Run terminal/VS Code as Administrator.

The `keyboard` library requires elevated permissions for global hotkeys.

---

### "No Lineup in Database" appears incorrectly

The OCR may be reading a slightly different position name.

Run:

```cmd
python ocr-experiments/combined_test.py
```

and compare detected text with your lineup folder names.

---

### Tesseract not found

Ensure this file exists:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

or manually set:

```cmd
set TESSERACT_CMD=C:\Path\To\tesseract.exe
```

---

### Overlay appears behind Valorant

Make sure Valorant is running in:

```text
Windowed Fullscreen
```

Exclusive Fullscreen blocks overlays from external applications.

---

## License

MIT — free to use, fork, and build on.

Lineup images and GIFs contributed by the community remain the property of their creators.

---

*ValoSarthi is an independent community project and is not affiliated with or endorsed by Riot Games.*
