#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  Pico Christmas Tree Installer  (macOS)
#
#  Usage:
#    ./install.sh                  -- remove_wifi_and_clock branch
#    ./install.sh -w | --wifi      -- master branch (wifi + clock)
#    ./install.sh -p | --pineapple -- led-pineapple branch
#
#  Everything installed by this script (Homebrew, git, python, mpremote) is
#  removed automatically after the Pico has been updated.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

BRANCH="remove_wifi_and_clock"
DO_WIFI=0

show_usage() {
    echo ""
    echo " Usage: $(basename "$0") [OPTION]"
    echo ""
    echo " Options:"
    echo "   (none)              Flash remove_wifi_and_clock branch  (LEDs, no wifi/clock)"
    echo "   -w, --wifi          Flash master branch  (LEDs + OLED + wifi + NTP clock)"
    echo "   -p, --pineapple     Flash led-pineapple branch"
    echo "   -h, --help          Show this help"
    echo ""
    echo " Requirements:"
    echo "   - Pico connected via a data-capable USB cable"
    echo "   - Internet connection  (for cloning the repo and downloading dependencies)"
    echo ""
    echo " Dependencies (Homebrew, git, Python 3, mpremote) are installed automatically"
    echo " if missing and are removed again when the script finishes."
    echo ""
}

for arg in "$@"; do
    case "$arg" in
        -w|--wifi)      BRANCH="master";        DO_WIFI=1 ;;
        -p|--pineapple) BRANCH="led-pineapple"            ;;
        -h|--help)      show_usage; trap - EXIT; exit 0   ;;
        *)              echo " Unknown option: $arg"; show_usage; trap - EXIT; exit 1 ;;
    esac
done

echo ""
echo " ============================================"
echo "  Pico Christmas Tree Installer  [macOS]"
echo "  Branch : $BRANCH"
echo " ============================================"
echo ""

# Track what this script installs so we only remove what we added
INSTALLED_BREW=0
INSTALLED_GIT=0
INSTALLED_PYTHON=0
INSTALLED_MPREMOTE=0

need() { command -v "$1" &>/dev/null; }

# ── Cleanup handler ────────────────────────────────────────────────────────────
CLONEDIR=""

cleanup() {
    echo ""
    echo "Cleaning up..."

    # Delete repo clone
    if [[ -n "$CLONEDIR" && -d "$CLONEDIR" ]]; then
        cd /tmp
        rm -rf "$CLONEDIR"
        echo "  Repo clone removed."
    fi

    # Uninstall mpremote if we installed it
    if [[ $INSTALLED_MPREMOTE -eq 1 ]]; then
        echo "  Uninstalling mpremote..."
        $PY -m pip uninstall -y mpremote pyserial &>/dev/null || true
        echo "  mpremote uninstalled."
    fi

    # Uninstall python if we installed it
    if [[ $INSTALLED_PYTHON -eq 1 ]]; then
        echo "  Uninstalling Python..."
        brew uninstall --ignore-dependencies python &>/dev/null || true
        echo "  Python uninstalled."
    fi

    # Uninstall git if we installed it
    if [[ $INSTALLED_GIT -eq 1 ]]; then
        echo "  Uninstalling Git..."
        brew uninstall git &>/dev/null || true
        echo "  Git uninstalled."
    fi

    # Uninstall Homebrew if we installed it
    if [[ $INSTALLED_BREW -eq 1 ]]; then
        echo "  Uninstalling Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)" -- --force &>/dev/null || true
        echo "  Homebrew uninstalled."
    fi
}

trap cleanup EXIT

# ── 1. Homebrew ───────────────────────────────────────────────────────────────
echo "[1/4] Checking Homebrew..."
if ! need brew; then
    echo "      Not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    INSTALLED_BREW=1

    # Add Homebrew to PATH for the remainder of this script
    if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi
echo "      OK  ($(brew --version | head -1))"
echo ""

# ── 2. Git ────────────────────────────────────────────────────────────────────
echo "[2/4] Checking Git..."
if ! need git; then
    echo "      Not found. Installing via Homebrew..."
    brew install git
    INSTALLED_GIT=1
fi
echo "      OK  ($(git --version))"
echo ""

# ── 3. Python 3 ───────────────────────────────────────────────────────────────
echo "[3/4] Checking Python 3..."
PY=""
if need python3; then
    PY="python3"
elif need python && python --version 2>&1 | grep -q "Python 3"; then
    PY="python"
fi

