"""
🗺️ Progress tracker — XP, badges, and a learning roadmap for the security studies.

Finishing guided labs and SOC scenarios earns XP. XP unlocks badges and moves you along a
roadmap (Foundations → Web → Network → Cloud → Blue Team → Advanced). Stored in data/progress.json.
"""

import json

import config

FILE = config.DATA_DIR / "progress.json"

BADGES = [
    (0, "🌱 Beginner", "Just started"),
    (50, "🔎 Recon Rookie", "First steps done"),
    (120, "⚔️ Lab Warrior", "Serious practice"),
    (220, "🛡️ Blue Belt", "Defender skills"),
    (350, "🥷 Pentest Pro", "Advanced"),
    (500, "🏆 Cyber Master", "Elite"),
]

ROADMAP = [
    ("🧱 Foundations", "Linux, networking, recon basics", 0),
    ("🌐 Web Security", "OWASP Top 10, SQLi, XSS", 60),
    ("🖧 Network & Exploitation", "scanning, Metasploit, services", 140),
    ("☁️ Cloud & Modern", "cloud, containers, mobile, AI", 240),
    ("🛡️ Blue Team", "detection, SOC, incident response", 340),
    ("🚀 Advanced / Future", "web3, OT, quantum, red+blue", 440),
]


def _load() -> dict:
    try:
        d = json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:
        d = {}
    d.setdefault("xp", 0)
    d.setdefault("labs", [])
    d.setdefault("soc", [])
    d.setdefault("domains", [])
    return d


def _save(d: dict) -> None:
    FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def award(kind: str, item_id: str, xp: int) -> str:
    """Record completion once; add XP. kind in {labs, soc, domains}."""
    d = _load()
    bucket = d.setdefault(kind, [])
    if item_id in bucket:
        return ""  # already counted
    bucket.append(item_id)
    d["xp"] = d.get("xp", 0) + int(xp)
    _save(d)
    return f"+{xp} XP! (total {d['xp']})"


def current_badge(xp: int) -> tuple[str, str]:
    b = BADGES[0]
    for threshold, name, desc in BADGES:
        if xp >= threshold:
            b = (threshold, name, desc)
    return b[1], b[2]


def next_badge(xp: int):
    for threshold, name, desc in BADGES:
        if xp < threshold:
            return threshold, name
    return None, None


def state() -> dict:
    d = _load()
    return {"xp": d["xp"], "labs": len(d["labs"]), "soc": len(d["soc"]),
            "domains": len(d["domains"])}


def roadmap_html() -> str:
    d = _load()
    xp = d["xp"]
    name, desc = current_badge(xp)
    nt, nn = next_badge(xp)
    nxt = (f'<div class="pg-next">Next badge: <b>{nn}</b> at {nt} XP '
           f'({nt-xp} to go)</div>' if nt else '<div class="pg-next">🏆 Max badge reached!</div>')

    cells = []
    for title, desc2, need in ROADMAP:
        done = xp >= need
        pct = min(100, int(xp / need * 100)) if need else 100
        state_cls = "pg-done" if done else ("pg-active" if xp >= need * 0.4 else "pg-locked")
        tick = "✅" if done else ("🔓" if state_cls == "pg-active" else "🔒")
        cells.append(
            f'<div class="pg-stage {state_cls}">'
            f'<div class="pg-stage-head">{tick} <b>{title}</b> <span class="pg-need">{need} XP</span></div>'
            f'<div class="pg-stage-desc">{desc2}</div></div>')

    return (
        '<div class="pg-wrap">'
        f'<div class="pg-hero"><div class="pg-xp">{xp}<span>XP</span></div>'
        f'<div class="pg-badge">{name}<div class="pg-badge-d">{desc}</div></div></div>'
        f'{nxt}'
        f'<div class="pg-stats">🎓 {len(d["labs"])} labs · 🛡️ {len(d["soc"])} SOC solved · '
        f'📚 {len(d["domains"])} domains</div>'
        f'<div class="pg-roadmap">{"".join(cells)}</div>'
        '<div class="pg-badgelist">' +
        "".join(f'<span class="pg-chip {"on" if xp>=t else "off"}">{n}</span>'
                for t, n, _ in BADGES) +
        '</div></div>')
