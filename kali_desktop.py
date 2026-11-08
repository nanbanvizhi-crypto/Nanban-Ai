"""
🖥️ Kali Desktop — the REAL Kali Linux XFCE desktop, full-page in the browser.

How it works (nothing is imitated — it is the actual Kali OS running in WSL):
  • Inside the Kali WSL distro: TigerVNC runs a real XFCE desktop session (display :7),
    websockify + noVNC serve it as a web page on port 6080.
  • Nanban installs/updates the small helper script + web page in Kali, starts them,
    waits until the page answers, and opens it in a new browser tab.

Public API
  installed()         -> bool      XFCE + noVNC present in Kali?
  start()             -> (ok, msg) start (idempotent) and wait until ready
  url()               -> str       the full-page desktop URL
  install_cmd()       -> str       apt command to install the desktop pieces
"""

import os
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

import config

DISTRO = "kali-linux"
WEB_PORT = 6080
ASSETS = Path(config.BASE_DIR) / "assets" / "kali_desktop"
IS_WIN = os.name == "nt"
_FLAGS = subprocess.CREATE_NO_WINDOW if IS_WIN else 0
_LOCK = threading.Lock()
_hold_proc = None
_installed_cache = {"t": 0.0, "v": None}

INSTALL_PKGS = ("kali-desktop-xfce tigervnc-standalone-server tigervnc-common tigervnc-tools novnc websockify "
                "dbus-x11 xfce4-terminal thunar mousepad htop firefox-esr "
                "fonts-dejavu-core fonts-noto-core fonts-noto-mono fonts-firacode fonts-noto-color-emoji")


def install_cmd() -> str:
    return f"sudo apt update && sudo apt install -y --no-install-recommends {INSTALL_PKGS}"


def _kali_user() -> str:
    try:
        import kali_panel
        return kali_panel._known_kali_user() or "nanbanlinux"
    except Exception:
        return "nanbanlinux"


def _wsl(cmd: str, user: str = "root", timeout: int = 60, stdin: bytes | None = None) -> tuple[int, str]:
    """Run one bash command inside Kali. Returns (exit code, combined output)."""
    try:
        p = subprocess.run(["wsl.exe", "-d", DISTRO, "-u", user, "--", "bash", "-c", cmd],
                           input=stdin, capture_output=True, timeout=timeout, creationflags=_FLAGS)
        out = (p.stdout or b"").decode("utf-8", "replace") + (p.stderr or b"").decode("utf-8", "replace")
        return p.returncode, out.replace("\x00", "").strip()
    except FileNotFoundError:
        return 127, "wsl.exe not found"
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except Exception as e:  # pragma: no cover
        return 1, str(e)


def available() -> bool:
    """Is this a Windows PC with the Kali WSL distro?"""
    if not IS_WIN:
        return False
    try:
        out = subprocess.run(["wsl.exe", "-l", "-q"], capture_output=True, timeout=15, creationflags=_FLAGS)
        return DISTRO in out.stdout.decode("utf-16-le", "ignore").replace("\x00", "").lower()
    except Exception:
        return False


def installed(fresh: bool = False) -> bool:
    """XFCE desktop + VNC + noVNC present inside Kali? (cached 60s)"""
    now = time.time()
    if not fresh and _installed_cache["v"] is not None and now - _installed_cache["t"] < 60:
        return _installed_cache["v"]
    code, out = _wsl("test -x /usr/bin/startxfce4 -a -e /usr/share/novnc/core/rfb.js "
                     "-a -x /usr/bin/websockify -a -x /usr/bin/Xtigervnc && echo OK", timeout=30)
    v = out.strip().endswith("OK")
    _installed_cache.update(t=now, v=v)
    return v


