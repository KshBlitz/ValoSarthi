"""
ValoSarthi — Game Tool (main.py)  [Sprint 2]
=============================================
Hotkeys:
  F5  — T1: Map + Agent setup window
  F6  — T2: Spike site selection → OCR auto-detects position → fire lineup
  F7  — Repeat / show same lineup again
  4–9 — Selection keys (only active during F6 Step 1 overlay)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Dependency check ──────────────────────────────────────────
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QLabel,
        QComboBox, QPushButton, QVBoxLayout, QHBoxLayout,
        QFrame, QSystemTrayIcon, QMenu, QAction, QSizePolicy,
    )
    from PyQt5.QtCore  import Qt, QTimer, pyqtSignal, QObject
    from PyQt5.QtGui   import QPixmap, QMovie, QFont, QIcon, QKeyEvent
except ImportError:
    print("ERROR: PyQt5 not found.\nRun: pip install PyQt5 keyboard")
    sys.exit(1)

try:
    import keyboard
    KEYBOARD_OK = True
except ImportError:
    KEYBOARD_OK = False
    print("WARNING: 'keyboard' package not found — hotkeys disabled.\nRun: pip install keyboard")

from engine.state      import AppState, MAPS, AGENTS, SITE_KEYS, THROW_DISPLAY
from engine.matcher    import match_lineup
from engine.ocr_engine import detect_player_position

# ── Palette ───────────────────────────────────────────────────
C = {
    "bg":       "#0D0F17",
    "surface":  "#161923",
    "border":   "#252836",
    "red":      "#FF4655",
    "dim_red":  "rgba(255,70,85,0.18)",
    "text":     "#E2E4EF",
    "sub":      "#6B7090",
    "gold":     "#F0B429",
    "green":    "#36C95F",
    "white":    "#FFFFFF",
    "key_bg":   "#1E2130",
}

OVERLAY_AUTO_CLOSE_MS = 7000
OVERLAY_WIDTH         = 300


# ══════════════════════════════════════════════════════════════
# Signal bridge (keyboard lib → Qt main thread)
# ══════════════════════════════════════════════════════════════
class HotkeyBridge(QObject):
    f5_pressed = pyqtSignal()
    f6_pressed = pyqtSignal()
    f7_pressed = pyqtSignal()
    key_pressed = pyqtSignal(str)   # "4"–"9"


# ══════════════════════════════════════════════════════════════
# T1 Setup Window
# ══════════════════════════════════════════════════════════════
class SetupWindow(QWidget):
    def __init__(self, state: AppState, on_confirm):
        super().__init__()
        self.state      = state
        self.on_confirm = on_confirm
        self.setWindowTitle("Lineup Assistant — Setup")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedWidth(360)
        self.setStyleSheet(self._sheet())
        self._build()

    def _sheet(self):
        return f"""
        QWidget      {{ background:{C['bg']}; color:{C['text']};
                        font-family:'Segoe UI',Arial; font-size:13px; }}
        QComboBox    {{ background:{C['surface']}; border:1px solid {C['border']};
                        border-radius:6px; padding:6px 10px; color:{C['text']}; }}
        QComboBox:focus {{ border-color:{C['red']}; }}
        QComboBox QAbstractItemView {{ background:{C['surface']};
                        selection-background-color:{C['red']};
                        border:1px solid {C['border']}; color:{C['text']}; }}
        QPushButton  {{ background:{C['red']}; color:#fff; font-weight:700;
                        border:none; border-radius:6px;
                        padding:9px 18px; letter-spacing:1px; }}
        QPushButton:hover {{ background:#FF6B77; }}
        QPushButton#cancel {{ background:{C['surface']}; color:{C['sub']};
                        border:1px solid {C['border']}; font-weight:400; }}
        QPushButton#cancel:hover {{ color:{C['text']}; }}
        """

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 22)
        lay.setSpacing(14)

        # Title
        t = QLabel("◈  SETUP")
        t.setStyleSheet(f"color:{C['red']};font-size:17px;font-weight:900;letter-spacing:3px;")
        lay.addWidget(t)
        sub = QLabel("Select map and agent for this match")
        sub.setStyleSheet(f"color:{C['sub']};font-size:11px;")
        lay.addWidget(sub)
        lay.addWidget(self._sep())

        # Map
        lay.addWidget(self._label("MAP"))
        self.map_cb = QComboBox()
        self.map_cb.addItems(MAPS)
        if self.state.map_name:
            idx = self.map_cb.findText(self.state.map_name)
            if idx >= 0: self.map_cb.setCurrentIndex(idx)
        lay.addWidget(self.map_cb)

        # Agent
        lay.addWidget(self._label("AGENT"))
        self.agent_cb = QComboBox()
        self.agent_cb.addItems(AGENTS)
        if self.state.agent:
            idx = self.agent_cb.findText(self.state.agent)
            if idx >= 0: self.agent_cb.setCurrentIndex(idx)
        lay.addWidget(self.agent_cb)

        lay.addSpacing(6)

        # Buttons
        row = QHBoxLayout()
        cancel = QPushButton("Cancel");  cancel.setObjectName("cancel")
        confirm = QPushButton("CONFIRM  ▶")
        cancel.clicked.connect(self.close)
        confirm.clicked.connect(self._confirm)
        row.addWidget(cancel); row.addWidget(confirm)
        lay.addLayout(row)

        hint = QLabel("F5 Setup  |  F6 Spike Site (auto-detects position)  |  F7 Repeat")
        hint.setStyleSheet(f"color:{C['sub']};font-size:10px;")
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint)

    def _label(self, txt):
        l = QLabel(txt)
        l.setStyleSheet(f"color:{C['sub']};font-size:10px;font-weight:700;"
                        f"letter-spacing:2px;margin-bottom:-8px;")
        return l

    def _sep(self):
        s = QFrame(); s.setFrameShape(QFrame.HLine)
        s.setStyleSheet(f"border:none;border-top:1px solid {C['border']};margin:2px 0;")
        return s

    def _confirm(self):
        self.state.set_t1(self.map_cb.currentText(), self.agent_cb.currentText())
        self.on_confirm()
        self.close()


# ══════════════════════════════════════════════════════════════
# F6 Input Overlay  (spike selection + position selection)
# ══════════════════════════════════════════════════════════════
class InputOverlay(QMainWindow):
    """
    Sprint 2: Single-step key-driven selection overlay.
    Step 1: spike site (keys 9,8,7,6,5,4)
    After spike key press: OCR fires automatically to detect position,
    then emits done(spike_site, agent_position_folder). Step 2 removed.
    """

    def __init__(self, state: AppState, on_done):
        super().__init__()
        self.state   = state
        self.on_done = on_done
        self.step    = 1          # 1 = spike, 2 = position
        self._spike  = ""

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint  |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(OVERLAY_WIDTH)
        self._build()
        self._position_window()

    # ── Layout ─────────────────────────────────────────────────
    def _build(self):
        root = QWidget()
        root.setObjectName("root")
        root.setStyleSheet(f"""
            #root {{
                background: rgba(13,15,23,0.95);
                border: 1px solid {C['red']};
                border-radius: 10px;
            }}
        """)
        self.setCentralWidget(root)

        lay = QVBoxLayout(root)
        lay.setContentsMargins(14, 12, 14, 14)
        lay.setSpacing(6)

        # Header label
        self.header_lbl = QLabel("")
        self.header_lbl.setStyleSheet(
            f"color:{C['red']};font-size:10px;font-weight:700;"
            f"letter-spacing:3px;padding:2px 0;"
        )
        lay.addWidget(self.header_lbl)

        lay.addWidget(self._sep())

        # Rows container
        self.rows_widget = QWidget()
        self.rows_lay    = QVBoxLayout(self.rows_widget)
        self.rows_lay.setContentsMargins(0, 4, 0, 0)
        self.rows_lay.setSpacing(4)
        lay.addWidget(self.rows_widget)

        self.adjustSize()

    def _sep(self):
        s = QFrame(); s.setFrameShape(QFrame.HLine)
        s.setStyleSheet(f"border:none;border-top:1px solid {C['border']};")
        return s

    # ── Steps ──────────────────────────────────────────────────
    def show_step1(self):
        self.step = 1
        self.header_lbl.setText("◈ SPIKE SITE")
        self._clear_rows()
        items = [
            ("9", "A Default"), ("8", "A Open"),
            ("7", "B Default"), ("6", "B Open"),
            ("5", "C Default"), ("4", "C Open"),
        ]
        for key, label in items:
            self._add_row(key, label)
        self.adjustSize()
        self._position_window()
        self.show()
        self.raise_()

    def show_step2(self, spike_site: str):
        self.step   = 2
        self._spike = spike_site
        letter = spike_site[0].upper()
        self.header_lbl.setText("◈ YOUR POSITION")
        self._clear_rows()
        self._add_row("9", f"{letter} Main")
        self._add_row("8", "Mid")
        self.adjustSize()
        self._position_window()

    def _clear_rows(self):
        while self.rows_lay.count():
            item = self.rows_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_row(self, key: str, label: str):
        row = QWidget()
        row.setStyleSheet(f"""
            QWidget {{ background:{C['key_bg']}; border-radius:6px; }}
        """)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(10, 6, 10, 6)
        rl.setSpacing(12)

        key_lbl = QLabel(key)
        key_lbl.setFixedWidth(20)
        key_lbl.setAlignment(Qt.AlignCenter)
        key_lbl.setStyleSheet(
            f"color:{C['gold']};font-size:14px;font-weight:900;"
            f"background:transparent;"
        )

        val_lbl = QLabel(label)
        val_lbl.setStyleSheet(
            f"color:{C['text']};font-size:13px;background:transparent;"
        )

        rl.addWidget(key_lbl)
        rl.addWidget(val_lbl)
        rl.addStretch()
        self.rows_lay.addWidget(row)

    # ── Key handler ────────────────────────────────────────────
    def handle_key(self, k: str):
        # Sprint 2: Step 1 only — OCR replaces the manual Step 2
        if self.step == 1:
            if k in SITE_KEYS:
                self._spike = SITE_KEYS[k]
                self.hide()                                    # close overlay immediately
                pos_folder = detect_player_position()          # OCR: capture → normalise
                self.on_done(self._spike, pos_folder)          # fire lineup

    # ── Positioning ────────────────────────────────────────────
    def _position_window(self):
        screen = QApplication.primaryScreen().geometry()
        self.adjustSize()
        x = screen.width() - self.width() - 18
        y = int(screen.height() * 0.35)
        self.move(x, y)


# ══════════════════════════════════════════════════════════════
# Lineup Overlay  (result display)
# ══════════════════════════════════════════════════════════════
class LineupOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint  |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(OVERLAY_WIDTH)
        self._movie  = None
        self._timer  = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self._build()
        self.hide()

    # ── Layout ─────────────────────────────────────────────────
    def _build(self):
        root = QWidget()
        root.setObjectName("root")
        root.setStyleSheet(f"""
            #root {{
                background: rgba(13,15,23,0.95);
                border: 1px solid {C['red']};
                border-radius: 10px;
            }}
        """)
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(8)

        # Stand image
        self.stand_lbl = QLabel()
        self.stand_lbl.setFixedSize(276, 155)
        self.stand_lbl.setAlignment(Qt.AlignCenter)
        self.stand_lbl.setStyleSheet(
            f"background:{C['surface']};border:1px solid {C['border']};"
            f"border-radius:7px;color:{C['sub']};font-size:11px;"
        )
        self.stand_lbl.setText("stand.png")
        lay.addWidget(self.stand_lbl)

        # Aim GIF
        self.aim_lbl = QLabel()
        self.aim_lbl.setFixedSize(276, 155)
        self.aim_lbl.setAlignment(Qt.AlignCenter)
        self.aim_lbl.setStyleSheet(
            f"background:{C['surface']};border:1px solid {C['border']};"
            f"border-radius:7px;color:{C['sub']};font-size:11px;"
        )
        self.aim_lbl.setText("aim.gif")
        lay.addWidget(self.aim_lbl)

        # Throw type
        self.throw_lbl = QLabel("")
        self.throw_lbl.setAlignment(Qt.AlignCenter)
        self.throw_lbl.setStyleSheet(
            f"font-size:14px;font-weight:900;letter-spacing:2px;"
            f"padding:6px;border-radius:6px;"
        )
        lay.addWidget(self.throw_lbl)

    # ── Load & show ────────────────────────────────────────────
    def show_lineup(self, lineup):
        # Stand image
        if lineup.has_stand:
            pix = QPixmap(lineup.stand_path)
            self.stand_lbl.setPixmap(
                pix.scaled(276, 155, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.stand_lbl.setText("")
        else:
            self.stand_lbl.clear()
            self.stand_lbl.setText("stand.png\n(add image)")

        # Aim GIF
        if self._movie:
            self._movie.stop()
            self._movie = None
        if lineup.has_aim:
            self._movie = QMovie(lineup.aim_path)

            # FIT GIF INSIDE OVERLAY BOX
            self._movie.setScaledSize(self.aim_lbl.size())

            self.aim_lbl.setScaledContents(True)
            self.aim_lbl.setMovie(self._movie)
            self.aim_lbl.setText("")

            self._movie.start()
        else:
            self.aim_lbl.clear()
            self.aim_lbl.setText("aim.gif\n(add animation)")

        # Throw label
        throw_text  = THROW_DISPLAY.get(lineup.throw, lineup.throw.upper())
        throw_color = C['gold'] if lineup.throw == "jump" else C['green']
        self.throw_lbl.setText(throw_text)
        self.throw_lbl.setStyleSheet(
            f"font-size:14px;font-weight:900;letter-spacing:2px;"
            f"padding:6px;border-radius:6px;"
            f"color:{throw_color};"
            f"background:rgba(255,255,255,0.04);"
            f"border:1px solid {throw_color}44;"
        )

        self._fire()

    def show_no_lineup(self):
        self.stand_lbl.clear()
        self.stand_lbl.setText("No Lineup\nin Database")
        self.stand_lbl.setStyleSheet(
            f"background:{C['surface']};border:1px solid {C['red']};"
            f"border-radius:7px;color:{C['red']};font-size:13px;font-weight:700;"
        )
        if self._movie:
            self._movie.stop(); self._movie = None
        self.aim_lbl.clear()
        self.aim_lbl.setText("")
        self.aim_lbl.setStyleSheet(
            f"background:{C['surface']};border:1px solid {C['border']};"
            f"border-radius:7px;"
        )
        self.throw_lbl.setText("")
        self._fire()

    def _fire(self):
        """Position, show, and (re)start the 7s timer."""
        screen = QApplication.primaryScreen().geometry()
        self.adjustSize()
        x = screen.width() - self.width() - 18
        y = int(screen.height() * 0.35)
        self.move(x, y)
        self.show()
        self.raise_()
        self._timer.stop()
        self._timer.start(OVERLAY_AUTO_CLOSE_MS)

    def kill_and_restart(self, lineup_fn):
        """Stop timer, hide, then immediately re-show. Used by F7."""
        self._timer.stop()
        self.hide()
        lineup_fn()


# ══════════════════════════════════════════════════════════════
# Controller
# ══════════════════════════════════════════════════════════════
class Controller:
    def __init__(self, app: QApplication):
        self.app    = app
        self.state  = AppState()
        self._last_lineup = None    # cached for F7

        self.setup_win    = None
        self.input_overlay  = InputOverlay(self.state, self._on_t2_done)
        self.lineup_overlay = LineupOverlay()

    # ── T1 ─────────────────────────────────────────────────────
    def open_setup(self):
        if self.setup_win and self.setup_win.isVisible():
            self.setup_win.raise_()
            return
        self.setup_win = SetupWindow(self.state, self._on_t1_confirmed)
        self.setup_win.show()
        self.setup_win.raise_()

    def _on_t1_confirmed(self):
        self._last_lineup = None   # T2 wiped by state.set_t1

    # ── T2 ─────────────────────────────────────────────────────
    def open_t2(self):
        if not self.state.t1_set:
            return   # T1 not set — do nothing
        self.lineup_overlay.hide()
        self.input_overlay.show_step1()

    def _on_t2_done(self, spike_site: str, agent_position: str):
        self.state.set_t2(spike_site, agent_position)
        self._fetch_and_show()

    # ── Fetch & show ───────────────────────────────────────────
    def _fetch_and_show(self):
        lineup = match_lineup(
            self.state.map_name,
            self.state.agent,
            self.state.spike_site,
            self.state.agent_position,
        )
        self._last_lineup = lineup
        if lineup:
            self.lineup_overlay.show_lineup(lineup)
        else:
            self.lineup_overlay.show_no_lineup()

    # ── F7 repeat ──────────────────────────────────────────────
    def repeat(self):
        if not self.state.ready:
            return
        self.lineup_overlay.kill_and_restart(self._fetch_and_show)

    # ── Selection key (during F6 overlay) ─────────────────────
    def handle_selection_key(self, k: str):
        if self.input_overlay.isVisible():
            self.input_overlay.handle_key(k)

    # ── Tray ───────────────────────────────────────────────────
    def build_tray(self):
        tray = QSystemTrayIcon(self.app)
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{ background:{C['surface']}; color:{C['text']};
                     border:1px solid {C['border']}; padding:4px; }}
            QMenu::item:selected {{ background:{C['red']}; }}
        """)
        a_setup  = QAction("⚙  Setup (F5)",          self.app)
        a_spike  = QAction("◈  Spike / Position (F6)", self.app)
        a_repeat = QAction("▶  Repeat Lineup (F7)",   self.app)
        a_quit   = QAction("✕  Quit",                 self.app)
        a_setup.triggered.connect(self.open_setup)
        a_spike.triggered.connect(self.open_t2)
        a_repeat.triggered.connect(self.repeat)
        a_quit.triggered.connect(self.app.quit)
        menu.addAction(a_setup)
        menu.addAction(a_spike)
        menu.addSeparator()
        menu.addAction(a_repeat)
        menu.addSeparator()
        menu.addAction(a_quit)
        tray.setContextMenu(menu)
        tray.setToolTip("Valorant Lineup Assistant")
        tray.activated.connect(
            lambda r: self.open_setup() if r == QSystemTrayIcon.DoubleClick else None
        )
        tray.show()
        return tray


