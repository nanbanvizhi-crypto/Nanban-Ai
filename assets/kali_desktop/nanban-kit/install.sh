#!/bin/bash
# Installs the Nanban Kali Kit (kali-intel, kali-pentest, nmap2, kali-forensics)
# inside Kali / Debian. Run as root:
#   sudo bash install.sh [user]
# The kit's .py files must sit next to this script.
set -e
USER_NAME="${1:-${SUDO_USER:-nanbanlinux}}"
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="/opt/nanban-kit"
[ "$(id -u)" = 0 ] || { echo "run as root (sudo)"; exit 1; }
for f in kitlib.py kali_intel.py kali_pentest.py nmap2.py kali_forensics.py; do
  [ -f "$SRC/$f" ] || { echo "missing $f next to the installer"; exit 1; }
done

echo "== core packages"
CORE="nmap whois dnsutils curl jq binutils file libimage-exiftool-perl python3"
NEED=""
for p in $CORE; do dpkg -s "$p" >/dev/null 2>&1 || NEED="$NEED $p"; done
export DEBIAN_FRONTEND=noninteractive
if [ -n "$NEED" ]; then apt-get update -qq; apt-get install -y -qq $NEED; fi

echo "== optional analysis tools (best effort)"
for p in whatweb binwalk yara pdfid; do
  dpkg -s "$p" >/dev/null 2>&1 || apt-get install -y -qq "$p" >/dev/null 2>&1 || echo "   (optional: $p not available)"
done
# nuclei is large; install if present in repo, else leave a hint
command -v nuclei >/dev/null 2>&1 || apt-get install -y -qq nuclei >/dev/null 2>&1 || echo "   (optional: install nuclei later for web scanning)"

echo "== program files -> $DEST"
mkdir -p "$DEST"
for f in kitlib.py kali_intel.py kali_pentest.py nmap2.py kali_forensics.py; do
  sed 's/\r$//' "$SRC/$f" > "$DEST/$f"
done
chmod 644 "$DEST"/*.py
python3 -m compileall -q "$DEST" >/dev/null 2>&1 || true   # root-owned __pycache__, so users don't write it

echo "== commands -> /usr/local/bin"
make_wrapper() { # name  module
  cat > "/usr/local/bin/$1" <<EOF
#!/bin/bash
exec python3 "$DEST/$2" "\$@"
EOF
  chmod 755 "/usr/local/bin/$1"
}
make_wrapper kali-intel      kali_intel.py
make_wrapper kali-pentest    kali_pentest.py
make_wrapper nmap2           nmap2.py
make_wrapper kali-forensics  kali_forensics.py

echo "== AI engine link (detect Ollama)"
HOME_DIR="$(getent passwd "$USER_NAME" | cut -d: -f6)"
KITDIR="$HOME_DIR/.nanban-kit"
install -d -o "$USER_NAME" -g "$USER_NAME" -m 700 "$KITDIR"
OLLAMA_URL=""
# candidate hosts: localhost, the WSL nameserver (Windows host), the default gateway
CANDS="http://127.0.0.1:11434"
NS="$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf 2>/dev/null)"
[ -n "$NS" ] && CANDS="$CANDS http://$NS:11434"
GW="$(ip route 2>/dev/null | awk '/default/{print $3; exit}')"
[ -n "$GW" ] && CANDS="$CANDS http://$GW:11434"
for u in $CANDS; do
  if curl -s -m 2 "$u/api/tags" >/dev/null 2>&1; then OLLAMA_URL="$u"; break; fi
done
MODEL="llama3.1:8b"
if [ -n "$OLLAMA_URL" ]; then
  M="$(curl -s -m 3 "$OLLAMA_URL/api/tags" | jq -r '.models[0].name // empty' 2>/dev/null)"
  [ -n "$M" ] && MODEL="$M"
  echo "   found Ollama at $OLLAMA_URL (model $MODEL)"
else
  echo "   Ollama not reachable now — tools work offline; AI turns on automatically when Ollama runs."
fi
cat > "$KITDIR/ai.json" <<EOF
{ "ollama_url": "$OLLAMA_URL", "model": "$MODEL", "hosted_url": "", "hosted_key": "", "hosted_model": "" }
EOF
chown "$USER_NAME:$USER_NAME" "$KITDIR/ai.json"; chmod 600 "$KITDIR/ai.json"
install -d -o "$USER_NAME" -g "$USER_NAME" "$HOME_DIR/nanban-kit" "$HOME_DIR/nanban-kit/case"

echo "== menu entries"
mk_desktop() { # name  exec  comment
  cat > "/usr/share/applications/$1.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$2
Comment=$3
Exec=$1
Icon=kali-menu
Terminal=true
Categories=Security;System;
EOF
}
mk_desktop kali-intel     "Kali Intel Hub"        "Unified OSINT & Threat Intelligence"
mk_desktop kali-pentest   "Kali Pentest Agent"    "AI-guided penetration testing"
mk_desktop nmap2          "Nmap 2.0"              "Visual Nmap with AI analysis"
mk_desktop kali-forensics "Kali Forensics Lab"    "AI-assisted digital forensics"

echo "== DONE — commands ready: kali-intel  kali-pentest  nmap2  kali-forensics"
