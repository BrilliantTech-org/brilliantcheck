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
    /// Validate an IMEI (15 digits) and report TAC/check-digit
    ImeiCheck {
        /// 15-digit IMEI
        imei: String,
    },
    /// Switch a USB-connected device to TCP (wireless) mode on port 5555
    AdbTcpip {
        /// Device serial (USB)
        serial: String,
        /// TCP port (default 5555)
        port: Option<u16>,
    },
    /// Connect adb to a wireless device (ip:port)
    AdbConnect {
        /// Target like 192.168.1.5:5555
        target: String,
    },
    /// Disconnect adb from a wireless device (or all if omitted)
    AdbDisconnect {
        /// Target like 192.168.1.5:5555 (optional)
        target: Option<String>,
    },
    /// Pair with an Android 11+ wireless debugging device using a pairing code
    AdbPair {
        /// Target like 192.168.1.5:42000
        target: String,
        /// 6-digit pairing code
        code: String,
    },
}

#[derive(Serialize, Default)]
struct ImeiReport {
    imei: String,
    valid_format: bool,
    valid_luhn: bool,
    tac: Option<String>,
    check_digit: Option<String>,
    verdict: String,
    note: String,
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

fn adb_full(args: &[&str]) -> (String, String, bool) {
    match Command::new("adb").args(args).output() {
        Ok(out) => (
            String::from_utf8_lossy(&out.stdout).to_string(),
            String::from_utf8_lossy(&out.stderr).to_string(),
            out.status.success(),
        ),
        Err(e) => (String::new(), e.to_string(), false),
    }
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

fn luhn_imei_valid(imei: &str) -> bool {
    if imei.len() != 15 || !imei.chars().all(|c| c.is_ascii_digit()) {
        return false;
    }
    let digits: Vec<u32> = imei.chars().filter_map(|c| c.to_digit(10)).collect();
    let mut sum = 0u32;
    // process from right, doubling every second digit (excluding check digit)
    for (i, d) in digits[..14].iter().rev().enumerate() {
        if i % 2 == 0 {
            // second from right position -> double
            let doubled = d * 2;
            sum += if doubled > 9 { doubled - 9 } else { doubled };
        } else {
            sum += d;
        }
    }
    let check = (10 - (sum % 10)) % 10;
    check == digits[14]
}

fn imei_check(imei: &str) -> ImeiReport {
    let valid_format = imei.len() == 15 && imei.chars().all(|c| c.is_ascii_digit());
    if !valid_format {
        return ImeiReport {
            imei: imei.to_string(),
            valid_format: false,
            valid_luhn: false,
            tac: None,
            check_digit: None,
            verdict: "invalid".to_string(),
            note: "IMEI must be exactly 15 digits.".to_string(),
        };
    }
    let valid_luhn = luhn_imei_valid(imei);
    let tac = Some(imei[..8].to_string());
    let check_digit = Some(imei[14..].to_string());
    let verdict = if valid_luhn { "valid" } else { "invalid" }.to_string();
    let note = if valid_luhn {
        "Luhn check digit OK. Cross-check TAC/model against official sources to confirm authenticity.".to_string()
    } else {
        "Luhn check digit FAILED — likely fake or mistyped IMEI.".to_string()
    };
    ImeiReport {
        imei: imei.to_string(),
        valid_format: true,
        valid_luhn,
        tac,
        check_digit,
        verdict,
        note,
    }
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Some(Commands::Version) | None => {
            println!("brilliantcheck {} (rust core)", env!("CARGO_PKG_VERSION"));
        }
        Some(Commands::Detect) => {
            let devices = detect_devices();
            let msg = if devices.is_empty() {
                "No device connected"
            } else {
                "Devices detected"
            };
            let out = serde_json::json!({ "devices": devices, "message": msg });
            println!("{}", serde_json::to_string_pretty(&out).unwrap_or_else(|_| "{}".to_string()));
        }
        Some(Commands::ImeiCheck { imei }) => {
            let report = imei_check(&imei);
            println!("{}", serde_json::to_string_pretty(&report).unwrap());
        }
        Some(Commands::AdbTcpip { serial, port }) => {
            let p = port.unwrap_or(5555).to_string();
            let sref = serial.as_str();
            let pref = p.as_str();
            let (stdout, stderr, ok) = adb_full(&["-s", sref, "tcpip", pref]);
            let msg = format!("{}{}", stdout.trim(), if stderr.trim().is_empty() { String::new() } else { format!(" ({})", stderr.trim()) });
            let out = serde_json::json!({ "ok": ok, "port": p, "message": msg.trim() });
            println!("{}", serde_json::to_string_pretty(&out).unwrap());
        }
        Some(Commands::AdbConnect { target }) => {
            let (stdout, stderr, ok) = adb_full(&["connect", &target]);
            let msg = if stdout.trim().is_empty() { stderr.trim().to_string() } else { stdout.trim().to_string() };
            let out = serde_json::json!({ "ok": ok, "target": target, "message": msg });
            println!("{}", serde_json::to_string_pretty(&out).unwrap());
        }
        Some(Commands::AdbDisconnect { target }) => {
            let (stdout, stderr, ok) = match &target {
                Some(t) => {
                    let tr = t.as_str();
                    adb_full(&["disconnect", tr])
                }
                None => adb_full(&["disconnect"]),
            };
            let msg = if stdout.trim().is_empty() { stderr.trim().to_string() } else { stdout.trim().to_string() };
            let out = serde_json::json!({ "ok": ok, "message": msg });
            println!("{}", serde_json::to_string_pretty(&out).unwrap());
        }
        Some(Commands::AdbPair { target, code }) => {
            use std::io::Write;
            let child = Command::new("adb")
                .args(["pair", &target])
                .stdin(std::process::Stdio::piped())
                .stdout(std::process::Stdio::piped())
                .stderr(std::process::Stdio::piped())
                .spawn();
            match child {
                Ok(mut c) => {
                    if let Some(mut stdin) = c.stdin.take() {
                        let _ = writeln!(stdin, "{}", code);
                    }
                    let out = c.wait_with_output();
                    match out {
                        Ok(o) => {
                            let stdout = String::from_utf8_lossy(&o.stdout).to_string();
                            let stderr = String::from_utf8_lossy(&o.stderr).to_string();
                            let msg = if stdout.trim().is_empty() { stderr.trim().to_string() } else { stdout.trim().to_string() };
                            let res = serde_json::json!({ "ok": o.status.success(), "target": target, "message": msg });
                            println!("{}", serde_json::to_string_pretty(&res).unwrap());
                        }
                        Err(e) => {
                            let res = serde_json::json!({ "ok": false, "target": target, "message": e.to_string() });
                            println!("{}", serde_json::to_string_pretty(&res).unwrap());
                        }
                    }
                }
                Err(e) => {
                    let res = serde_json::json!({ "ok": false, "target": target, "message": e.to_string() });
                    println!("{}", serde_json::to_string_pretty(&res).unwrap());
                }
            }
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