#!/bin/bash
# Nanban — real Kali XFCE desktop in the browser (TigerVNC + noVNC).
# Installed by Nanban to /usr/local/bin/nanban-desktop inside the Kali WSL distro.
#
#   nanban-desktop start   [user]   start desktop (idempotent)
#   nanban-desktop stop    [user]
#   nanban-desktop status  [user]
#   nanban-desktop ready            exit 0 when the browser page is being served

U="${2:-${NANBAN_USER:-nanbanlinux}}"
DISP=":7"; VPORT=5907
WPORT="${NANBAN_WEB_PORT:-6080}"
GEOM="${NANBAN_GEOM:-1600x900}"
WEB=/opt/nanban-desktop/web
LOG=/var/log/nanban-desktop.log

home_of() { getent passwd "$1" | cut -d: -f6; }

prep_web() {
  mkdir -p "$WEB"
  for f in core vendor app; do
    [ -e "/usr/share/novnc/$f" ] && ln -sfn "/usr/share/novnc/$f" "$WEB/$f"
  done
  # index.html (the Nanban page) is pushed by Nanban; fall back to plain noVNC
  [ -e "$WEB/index.html" ] || ln -sfn /usr/share/novnc/vnc.html "$WEB/index.html"
}

vnc_running() { pgrep -u "$U" -f "Xtigervnc.*$DISP" >/dev/null 2>&1 || pgrep -u "$U" -f "Xvnc.*$DISP" >/dev/null 2>&1; }
ws_running()  { pgrep -f "websockify.*:$WPORT" >/dev/null 2>&1; }

