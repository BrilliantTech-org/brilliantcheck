# Architecture

## Overview

**brilliantcheck (bdc)** is a read-only device identity, authenticity verification, and hardware diagnosis platform.

```
┌────────────────────┐        ┌──────────────────────┐
│  Python GUI (PyQt6)│  <---> │  Rust core (bridge)  │
│  desktop app       │  IPC   │  transport + verify  │
└────────────────────┘        └──────────┬───────────┘
                                         │ USB
                              ┌──────────┴───────────┐
                              │  Devices (ADB/Apple) │
                              └──────────────────────┘
┌────────────────────┐
│  React + Vite web  │  (optional, later)
└────────────────────┘
┌────────────────────┐
│  SQLite → Postgres │  fingerprints, history, audit
└────────────────────┘
```

## Components

- **Rust core** (`src/`): USB transport, protocol handlers (ADB, libimobiledevice), device identity extraction, fingerprint comparison, verdict engine. Exposed as a CLI bridge (`flow-list`, `flow-run` style) consumed by Python.
- **Python GUI** (`python/`): PyQt6 desktop app; renders menus from the bridge's flow registry; delegates execution to the Rust binary. No Qt-independent core logic.
- **Web UI** (`web/`, optional): React + Vite dashboard for reports/history.
- **Database**: SQLite in v0.01; migration path to PostgreSQL. Stores known-good fingerprints, verification history, audit logs.

## Data flow

1. User connects device → Rust enumerates via ADB/Apple transport.
2. Extract identity (IMEI, serial, model, brand, chipset, firmware).
3. Compare against bundled fingerprint DB (offline) → fall back to online lookup.
4. Produce verdict: **original / fake / clone / malfunctioning** + evidence.
5. Persist result + audit log.

## Safety

- Read-only in v0.01: no flashing, unlocking, or IMEI writes.
- All device identifiers treated as sensitive.
- See [SECURITY.md](./SECURITY.md).