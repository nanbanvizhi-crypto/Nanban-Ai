"""
📱 Nanban Telegram bot — chat with Nanban from Telegram, from anywhere.

Setup (free, 2 min):
  1. In Telegram, message @BotFather -> /newbot -> follow it -> you get a TOKEN.
  2. Put the token in config.py:  TELEGRAM_TOKEN = "123456:ABC..."   (or env NANBAN_TELEGRAM_TOKEN)
  3. Run:  python telegram_bot.py      (or double-click start_telegram.bat)
  4. Open your bot in Telegram and start chatting. Each person gets their own memory.

The laptop must stay on while you use it (same as the app). WhatsApp isn't included because it
needs a paid provider (Meta Cloud API / Twilio); Telegram is free and instant.
"""

import os
import threading
import time

import requests

import config

_agents: dict[str, object] = {}
_running = False


def _token() -> str:
    return os.environ.get("NANBAN_TELEGRAM_TOKEN") or getattr(config, "TELEGRAM_TOKEN", "")


def _api() -> str:
    return f"https://api.telegram.org/bot{_token()}"


def configured() -> bool:
    return bool(_token())


def is_running() -> bool:
    return _running


def push(text: str, chat_id: str = "") -> bool:
    """Send a message. chat_id defaults to config.TELEGRAM_CHAT_ID (for scheduled pushes)."""
    chat_id = chat_id or os.environ.get("NANBAN_TELEGRAM_CHAT_ID") or getattr(config, "TELEGRAM_CHAT_ID", "")
    if not _token() or not chat_id:
        return False
    try:
        requests.post(f"{_api()}/sendMessage", json={"chat_id": chat_id, "text": text[:4000]}, timeout=15)
        return True
    except Exception:
        return False


def _reply(chat_id, text):
    try:
        requests.post(f"{_api()}/sendMessage", json={"chat_id": chat_id, "text": text[:4000]}, timeout=20)
    except Exception:
        pass


def start_background() -> bool:
    """Start the polling loop in a background thread (used by the in-app button)."""
    global _running
    if _running or not configured():
        return _running
    _running = True
    threading.Thread(target=main, daemon=True).start()
    return True


def _answer(user_key: str, message: str) -> str:
    from agent_core import Agent
    agent = _agents.get(user_key)
    if agent is None:
        agent = _agents[user_key] = Agent("assistant", user=f"tg:{user_key}")
    text = ""
    for ev in agent.stream(message):
        if ev.kind == "text":
            text += ev.data
        elif ev.kind == "error":
            text += f"\n⚠️ {ev.data}"
    return text or "(no reply)"


def main():
    if not _token():
        print("No Telegram token. Set TELEGRAM_TOKEN in config.py (from @BotFather) and run again.")
        return
    print("🤖 Nanban Telegram bot running. Message your bot in Telegram. Ctrl+C to stop.")
    offset = 0
    while True:
        try:
            r = requests.get(f"{_api()}/getUpdates", params={"timeout": 30, "offset": offset}, timeout=40)
            for upd in r.json().get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message") or {}
                chat_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "")
                if not chat_id or not text:
                    continue
                if text.strip() in ("/start", "/help"):
                    _reply(chat_id, "👋 Naan Nanban. Edhuvum kelunga — Tamil, English, Tanglish.")
                    continue
                _reply(chat_id, _answer(chat_id, text))
        except KeyboardInterrupt:
            print("\nStopped.")
            return
        except Exception:
            time.sleep(3)


if __name__ == "__main__":
    main()
