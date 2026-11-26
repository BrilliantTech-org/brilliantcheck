use clap::{Parser, Subcommand};
use serde::Serialize;
use std::process::Command;

#[derive(Parser, Debug)]
#[command(name = "brilliantcheck", version, about = "Brilliant Device Check (bdc) — Rust core")]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Print version info
    Version,
    /// Detect connected devices (ADB)
    Detect,
    /// Show device identity for a given serial
    Info {
        /// Device serial / identifier
        serial: String,
    },
}

#[derive(Serialize, Default)]
struct DeviceInfo {
    serial: String,
    brand: Option<String>,
    model: Option<String>,
    manufacturer: Option<String>,
    android_version: Option<String>,
    imei: Option<String>,
    transport: String,
    verdict: String,
}

fn adb(args: &[&str]) -> Option<String> {
    let out = Command::new("adb").args(args).output().ok()?;
    if !out.status.success() {
        // adb returns nonzero sometimes but still prints; keep stdout
    }
    Some(String::from_utf8_lossy(&out.stdout).to_string())
}

fn prop(serial: &str, key: &str) -> Option<String> {
    let out = adb(&["-s", serial, "shell", "getprop", key])?;
    let v = out.trim().to_string();
    if v.is_empty() { None } else { Some(v) }
}

fn imei(serial: &str) -> Option<String> {
    // Try service call (works on many Android builds)
    if let Some(out) = adb(&["-s", serial, "shell", "service", "call", "iphonesubinfo", "1"]) {
        // parse hex string in output like 'Result: Parcel( ... )'
        let mut hex = String::new();
        for line in out.lines() {
            for tok in line.split_whitespace() {
                // tokens like '3132...' or "'3132...'"
                let t = tok.trim_matches(|c: char| c == '\'' || c == '"' || c == ',');
                if t.len() >= 4 && t.chars().all(|c| c.is_ascii_hexdigit()) {
                    hex.push_str(t);
                }
            }
        }
        if !hex.is_empty() {
            // convert hex pairs to chars (skip non-printable)
            let mut s = String::new();
            for chunk in hex.as_bytes().chunks(2) {
                if chunk.len() == 2 {
                    if let Ok(b) = u8::from_str_radix(std::str::from_utf8(chunk).unwrap_or(""), 16) {
                        if b.is_ascii_digit() {
                            s.push(b as char);
                        }
                    }
                }
            }
            if !s.is_empty() {
                return Some(s);
            }
        }
    }
    // Fallback: dumpsys
    if let Some(out) = adb(&["-s", serial, "shell", "dumpsys", "iphonesubinfo"]) {
        for line in out.lines() {
            let l = line.trim();
            if l.to_lowercase().contains("device id") || l.to_lowercase().contains("imei") {
                if let Some(idx) = l.find(':') {
                    let v = l[idx + 1..].trim().to_string();
                    if !v.is_empty() && v.chars().all(|c| c.is_ascii_digit()) {
                        return Some(v);
                    }
                }
            }
        }
    }
    None
}

fn detect_devices() -> Vec<DeviceInfo> {
    let mut devices = Vec::new();
    let Some(out) = adb(&["devices"]) else {
        return devices;
    };
    for line in out.lines().skip(1) {
        let line = line.trim();
        if line.is_empty() { continue; }
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() < 2 { continue; }
        let serial = parts[0];
        let state = parts[1];
        if state != "device" { continue; }
        let info = DeviceInfo {
            serial: serial.to_string(),
            brand: prop(serial, "ro.product.brand"),
            model: prop(serial, "ro.product.model"),
            manufacturer: prop(serial, "ro.product.manufacturer"),
            android_version: prop(serial, "ro.build.version.release"),
            imei: imei(serial),
            transport: "adb".to_string(),
            verdict: "unknown".to_string(),
        };
        devices.push(info);
    }
    devices
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Some(Commands::Version) | None => {
            println!("brilliantcheck {} (rust core)", env!("CARGO_PKG_VERSION"));
        }
        Some(Commands::Detect) => {
            let devices = detect_devices();
            println!("{}", serde_json::to_string_pretty(&devices).unwrap_or_else(|_| "[]".to_string()));
        }
        Some(Commands::Info { serial }) => {
            // If serial matches a connected device, gather; else treat as identifier
            let adb_devices: Vec<String> = detect_devices().into_iter().map(|d| d.serial).collect();
            let info = if adb_devices.contains(&serial) {
                detect_devices().into_iter().find(|d| d.serial == serial).unwrap()
            } else {
                DeviceInfo {
                    serial: serial.clone(),
                    brand: None,
                    model: None,
                    manufacturer: None,
                    android_version: None,
                    imei: None,
                    transport: "identifier".to_string(),
                    verdict: "unknown".to_string(),
                }
            };
            println!("{}", serde_json::to_string_pretty(&info).unwrap());
        }
    }
}