"""
Nanban desktop launcher: a system-tray app (bottom-right, near the clock).

It starts the chat server in the background and gives you a menu:
Open chat · Open AI terminal · Phone access (QR) · VPN status · Quit.

Run it with  pythonw launcher.py  (no black window), or build Nanban.exe with build_app.bat.
"""

import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

# When frozen into Nanban.exe the app folder is where the exe lives; otherwise this file's folder.
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
os.chdir(APP_DIR)
sys.path.insert(0, str(APP_DIR))

import config  # noqa: E402
import vpn  # noqa: E402

IS_WINDOWS = os.name == "nt"
VENV_PY = APP_DIR / ".venv" / "Scripts" / ("pythonw.exe" if IS_WINDOWS else "python")
VENV_PY_CONSOLE = APP_DIR / ".venv" / "Scripts" / "python.exe"
if not VENV_PY.exists():
    VENV_PY = Path(sys.executable)
    VENV_PY_CONSOLE = Path(sys.executable)

server: subprocess.Popen | None = None


def lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def local_url() -> str:
    return f"http://127.0.0.1:{config.WEB_PORT}"


def phone_url() -> str:
    return f"http://{lan_ip()}:{config.WEB_PORT}"


def server_ready() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", config.WEB_PORT), timeout=0.5):
            return True
    except OSError:
        return False


def start_server() -> None:
    global server
    if server_ready():
        return
    flags = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
    server = subprocess.Popen([str(VENV_PY), str(APP_DIR / "app.py"), "--no-browser"],
                              cwd=APP_DIR, creationflags=flags)


def stop_server() -> None:
    global server
    if server and server.poll() is None:
        server.terminate()
        try:
            server.wait(5)
        except subprocess.TimeoutExpired:
            server.kill()
    server = None


def open_chat(*_) -> None:
    start_server()
    for _ in range(60):
        if server_ready():
            break
        time.sleep(0.5)
    webbrowser.open(local_url())


def open_terminal(*_) -> None:
    script = str(APP_DIR / "terminal.py")
    home = str(Path.home())
    if IS_WINDOWS:
        import shutil
        if shutil.which("wt"):   # Windows Terminal looks best
            subprocess.Popen(["wt", "-d", home, str(VENV_PY_CONSOLE), script])
        else:
            subprocess.Popen(["cmd", "/c", "start", "Nanban Terminal", str(VENV_PY_CONSOLE), script], cwd=home)
    else:
        subprocess.Popen(["x-terminal-emulator", "-e", str(VENV_PY_CONSOLE), script])


def show_phone_qr(*_) -> None:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont

    url = phone_url()
    path = APP_DIR / "data" / "phone_qr.png"
    path.parent.mkdir(exist_ok=True)
    canvas = qrcode.make(url).convert("RGB")
    out = Image.new("RGB", (canvas.width, canvas.height + 70), "white")
    out.paste(canvas, (0, 0))
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    note = url if config.LAN_ACCESS else "Set LAN_ACCESS = True in config.py first"
    draw.text((15, canvas.height + 10), note, fill="black", font=font)
    draw.text((15, canvas.height + 38), "Same Wi-Fi · login: nanban", fill="gray", font=font)
    out.save(path)
    if IS_WINDOWS:
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        webbrowser.open(path.as_uri())


def open_folder(*_) -> None:
    if IS_WINDOWS:
        os.startfile(APP_DIR)  # type: ignore[attr-defined]
    else:
        webbrowser.open(APP_DIR.as_uri())


def quit_app(icon, *_) -> None:
    stop_server()
    icon.stop()


def main() -> None:
    import pystray
    from PIL import Image

    image = Image.open(APP_DIR / "assets" / "nanban.png")

    def vpn_label(_item):
        return vpn.badge()

    def lan_label(_item):
        return f"Phone access: {'ON · ' + phone_url() if config.LAN_ACCESS else 'off (see config.py)'}"

    menu = pystray.Menu(
        pystray.MenuItem("💬 Open chat", open_chat, default=True),
        pystray.MenuItem("💻 Open AI terminal", open_terminal),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("📱 Phone: show QR code", show_phone_qr),
        pystray.MenuItem(lan_label, None, enabled=False),
        pystray.MenuItem(vpn_label, None, enabled=False),
        pystray.MenuItem("🌍 Check public IP (VPN test)", lambda *_: webbrowser.open("https://ipinfo.io/json")),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("📂 Open Nanban folder", open_folder),
        pystray.MenuItem("✖ Quit Nanban", quit_app),
    )
    icon = pystray.Icon("Nanban", image, f"{config.AGENT_NAME} · local AI", menu)

    def boot():
        # start the practice lab too (if enabled + Docker present), same as the one-click launcher
        try:
            import run_nanban
            run_nanban.start_lab_background()
        except Exception:
            pass
        start_server()
        for _ in range(60):
            if server_ready():
                break
            time.sleep(0.5)
        icon.notify("Nanban is running. Click the tray icon to open the chat.", "Nanban")
        if "--open" in sys.argv:
            webbrowser.open(local_url())

    threading.Thread(target=boot, daemon=True).start()
    icon.run()


if __name__ == "__main__":
    main()
