from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QTextEdit, QComboBox,
)
from ...core.bridge import run


class WirelessWorker(QThread):
    finished = Signal(dict)

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        self.finished.emit(run(self.args))


class WirelessPage(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        title = QLabel("Wireless Debugging")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        sub = QLabel("Connect to a device over Wi-Fi (ADB TCP mode).")
        sub.setStyleSheet("color:#9AA0AA;font-size:12px;")
        lay.addWidget(title)
        lay.addWidget(sub)

        # Switch USB device to TCP
        card1 = QFrame(); card1.setProperty("class", "card")
        c1 = QVBoxLayout(card1); c1.setContentsMargins(16, 14, 16, 14); c1.setSpacing(10)
        c1.addWidget(QLabel("1) Switch a USB-connected device to wireless mode"))
        row = QHBoxLayout()
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("USB device serial (leave blank to use first)")
        row.addWidget(self.serial_input, 1)
        self.tcpip_btn = QPushButton("Enable TCP/IP (5555)")
        self.tcpip_btn.setProperty("class", "primary")
        self.tcpip_btn.setCursor(Qt.PointingHandCursor)
        self.tcpip_btn.clicked.connect(self.do_tcpip)
        row.addWidget(self.tcpip_btn)
        c1.addLayout(row)
        lay.addWidget(card1)

        # Connect to IP
        card2 = QFrame(); card2.setProperty("class", "card")
        c2 = QVBoxLayout(card2); c2.setContentsMargins(16, 14, 16, 14); c2.setSpacing(10)
        c2.addWidget(QLabel("2) Connect to device over Wi-Fi"))
        row2 = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.5:5555")
        row2.addWidget(self.ip_input, 1)
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setProperty("class", "primary")
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(self.do_connect)
        row2.addWidget(self.connect_btn)
        self.disc_btn = QPushButton("Disconnect")
        self.disc_btn.setProperty("class", "ghost")
        self.disc_btn.clicked.connect(self.do_disconnect)
        row2.addWidget(self.disc_btn)
        c2.addLayout(row2)
        lay.addWidget(card2)

        # Output
        card3 = QFrame(); card3.setProperty("class", "card")
        c3 = QVBoxLayout(card3); c3.setContentsMargins(16, 14, 16, 14)
        c3.addWidget(QLabel("Output"))
        self.output = QTextEdit(); self.output.setReadOnly(True); self.output.setMinimumHeight(220)
        c3.addWidget(self.output)
        lay.addWidget(card3, 1)

        self.status = QLabel("Ready.")
        self.status.setStyleSheet("color:#9AA0AA;font-size:11px;")
        lay.addWidget(self.status)

    def run_cmd(self, args):
        self.status.setText("Running…")
        self.worker = WirelessWorker(args)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, res):
        if res.get("ok"):
            data = res.get("data", {})
            self.output.setPlainText(__import__("json").dumps(data, indent=2))
            msg = data.get("message") if isinstance(data, dict) else None
            self.status.setText(msg or "Done.")
        else:
            self.output.setPlainText(res.get("stderr") or res.get("error", "Unknown error"))
            self.status.setText("Failed.")

    def do_tcpip(self):
        serial = self.serial_input.text().strip()
        if not serial:
            # use first connected device
            r = run(["detect"])
            data = r.get("data", {})
            devs = data.get("devices", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
            if not devs:
                self.status.setText("No USB device connected.")
                return
            serial = devs[0].get("serial") if isinstance(devs[0], dict) else str(devs[0])
        self.run_cmd(["adb-tcpip", serial])

    def do_connect(self):
        target = self.ip_input.text().strip()
        if not target:
            self.status.setText("Enter an IP:port.")
            return
        if ":" not in target:
            target = target + ":5555"
            self.ip_input.setText(target)
        self.run_cmd(["adb-connect", target])

    def do_disconnect(self):
        target = self.ip_input.text().strip()
        if target:
            self.run_cmd(["adb-disconnect", target])
        else:
            self.run_cmd(["adb-disconnect"])