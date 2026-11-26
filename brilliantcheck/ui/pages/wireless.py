from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QTextEdit, QComboBox,
)
import io
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QByteArray
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
        sub = QLabel("Connect to a device over Wi-Fi (ADB TCP mode). Phone and PC must be on the same Wi-Fi network.")
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

        # Pairing (Android 11+)
        cardp = QFrame(); cardp.setProperty("class", "card")
        cp = QVBoxLayout(cardp); cp.setContentsMargins(16, 14, 16, 14); cp.setSpacing(10)
        cp.addWidget(QLabel("Android 11+ wireless pairing (uses pairing code)"))
        rp = QHBoxLayout()
        self.pair_target = QLineEdit(); self.pair_target.setPlaceholderText("192.168.1.5:42000")
        rp.addWidget(self.pair_target, 1)
        self.pair_code = QLineEdit(); self.pair_code.setPlaceholderText("6-digit code")
        self.pair_code.setFixedWidth(120)
        rp.addWidget(self.pair_code)
        self.pair_btn = QPushButton("Pair")
        self.pair_btn.setProperty("class", "primary")
        self.pair_btn.setCursor(Qt.PointingHandCursor)
        self.pair_btn.clicked.connect(self.do_pair)
        rp.addWidget(self.pair_btn)
        cp.addLayout(rp)
        lay.addWidget(cardp)

        # QR code
        cardq = QFrame(); cardq.setProperty("class", "card")
        cq = QVBoxLayout(cardq); cq.setContentsMargins(16, 14, 16, 14); cq.setSpacing(10)
        cq.addWidget(QLabel("3) QR code for connecting"))
        self.qr_label = QLabel("No QR generated yet.")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(220, 220)
        cq.addWidget(self.qr_label, 0, Qt.AlignmentFlag.AlignCenter)
        qrow = QHBoxLayout()
        self.qr_input = QLineEdit()
        self.qr_input.setPlaceholderText("Text to encode (e.g. 192.168.1.5:5555)")
        qrow.addWidget(self.qr_input, 1)
        self.qr_btn = QPushButton("Generate QR")
        self.qr_btn.setProperty("class", "primary")
        self.qr_btn.setCursor(Qt.PointingHandCursor)
        self.qr_btn.clicked.connect(self.do_qr)
        qrow.addWidget(self.qr_btn)
        cq.addLayout(qrow)
        lay.addWidget(cardq)

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

    def do_pair(self):
        target = self.pair_target.text().strip()
        code = self.pair_code.text().strip()
        if not target or not code:
            self.status.setText("Enter target and pairing code.")
            return
        self.run_cmd(["adb-pair", target, code])

    def do_qr(self):
        text = self.qr_input.text().strip()
        if not text:
            text = self.ip_input.text().strip() or "brilliantcheck"
        try:
            import qrcode
            img = qrcode.make(text)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            pm = QPixmap()
            pm.loadFromData(QByteArray(buf.getvalue()), "PNG")
            self.qr_label.setPixmap(pm.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.qr_label.setText("")
            self.status.setText(f"QR generated for: {text}")
        except Exception as e:
            self.status.setText(f"QR failed: {e}")