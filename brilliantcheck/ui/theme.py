"""Design tokens and QSS for the brilliantcheck UI."""

ACCENT = "#4F8CFF"
ACCENT_DARK = "#3A6FE0"
BG = "#0F1115"
BG_ELEV = "#171A21"
BG_CARD = "#1E222B"
BORDER = "#2A2F3A"
TEXT = "#E6E8EC"
TEXT_MUTED = "#9AA0AA"
SUCCESS = "#3DDC97"
WARN = "#FFB020"
DANGER = "#FF5A5F"

QSS = f"""
QWidget {{
    color: {TEXT};
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    font-size: 13px;
}}
QMainWindow, QWidget#root {{
    background: {BG};
}}
QFrame#sidebar {{
    background: {BG_ELEV};
    border-right: 1px solid {BORDER};
}}
QPushButton.navBtn {{
    text-align: left;
    padding: 10px 14px;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: {TEXT_MUTED};
    font-weight: 500;
}}
QPushButton.navBtn:hover {{
    background: {BG_CARD};
    color: {TEXT};
}}
QPushButton.navBtn[active="true"] {{
    background: {ACCENT};
    color: white;
}}
QPushButton.primary {{
    background: {ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}}
QPushButton.primary:hover {{
    background: {ACCENT_DARK};
}}
QPushButton.ghost {{
    background: transparent;
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 16px;
}}
QPushButton.ghost:hover {{
    background: {BG_CARD};
}}
QFrame.card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QLabel.title {{
    font-size: 20px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel.subtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
QLabel.hint {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {BG_ELEV};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 10px;
    color: {TEXT};
}}
QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}
QTableWidget {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
}}
QHeaderView::section {{
    background: {BG_ELEV};
    color: {TEXT_MUTED};
    padding: 6px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 600;
}}
QScrollBar:vertical {{
    background: {BG};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
}}
"""