if [[ -z "$PY" ]]; then
    echo "      Not found. Installing via Homebrew..."
    brew install python
    INSTALLED_PYTHON=1
    PY="python3"
fi
echo "      OK  ($($PY --version))"
echo ""

# ── 4. mpremote ───────────────────────────────────────────────────────────────
echo "[4/4] Checking mpremote..."
if ! $PY -m mpremote version &>/dev/null; then
    echo "      Not found. Installing via pip..."
    $PY -m pip install --upgrade mpremote
    INSTALLED_MPREMOTE=1
fi
echo "      OK  ($($PY -m mpremote version 2>/dev/null || echo 'installed'))"
echo ""

# ── Clone repo ────────────────────────────────────────────────────────────────
echo "Cloning repository  (branch: $BRANCH)..."
REPO_URL="https://github.com/jcksnvllxr80/raspi_pico_christmas_tree.git"
CLONEDIR="$(mktemp -d)"
git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$CLONEDIR"
echo "      OK  ($CLONEDIR)"
echo ""

cd "$CLONEDIR"

# ── WiFi config (master branch only) ──────────────────────────────────────────
if [[ $DO_WIFI -eq 1 ]]; then
    echo "Collecting WiFi credentials..."

    SSID=$(osascript \
        -e 'tell application "System Events"' \
        -e '  activate' \
        -e '  set r to display dialog "Enter WiFi SSID:" default answer "" with title "Pico Tree  -  WiFi Setup"' \
        -e '  text returned of r' \
        -e 'end tell' 2>/dev/null) || {
        echo " ERROR: SSID dialog cancelled or failed."
        exit 1
    }

    if [[ -z "$SSID" ]]; then
        echo " ERROR: SSID cannot be empty."
        exit 1
    fi

    WIFIPASS=$(osascript \
        -e 'tell application "System Events"' \
        -e '  activate' \
        -e '  set r to display dialog "Enter WiFi Password:" default answer "" with title "Pico Tree  -  WiFi Setup" with hidden answer' \
        -e '  text returned of r' \
        -e 'end tell' 2>/dev/null) || {
        echo " ERROR: Password dialog cancelled or failed."
        exit 1
    }

    echo "Generating config.json from credentials..."
    # Pass creds via env vars to avoid shell-quoting issues with special characters
    SSID="$SSID" WIFIPASS="$WIFIPASS" $PY - <<'PYEOF'
import json, base64, os

ssid = os.environ["SSID"]
pw   = os.environ["WIFIPASS"]

with open("conf/example_config.json") as f:
    cfg = json.load(f)

cfg["wifi"]["ssid"]     = base64.b64encode(ssid.encode()).decode()
cfg["wifi"]["password"] = base64.b64encode(pw.encode()).decode()

with open("conf/config.json", "w") as f:
    json.dump(cfg, f, indent=2)

print("      config.json written.")
PYEOF
    echo ""
fi

# ── Upload files via mpremote ─────────────────────────────────────────────────
MP="$PY -m mpremote"

echo "Uploading files to Pico..."
echo "  (Make sure the Pico is connected via a data-capable USB cable)"
echo ""

upload_file() {
    local src="$1" dst="$2"
    echo "  $src  ->  :$dst"
    $MP cp "$src" ":$dst"
}

if [[ $DO_WIFI -eq 1 ]]; then
    echo "  Creating /conf directory on Pico (safe to ignore if already exists)..."
    $MP fs mkdir /conf 2>/dev/null || true
    echo ""

    upload_file main.py                  main.py
    upload_file img/img_utils.py         img_utils.py
    upload_file base64/base64.py         base64.py
    upload_file display/ssd1306.py       ssd1306.py
    upload_file eeprom/EEPROM_24LC512.py EEPROM_24LC512.py
    upload_file http/httpParser.py       httpParser.py
    upload_file neopixel/neopixel.py     neopixel.py
    upload_file wifi/esp8266.py          esp8266.py
    upload_file conf/config.json         conf/config.json

    rm -f conf/config.json
else
    upload_file main.py                  main.py
    upload_file img/img_utils.py         img_utils.py
    upload_file display/ssd1306.py       ssd1306.py
    upload_file eeprom/EEPROM_24LC512.py EEPROM_24LC512.py
    upload_file neopixel/neopixel.py     neopixel.py
fi

echo ""
echo " ============================================"
echo "  Done!  Pico updated successfully."
echo "  Branch : $BRANCH"
echo " ============================================"
echo ""

# cleanup() fires automatically via trap EXIT
