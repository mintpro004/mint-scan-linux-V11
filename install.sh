#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   MINT SCAN v11.1 — ULTRA PROFESSIONAL AUTO-INSTALLER        ║
# ║   Supports: Debian/Ubuntu · Fedora · Arch · Chromebook      ║
# ║   Arch:     x86_64 · aarch64 (ARM64) · armv7l               ║
# ╚══════════════════════════════════════════════════════════════╝
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${CYAN}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   MINT SCAN v11.1 — UNIVERSAL AUTO-CONFIGURATION           ║"
echo "║   Pretoria · Mint Projects PTY (Ltd) · South Africa         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── [0/9] Platform / Package Manager Detection ───────────────────
echo "[0/9] Detecting system environment..."
IS_AARCH64=false; [[ "$(uname -m)" == "aarch64" || "$(uname -m)" == "arm64" ]] && IS_AARCH64=true
IS_CHROMEBOOK=false; [ -f /proc/version ] && grep -qi "cros\|chrome" /proc/version 2>/dev/null && IS_CHROMEBOOK=true

PM=""
if command -v apt-get &>/dev/null; then PM="apt"; elif command -v dnf &>/dev/null; then PM="dnf"; elif command -v pacman &>/dev/null; then PM="pacman"; fi

echo "  ✓ Architecture: $(uname -m)"
echo "  ✓ Package Manager: ${PM:-"Not detected"}"
$IS_CHROMEBOOK && echo "  ✓ Chromebook detected"

# ── [1/9] Terminal & Visual Configuration ────────────────────────
echo "[1/9] Configuring Terminal Visuals (True Color)..."
FORCE_COLOR="export COLORTERM=truecolor"
for RC in "$HOME/.bashrc" "$HOME/.profile" "$HOME/.zshrc"; do
    if [ -f "$RC" ]; then
        if ! grep -q "COLORTERM=truecolor" "$RC"; then
            echo -e "\n# Enable True Color support\n$FORCE_COLOR" >> "$RC"
            echo "  ✓ Applied to $RC"
        fi
    fi
done
export COLORTERM=truecolor
echo "  ✓ Current session updated"

# ── [2/9] System Dependencies ────────────────────────────────────
echo "[2/9] Installing system packages..."
PKGS_DEB="python3 python3-pip python3-tk python3-dev python3-venv git ripgrep adb nmap ufw x11-utils xdotool net-tools dbus"
PKGS_RPM="python3 python3-pip python3-tkinter python3-devel git ripgrep adb nmap ufw xorg-x11-utils xdotool net-tools dbus"
PKGS_ARCH="python python-pip tk git ripgrep android-tools nmap ufw xorg-xdpyinfo xdotool net-tools dbus"

case $PM in
    apt)
        sudo apt-get update -qq
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq $PKGS_DEB
        if $IS_AARCH64; then
            sudo apt-get install -y -qq python3-pil python3-pil.imagetk libtk8.6 libglib2.0-0
        fi
        ;;
    dnf)
        sudo dnf install -y $PKGS_RPM
        ;;
    pacman)
        sudo pacman -S --noconfirm --needed $PKGS_ARCH
        ;;
    *)
        echo -e "  ${YELLOW}⚠ Unknown package manager. Please install dependencies manually.${NC}"
        ;;
esac

# ── [3/9] CLI Tool Compatibility (Ripgrep Fix) ──────────────────
echo "[3/9] Optimizing CLI tools..."
# Ensure 'ripgrep' symlink exists for tools that look for it instead of 'rg'
if command -v rg &>/dev/null; then
    RG_PATH=$(which rg)
    sudo ln -sf "$RG_PATH" /usr/bin/ripgrep 2>/dev/null || true
    sudo ln -sf "$RG_PATH" /usr/local/bin/ripgrep 2>/dev/null || true
    echo "  ✓ Ripgrep symlinks created"
fi

# ── [4/9] Python Environment ─────────────────────────────────────
echo "[4/9] Setting up Python environment..."
[ ! -d "venv" ] && python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
echo "  ✓ Virtualenv ready"

# ── [5/9] Python Dependencies ────────────────────────────────────
echo "[5/9] Installing Python modules..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt || pip install -r requirements.txt
else
    pip install -q customtkinter==5.2.2 darkdetect psutil pillow qrcode pycryptodome requests netifaces speedtest-cli pystray plyer reportlab
fi
echo "  ✓ Done"

# ── [6/9] Verification ──────────────────────────────────────────
echo "[6/9] Verifying module integrity..."
FAIL_COUNT=0
for pyfile in widgets.py main.py app.py; do
    if [ -f "$pyfile" ]; then
        python3 -m py_compile "$pyfile" 2>/dev/null || {
            echo -e "    ${RED}✗ $pyfile has syntax errors${NC}"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        }
    fi
done

if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "  ${RED}✗ Critical files have errors. Setup aborted.${NC}"
    exit 1
fi
echo "  ✓ Core files OK"

# ── [7/9] Security Tools Config ──────────────────────────────────
echo "[7/9] Configuring system tools..."
if command -v ufw &>/dev/null; then
    sudo ufw --force enable 2>/dev/null || true
    echo "  ✓ Firewall (UFW) enabled"
fi
echo "  ✓ Done"

# ── [8/9] Desktop Shortcut ──────────────────────────────────────
echo "[8/9] Creating desktop integration..."
DESKTOP_DIR="$HOME/Desktop"
[ -d "$DESKTOP_DIR" ] || DESKTOP_DIR="$HOME"
cat > "$DESKTOP_DIR/MintScan.desktop" << EOF
[Desktop Entry]
Name=Mint Scan v11.1
Comment=Advanced Linux Security Auditor
Exec=bash $SCRIPT_DIR/run.sh
Icon=$SCRIPT_DIR/icon.png
Terminal=false
Type=Application
Categories=System;Security;
StartupWMClass=MintScan
EOF
chmod +x "$DESKTOP_DIR/MintScan.desktop" 2>/dev/null || true
echo "  ✓ Shortcut created"

# ── [9/9] Finalizing ─────────────────────────────────────────────
echo "[9/9] Cleaning up..."
for f in reproduce_injection.py test_fix.py verify_fix.py; do [ -f "$f" ] && rm "$f"; done
echo "  ✓ Done"

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════╗"
echo "║   ✓ MINT SCAN v11.1 — AUTO-CONFIGURATION COMPLETE          ║"
echo "║                                                              ║"
echo "║   1. RESTART your terminal to apply visual settings.         ║"
echo "║   2. Type 'bash run.sh' to launch the security auditor.      ║"
echo "║   3. The Gemini CLI will now detect Ripgrep correctly.       ║"
echo "╚══════════════════════════════════════════════════════════════╝${NC}"
