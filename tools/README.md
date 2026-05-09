# Pico Christmas Tree — Installer Scripts

One-shot scripts to flash the correct branch of firmware onto the Pico from a machine that may have nothing pre-installed. Both scripts handle every dependency, upload all necessary files, and clean up after themselves when finished.

---

## Scripts

| Script | Platform |
|---|---|
| `install.bat` | Windows |
| `install.sh` | macOS |

---

## Requirements (hardware)

- Raspberry Pi Pico connected via a **data-capable** USB cable (not a charge-only cable)
- Internet connection (for cloning the repo and downloading dependencies)

---

## Usage

### Windows

```cmd
install.bat              # default: remove_wifi_and_clock branch
install.bat -w           # master branch (wifi + clock)
install.bat --wifi       # same as -w
install.bat -p           # led-pineapple branch
install.bat --pineapple  # same as -p
```

### macOS

Make the script executable once, then run it:

```bash
chmod +x install.sh
./install.sh              # default: remove_wifi_and_clock branch
./install.sh -w           # master branch (wifi + clock)
./install.sh --wifi       # same as -w
./install.sh -p           # led-pineapple branch
./install.sh --pineapple  # same as -p
```

---

## Branch / flag reference

| Flag | Branch | Description |
|---|---|---|
| *(none)* | `remove_wifi_and_clock` | LED effects only — no wifi, no clock |
| `-w` / `--wifi` | `master` | Full firmware: LED effects, OLED display, wifi, NTP time sync |
| `-p` / `--pineapple` | `led-pineapple` | LED effects configured for pineapple shape |

---

## What the scripts do

### Step 1 — Dependency checks and installs

The scripts check for each dependency and install it only if it is missing. Nothing is installed that is already present.

| Dependency | Windows — primary | Windows — fallback | macOS |
|---|---|---|---|
| Git | `winget` | Direct download via PowerShell (GitHub releases API) | Homebrew |
| Python 3.11 | `winget` | Direct download via PowerShell (python.org) | Homebrew |
| mpremote + pyserial | `pip` | `pip` | `pip` |
| Homebrew | — | — | Official install script |

**Windows installer fallback**

`winget` (App Installer) ships with all Windows 11 builds and Windows 10 version 1809+, but it can be missing on older Win10 machines, LTSC/enterprise images, or fresh VM installs. The script handles this gracefully:

1. Checks whether `winget` is available.
2. If yes, uses `winget install` as normal.
3. If no (or if `winget` reports success but the install fails), falls back to downloading the installer directly with PowerShell's `Invoke-WebRequest`:
   - **Git:** queries the [git-for-windows GitHub releases API](https://api.github.com/repos/git-for-windows/git/releases/latest) to get the latest 64-bit `.exe`, downloads it, and runs it silently.
   - **Python:** downloads the pinned `python-3.11.9-amd64.exe` directly from `python.org/ftp` and runs it silently with `PrependPath=1` (per-user install, no elevation required).

Both installers are deleted from the temp directory immediately after running.

> **Note (macOS):** After a fresh Homebrew install the script updates the shell's `PATH` automatically so subsequent steps work in the same session.

### Step 2 — Clone the repo

The target branch is cloned at depth 1 into a temporary directory. Nothing is written to your current working directory.

### Step 3 — WiFi credentials (`-w` / `--wifi` only)

A GUI popup asks for your WiFi SSID and password:

- **Windows:** two sequential Tkinter dialogs (password field is masked)
- **macOS:** two sequential system dialogs via `osascript` (password field is hidden)

The SSID and password are **base64-encoded** and injected into the config template (`conf/example_config.json`) to produce `conf/config.json`. This file is uploaded to the Pico and then immediately deleted from the local clone. It is also listed in `.gitignore` so it can never be accidentally committed.

### Step 4 — File upload via mpremote

Files are copied from the local clone to the root of the Pico's filesystem using `mpremote cp`. The `conf/` directory is the only subdirectory maintained on the Pico (master branch only).

#### Files uploaded per branch

| File (local path) | Pico destination | master | remove\_wifi | pineapple |
|---|---|---|---|---|
| `main.py` | `/main.py` | ✓ | ✓ | ✓ |
| `img/img_utils.py` | `/img_utils.py` | ✓ | ✓ | ✓ |
| `display/ssd1306.py` | `/ssd1306.py` | ✓ | ✓ | ✓ |
| `eeprom/EEPROM_24LC512.py` | `/EEPROM_24LC512.py` | ✓ | ✓ | ✓ |
| `neopixel/neopixel.py` | `/neopixel.py` | ✓ | ✓ | ✓ |
| `base64/base64.py` | `/base64.py` | ✓ | — | — |
| `http/httpParser.py` | `/httpParser.py` | ✓ | — | — |
| `wifi/esp8266.py` | `/esp8266.py` | ✓ | — | — |
| `conf/config.json` *(generated)* | `/conf/config.json` | ✓ | — | — |

> `img_utils.py` is a large pre-compiled file containing all LED effect image data as embedded bytearrays. The source PNG files under `img/numbers/` and `img/words/` are not uploaded.

> `eeprom/main.py` is a standalone test file and is intentionally excluded to avoid overwriting `/main.py` on the Pico.

### Step 5 — Cleanup

After the upload completes (or if an error occurs), everything the script installed is removed in reverse order:

1. Local repo clone (temp directory) — always removed
2. `mpremote` and `pyserial` — `pip uninstall`
3. Python — `winget uninstall` / `brew uninstall`
4. Git — `winget uninstall` / `brew uninstall`
5. Homebrew — official uninstall script (macOS only, if Homebrew was not present before)

Only items that were **installed by the script** are removed. If Python or Git was already on the machine before running the script, it will not be touched.

> **macOS:** cleanup is registered with `trap EXIT` so it runs even if the script fails partway through — no stranded installs.

> **Windows:** all error paths route through a shared cleanup block for the same guarantee.

---

## Troubleshooting

**Upload fails immediately**
The most common cause is a charge-only USB cable. Swap to a data cable and re-run.

**mpremote can't find the Pico**
If you have multiple serial devices connected, mpremote may pick the wrong one. Identify the correct port (`/dev/cu.usbmodemXXXX` on Mac, `COMX` on Windows) and prefix each `mpremote` call with `connect <port>`. The scripts currently rely on auto-detection.

**Windows: "Git/Python was installed but is not yet on PATH"**
This can happen if the installer updated the system PATH but the current cmd session hasn't picked it up. Close the terminal, open a new one, and re-run `install.bat`.

**Windows: winget fails and the PowerShell download also fails**
This usually means no internet access, or a corporate firewall is blocking `api.github.com` or `python.org`. Install [Git](https://git-scm.com) and [Python 3.11](https://python.org) manually, then re-run the script — it will detect them and skip straight to the upload.

**macOS: Homebrew install requires sudo / Xcode CLT prompt**
The Homebrew installer may pause to install Xcode Command Line Tools if they are missing. Follow the on-screen prompt and let it complete — the script will continue once Homebrew is ready.

**WiFi dialog doesn't appear (Windows)**
Tkinter is bundled with the official Python installer from python.org and the winget Python package. If it is missing, install Python manually with the standard installer and ensure the "tcl/tk and IDLE" option is checked.
