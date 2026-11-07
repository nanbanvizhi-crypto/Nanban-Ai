"""
Nanban Server: the web app (with logins) + the API, on one port, meant to stay running.

    python server.py                     start (http://0.0.0.0:8000, API at /v1 and /api, docs at /docs)
    python server.py --install-autostart start automatically when you log in to Windows
    python server.py --remove-autostart
    python server.py --local             listen on 127.0.0.1 only

Who can use it:
  - Web app: everyone in config.USERS (each gets their own memory and to-do list). Admins see the Admin tab.
  - API: anyone with a key from config.API_KEYS (see api.py).
From outside your Wi-Fi, put Tailscale on both devices, or run a Cloudflare tunnel (see README).
"""

import logging
import os
import subprocess
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import gradio as gr
import uvicorn

import config

APP_DIR = Path(__file__).resolve().parent
os.chdir(APP_DIR)
LOG_FILE = config.DATA_DIR / "server.log"


def setup_logging() -> None:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    if sys.stdout and sys.stdout.isatty():
        root.addHandler(logging.StreamHandler())


def check_login(username: str, password: str) -> bool:
    return bool(config.USERS) and config.USERS.get(username) == password


def build():
    import api
    import app as webapp
    import ui_theme
    import web_computer

    web_computer.SERVER_MODE = True
    auth = check_login if config.USERS else None
    fastapi_app = api.app
    try:
        import whatsapp
        whatsapp.register(fastapi_app)            # 📲 WhatsApp Cloud API webhook (if configured)
    except Exception:
        pass
    gr.mount_gradio_app(
        fastapi_app, webapp.demo.queue(), path="/", auth=auth, pwa=True,
        auth_message=f"{config.AGENT_NAME} Server · login with the name and password your admin gave you" if auth else None,
        favicon_path=str(APP_DIR / "assets" / "nanban.png"), theme=ui_theme.theme(), css=webapp.CSS, footer_links=[],
    )
    return fastapi_app, web_computer.lan_ip()


def install_autostart() -> None:
    if os.name != "nt":
        print("Autostart install is for Windows. On Linux use a systemd service (see README).")
        return
    pythonw = APP_DIR / ".venv" / "Scripts" / "pythonw.exe"
    exe = pythonw if pythonw.exists() else Path(sys.executable)
    command = f'"{exe}" "{APP_DIR / "server.py"}"'
    result = subprocess.run(["schtasks", "/create", "/f", "/tn", "Nanban Server", "/sc", "onlogon",
                             "/tr", command, "/rl", "limited"], capture_output=True, text=True)
    print(result.stdout or result.stderr)
    print("Nanban Server will start every time you log in to Windows (no window). "
          "To make the laptop skip the login screen: run 'netplwiz' and untick 'Users must enter a user name and password'.")
    print("Start it now without logging out:  schtasks /run /tn \"Nanban Server\"")


def remove_autostart() -> None:
    result = subprocess.run(["schtasks", "/delete", "/f", "/tn", "Nanban Server"], capture_output=True, text=True)
    print(result.stdout or result.stderr)


def main() -> None:
    if "--install-autostart" in sys.argv:
        install_autostart()
        return
    if "--remove-autostart" in sys.argv:
        remove_autostart()
        return
    setup_logging()
    host = "127.0.0.1" if "--local" in sys.argv else "0.0.0.0"
    if host == "0.0.0.0" and not config.USERS:
        logging.warning("No USERS in config.py: the web app has no login, so it is only served on 127.0.0.1. "
                        "Add users to open it to your network.")
        host = "127.0.0.1"
    fastapi_app, ip = build()
    logging.info("Nanban Server starting on http://%s:%s", host, config.SERVER_PORT)
    print(f"\n🤖 {config.AGENT_NAME} Server")
    print(f"   Web app : http://127.0.0.1:{config.SERVER_PORT}" + (f"   ·   http://{ip}:{config.SERVER_PORT} (Wi-Fi)" if host == "0.0.0.0" else ""))
    print(f"   API     : http://{ip if host == '0.0.0.0' else '127.0.0.1'}:{config.SERVER_PORT}/v1   ·   docs: /docs")
    print(f"   Users   : {', '.join(config.USERS) or 'none (no login)'}   ·   API keys: {len(config.API_KEYS)}")
    print("   Stop    : Ctrl+C\n")
    uvicorn.run(fastapi_app, host=host, port=config.SERVER_PORT, log_level="info", access_log=False)


if __name__ == "__main__":
    main()
