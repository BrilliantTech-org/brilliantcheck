from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton,
)


class HistoryPage(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        title = QLabel("History")
        title.setStyleSheet("font-size:20px;font-weight:700;")
        sub = QLabel("Past device checks and verification results.")
        sub.setStyleSheet("color:#9AA0AA;font-size:12px;")
        lay.addWidget(title)
        lay.addWidget(sub)

        card = QFrame()
        card.setProperty("class", "card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Identifier", "Brand", "Model", "Verdict"])
        self.table.horizontalHeader().setStretchLastSection(True)
        cl.addWidget(self.table)

        row = QHBoxLayout()
        clear = QPushButton("Clear History")
        clear.setProperty("class", "ghost")
        row.addStretch(1)
        row.addWidget(clear)
        cl.addLayout(row)

        lay.addWidget(card, 1)

        empty = QLabel("No history yet.")
        empty.setStyleSheet("color:#9AA0AA;font-size:12px;")
        empty.setAlignment(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(empty)