start_vnc() {
  local H; H="$(home_of "$U")"
  [ -n "$H" ] || { echo "no such user: $U"; exit 2; }
  # X socket dir must be writable by the user (WSLg sometimes makes it a root-only link)
  if [ -L /tmp/.X11-unix ] || [ ! -w /tmp/.X11-unix ]; then
    rm -rf /tmp/.X11-unix.nanban 2>/dev/null
    [ -L /tmp/.X11-unix ] && { cp -a "$(readlink -f /tmp/.X11-unix)" /tmp/.X11-unix.nanban 2>/dev/null; rm -f /tmp/.X11-unix; }
    mkdir -p /tmp/.X11-unix; chmod 1777 /tmp/.X11-unix
    [ -S /mnt/wslg/.X11-unix/X0 ] && ln -sfn /mnt/wslg/.X11-unix/X0 /tmp/.X11-unix/X0
  fi
  service dbus start >/dev/null 2>&1 || true
  usermod -aG video,render "$U" 2>/dev/null || true     # software GL for the compositor
  pkill -u "$U" -f "Xtigervnc.*$DISP" 2>/dev/null; sleep 0.3
  rm -f "/tmp/.X${DISP#:}-lock" "/tmp/.X11-unix/X${DISP#:}" 2>/dev/null
  # Run Xtigervnc directly (the perl 'vncserver' wrapper misdetects start-up under WSL).
  su - "$U" -s /bin/bash -c "
    umask 077
    mkdir -p ~/.vnc
    VP=\$(command -v tigervncpasswd || command -v vncpasswd || true)
    [ -n \"\$VP\" ] && printf 'nanban' | \$VP -f > ~/.vnc/passwd
    SEC='-SecurityTypes VncAuth -PasswordFile '\$HOME'/.vnc/passwd'
    if [ ! -s ~/.vnc/passwd ]; then
      echo 'nanban-desktop: no vncpasswd tool (apt install tigervnc-tools) - running without VNC password (localhost only)' >> $LOG
      SEC='-SecurityTypes None'
    fi
    cat > ~/.vnc/xstartup <<'XS'
#!/bin/sh
# WSLg leaks a Wayland display into every shell; XFCE must run on OUR X display.
unset SESSION_MANAGER DBUS_SESSION_BUS_ADDRESS WAYLAND_DISPLAY
export XDG_SESSION_TYPE=x11 XDG_CURRENT_DESKTOP=XFCE GDK_BACKEND=x11 QT_QPA_PLATFORM=xcb
export CLUTTER_BACKEND=x11 SDL_VIDEODRIVER=x11 MOZ_ENABLE_WAYLAND=0 LIBGL_ALWAYS_SOFTWARE=1
[ -r \$HOME/.Xresources ] && xrdb \$HOME/.Xresources
# push the X11 env into systemd --user / D-Bus activation, so D-Bus-started helpers
# (xfce4-notifyd, agents…) open on THIS display instead of WSLg's Wayland.
systemctl --user unset-environment WAYLAND_DISPLAY 2>/dev/null
dbus-update-activation-environment --systemd --all 2>/dev/null
exec dbus-launch --exit-with-session startxfce4
XS
    chmod +x ~/.vnc/xstartup
    # xfce4-notifyd is started by systemd --user (D-Bus activation); keep it off WSLg's Wayland
    mkdir -p ~/.config/systemd/user/xfce4-notifyd.service.d
    printf '[Service]
UnsetEnvironment=WAYLAND_DISPLAY
Environment=DISPLAY=$DISP GDK_BACKEND=x11
' > ~/.config/systemd/user/xfce4-notifyd.service.d/nanban.conf
    systemctl --user daemon-reload 2>/dev/null
    systemctl --user unset-environment WAYLAND_DISPLAY 2>/dev/null
    systemctl --user set-environment DISPLAY=$DISP GDK_BACKEND=x11 2>/dev/null
    # polish (wallpaper, left dock, no screen-lock) runs INSIDE the session via XFCE autostart,
    # so it talks to the session's own D-Bus / xfconfd / panel.
    mkdir -p ~/.config/autostart
    cat > ~/.config/autostart/nanban-xfce-tune.desktop <<'AS'
[Desktop Entry]
Type=Application
Name=Nanban desktop tune
Comment=Kali wallpaper, left dock and remote-desktop settings for the Nanban browser desktop
Exec=sh -c '/usr/local/bin/nanban-xfce-tune > \$HOME/.vnc/tune.log 2>&1'
OnlyShowIn=XFCE;
NoDisplay=true
X-GNOME-Autostart-enabled=true
AS
    touch ~/.Xauthority; xauth -q add $DISP . \$(mcookie) 2>/dev/null
    setsid nohup Xtigervnc $DISP -auth ~/.Xauthority -geometry $GEOM -depth 24 -rfbport $VPORT \
      -localhost \$SEC -AlwaysShared -desktop 'Kali Linux' >>$LOG 2>&1 < /dev/null &
    for i in \$(seq 1 40); do [ -S /tmp/.X11-unix/X${DISP#:} ] && break; sleep 0.25; done
    DISPLAY=$DISP XAUTHORITY=~/.Xauthority setsid nohup ~/.vnc/xstartup >>~/.vnc/session.log 2>&1 < /dev/null &
  "
}

start_ws() {
  prep_web
  setsid nohup websockify --web="$WEB" "0.0.0.0:$WPORT" "localhost:$VPORT" >>"$LOG" 2>&1 < /dev/null &
}

case "$1" in
  start)
    touch "$LOG"; chmod 666 "$LOG"
    vnc_running || start_vnc
    ws_running  || start_ws
    for _ in $(seq 1 40); do ws_running && vnc_running && break; sleep 0.25; done
    "$0" status "$U"
    ;;
  stop)
    pkill -f "websockify.*:$WPORT" 2>/dev/null
    su - "$U" -s /bin/bash -c "vncserver -kill $DISP" >/dev/null 2>&1
    pkill -u "$U" -f "Xtigervnc.*$DISP" 2>/dev/null
    echo "stopped"
    ;;
  status)
    v=down; w=down
    vnc_running && v=up
    ws_running  && w=up
    echo "vnc=$v web=$w port=$WPORT display=$DISP user=$U"
    [ "$v" = up ] && [ "$w" = up ]
    ;;
  ready)
    ws_running && vnc_running
    ;;
  *)
    echo "usage: nanban-desktop start|stop|status|ready [user]"; exit 1
    ;;
esac
