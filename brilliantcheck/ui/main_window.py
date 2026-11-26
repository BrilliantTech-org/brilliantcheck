from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QScrollArea,
)
from .theme import QSS

NAV = [
    ("🏠", "Dashboard", "dashboard"),
    ("🔍", "Device Scan", "scan"),
    ("✅", "Verify", "verify"),
    ("📶", "Wireless", "wireless"),
    ("📜", "History", "history"),
    ("⚙️", "Settings", "settings"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("brilliantcheck — Brilliant Device Check")
        self.resize(1180, 720)
        self.setStyleSheet(QSS)

        root = QWidget(objectName="root")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(220)
        sbl = QVBoxLayout(sidebar)
        sbl.setContentsMargins(16, 20, 16, 20)
        sbl.setSpacing(6)

        brand = QLabel("brilliantcheck")
        brand.setStyleSheet("font-size:18px;font-weight:800;color:#4F8CFF;")
        sub = QLabel("Brilliant Device Check")
        sub.setProperty("class", "subtitle")
        sub.setStyleSheet("color:#9AA0AA;font-size:11px;")
        sbl.addWidget(brand)
        sbl.addWidget(sub)
        sbl.addSpacing(16)

        self.nav_buttons = {}
        for icon, label, key in NAV:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setProperty("class", "navBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.switch_page(k))
            sbl.addWidget(btn)
            self.nav_buttons[key] = btn

        sbl.addStretch(1)

        footer = QLabel("v0 — early dev\nRust core + PySide6")
        footer.setStyleSheet("color:#5A6070;font-size:10px;")
        sbl.addWidget(footer)

        layout.addWidget(sidebar)

        # Content
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        from .pages.dashboard import DashboardPage
        from .pages.scan import ScanPage
        from .pages.verify import VerifyPage
        from .pages.wireless import WirelessPage
        from .pages.history import HistoryPage
        from .pages.settings import SettingsPage

        self.pages = {
            "dashboard": DashboardPage(self),
            "scan": ScanPage(self),
            "verify": VerifyPage(self),
            "wireless": WirelessPage(self),
            "history": HistoryPage(self),
            "settings": SettingsPage(self),
        }
        for key in ("dashboard", "scan", "verify", "wireless", "history", "settings"):
            self.stack.addWidget(self.pages[key])

        self.switch_page("dashboard")

        # Status bar
        from PySide6.QtWidgets import QStatusBar
        from PySide6.QtCore import QTimer
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._bridge_label = QLabel("Bridge: " + ("ready" if __import__("brilliantcheck.core.bridge", fromlist=["bridge_path"]).bridge_path() else "missing"))
        sb.addWidget(self._bridge_label)
        self._clock = QLabel()
        sb.addPermanentWidget(self._clock)
        t = QTimer(self)
        t.timeout.connect(lambda: self._clock.setText(__import__("datetime").datetime.now().strftime("%H:%M:%S")))
        t.start(1000)
        self._clock.setText(__import__("datetime").datetime.now().strftime("%H:%M:%S"))

    def switch_page(self, key):
        target = self.pages[key]
        # fade transition
        eff = QGraphicsOpacityEffect(target)
        target.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.stack.setCurrentWidget(target)
        anim.start()
        self._anim = anim
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)