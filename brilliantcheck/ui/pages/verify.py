from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QTextEdit,
)
from ...core.bridge import run
from ...core.db import add_check


class VerifyPage(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        title = QLabel("Verify Device")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        sub = QLabel("Enter an IMEI or serial to check authenticity against official sources.")
        sub.setStyleSheet("color:#9AA0AA;font-size:12px;")
        lay.addWidget(title)
        lay.addWidget(sub)

        card = QFrame()
        card.setProperty("class", "card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(10)

        cl.addWidget(QLabel("Identifier"))
        self.input = QLineEdit()
        self.input.setPlaceholderText("IMEI (15 digits) or serial number")
        cl.addWidget(self.input)

        row = QHBoxLayout()
        self.verify_btn = QPushButton("Verify")
        self.verify_btn.setProperty("class", "primary")
        self.verify_btn.setCursor(Qt.PointingHandCursor)
        self.verify_btn.clicked.connect(self.do_verify)
        row.addWidget(self.verify_btn)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setProperty("class", "ghost")
        self.clear_btn.clicked.connect(lambda: self.input.clear())
        row.addWidget(self.clear_btn)
        row.addStretch(1)
        cl.addLayout(row)

        lay.addWidget(card)

        res_card = QFrame()
        res_card.setProperty("class", "card")
        rl = QVBoxLayout(res_card)
        rl.setContentsMargins(16, 14, 16, 14)
        rl.addWidget(QLabel("Result"))
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setPlaceholderText("Verification result will appear here.")
        self.result.setMinimumHeight(300)
        rl.addWidget(self.result)
        lay.addWidget(res_card, 1)

        self.status = QLabel("Ready.")
        self.status.setStyleSheet("color:#9AA0AA;font-size:11px;")
        lay.addWidget(self.status)

    def do_verify(self):
        ident = self.input.text().strip()
        if not ident:
            self.status.setText("Please enter an identifier.")
            return
        self.status.setText("Verifying…")
        if ident.isdigit() and len(ident) == 15:
            res = run(["imei-check", ident])
        else:
            res = run(["info", ident])
        if res.get("ok"):
            data = res.get("data", {}) or {}
            self.result.setPlainText(__import__("json").dumps(data, indent=2))
            verdict = data.get("verdict", "unknown")
            add_check(ident, brand=data.get("brand"), model=data.get("model"),
                      imei=ident if ident.isdigit() else data.get("imei"),
                      verdict=verdict, raw=data)
            self.status.setText("Verification complete.")
        else:
            self.result.setPlainText(res.get("stderr") or res.get("error", "Unknown error"))
            self.status.setText("Verification failed.")