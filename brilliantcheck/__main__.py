import sys
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter
from PySide6.QtCore import Qt, QTimer
from .ui.main_window import MainWindow


def make_splash():
    pm = QPixmap(480, 280)
    pm.fill(QColor("#0F1115"))
    p = QPainter(pm)
    p.setPen(QColor("#4F8CFF"))
    f = QFont("Segoe UI", 26, QFont.Bold)
    p.setFont(f)
    p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "brilliantcheck")
    p.setPen(QColor("#9AA0AA"))
    p.setFont(QFont("Segoe UI", 11))
    p.drawText(pm.rect().adjusted(0, 60, 0, 0), Qt.AlignmentFlag.AlignCenter, "Brilliant Device Check")
    p.drawText(pm.rect().adjusted(0, 100, 0, 0), Qt.AlignmentFlag.AlignCenter, "Loading Rust core…")
    p.end()
    return QSplashScreen(pm, Qt.WindowType.WindowStaysOnTopHint)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("brilliantcheck")
    splash = make_splash()
    splash.show()
    app.processEvents()
    win = MainWindow()
    QTimer.singleShot(900, lambda: (splash.finish(win), win.show()))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()