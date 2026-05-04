"""
Valorant Lineup Assistant — Lineup Manager (manager.py)
=======================================================
Run this separately (before/after matches) to add, view, and delete lineups.
No hotkeys, no overlay. Full mouse + keyboard interaction.
"""

import sys
import os
import json
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QLabel, QComboBox,
        QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
        QFrame, QFileDialog, QScrollArea, QMessageBox,
        QStackedWidget, QSizePolicy, QSpacerItem,
    )
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui  import QPixmap, QMovie, QFont, QIcon
except ImportError:
    print("ERROR: PyQt5 not found.\nRun: pip install PyQt5")
    sys.exit(1)

from engine.state import (
    MAPS, AGENTS, SPIKE_SITES, THROW_TYPES,
    site_to_folder, folder_to_site,
    get_position_label, get_position_folder,
    LINEUPS_DIR,
)

# ── Palette ───────────────────────────────────────────────────
C = {
    "bg":      "#0D0F17",
    "surface": "#161923",
    "panel":   "#1C2030",
    "border":  "#252836",
    "red":     "#FF4655",
    "text":    "#E2E4EF",
    "sub":     "#6B7090",
    "gold":    "#F0B429",
    "green":   "#36C95F",
    "white":   "#FFFFFF",
    "danger":  "#C0392B",
}

THUMB_W, THUMB_H = 220, 124


# ── Helpers ───────────────────────────────────────────────────
def sep():
    s = QFrame(); s.setFrameShape(QFrame.HLine)
    s.setStyleSheet(f"border:none;border-top:1px solid {C['border']};margin:4px 0;")
    return s

def label(txt, color=None, size=10, bold=False, spacing=False):
    l = QLabel(txt)
    style = (
        f"color:{color or C['sub']};"
        f"font-size:{size}px;"
        f"{'font-weight:700;' if bold else ''}"
        f"{'letter-spacing:2px;' if spacing else ''}"
        f"margin-bottom:-6px;"
    )
    l.setStyleSheet(style)
    return l

def lineup_folder(map_n, agent, site, pos_folder) -> str:
    return os.path.join(
        LINEUPS_DIR,
        map_n.lower(),
        agent.lower(),
        site_to_folder(site),
        pos_folder,
    )

def all_lineups():
    """
    Scan lineups/ directory and return list of dicts with info.
    """
    results = []
    if not os.path.isdir(LINEUPS_DIR):
        return results
    for map_n in sorted(os.listdir(LINEUPS_DIR)):
        map_path = os.path.join(LINEUPS_DIR, map_n)
        if not os.path.isdir(map_path): continue
        for agent in sorted(os.listdir(map_path)):
            agent_path = os.path.join(map_path, agent)
            if not os.path.isdir(agent_path): continue
            for site_folder in sorted(os.listdir(agent_path)):
                site_path = os.path.join(agent_path, site_folder)
                if not os.path.isdir(site_path): continue
                for pos_folder in sorted(os.listdir(site_path)):
                    pos_path = os.path.join(site_path, pos_folder)
                    if not os.path.isdir(pos_path): continue
                    meta_path = os.path.join(pos_path, "meta.json")
                    throw = "normal"
                    if os.path.isfile(meta_path):
                        with open(meta_path) as f:
                            throw = json.load(f).get("throw", "normal")
                    results.append({
                        "map":        map_n.title(),
                        "agent":      agent.title(),
                        "site":       folder_to_site(site_folder),
                        "pos_folder": pos_folder,
                        "pos_label":  pos_folder.replace("_", " ").title(),
                        "throw":      throw,
                        "folder":     pos_path,
                        "stand":      os.path.join(pos_path, "stand.png"),
                        "aim":        os.path.join(pos_path, "aim.gif"),
                    })
    return results


