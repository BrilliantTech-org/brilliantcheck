import json
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QFrame, QProgressBar,
)
from ...core.bridge import run


class ScanWorker(QThread):
    finished = Signal(dict)

    def run(self):
        res = run(["detect"])
        self.finished.emit(res)


class ScanPage(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        title = QLabel("Device Scan")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        sub = QLabel("Connect a device via USB and detect its identity.")
        sub.setStyleSheet("color:#9AA0AA;font-size:12px;")
        lay.addWidget(title)
        lay.addWidget(sub)

        # Action bar
        bar = QHBoxLayout()
        self.scan_btn = QPushButton("Scan for Devices")
        self.scan_btn.setProperty("class", "primary")
        self.scan_btn.setCursor(Qt.PointingHandCursor)
        self.scan_btn.clicked.connect(self.start_scan)
        bar.addWidget(self.scan_btn)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setFixedHeight(6)
        bar.addWidget(self.progress, 1)
        lay.addLayout(bar)

        # Results card
        card = QFrame()
        card.setProperty("class", "card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.addWidget(QLabel("Detected Devices"))
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setPlaceholderText("No devices detected yet.")
        self.results.setMinimumHeight(360)
        cl.addWidget(self.results)
        lay.addWidget(card, 1)

        self.status = QLabel("Ready.")
        self.status.setStyleSheet("color:#9AA0AA;font-size:11px;")
        lay.addWidget(self.status)

    def start_scan(self):
        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status.setText("Scanning…")
        self.worker = ScanWorker()
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, res):
        self.scan_btn.setEnabled(True)
        self.progress.setVisible(False)
        if res.get("ok"):
            data = res.get("data", {})
            self.results.setPlainText(json.dumps(data, indent=2))
            if isinstance(data, list):
                devs = data
            elif isinstance(data, dict):
                devs = data.get("devices", [])
            else:
                devs = []
            self.status.setText(f"Found {len(devs)} device(s).")
        else:
            self.results.setPlainText(res.get("stderr") or res.get("error", "Unknown error"))
            self.status.setText("Scan failed.")