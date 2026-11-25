use clap::{Parser, Subcommand};
use serde::Serialize;

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
    /// Detect connected devices (ADB + Apple)
    Detect,
    /// Show device identity for a given serial
    Info {
        /// Device serial / identifier
        serial: String,
    },
}

#[derive(Serialize)]
struct DeviceInfo {
    serial: String,
    brand: Option<String>,
    model: Option<String>,
    imei: Option<String>,
    transport: String,
    verdict: String,
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Some(Commands::Version) | None => {
            println!("brilliantcheck {} (rust core)", env!("CARGO_PKG_VERSION"));
        }
        Some(Commands::Detect) => {
            // TODO: enumerate ADB + libimobiledevice devices
            println!("{}", serde_json::json!({"devices": [], "note": "detect not implemented yet"}));
        }
        Some(Commands::Info { serial }) => {
            let info = DeviceInfo {
                serial,
                brand: None,
                model: None,
                imei: None,
                transport: "unknown".to_string(),
                verdict: "unknown".to_string(),
            };
            println!("{}", serde_json::to_string_pretty(&info).unwrap());
        }
    }
}