"""Thin bridge to the Rust ``brilliantcheck`` binary."""

import json
import os
import shutil
import subprocess
from pathlib import Path


def _candidate_paths():
    env = os.environ.get("BDC_BRIDGE")
    if env:
        yield Path(env)
    # relative to repo root
    here = Path(__file__).resolve().parents[2]
    yield here / "target" / "release" / "brilliantcheck"
    yield here / "target" / "debug" / "brilliantcheck"
    # PATH
    found = shutil.which("brilliantcheck")
    if found:
        yield Path(found)


def bridge_path() -> Path | None:
    for p in _candidate_paths():
        if p and p.exists():
            return p
    return None


def run(args: list[str], timeout: int = 30) -> dict:
    bp = bridge_path()
    if bp is None:
        return {"ok": False, "error": "bridge binary not found; build with cargo build"}
    try:
        proc = subprocess.run(
            [str(bp), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    try:
        data = json.loads(out) if out else {}
    except json.JSONDecodeError:
        data = {"raw": out}
    return {"ok": proc.returncode == 0, "code": proc.returncode, "data": data, "stderr": err}