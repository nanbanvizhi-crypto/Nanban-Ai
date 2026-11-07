"""
Nanban — single-click launcher. One run brings up EVERYTHING:

    • the practice lab (Docker)      — if AUTOSTART_LAB is on and Docker is available
    • the Nanban server              — web app + API on one port
    • your browser                   — opened to the app once it's ready
    • Kali                           — auto-connected if a 'kali' server is registered

Double-click Nanban.bat (or the Desktop "Nanban" shortcut) and wait a few seconds.
Nothing else to click. Close this window to stop everything.
"""

import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
os.chdir(APP_DIR)
sys.path.insert(0, str(APP_DIR))

import config  # noqa: E402

IS_WINDOWS = os.name == "nt"
LAB_DIR = APP_DIR / "security" / "lab"


# ---------------------------------------------------------------- helpers

def line(msg: str) -> None:
    print(msg, flush=True)


def lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def port() -> int:
    # Server mode uses SERVER_PORT; plain local mode uses WEB_PORT.
    return config.SERVER_PORT if (config.USERS or _server_mode()) else config.WEB_PORT


def _server_mode() -> bool:
    # Full server (multi-user + API) when logins or API keys are configured.
    return bool(config.USERS) or bool(config.API_KEYS)


def wait_for_port(p: int, timeout: float = 90) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            with socket.create_connection(("127.0.0.1", p), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def _port_busy(p: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", p), timeout=0.6):
            return True
    except OSError:
        return False


def _pids_on_port(p: int) -> set:
    """PIDs LISTENING on port p (best-effort, per OS)."""
    pids = set()
    try:
        if IS_WINDOWS:
            out = subprocess.run(["netstat", "-ano", "-p", "tcp"],
                                 capture_output=True, text=True, timeout=10).stdout
            for ln in out.splitlines():
                if f":{p} " in ln and "LISTEN" in ln.upper():
                    pids.add(ln.split()[-1])
        else:
            out = subprocess.run(["lsof", "-ti", f"tcp:{p}", "-sTCP:LISTEN"],
                                 capture_output=True, text=True, timeout=10).stdout
            pids.update(x.strip() for x in out.split() if x.strip())
    except Exception:
        pass
    return pids


def _is_python(pid: str) -> bool:
    try:
        if IS_WINDOWS:
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, timeout=10).stdout
        else:
            out = subprocess.run(["ps", "-p", str(pid), "-o", "comm="],
                                 capture_output=True, text=True, timeout=10).stdout
        return "python" in out.lower()
    except Exception:
        return False


def _kill(pid: str) -> None:
    try:
        if IS_WINDOWS:
            subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"],
                           capture_output=True, timeout=10)
        else:
            os.kill(int(pid), 15)
    except Exception:
        pass


def free_stale_instance(p: int) -> None:
    """A previous Nanban still holding the port means a re-launch would serve the OLD
    code (or fail to bind). Stop that stale instance so THIS launch — with the latest
    code — takes over. Only ever targets a python process listening on our own port."""
    if not _port_busy(p):
        return
    line(f"   • Previous Nanban still running on port {p} — replacing it with the latest version…")
    me = os.getpid()
    for pid in _pids_on_port(p):
        if pid and pid.isdigit() and int(pid) != me and _is_python(pid):
            _kill(pid)
    for _ in range(24):          # wait up to ~12s for the port to release
        if not _port_busy(p):
            return
        time.sleep(0.5)
    line(f"   • Port {p} is still busy. Close any other Nanban window, then run this again.")


# ---------------------------------------------------------------- the pieces

def start_lab_background() -> None:
    """Start the Docker lab without blocking. Safe if Docker isn't installed."""
    if not getattr(config, "AUTOSTART_LAB", False):
        return
    import shutil
    docker = shutil.which("docker")
    if not docker:
        line("   • Lab: skipped (Docker not installed — install Docker Desktop to use the practice lab)")
        return

    def run():
        try:
            flags = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
            check = subprocess.run([docker, "info"], capture_output=True, timeout=20, creationflags=flags)
            if check.returncode != 0:
                line("   • Lab: skipped (Docker Desktop isn't running)")
                return
            line("   • Lab: starting practice targets in the background (first run downloads images)…")
            subprocess.run([docker, "compose", "up", "-d"], cwd=LAB_DIR, capture_output=True,
                           timeout=1800, creationflags=flags)
            line("   • Lab: ready → DVWA :8080 · Juice Shop :3000 · WebGoat :8081")
        except Exception as e:
            line(f"   • Lab: could not start ({e}). You can start it later from the Security tab.")

    threading.Thread(target=run, daemon=True).start()


def connect_kali_background() -> None:
    """If a 'kali' server is registered, warm the connection so the Terminal is ready."""
    try:
        import servers
        if "kali" not in servers.names():
            return

        def run():
            try:
                servers.connect("kali")
                line("   • Kali: connected and ready (use it in the Terminal tab)")
            except Exception:
                line("   • Kali: registered but not reachable yet (start SSH in Kali: sudo service ssh start)")

        threading.Thread(target=run, daemon=True).start()
    except Exception:
        pass


def open_browser_when_ready(p: int) -> None:
    def run():
        if wait_for_port(p, 90) and getattr(config, "OPEN_BROWSER_ON_START", True):
            webbrowser.open(f"http://127.0.0.1:{p}")
    threading.Thread(target=run, daemon=True).start()


# ---------------------------------------------------------------- main

def main() -> None:
    p = port()
    line("")
    line("  ╔══════════════════════════════════════════╗")
    line(f"  ║   🤖 {config.AGENT_NAME} — starting everything        ║")
    line("  ╚══════════════════════════════════════════╝")
    line("")

    # 0. If an older Nanban is still holding the port, replace it so this run serves
    #    the latest code (otherwise the browser keeps showing the old version).
    free_stale_instance(p)

    # 1. Lab + Kali, in the background (never block the app coming up)
    start_lab_background()
    connect_kali_background()

    # 2. Browser opens itself once the server answers
    open_browser_when_ready(p)

    # 3. The server (this blocks and keeps everything alive)
    line(f"   • App:  http://127.0.0.1:{p}" + (f"   ·   http://{lan_ip()}:{p} (Wi-Fi)" if _server_mode() else ""))
    if _server_mode():
        line(f"   • API:  http://127.0.0.1:{p}/v1   ·   docs /docs")
    line("")
    line("   Everything is coming up. Your browser will open automatically.")
    line("   Keep this window open. Close it to stop Nanban.")
    line("")

    if _server_mode():
        import server
        server.main()                       # web app + API (multi-user)
    else:
        import app                           # plain local web app
        import ui_theme
        try:
            app._ensure_ai_ready()           # wake the local AI engine so every tab's AI works
        except Exception:
            pass
        app.demo.queue().launch(
            inbrowser=False, server_name="127.0.0.1", server_port=p,
            theme=ui_theme.theme(), css=app.CSS, footer_links=[], pwa=True,
            favicon_path=str(APP_DIR / "assets" / "nanban.png"),
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        line("\n   Nanban stopped. Bye! 👋")