# ══════════════════════════════════════════════════════════════
# Add Lineup Panel
# ══════════════════════════════════════════════════════════════
class AddPanel(QWidget):
    def __init__(self, on_saved):
        super().__init__()
        self.on_saved    = on_saved
        self._stand_src  = ""
        self._aim_src    = ""
        self.setStyleSheet(self._sheet())
        self._build()

    def _sheet(self):
        return f"""
        QWidget      {{ background:{C['bg']}; color:{C['text']};
                        font-family:'Segoe UI',Arial; font-size:13px; }}
        QComboBox    {{ background:{C['surface']}; border:1px solid {C['border']};
                        border-radius:6px; padding:7px 10px; color:{C['text']}; }}
        QComboBox:focus {{ border-color:{C['red']}; }}
        QComboBox QAbstractItemView {{ background:{C['surface']};
                        selection-background-color:{C['red']};
                        border:1px solid {C['border']}; color:{C['text']}; }}
        QPushButton  {{ background:{C['surface']}; color:{C['text']};
                        border:1px solid {C['border']}; border-radius:6px;
                        padding:7px 14px; }}
        QPushButton:hover {{ border-color:{C['text']}; }}
        QPushButton#save {{ background:{C['red']}; color:#fff;
                        font-weight:700; border:none; letter-spacing:1px; }}
        QPushButton#save:hover {{ background:#FF6B77; }}
        QPushButton#save:disabled {{ background:{C['border']}; color:{C['sub']}; }}
        """

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 20, 28, 24)
        outer.setSpacing(0)

        # Title
        t = QLabel("ADD LINEUP")
        t.setStyleSheet(f"color:{C['red']};font-size:16px;font-weight:900;"
                        f"letter-spacing:3px;margin-bottom:4px;")
        outer.addWidget(t)
        outer.addWidget(label("Fill in all fields, then upload images and save."))
        outer.addSpacing(14)
        outer.addWidget(sep())
        outer.addSpacing(14)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(12)

        # Map
        grid.addWidget(label("MAP", spacing=True), 0, 0)
        self.map_cb = QComboBox(); self.map_cb.addItems(MAPS)
        grid.addWidget(self.map_cb, 1, 0)

        # Agent
        grid.addWidget(label("AGENT", spacing=True), 0, 1)
        self.agent_cb = QComboBox(); self.agent_cb.addItems(AGENTS)
        grid.addWidget(self.agent_cb, 1, 1)

        # Spike site
        grid.addWidget(label("SPIKE SITE", spacing=True), 2, 0)
        self.site_cb = QComboBox(); self.site_cb.addItems(SPIKE_SITES)
        self.site_cb.currentTextChanged.connect(self._update_pos_options)
        grid.addWidget(self.site_cb, 3, 0)

        # Agent position
        grid.addWidget(label("AGENT POSITION", spacing=True), 2, 1)
        self.pos_cb = QComboBox()
        grid.addWidget(self.pos_cb, 3, 1)

        # Throw type
        grid.addWidget(label("THROW TYPE", spacing=True), 4, 0)
        self.throw_cb = QComboBox(); self.throw_cb.addItems(THROW_TYPES)
        grid.addWidget(self.throw_cb, 5, 0)

        outer.addLayout(grid)
        self._update_pos_options(self.site_cb.currentText())

        outer.addSpacing(20)
        outer.addWidget(sep())
        outer.addSpacing(16)

        # Image upload row
        img_row = QHBoxLayout()
        img_row.setSpacing(16)

        # Stand
        stand_col = QVBoxLayout()
        stand_col.addWidget(label("STAND.PNG", spacing=True))
        stand_col.addSpacing(6)
        self.stand_preview = self._thumb()
        stand_col.addWidget(self.stand_preview)
        stand_col.addSpacing(6)
        self.stand_btn = QPushButton("Upload stand.png")
        self.stand_btn.clicked.connect(self._pick_stand)
        stand_col.addWidget(self.stand_btn)
        img_row.addLayout(stand_col)

        # Aim
        aim_col = QVBoxLayout()
        aim_col.addWidget(label("AIM.GIF", spacing=True))
        aim_col.addSpacing(6)
        self.aim_preview = self._thumb()
        aim_col.addWidget(self.aim_preview)
        aim_col.addSpacing(6)
        self.aim_btn = QPushButton("Upload aim.gif")
        self.aim_btn.clicked.connect(self._pick_aim)
        aim_col.addWidget(self.aim_btn)
        img_row.addLayout(aim_col)

        outer.addLayout(img_row)
        outer.addSpacing(20)

        # Save button
        self.save_btn = QPushButton("SAVE LINEUP  ▶")
        self.save_btn.setObjectName("save")
        self.save_btn.clicked.connect(self._save)
        outer.addWidget(self.save_btn)
        outer.addStretch()

    def _thumb(self):
        lbl = QLabel()
        lbl.setFixedSize(THUMB_W, THUMB_H)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"background:{C['surface']};border:1px solid {C['border']};"
            f"border-radius:7px;color:{C['sub']};font-size:11px;"
        )
        lbl.setText("No file selected")
        return lbl

    def _update_pos_options(self, site: str):
        self.pos_cb.clear()
        letter = site[0].upper()
        self.pos_cb.addItem(f"{letter} Main")
        self.pos_cb.addItem("Mid")

    def _pick_stand(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select stand.png", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self._stand_src = path
            pix = QPixmap(path).scaled(THUMB_W, THUMB_H, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.stand_preview.setPixmap(pix)
            self.stand_preview.setText("")

    def _pick_aim(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select aim.gif", "", "Animated GIF (*.gif)")
        if path:
            self._aim_src = path
            # Show first frame as preview
            movie = QMovie(path)
            movie.jumpToFrame(0)
            frame = movie.currentPixmap().scaled(THUMB_W, THUMB_H, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.aim_preview.setPixmap(frame)
            self.aim_preview.setText("")

    def _save(self):
        map_n  = self.map_cb.currentText()
        agent  = self.agent_cb.currentText()
        site   = self.site_cb.currentText()
        pos_t  = self.pos_cb.currentText()   # e.g. "B Main" or "Mid"
        throw  = self.throw_cb.currentText().lower()

        # Derive folder name from label
        if pos_t.lower() == "mid":
            pos_folder = "mid"
        else:
            letter = pos_t[0].lower()         # "b"
            pos_folder = f"{letter}_main"

        folder = lineup_folder(map_n, agent, site, pos_folder)

        # Warn if lineup already exists
        if os.path.isdir(folder):
            reply = QMessageBox.question(
                self, "Overwrite?",
                f"A lineup already exists for:\n{map_n} / {agent} / {site} / {pos_t}\n\nOverwrite it?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        os.makedirs(folder, exist_ok=True)

        # Save meta.json
        with open(os.path.join(folder, "meta.json"), "w") as f:
            json.dump({"throw": throw}, f, indent=2)

        # Copy images if provided
        if self._stand_src:
            shutil.copy(self._stand_src, os.path.join(folder, "stand.png"))
        if self._aim_src:
            shutil.copy(self._aim_src, os.path.join(folder, "aim.gif"))

        QMessageBox.information(
            self, "Saved",
            f"Lineup saved:\n{map_n} / {agent} / {site} / {pos_t}\nThrow: {throw.title()}"
        )
        self._reset_form()
        self.on_saved()

    def _reset_form(self):
        self._stand_src = ""
        self._aim_src   = ""
        self.stand_preview.clear(); self.stand_preview.setText("No file selected")
        self.aim_preview.clear();   self.aim_preview.setText("No file selected")


# ══════════════════════════════════════════════════════════════
# View / Delete Panel
# ══════════════════════════════════════════════════════════════
class ViewPanel(QWidget):
    def __init__(self, on_deleted):
        super().__init__()
        self.on_deleted = on_deleted
        self._movie     = None
        self.setStyleSheet(f"""
            QWidget      {{ background:{C['bg']}; color:{C['text']};
                            font-family:'Segoe UI',Arial; font-size:13px; }}
            QPushButton  {{ background:{C['surface']}; color:{C['text']};
                            border:1px solid {C['border']}; border-radius:6px;
                            padding:6px 12px; }}
            QPushButton:hover {{ border-color:{C['text']}; }}
            QPushButton#del {{ background:{C['danger']}; color:#fff;
                            border:none; font-weight:700; }}
            QPushButton#del:hover {{ background:#E74C3C; }}
            QComboBox    {{ background:{C['surface']}; border:1px solid {C['border']};
                            border-radius:6px; padding:6px 10px; color:{C['text']}; }}
            QComboBox QAbstractItemView {{ background:{C['surface']};
                            selection-background-color:{C['red']};
                            border:1px solid {C['border']}; color:{C['text']}; }}
            QScrollArea  {{ border:none; }}
        """)
        self._build()
        self.refresh()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 20, 28, 24)
        outer.setSpacing(0)

        t = QLabel("LINEUPS")
        t.setStyleSheet(f"color:{C['red']};font-size:16px;font-weight:900;"
                        f"letter-spacing:3px;margin-bottom:4px;")
        outer.addWidget(t)
        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet(f"color:{C['sub']};font-size:11px;")
        outer.addWidget(self.count_lbl)
        outer.addSpacing(10)
        outer.addWidget(sep())
        outer.addSpacing(10)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cards_widget = QWidget()
        self.cards_lay    = QVBoxLayout(self.cards_widget)
        self.cards_lay.setContentsMargins(0, 0, 0, 0)
        self.cards_lay.setSpacing(10)
        self.cards_lay.addStretch()
        scroll.setWidget(self.cards_widget)
        outer.addWidget(scroll)

    def refresh(self):
        # Clear existing cards
        while self.cards_lay.count() > 1:   # keep the stretch
            item = self.cards_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        lineups = all_lineups()
        self.count_lbl.setText(f"{len(lineups)} lineup{'s' if len(lineups) != 1 else ''} in database")

        if not lineups:
            empty = QLabel("No lineups added yet.\nUse the Add tab to create your first lineup.")
            empty.setStyleSheet(f"color:{C['sub']};font-size:13px;")
            empty.setAlignment(Qt.AlignCenter)
            self.cards_lay.insertWidget(0, empty)
            return

        for ln in lineups:
            card = self._make_card(ln)
            self.cards_lay.insertWidget(self.cards_lay.count() - 1, card)

    def _make_card(self, ln: dict) -> QWidget:
        card = QWidget()
        card.setStyleSheet(
            f"QWidget {{ background:{C['surface']}; border:1px solid {C['border']};"
            f"border-radius:8px; }}"
        )
        lay = QHBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(14)

        # Stand thumbnail
        stand_lbl = QLabel()
        stand_lbl.setFixedSize(80, 45)
        stand_lbl.setAlignment(Qt.AlignCenter)
        stand_lbl.setStyleSheet(
            f"background:{C['panel']};border:1px solid {C['border']};"
            f"border-radius:5px;color:{C['sub']};font-size:9px;"
        )
        if os.path.isfile(ln["stand"]):
            pix = QPixmap(ln["stand"]).scaled(80, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            stand_lbl.setPixmap(pix)
        else:
            stand_lbl.setText("no img")
        lay.addWidget(stand_lbl)

        # Info
        info = QVBoxLayout()
        info.setSpacing(2)
        top = QLabel(f"{ln['map']}  ·  {ln['agent']}")
        top.setStyleSheet(f"color:{C['text']};font-size:12px;font-weight:700;background:transparent;")
        mid_ = QLabel(f"{ln['site']}  ·  {ln['pos_label']}")
        mid_.setStyleSheet(f"color:{C['sub']};font-size:11px;background:transparent;")
        throw_color = C['gold'] if ln['throw'] == 'jump' else C['green']
        throw_lbl = QLabel(ln['throw'].upper() + " THROW")
        throw_lbl.setStyleSheet(
            f"color:{throw_color};font-size:10px;font-weight:700;"
            f"letter-spacing:1px;background:transparent;"
        )
        info.addWidget(top)
        info.addWidget(mid_)
        info.addWidget(throw_lbl)
        lay.addLayout(info)
        lay.addStretch()

        # Image status
        status_col = QVBoxLayout()
        status_col.setSpacing(2)
        def dot(ok, label_txt):
            l = QLabel(("✓ " if ok else "✗ ") + label_txt)
            l.setStyleSheet(
                f"color:{C['green'] if ok else C['sub']};"
                f"font-size:10px;background:transparent;"
            )
            return l
        status_col.addWidget(dot(os.path.isfile(ln["stand"]), "stand.png"))
        status_col.addWidget(dot(os.path.isfile(ln["aim"]),   "aim.gif"))
        lay.addLayout(status_col)

        # Delete button
        del_btn = QPushButton("Delete")
        del_btn.setObjectName("del")
        del_btn.setFixedWidth(70)
        folder = ln["folder"]
        del_btn.clicked.connect(lambda _, f=folder, d=ln: self._delete(f, d))
        lay.addWidget(del_btn)

        return card

    def _delete(self, folder: str, ln: dict):
        reply = QMessageBox.question(
            self, "Delete Lineup",
            f"Delete lineup:\n{ln['map']} / {ln['agent']} / {ln['site']} / {ln['pos_label']}?\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            shutil.rmtree(folder, ignore_errors=True)
            self.refresh()
            self.on_deleted()


# ══════════════════════════════════════════════════════════════
# Main Window
# ══════════════════════════════════════════════════════════════
class ManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Valorant Lineup Assistant — Manager")
        self.setMinimumSize(780, 620)
        self.setStyleSheet(f"QMainWindow {{ background:{C['bg']}; }}")
        self._build()

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_lay = QHBoxLayout(root)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet(f"background:{C['surface']};border-right:1px solid {C['border']};")
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)

        logo = QLabel("◈ LINEUP\nMANAGER")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(
            f"color:{C['red']};font-size:13px;font-weight:900;"
            f"letter-spacing:2px;padding:22px 10px 18px;line-height:1.6;"
        )
        sb_lay.addWidget(logo)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"border:none;border-top:1px solid {C['border']};")
        sb_lay.addWidget(div)
        sb_lay.addSpacing(8)

        self.btn_add  = self._nav_btn("＋  Add Lineup",  active=True)
        self.btn_view = self._nav_btn("☰  View / Delete", active=False)
        sb_lay.addWidget(self.btn_add)
        sb_lay.addWidget(self.btn_view)
        sb_lay.addStretch()

        version = QLabel("MVP v1.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(f"color:{C['border']};font-size:10px;padding:10px;")
        sb_lay.addWidget(version)

        main_lay.addWidget(sidebar)

        # ── Content stack ──
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{C['bg']};")

        self.add_panel  = AddPanel(on_saved=self._on_saved)
        self.view_panel = ViewPanel(on_deleted=self._on_deleted)

        self.stack.addWidget(self.add_panel)   # index 0
        self.stack.addWidget(self.view_panel)  # index 1
        main_lay.addWidget(self.stack)

        self.btn_add.clicked.connect(lambda: self._switch(0))
        self.btn_view.clicked.connect(lambda: self._switch(1))

    def _nav_btn(self, txt, active=False):
        btn = QPushButton(txt)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {'rgba(255,70,85,0.12)' if active else 'transparent'};
                color: {C['red'] if active else C['sub']};
                border: none;
                border-left: 3px solid {'#FF4655' if active else 'transparent'};
                padding: 12px 18px;
                text-align: left;
                font-size: 13px;
            }}
            QPushButton:hover {{ color:{C['text']}; background:rgba(255,255,255,0.04); }}
            QPushButton:checked {{
                color:{C['red']};
                background:rgba(255,70,85,0.12);
                border-left:3px solid {C['red']};
            }}
        """)
        return btn

    def _switch(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self.btn_add.setChecked(idx == 0)
        self.btn_view.setChecked(idx == 1)
        if idx == 1:
            self.view_panel.refresh()

    def _on_saved(self):
        self._switch(1)

    def _on_deleted(self):
        pass   # view_panel refreshes itself


# ══════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Lineup Manager")
    win = ManagerWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
