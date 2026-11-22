#!/bin/bash
# Installs dark-osint (Tor terminal browser + Dark Web OSINT toolkit) inside Kali / Debian.
# Run as root:  sudo bash dark-osint-install.sh [user]   (dark-osint.py must sit next to this script)
set -e
USER_NAME="${1:-${SUDO_USER:-nanbanlinux}}"
SRC="$(cd "$(dirname "$0")" && pwd)/dark-osint.py"
[ "$(id -u)" = 0 ] || { echo "run as root (sudo)"; exit 1; }
[ -f "$SRC" ] || { echo "dark-osint.py not found next to the installer"; exit 1; }

echo "== packages (tor, torsocks, nyx, jq, exiftool, strings, file, curl)"
NEED=""
for p in tor tor-geoipdb torsocks jq libimage-exiftool-perl binutils file curl; do
  dpkg -s "$p" >/dev/null 2>&1 || NEED="$NEED $p"
done
export DEBIAN_FRONTEND=noninteractive
if [ -n "$NEED" ]; then
  apt-get update -qq
  apt-get install -y -qq $NEED
fi
# nyx is optional: some Kali/Debian releases dropped the package. Without it,
# "dark-osint monitor" uses its own built-in live monitor.
if ! command -v nyx >/dev/null 2>&1; then
  apt-get install -y -qq nyx >/dev/null 2>&1 || echo "   (nyx package not available here - built-in monitor will be used)"
fi

echo "== program"
sed 's/\r$//' "$SRC" > /usr/local/bin/dark-osint
chmod 755 /usr/local/bin/dark-osint

echo "== permissions for $USER_NAME"
# debian-tor group = may read Tor's control cookie (circuit display, new identity, nyx)
usermod -aG debian-tor "$USER_NAME"
# start/stop/status of the tor service without a password prompt (only these commands)
cat > /etc/sudoers.d/dark-osint <<EOF
$USER_NAME ALL=(root) NOPASSWD: /usr/bin/systemctl start tor, /usr/bin/systemctl stop tor, /usr/bin/systemctl restart tor, /usr/bin/systemctl status tor
EOF
chmod 440 /etc/sudoers.d/dark-osint
visudo -cf /etc/sudoers.d/dark-osint >/dev/null

echo "== menu entry"
cat > /usr/share/applications/dark-osint.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Dark OSINT (Tor terminal browser)
Comment=Browse .onion sites in the terminal through Tor + 15 OSINT commands
Exec=dark-osint
Icon=utilities-terminal
Terminal=true
Categories=Network;Security;
EOF

echo "== tor service"
systemctl enable tor >/dev/null 2>&1 || true
systemctl start tor || service tor start || true

HOME_DIR="$(getent passwd "$USER_NAME" | cut -d: -f6)"
install -d -o "$USER_NAME" -g "$USER_NAME" -m 700 "$HOME_DIR/dark-osint" "$HOME_DIR/dark-osint/case"
echo "== DONE — open a new terminal and run:  dark-osint"
