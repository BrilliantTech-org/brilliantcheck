"""Lightweight SQLite persistence (v0 scaffold)."""

import json
import os
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(os.environ.get("BDC_DB", Path.home() / ".brilliantcheck" / "bdc.db"))


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def init():
    with _conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at REAL NOT NULL,
                identifier TEXT,
                brand TEXT,
                model TEXT,
                imei TEXT,
                verdict TEXT,
                raw TEXT
            )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )"""
        )
        c.commit()


def add_check(identifier, brand=None, model=None, imei=None, verdict=None, raw=None):
    init()
    with _conn() as c:
        c.execute(
            "INSERT INTO checks (created_at, identifier, brand, model, imei, verdict, raw) VALUES (?,?,?,?,?,?,?)",
            (time.time(), identifier, brand, model, imei, verdict, json.dumps(raw) if raw is not None else None),
        )
        c.commit()


def list_checks(limit=200):
    init()
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM checks ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def clear_checks():
    init()
    with _conn() as c:
        c.execute("DELETE FROM checks")
        c.commit()


def counts():
    init()
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM checks").fetchone()[0]
        verified = c.execute("SELECT COUNT(*) FROM checks WHERE verdict='original'").fetchone()[0]
        flagged = c.execute("SELECT COUNT(*) FROM checks WHERE verdict IN ('fake','clone')").fetchone()[0]
    return {"total": total, "verified": verified, "flagged": flagged}