# ══════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Valorant Lineup Assistant")
    app.setQuitOnLastWindowClosed(False)

    ctrl  = Controller(app)
    tray  = ctrl.build_tray()           # noqa — must stay alive
    bridge = HotkeyBridge()

    # Wire signals (always runs on Qt main thread)
    bridge.f5_pressed.connect(ctrl.open_setup)
    bridge.f6_pressed.connect(ctrl.open_t2)
    bridge.f7_pressed.connect(ctrl.repeat)
    bridge.key_pressed.connect(ctrl.handle_selection_key)

    # Register hotkeys
    if KEYBOARD_OK:
        keyboard.add_hotkey("F5", lambda: bridge.f5_pressed.emit())
        keyboard.add_hotkey("F6", lambda: bridge.f6_pressed.emit())
        keyboard.add_hotkey("F7", lambda: bridge.f7_pressed.emit())
        for k in ("4", "5", "6", "7", "8", "9"):
            keyboard.add_hotkey(k, lambda _k=k: bridge.key_pressed.emit(_k))

        print("Hotkeys active:")
        print("  F5 — Setup (map + agent)")
        print("  F6 — Spike site → position → lineup")
        print("  F7 — Repeat lineup")
        print("  4–9 — Selection (during F6 overlay only)")
    else:
        print("Hotkeys unavailable. Use the tray icon.")
        ctrl.open_setup()

    print("\nValorant Lineup Assistant running. Right-click tray icon for menu.")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
