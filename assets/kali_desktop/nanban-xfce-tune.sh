#!/bin/bash
# Nanban — first-login polish for the real Kali XFCE desktop shown in the browser.
# Runs in the background from ~/.vnc/xstartup (as the desktop user, DISPLAY already set).
#   • Kali wallpaper on the VNC monitor (xfdesktop only ships defaults for "monitor0"),
#   • a left-side dock (second xfce4-panel) with the everyday Kali launchers,
#   • sane power/screensaver settings for a remote desktop (never lock/blank).
# Everything is idempotent; the dock is created once (marker file) so user changes stick.

export DISPLAY="${DISPLAY:-:7}"
MARK="$HOME/.config/nanban-desktop.tuned"
WALL=/usr/share/backgrounds/kali-16x9/default
[ -e "$WALL" ] || WALL=$(ls /usr/share/backgrounds/kali/*16x9*.jpg 2>/dev/null | head -1)

# wait for the session (xfconfd + xfdesktop + panel) — up to ~60s
for _ in $(seq 1 120); do
  pgrep -u "$USER" -x xfdesktop >/dev/null && pgrep -u "$USER" -x xfce4-panel >/dev/null && break
  sleep 0.5
done
sleep 2

# ---- wallpaper on every monitor xfdesktop knows about (VNC-0 and future resizes) ----
if [ -n "$WALL" ]; then
  mons=$(xrandr 2>/dev/null | awk '/ connected/{print $1}')
  for m in ${mons:-VNC-0} 0; do
    for ws in 0 1 2 3; do
      base="/backdrop/screen0/monitor$m/workspace$ws"
      xfconf-query -c xfce4-desktop -p "$base/last-image"  -n -t string -s "$WALL" 2>/dev/null
      xfconf-query -c xfce4-desktop -p "$base/image-style" -n -t int    -s 5       2>/dev/null
      xfconf-query -c xfce4-desktop -p "$base/color-style" -n -t int    -s 0       2>/dev/null
    done
  done
  xfconf-query -c xfce4-desktop -p /backdrop/single-workspace-mode -n -t bool -s true 2>/dev/null
  xfdesktop --reload >/dev/null 2>&1 || true
fi

# ---- remote-desktop friendly: no screen lock / blanking / DPMS ----
xfconf-query -c xfce4-screensaver -p /saver/enabled -n -t bool -s false 2>/dev/null
xfconf-query -c xfce4-screensaver -p /lock/enabled  -n -t bool -s false 2>/dev/null
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled -n -t bool -s false 2>/dev/null
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac -n -t int -s 0 2>/dev/null
xset s off -dpms 2>/dev/null

[ -e "$MARK" ] && exit 0

# ---- left dock: a second, vertical xfce4-panel with launchers ----
APPS=/usr/share/applications
pick() { for f in "$@"; do [ -e "$APPS/$f" ] && { echo "$f"; return; }; done; }
ITEMS=(
  "$(pick xfce4-terminal.desktop qterminal.desktop xfce4-terminal-emulator.desktop)"
  "$(pick thunar.desktop org.xfce.thunar.desktop)"
  "$(pick org.xfce.mousepad.desktop mousepad.desktop)"
  "$(pick firefox-esr.desktop firefox.desktop)"
  "$(pick kali-msfconsole.desktop)"
  "$(pick kali-burpsuite.desktop)"
  "$(pick kali-wireshark.desktop org.wireshark.Wireshark.desktop)"
  "$(pick kali-nmap.desktop kali-zenmap.desktop)"
  "$(pick kali-john.desktop)"
  "$(pick kali-sqlmap.desktop)"
  "$(pick xfce4-appfinder.desktop)"
  "$(pick kali-docs.desktop)"
)
ids=(); n=1000
for it in "${ITEMS[@]}"; do
  [ -n "$it" ] || continue
  n=$((n+1)); ids+=("$n")
  d="$HOME/.config/xfce4/panel/launcher-$n"; mkdir -p "$d"; cp -f "$APPS/$it" "$d/$it"
  xfconf-query -c xfce4-panel -p "/plugins/plugin-$n" -n -t string -s launcher 2>/dev/null
  xfconf-query -c xfce4-panel -p "/plugins/plugin-$n/items" -n -t string -s "$it" --force-array 2>/dev/null
done
if [ "${#ids[@]}" -gt 0 ]; then
  args=(); for i in "${ids[@]}"; do args+=(-t int -s "$i"); done
  P=/panels/panel-2
  xfconf-query -c xfce4-panel -p $P/position         -n -t string -s "p=5;x=0;y=0"   # p=5 = left edge
  xfconf-query -c xfce4-panel -p $P/mode             -n -t int    -s 1                # vertical
  xfconf-query -c xfce4-panel -p $P/length           -n -t int    -s 100
  xfconf-query -c xfce4-panel -p $P/size             -n -t int    -s 44
  xfconf-query -c xfce4-panel -p $P/icon-size        -n -t int    -s 28
  xfconf-query -c xfce4-panel -p $P/position-locked  -n -t bool   -s true
  xfconf-query -c xfce4-panel -p $P/autohide-behavior -n -t int   -s 0
  xfconf-query -c xfce4-panel -p $P/background-style -n -t int    -s 1
  xfconf-query -c xfce4-panel -p $P/background-rgba  -n -t double -s 0.04 -t double -s 0.07 -t double -s 0.10 -t double -s 0.85 --force-array
  xfconf-query -c xfce4-panel -p $P/plugin-ids       -n "${args[@]}" --force-array
  # register panel 2 next to the existing top panel(s)
  cur=$(xfconf-query -c xfce4-panel -p /panels 2>/dev/null | grep -E '^[0-9]+$' | sort -un)
  pargs=(); for p in $cur 2; do pargs+=(-t int -s "$p"); done
  [ -z "$cur" ] && pargs=(-t int -s 1 -t int -s 2)
  xfconf-query -c xfce4-panel -p /panels -n "${pargs[@]}" --force-array 2>/dev/null \
    || xfconf-query -c xfce4-panel -p /panels "${pargs[@]}" --force-array 2>/dev/null
  xfce4-panel -r >/dev/null 2>&1 || true
fi

mkdir -p "$(dirname "$MARK")"; date > "$MARK"
exit 0