def _hold_kali_alive() -> None:
    """WSL stops an idle distro after a few seconds — keep one process in it for the app's lifetime."""
    global _hold_proc
    if _hold_proc is not None and _hold_proc.poll() is None:
        return
    try:
        _hold_proc = subprocess.Popen(
            ["wsl.exe", "-d", DISTRO, "-u", "root", "--", "sh", "-c",
             "service ssh start >/dev/null 2>&1; exec sleep infinity"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_FLAGS)
    except Exception:
        _hold_proc = None


def _push_files() -> str:
    """Install/refresh the helper script + web page inside Kali (always LF, root-owned)."""
    script = (ASSETS / "nanban-desktop.sh").read_bytes().replace(b"\r\n", b"\n")
    tune = (ASSETS / "nanban-xfce-tune.sh").read_bytes().replace(b"\r\n", b"\n")
    page = (ASSETS / "index.html").read_bytes().replace(b"\r\n", b"\n")
    code, out = _wsl("cat > /usr/local/bin/nanban-desktop && chmod 755 /usr/local/bin/nanban-desktop", stdin=script)
    if code != 0:
        return f"could not install helper script: {out}"
    code, out = _wsl("cat > /usr/local/bin/nanban-xfce-tune && chmod 755 /usr/local/bin/nanban-xfce-tune", stdin=tune)
    if code != 0:
        return f"could not install desktop tune script: {out}"
    code, out = _wsl("mkdir -p /opt/nanban-desktop/web && cat > /opt/nanban-desktop/web/index.html", stdin=page)
    if code != 0:
        return f"could not install web page: {out}"
    return ""


def url(back: str = "") -> str:
    u = f"http://127.0.0.1:{WEB_PORT}/"
    if back:
        from urllib.parse import quote
        u += f"?back={quote(back, safe='')}"
    return u


def _page_up(timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{WEB_PORT}/", timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def ready() -> bool:
    """Web page served AND the real desktop (X server) is up."""
    if not _page_up():
        return False
    code, _ = _wsl(f"/usr/local/bin/nanban-desktop ready {_kali_user()}", timeout=20)
    return code == 0


def status() -> str:
    code, out = _wsl(f"/usr/local/bin/nanban-desktop status {_kali_user()} 2>/dev/null || echo 'not started'", timeout=30)
    return out


def start(wait: float = 45.0) -> tuple[bool, str]:
    """Start the real Kali desktop (idempotent) and wait until the page is served."""
    with _LOCK:
        if not available():
            return False, "Kali (WSL) is not installed on this PC. Install it from the 🛡️ Security tab first."
        _hold_kali_alive()
        if ready():
            return True, "Kali desktop is running."
        if not installed(fresh=True):
            return False, ("Kali desktop pieces are not installed yet. Run this once inside Kali:\n\n"
                           f"`{install_cmd()}`")
        err = _push_files()
        if err:
            return False, err
        code, out = _wsl(f"/usr/local/bin/nanban-desktop start {_kali_user()}", timeout=90)
        t0 = time.time()
        while time.time() - t0 < wait:
            if ready():
                return True, "Kali desktop started."
            time.sleep(0.7)
        return False, f"Desktop did not come up in time.\n\n{out}\n\nLog: /var/log/nanban-desktop.log (inside Kali)"


def stop() -> str:
    code, out = _wsl(f"/usr/local/bin/nanban-desktop stop {_kali_user()}", timeout=30)
    return out or "stopped"


# ---------------------------------------------------------------- full arsenal (detached)

ARSENAL_LOG = "/var/log/nanban-arsenal.log"


def arsenal_running() -> bool:
    code, _ = _wsl("pgrep -f '^/bin/bash /usr/local/bin/nanban-arsenal' >/dev/null", timeout=20)
    return code == 0


def arsenal_start() -> tuple[bool, str]:
    """Install the official Kali arsenal metapackages, detached inside Kali (survives closing the tab)."""
    if not available():
        return False, "Kali (WSL) is not installed on this PC."
    _hold_kali_alive()
    if arsenal_running():
        return True, "already running"
    script = (ASSETS / "nanban-arsenal.sh").read_bytes().replace(b"\r\n", b"\n")
    code, out = _wsl("cat > /usr/local/bin/nanban-arsenal && chmod 755 /usr/local/bin/nanban-arsenal", stdin=script)
    if code != 0:
        return False, f"could not install arsenal script: {out}"
    code, out = _wsl(f": > {ARSENAL_LOG}; chmod 644 {ARSENAL_LOG}; "
                     f"(setsid nohup /usr/local/bin/nanban-arsenal {_kali_user()} >> {ARSENAL_LOG} 2>&1 < /dev/null &); "
                     "sleep 1; echo started", timeout=30)
    return (code == 0), out


def arsenal_log(lines: int = 40) -> str:
    code, out = _wsl(f"tail -n {lines} {ARSENAL_LOG} 2>/dev/null", timeout=20)
    return out


def arsenal_done() -> bool:
    code, _ = _wsl(f"grep -q '^=== DONE' {ARSENAL_LOG} 2>/dev/null", timeout=20)
    return code == 0


def start_background() -> None:
    """Warm the desktop up without blocking (used at app start)."""
    threading.Thread(target=lambda: start(wait=60), daemon=True).start()


if __name__ == "__main__":
    print("available:", available())
    print("installed:", installed(fresh=True))
    ok, msg = start()
    print(ok, msg)
    print("url:", url())
