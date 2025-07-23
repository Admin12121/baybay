# Baybay

Baybay is a Python-based Command and Control (C2) framework that enables users to easily build, configure, and deploy C2 payloads using a Terminal User Interface (TUI) application. The framework is designed specifically for stealth, leveraging Discord webhooks for C2 communications—making it more difficult for traditional Windows antivirus and firewalls to detect or block traffic.

---

## Why Use Discord Webhooks for C2?

Baybay uses Discord as its C2 server. Discord webhooks allow payloads to communicate over HTTPS to the Discord platform, blending C2 traffic with legitimate Discord traffic. This approach offers several advantages:

- **Evasion:** Discord traffic is common and typically allowed through firewalls, making it less likely to be blocked or flagged by default security policies.
- **Obfuscation:** Communication via Discord webhooks appears as legitimate HTTPS POST requests to Discord servers, bypassing most signature-based antivirus and network security tools.
- **Reliability:** Discord is a robust, globally distributed platform, ensuring high availability and low latency for C2 operations.
- **No Infrastructure Needed:** You do not need to host your own C2 server—just create a Discord channel and webhook.

> **Note:** This project is for educational and authorized security research purposes only. Misuse is strictly prohibited.

---

## Features

- **TUI Payload Builder:** Easily craft payloads via a user-friendly terminal interface.
- **Discord Webhook Integration:** All C2 communications use Discord webhooks for stealth and evasion.
- **Payload Customization:** Configure build options for different attack scenarios.
- **Modular Loader and Builder:** Separate logic for creating and launching payloads.
- **Cross-Platform:** 100% Python implementation.
- **Automatic Dependency Management:** Uses [uv](https://github.com/astral-sh/uv) to install and manage dependencies seamlessly.

---

## Project Structure

Baybay consists of several core components and helpers:

```
baybay/
├── img/                # Images for exe icon after build
├── libraries/          # Support libraries for payload building and runtime
├── .gitignore          # Git ignore rules
├── .python-version     # Python version specification for the project
├── README.md           # Project documentation (this file)
├── app.py              # TUI application entry point
├── builder.py          # EXE and payload builder logic
├── loader.py           # Loader logic for payload execution, TUI loader
├── main.py             # Main payload execution logic
├── pyproject.toml      # Project metadata and dependency list for uv
├── uv.lock             # Dependency lock file for uv
└── version.txt         # Meta data for exe application
```

### Key Files & Their Roles

- **img/**: Contains images for exec icon after build
- **libraries/**: Houses additional libraries needed for advanced payloads.
- **.python-version**: Specifies the Python version for development and deployment consistency.
- **app.py**: Launches the TUI interface for building and managing payloads.
- **builder.py**: Handles the creation of executable payloads, wrapping scripts as necessary.
- **loader.py**: Acts as the TUI loader for launching or deploying payloads.
- **main.py**: Implements the core functionality of the payload itself.
- **pyproject.toml & uv.lock**: Used by `uv` for reproducible, fast dependency management.
- **version.txt**: Tracks the current project version.

---

## Getting Started

### Prerequisites

- **Python 3.7+**
### Install `uv`

| Platform | Command |
|----------|---------|
| **Linux** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Windows** | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |

For more details, see the [official uv documentation](https://github.com/astral-sh/uv).

### Running Baybay

No need to manually install dependencies—just use `uv`!

```bash
uv run app.py
```

This will automatically install all required dependencies and start the TUI builder.

---

## How It Works

1. **Payload Creation:** Use the TUI to select payload options and generate a custom payload.
2. **Discord C2 Setup:** Configure your Discord webhook URL in the builder.
3. **Deployment:** Deploy the generated payload to your test system.
4. **C2 Communication:** The payload uses Discord webhooks to send/receive commands, evading most network security tools.

---



## Security & Legal Notice

Baybay is intended for **authorized security research, red teaming, and educational purposes only**. Use of this framework in unauthorized environments or for malicious activities is strictly forbidden. The authors disclaim all liability for misuse.

---

## License

MIT License

---

## Contributing

Pull requests and suggestions are welcome! Please open an issue or submit a PR to help improve Baybay.

---

**Always use Baybay responsibly and legally.**

![Project Structure Overview](image1)

