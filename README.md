# brilliantcheck (bdc — Brilliant Device Check)

A universal **device identity, authenticity verification, and hardware diagnosis platform** by **Brilliant Tech**.

Brilliantcheck helps repair shops, resellers, and end users determine whether a device is **original, fake, or cloned**, and diagnose hardware health — for **Samsung, Apple, Tecno, Itel, Oppo, Xiaomi, Nokia, Infinix**, and more devices that are quick to pirate.

> Status: **Early development.** Read-only verification only — no flashing, no unlocking.

## Scope

- Read device identity: **IMEI, serial, model, brand, chipset, firmware**.
- Verify against **official/bundled fingerprint data** + online lookup (fallback).
- Report **original / fake / clone / malfunctioning** verdict with evidence.
- Hardware diagnostics: battery, storage, sensors, camera, network (planned).
- **No flashing, no unlocking, no IMEI writes** — read-only.

## Supported transports

- **ADB** (Android — Samsung, Tecno, Itel, Oppo, Xiaomi, Nokia, Infinix, …)
- **Apple / libimobiledevice** (iOS devices)

## Architecture

- **Core:** Rust (`flashpilot`-style bridge binary) — USB/transport, protocol, verification logic.
- **GUI:** Python (PyQt6) — desktop app, delegates to the Rust bridge.
- **Web (optional later):** React + Vite dashboard.
- **Database:** SQLite, migrating to PostgreSQL later.
- **JavaScript:** auxiliary tooling where needed.

## Safety

Brilliantcheck is **read-only**. It never writes to a device.
Always verify device identity before trusting a verdict. Use only on devices you own or are authorized to service.

## Getting started

```bash
git clone <this-repo> brilliantcheck
cd brilliantcheck
# Rust core
cargo build --release
# Python GUI
python -m venv .venv
.venv/bin/pip install -r requirements.txt
# Run (display is auto-detected; no need to set DISPLAY)
.venv/bin/python brilliantcheck
```

## License

MIT — Brilliant Tech. You are responsible for how you use this software.