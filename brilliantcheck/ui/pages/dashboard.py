from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from ...core.db import counts as db_counts
from ..theme import TEXT_MUTED


def card(title, value, hint, accent="#4F8CFF"):
    f = QFrame()
    f.setProperty("class", "card")
    f.setMinimumHeight(110)
    lay = QVBoxLayout(f)
    lay.setContentsMargins(16, 14, 16, 14)
    t = QLabel(title)
    t.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;font-weight:600;")
    v = QLabel(value)
    v.setStyleSheet(f"font-size:26px;font-weight:800;color:{accent};")
    h = QLabel(hint)
    h.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;")
    lay.addWidget(t)
    lay.addWidget(v)
    lay.addStretch(1)
    lay.addWidget(h)
    return f


class DashboardPage(QWidget):
    def __init__(self, main):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(18)

        title = QLabel("Dashboard")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        sub = QLabel("Overview of device checks and verification activity.")
        sub.setStyleSheet("color:#9AA0AA;font-size:12px;")
        lay.addWidget(title)
        lay.addWidget(sub)

        c = db_counts()
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.addWidget(card("Devices Scanned", str(c["total"]), "Total devices checked"), 0, 0)
        grid.addWidget(card("Verified Original", str(c["verified"]), "Passed authenticity", "#3DDC97"), 0, 1)
        grid.addWidget(card("Flagged Fake/Clone", str(c["flagged"]), "Needs attention", "#FF5A5F"), 0, 2)
        grid.addWidget(card("Hardware Issues", "0", "Diagnostics found", "#FFB020"), 1, 0)
        grid.addWidget(card("Avg. Check Time", "—", "Per device"), 1, 1)
        grid.addWidget(card("Bridge Status", "Ready", "Rust core available", "#3DDC97"), 1, 2)
        lay.addLayout(grid)

        # Recent activity
        sec = QLabel("Recent Activity")
        sec.setStyleSheet("font-size:15px;font-weight:700;margin-top:8px;")
        lay.addWidget(sec)

        empty = QLabel("No checks yet. Connect a device and run a scan to get started.")
        empty.setStyleSheet("color:#9AA0AA;font-size:12px;padding:20px;background:#1E222B;border-radius:12px;")
        empty.setAlignment(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(empty)
        lay.addStretch(1)