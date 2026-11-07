"""
📲 Nanban on WhatsApp — official Meta WhatsApp Cloud API (free tier).

Nanban's server exposes a webhook; WhatsApp sends your messages to it, Nanban answers, and
replies back on WhatsApp. Each sender gets their own memory.

Setup is in WHATSAPP-SETUP.md. You need (all free): a Meta developer app with the WhatsApp
product, a test phone number, an access token and a phone-number id — and the webhook URL must be
public (use Admin → 🌍 Remote access to get a https link, or the cloud deploy).

config.py / env:
    WHATSAPP_TOKEN          (Bearer access token from Meta)
    WHATSAPP_PHONE_ID       (the phone number id)
    WHATSAPP_VERIFY_TOKEN   (any word you choose; put the same word in Meta's webhook setup)
"""

import os
import threading

import requests

import config

GRAPH = "https://graph.facebook.com/v21.0"
_agents: dict[str, object] = {}


def _tok() -> str:
    return os.environ.get("NANBAN_WHATSAPP_TOKEN") or getattr(config, "WHATSAPP_TOKEN", "")


def _phone_id() -> str:
    return os.environ.get("NANBAN_WHATSAPP_PHONE_ID") or getattr(config, "WHATSAPP_PHONE_ID", "")


def _verify_token() -> str:
    return os.environ.get("NANBAN_WHATSAPP_VERIFY_TOKEN") or getattr(config, "WHATSAPP_VERIFY_TOKEN", "nanban")


def configured() -> bool:
    return bool(_tok() and _phone_id())


def send(to: str, text: str) -> bool:
    if not configured():
        return False
    try:
        requests.post(
            f"{GRAPH}/{_phone_id()}/messages",
            headers={"Authorization": f"Bearer {_tok()}", "Content-Type": "application/json"},
            json={"messaging_product": "whatsapp", "to": to, "type": "text",
                  "text": {"body": (text or "")[:4000]}},
            timeout=20)
        return True
    except Exception:
        return False


def _answer(wa_id: str, message: str) -> str:
    from agent_core import Agent
    agent = _agents.get(wa_id)
    if agent is None:
        agent = _agents[wa_id] = Agent("assistant", user=f"wa:{wa_id}")
    text = ""
    for ev in agent.stream(message):
        if ev.kind == "text":
            text += ev.data
        elif ev.kind == "error":
            text += f"\n⚠️ {ev.data}"
    return text or "(no reply)"


def _handle(data: dict) -> None:
    try:
        for entry in data.get("entry", []):
            for ch in entry.get("changes", []):
                for msg in ch.get("value", {}).get("messages", []):
                    if msg.get("type") == "text":
                        frm = msg.get("from", "")
                        body = msg.get("text", {}).get("body", "")
                        if frm and body:
                            send(frm, _answer(frm, body))
    except Exception:
        pass


def register(app) -> None:
    """Add the WhatsApp webhook routes to the FastAPI app (called from server.build)."""
    from fastapi import Request
    from fastapi.responses import JSONResponse, PlainTextResponse

    @app.get("/whatsapp/webhook")
    async def whatsapp_verify(request: Request):          # Meta verification handshake
        p = request.query_params
        if p.get("hub.mode") == "subscribe" and p.get("hub.verify_token") == _verify_token():
            return PlainTextResponse(p.get("hub.challenge", ""))
        return PlainTextResponse("forbidden", status_code=403)

    @app.post("/whatsapp/webhook")
    async def whatsapp_incoming(request: Request):        # incoming messages
        try:
            data = await request.json()
        except Exception:
            data = {}
        threading.Thread(target=_handle, args=(data,), daemon=True).start()
        return JSONResponse({"status": "ok"})             # ack fast; answer in the background
