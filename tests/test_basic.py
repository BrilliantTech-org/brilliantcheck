import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_bridge_import():
    from brilliantcheck.core.bridge import bridge_path, run
    # bridge may or may not exist; run should not crash
    r = run(["version"])
    assert isinstance(r, dict)


def test_db_roundtrip(tmp_path):
    os.environ["BDC_DB"] = str(tmp_path / "t.db")
    from brilliantcheck.core import db
    db.init()
    db.add_check("123456789012345", brand="Test", model="M", verdict="original")
    rows = db.list_checks()
    assert len(rows) == 1
    assert rows[0]["identifier"] == "123456789012345"
    c = db.counts()
    assert c["total"] == 1
    assert c["verified"] == 1
    db.clear_checks()
    assert db.counts()["total"] == 0


def test_ui_import():
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from brilliantcheck.ui.main_window import MainWindow
    w = MainWindow()
    assert w.windowTitle().startswith("brilliantcheck")
