"""
Chat history — every conversation is saved to disk and kept for one week, so you can close
the app, reboot, and pick any chat up again from the sidebar (like ChatGPT / Claude).

  data/chats/<user>/<chat_id>.json   {id, title, mode, created, updated, display}

`display` is the list of chat-bubble dicts the UI shows. The agent's working history is rebuilt
from it on load (plain user/assistant turns only — tool scratch-work is not replayed).
Also gives the AI a light "memory of the week": recent topics for the system prompt and a
keyword search over past chats (the `search_past_chats` tool).
"""

import html
import json
import re
import secrets
import time
from pathlib import Path

import config

KEEP_DAYS = 7
DIR = config.DATA_DIR / "chats"
_ID_RE = re.compile(r"^[0-9A-Za-z\-]{6,40}$")
_IMG_MARK = "  🖼️ _(image attached)_"


def _udir(user: str = "") -> Path:
    name = re.sub(r"[^0-9A-Za-z_\-]", "_", user or "local")[:40] or "local"
    d = DIR / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def _path(user: str, chat_id: str) -> Path | None:
    return (_udir(user) / f"{chat_id}.json") if _ID_RE.match(chat_id or "") else None


def _plain(m: dict) -> bool:
    """A real conversation turn (not a tool-call card)."""
    return m.get("role") in ("user", "assistant") and not m.get("metadata") and str(m.get("content", "")).strip()


def new_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(2)


def save(user: str, chat_id: str, mode: str, display: list) -> str:
    """Create/update a chat. Returns its id ('' if there is nothing worth saving yet)."""
    display = [m for m in (display or []) if isinstance(m, dict)]
    first_user = next((m for m in display if m.get("role") == "user" and str(m.get("content", "")).strip()), None)
    if not first_user:
        return chat_id or ""
    chat_id = chat_id if _ID_RE.match(chat_id or "") else new_id()
    path = _path(user, chat_id)
    created = time.time()
    try:
        created = json.loads(path.read_text(encoding="utf-8")).get("created", created)
    except Exception:
        pass
    title = " ".join(str(first_user["content"]).replace(_IMG_MARK, "").split())[:60] or "New chat"
    data = {"id": chat_id, "title": title, "mode": mode, "created": created, "updated": time.time(),
            "display": display}
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
    except Exception:
        return chat_id
    return chat_id


def load(user: str, chat_id: str) -> dict | None:
    path = _path(user, chat_id)
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path else None
    except Exception:
        return None


def delete(user: str, chat_id: str) -> None:
    path = _path(user, chat_id)
    try:
        if path:
            path.unlink(missing_ok=True)
    except Exception:
        pass


def list_chats(user: str = "") -> list[dict]:
    """This week's chats, newest first. Anything older than KEEP_DAYS is removed."""
    cutoff = time.time() - KEEP_DAYS * 86400
    out = []
    for f in _udir(user).glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            if d.get("updated", 0) < cutoff:
                f.unlink(missing_ok=True)
                continue
            out.append({"id": d["id"], "title": d.get("title", "Chat"), "mode": d.get("mode", ""),
                        "updated": d.get("updated", 0)})
        except Exception:
            continue
    return sorted(out, key=lambda x: x["updated"], reverse=True)


def to_agent_history(display: list, limit: int = 30) -> list[dict]:
    """Rebuild the model's conversation memory from saved bubbles."""
    turns = [{"role": m["role"], "content": str(m["content"]).replace(_IMG_MARK, "")}
             for m in (display or []) if isinstance(m, dict) and _plain(m)]
    turns = turns[-limit:]
    while turns and turns[0]["role"] != "user":
        turns = turns[1:]
    return turns


# ---------------------------------------------------------------- sidebar list

def _when(ts: float) -> str:
    now = time.localtime()
    t = time.localtime(ts)
    days = (time.mktime((now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, -1))
            - time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, -1))) / 86400
    if days < 1:
        return "Today"
    if days < 2:
        return "Yesterday"
    return "Earlier this week"


def sidebar_html(user: str = "", active_id: str = "") -> str:
    chats = list_chats(user)
    if not chats:
        return ("<div id='nb-hist'><div class='nbh-empty'>No chats yet — your conversations are kept here "
                "for 7 days.</div></div>")
    parts, group = ["<div id='nb-hist'>"], None
    for c in chats[:60]:
        g = _when(c["updated"])
        if g != group:
            group = g
            parts.append(f"<div class='nbh-group'>{g}</div>")
        cls = "nbh-item active" if c["id"] == active_id else "nbh-item"
        parts.append(
            f"<div class='{cls}' data-chat='{c['id']}' title='{html.escape(c['title'], quote=True)}'>"
            f"<span class='nbh-title'>{html.escape(c['title'])}</span>"
            f"<span class='nbh-del' data-del='{c['id']}' title='Delete this chat'>✕</span></div>")
    parts.append("</div>")
    return "".join(parts)


# ---------------------------------------------------------------- memory of the week

_topics_cache: dict = {}


def recent_topics(user: str = "", n: int = 8, exclude: str = "") -> list[str]:
    """Titles of this week's other chats (cached 30s) — a cheap continuity hint for the model."""
    key = (user, exclude)
    hit = _topics_cache.get(key)
    if hit and time.time() - hit[0] < 30:
        return hit[1]
    titles = [c["title"] for c in list_chats(user) if c["id"] != exclude][:n]
    _topics_cache[key] = (time.time(), titles)
    return titles


def search(user: str, query: str, limit: int = 5) -> str:
    """Keyword search over this week's chats → short snippets with dates."""
    words = [w for w in re.findall(r"\w+", (query or "").lower()) if len(w) > 2]
    if not words:
        return "Give a few keywords to search past chats."
    hits = []
    for c in list_chats(user):
        d = load(user, c["id"]) or {}
        for m in d.get("display", []):
            if not (isinstance(m, dict) and _plain(m)):
                continue
            text = str(m["content"])
            low = text.lower()
            score = sum(low.count(w) for w in words)
            if score:
                i = max(0, min((low.find(w) for w in words if w in low), default=0) - 80)
                hits.append((score, c["updated"], c["title"], m["role"], " ".join(text[i:i + 320].split())))
    if not hits:
        return "Nothing about that in this week's chats."
    hits.sort(key=lambda h: (h[0], h[1]), reverse=True)
    return "\n\n".join(f"[{time.strftime('%a %d %b', time.localtime(ts))} · chat: {title}] {role}: {snip}"
                       for _, ts, title, role, snip in hits[:limit])
