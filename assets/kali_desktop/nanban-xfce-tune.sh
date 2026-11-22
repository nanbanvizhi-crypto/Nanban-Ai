#!/bin/bash
# Nanban — first-login polish for the real Kali XFCE desktop shown in the browser.
# Runs in the background from ~/.vnc/xstartup (as the desktop user, DISPLAY already set).
#   • Kali wallpaper on the VNC monitor (xfdesktop only ships defaults for "monitor0"),
#   • a left-side dock (second xfce4-panel) with the everyday Kali launchers,
#   • sane power/screensaver settings for a remote desktop (never lock/blank).
# Everything is idempotent; the dock is created once (marker file) so user changes stick.

export DISPLAY="${DISPLAY:-:7}"

# Reload the panel ONLY when it is registered on the session bus, so we never trigger
# the "Failed to restart the panel" (org.xfce.Panel not provided) error dialog during
# the start-up race. If it never appears, the fresh panel already read the new config.
panel_reload() {
  for _ in $(seq 1 30); do
    if gdbus introspect --session --dest org.xfce.Panel          --object-path /org/xfce/Panel >/dev/null 2>&1; then
      xfce4-panel -r >/dev/null 2>&1 || true
      return 0
    fi
    sleep 0.5
  done
  return 0
}
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

# ---- real Kali application menu: point the whisker menu at the Kali menu ----
# kali-menu ships /etc/xdg/menus/applications-merged/kali-applications.menu with the
# full Kali tool categories (Reconnaissance, Initial Access, Privilege Escalation, …).
# The whisker menu defaults to xfce-applications.menu, which does NOT show them, so we
# point it at the Kali menu and turn on the category tree. (Runs every login, pre-marker.)
KMENU=/etc/xdg/menus/applications-merged/kali-applications.menu
WPID=$(xfconf-query -c xfce4-panel -p /plugins -lv 2>/dev/null | awk '/whiskermenu/{print $1}' | grep -oE '[0-9]+$' | head -1)
if [ -n "$WPID" ] && [ -e "$KMENU" ]; then
  RC="$HOME/.config/xfce4/panel/whiskermenu-$WPID.rc"
  mkdir -p "$(dirname "$RC")"
  cat > "$RC" <<RCEOF
favorites=
recent=
button-title=Applications
button-icon=kali-panel-menu
show-button-title=false
show-button-icon=true
menu=$KMENU
show-category-names=true
view-as-icons=false
load-hierarchy=true
default-category=0
position-categories-alternate=true
launcher-show-name=true
launcher-show-description=true
item-icon-size=2
category-icon-size=1
RCEOF
fi
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null
xdg_user=1

# ---- PERFORMANCE: this desktop is drawn in software and sent over VNC ----
# Compositing (shadows/transparency) costs a lot of CPU for zero benefit here -> off.
xfconf-query -c xfwm4 -p /general/use_compositing -n -t bool -s false 2>/dev/null
xfconf-query -c xfwm4 -p /general/box_move   -n -t bool -s false 2>/dev/null
xfconf-query -c xfwm4 -p /general/box_resize -n -t bool -s false 2>/dev/null
xfconf-query -c xsettings -p /Gtk/EnableAnimations -n -t bool -s false 2>/dev/null
xfconf-query -c xsettings -p /Net/EnableEventSounds -n -t bool -s false 2>/dev/null
# Background helpers that are useless inside WSL (no battery, no NetworkManager, no lock screen)
mkdir -p "$HOME/.config/autostart"
for f in xfce4-power-manager xfce4-screensaver nm-applet kali-vboxclient xcape-super-key-bind; do
  printf '[Desktop Entry]
Type=Application
Name=%s
Hidden=true
' "$f" > "$HOME/.config/autostart/$f.desktop"
done
pkill -u "$USER" -x xfce4-power-man 2>/dev/null; pkill -u "$USER" -x xfce4-screensav 2>/dev/null; pkill -u "$USER" -x nm-applet 2>/dev/null
# Warm the disk cache for the heavy tools (Kali lives on a hard disk): after this runs once
# per boot, Metasploit / Burp / Wireshark / Firefox open several times faster.
( sleep 90
  for d in /usr/share/metasploit-framework/lib /usr/share/metasploit-framework/vendor/bundle            /usr/share/burpsuite /usr/lib/x86_64-linux-gnu/wireshark /usr/lib/firefox-esr            /usr/lib/jvm/default-java/lib /usr/share/zaproxy; do
    [ -d "$d" ] && find "$d" -type f -size -80M -print0 2>/dev/null | xargs -0 -r cat > /dev/null 2>&1
  done
  for b in wireshark nmap sqlmap hydra john hashcat msfconsole ruby java xfce4-terminal thunar; do
    b=$(command -v "$b" 2>/dev/null) && cat "$b" > /dev/null 2>&1
  done ) >/dev/null 2>&1 &

# ---- remote-desktop friendly: no screen lock / blanking / DPMS ----
xfconf-query -c xfce4-screensaver -p /saver/enabled -n -t bool -s false 2>/dev/null
xfconf-query -c xfce4-screensaver -p /lock/enabled  -n -t bool -s false 2>/dev/null
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled -n -t bool -s false 2>/dev/null
xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac -n -t int -s 0 2>/dev/null
xset s off -dpms 2>/dev/null

# ---- match real Kali: single top panel, whisker (dragon) menu at far left ----
# A left dock would cover the top panel's whisker button, so remove any we created
# before and make sure the Kali menu button is reachable at the top-left corner.
panels=$(xfconf-query -c xfce4-panel -p /panels 2>/dev/null | grep -E '^[0-9]+$')
if echo "$panels" | grep -qx 2; then
  keep=$(echo "$panels" | grep -vx 2)
  pargs=(); for p in $keep; do pargs+=(-t int -s "$p"); done
  [ ${#pargs[@]} -gt 0 ] && xfconf-query -c xfce4-panel -p /panels -n "${pargs[@]}" --force-array 2>/dev/null
  xfconf-query -c xfce4-panel -p /panels/panel-2 -rR 2>/dev/null
fi

# make the top panel (panel-1) look like Kali and keep the whisker menu first
xfconf-query -c xfce4-panel -p /panels/panel-1/position        -n -t string -s "p=6;x=0;y=0" 2>/dev/null  # top, full width
xfconf-query -c xfce4-panel -p /panels/panel-1/length          -n -t uint   -s 100 2>/dev/null
xfconf-query -c xfce4-panel -p /panels/panel-1/size            -n -t uint   -s 30  2>/dev/null
xfconf-query -c xfce4-panel -p /panels/panel-1/position-locked -n -t bool   -s true 2>/dev/null
# whisker plugin must be the first id in panel-1's plugin list
wpid=$(xfconf-query -c xfce4-panel -p /plugins -lv 2>/dev/null | awk '/whiskermenu/{print $1}' | grep -oE '[0-9]+$' | head -1)
if [ -n "$wpid" ]; then
  cur=$(xfconf-query -c xfce4-panel -p /panels/panel-1/plugin-ids 2>/dev/null | grep -E '^[0-9]+$')
  rest=$(echo "$cur" | grep -vx "$wpid")
  pargs=(-t int -s "$wpid"); for i in $rest; do pargs+=(-t int -s "$i"); done
  xfconf-query -c xfce4-panel -p /panels/panel-1/plugin-ids -n "${pargs[@]}" --force-array 2>/dev/null
fi
panel_reload

[ -e "$MARK" ] && exit 0

mkdir -p "$(dirname "$MARK")"; date > "$MARK"
exit 0
