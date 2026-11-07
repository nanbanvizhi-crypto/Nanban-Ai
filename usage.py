"""
📊 Usage dashboard — which models/modes you've used, and how much.

Lightweight: appends one line per chat to data/usage.jsonl and renders a small summary of
totals, last-24h activity, and a breakdown by model and by mode. No tokens leave your machine.
"""

import json
import time
from collections import Counter
from pathlib import Path

import config

USAGE_FILE = config.DATA_DIR / "usage.jsonl"


def record(user: str, mode: str, model: str) -> None:
    try:
        with open(USAGE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.time(), "user": user or "local",
                                "mode": mode, "model": model}) + "\n")
    except Exception:
        pass


def _rows() -> list[dict]:
    try:
        return [json.loads(x) for x in Path(USAGE_FILE).read_text(encoding="utf-8").splitlines() if x.strip()]
    except Exception:
        return []


def _bars(counter: Counter, top: int = 6) -> str:
    if not counter:
        return "<div class='stor-item'><span class='stor-lbl'>—</span><span></span></div>"
    mx = max(counter.values())
    out = []
    for name, n in counter.most_common(top):
        pct = int(n / mx * 100)
        out.append(
            f'<div class="use-row"><span class="use-name">{name}</span>'
            f'<span class="use-track"><span class="use-fill" style="width:{pct}%"></span></span>'
            f'<span class="use-n">{n}</span></div>')
    return "".join(out)


def usage_html() -> str:
    rows = _rows()
    if not rows:
        return '<div class="stor-empty">No chats yet — your model/mode usage will appear here.</div>'
    total = len(rows)
    cut = time.time() - 86400
    today = sum(1 for r in rows if r.get("t", 0) > cut)
    by_model = Counter(r.get("model", "?") for r in rows)
    by_mode = Counter(r.get("mode", "?") for r in rows)
    return (
        '<div class="stor-wrap">'
        f'<div class="stor-drive"><div class="stor-drive-top"><span>💬 Total chats</span>'
        f'<span><b>{total}</b> all-time · {today} in last 24h</span></div></div>'
        '<div class="stor-grid">'
        f'<div class="stor-card"><div class="stor-head"><span class="stor-ico">🧠</span>'
        f'<span class="stor-name">By model</span></div><div class="stor-body">{_bars(by_model)}</div></div>'
        f'<div class="stor-card"><div class="stor-head"><span class="stor-ico">🎛️</span>'
        f'<span class="stor-name">By mode</span></div><div class="stor-body">{_bars(by_mode)}</div></div>'
        '</div></div>')
