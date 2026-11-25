import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton, QLineEdit,
)
from ...core.bridge import bridge_path


class SettingsPage(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        title = QLabel("Settings")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        sub = QLabel("Configure the Rust bridge and application preferences.")
        sub.setStyleSheet("color:#9AA0AA;font-size:12px;")
        lay.addWidget(title)
        lay.addWidget(sub)

        card = QFrame()
        card.setProperty("class", "card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(10)

        cl.addWidget(QLabel("Bridge binary path"))
        self.bridge_input = QLineEdit(str(bridge_path() or ""))
        self.bridge_input.setPlaceholderText("/path/to/brilliantcheck binary")
        cl.addWidget(self.bridge_input)

        row = QHBoxLayout()
        save = QPushButton("Save")
        save.setProperty("class", "primary")
        save.clicked.connect(self.save)
        row.addWidget(save)
        row.addStretch(1)
        cl.addLayout(row)

        cl.addWidget(QLabel("Database"))
        db = QLabel("SQLite (local). Migration to PostgreSQL planned.")
        db.setStyleSheet("color:#9AA0AA;font-size:12px;")
        cl.addWidget(db)

        cl.addWidget(QLabel("Theme"))
        th = QLabel("Dark (default)")
        th.setStyleSheet("color:#9AA0AA;font-size:12px;")
        cl.addWidget(th)

        lay.addWidget(card)
        lay.addStretch(1)

        self.status = QLabel("")
        self.status.setStyleSheet("color:#9AA0AA;font-size:11px;")
        lay.addWidget(self.status)

    def save(self):
        os.environ["BDC_BRIDGE"] = self.bridge_input.text().strip()
        self.status.setText("Saved for this session.")