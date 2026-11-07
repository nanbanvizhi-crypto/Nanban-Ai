"""
Storage breakdown for Nanban's Admin tab.

Shows every installed piece — AI models (Ollama), Kali / WSL Linux, the Docker lab,
and Nanban's own folders — grouped into separate sections with their sizes, so you can
see exactly what is using disk and how to free space. Everything is best-effort and
degrades gracefully: a component that isn't installed is simply skipped.
"""

import os
import subprocess
import sys
from pathlib import Path

import config


# ---------------------------------------------------------------- helpers

def fmt(n: float) -> str:
    """Human-readable bytes."""
    n = float(n or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit in ("B", "KB") else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _dir_size(path) -> int:
    total = 0
    try:
        for root, _dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
    except OSError:
        pass
    return total


def _run(cmd, timeout=15):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout)
    except Exception:
        return None


# ---------------------------------------------------------------- data gatherers

def disk_overall() -> dict:
    try:
        import psutil
        d = psutil.disk_usage(str(Path.home().anchor or "/"))
        return {"used": d.used, "total": d.total, "free": d.free, "percent": d.percent}
    except Exception:
        return {}


def ollama_models() -> list[tuple[str, int]]:
    out = []
    try:
        import ollama
        for m in ollama.list().models:
            out.append((m.model, int(getattr(m, "size", 0) or 0)))
    except Exception:
        pass
    return sorted(out, key=lambda x: -x[1])


def app_breakdown() -> list[tuple[str, int]]:
    base = config.BASE_DIR
    candidates = [
        (".venv (Python environment)", base / ".venv"),
        ("data (memory, settings, index)", config.DATA_DIR),
        ("documents (your PDFs/notes)", config.DOCUMENTS_DIR),
        ("workspace (AI's files)", config.WORKSPACE_DIR),
        ("security pack (course + labs)", base / "security"),
    ]
    res = []
    for name, p in candidates:
        if Path(p).exists():
            res.append((name, _dir_size(p)))
    # everything else under the app folder = "app code"
    tracked = {str(Path(p)) for _n, p in candidates}
    code = 0
    try:
        for entry in os.scandir(base):
            if entry.is_file():
                try:
                    code += entry.stat().st_size
                except OSError:
                    pass
            elif entry.is_dir() and str(Path(entry.path)) not in tracked and entry.name != "__pycache__":
                code += _dir_size(entry.path)
    except OSError:
        pass
    if code:
        res.append(("app code & other files", code))
    return sorted(res, key=lambda x: -x[1])


def docker_usage() -> str | None:
    r = _run(["docker", "system", "df"])
    if r and r.returncode == 0:
        return r.stdout.decode("utf-8", errors="ignore").strip()
    return None


def wsl_breakdown() -> tuple[list[str], list[tuple[str, int]]]:
    """(distro names, [(label, bytes)] from the WSL virtual disks)."""
    if sys.platform != "win32":
        return [], []
    distros = []
    r = _run(["wsl", "-l", "-v"])
    if r and r.returncode == 0:
        text = r.stdout.decode("utf-16-le", errors="ignore")
        for line in text.splitlines()[1:]:
            parts = line.replace("*", "").split()
            if parts:
                distros.append(parts[0].strip())
    # find the ext4.vhdx virtual disks (WSL2 stores each distro's files in one)
    disks = []
    roots = []
    for env in ("LOCALAPPDATA",):
        v = os.environ.get(env)
        if v:
            roots.append(Path(v) / "Packages")
            roots.append(Path(v) / "wsl")
    for root in roots:
        if not root.exists():
            continue
        try:
            for vhdx in root.glob("**/*.vhdx"):
                try:
                    size = vhdx.stat().st_size
                except OSError:
                    continue
                label = vhdx.parent.parent.name if "Packages" in str(root) else vhdx.parent.name
                label = label.split("_")[0] or vhdx.stem
                disks.append((label, size))
        except OSError:
            pass
    return distros, sorted(disks, key=lambda x: -x[1])


# ---------------------------------------------------------------- render

def _rows_html(items) -> str:
    out = []
    for label, val in items:
        sz = fmt(val) if isinstance(val, (int, float)) else str(val)
        out.append(f'<div class="stor-item"><span class="stor-lbl">{label}</span>'
                   f'<span class="stor-val">{sz}</span></div>')
    return "".join(out)


def _card(icon: str, name: str, size_label: str, body_html: str, tip: str = "") -> str:
    size = f'<span class="stor-size">{size_label}</span>' if size_label else ""
    tiph = f'<div class="stor-tip">{tip}</div>' if tip else ""
    return (f'<div class="stor-card"><div class="stor-head"><span class="stor-ico">{icon}</span>'
            f'<span class="stor-name">{name}</span>{size}</div>'
            f'<div class="stor-body">{body_html}{tiph}</div></div>')


def storage_html() -> str:
    """Each installed component as its own folder-style card, in a grid."""
    cards = []

    d = disk_overall()
    drive = ""
    if d:
        pct = d.get("percent", 0)
        drive = (f'<div class="stor-drive"><div class="stor-drive-top">'
                 f'<span>💽 This drive</span><span><b>{fmt(d["free"])}</b> free of {fmt(d["total"])}</span></div>'
                 f'<div class="stor-bar"><div class="stor-bar-fill" style="width:{pct:.0f}%"></div></div>'
                 f'<div class="stor-drive-sub">{fmt(d["used"])} used · {pct:.0f}% full</div></div>')

    models = ollama_models()
    if models:
        total = sum(s for _n, s in models)
        cards.append(_card("🧠", "AI models — Ollama", fmt(total), _rows_html(models),
                           "Free space: <code>ollama rm &lt;name&gt;</code>"))

    distros, disks = wsl_breakdown()
    if distros or disks:
        total = sum(s for _n, s in disks)
        if disks:
            body = _rows_html([(f"{l} (virtual disk)", s) for l, s in disks])
        else:
            body = ('<div class="stor-item"><span class="stor-lbl">Installed: '
                    + ", ".join(distros) + "</span><span></span></div>")
        cards.append(_card("🐉", "Kali / WSL Linux", fmt(total) if total else "", body,
                           "Remove one: <code>wsl --unregister &lt;name&gt;</code>"))

    docker = docker_usage()
    if docker:
        body = '<pre class="stor-pre">' + docker.replace("<", "&lt;") + "</pre>"
        cards.append(_card("🐳", "Docker lab", "", body,
                           "Reclaim: <code>docker system prune -a</code>"))

    app = app_breakdown()
    if app:
        total = sum(s for _n, s in app)
        cards.append(_card("📦", "Nanban app", fmt(total), _rows_html(app)))

    if not cards:
        cards.append('<div class="stor-empty">No components detected yet. Install Ollama models, '
                     "Kali, or the Docker lab and refresh to see them here.</div>")

    return f'<div class="stor-wrap">{drive}<div class="stor-grid">{"".join(cards)}</div></div>'


def storage_markdown() -> str:
    lines = ["### 💾 Storage — what's installed & using disk", ""]

    d = disk_overall()
    if d:
        lines.append(f"**This drive:** {fmt(d['used'])} used of {fmt(d['total'])} "
                     f"({d['percent']:.0f}%) · **{fmt(d['free'])} free**")
        lines.append("")

    # 1) AI models
    models = ollama_models()
    if models:
        total = sum(s for _n, s in models)
        lines.append(f"#### 🧠 AI models — Ollama  ·  _{fmt(total)}_")
        for name, size in models:
            lines.append(f"- `{name}` — {fmt(size)}")
        lines.append("")
        lines.append("_Free space: remove one with_ `ollama rm <name>`.")
        lines.append("")

    # 2) Kali / WSL
    distros, disks = wsl_breakdown()
    if distros or disks:
        total = sum(s for _n, s in disks)
        head = f"#### 🐉 Kali / WSL Linux" + (f"  ·  _{fmt(total)}_" if total else "")
        lines.append(head)
        if disks:
            for label, size in disks:
                lines.append(f"- {label} (virtual disk) — {fmt(size)}")
        elif distros:
            lines.append("- Installed: " + ", ".join(f"`{x}`" for x in distros))
        lines.append("")
        lines.append("_These live in the WSL virtual disk. Remove one with_ `wsl --unregister <name>`.")
        lines.append("")

    # 3) Docker lab
    docker = docker_usage()
    if docker:
        lines.append("#### 🐳 Docker lab")
        lines.append("```\n" + docker + "\n```")
        lines.append("")
        lines.append("_Free space:_ `docker system prune -a` _(removes unused images)._")
        lines.append("")

    # 4) Nanban app
    app = app_breakdown()
    if app:
        total = sum(s for _n, s in app)
        lines.append(f"#### 📦 Nanban app  ·  _{fmt(total)}_")
        for name, size in app:
            lines.append(f"- {name} — {fmt(size)}")
        lines.append("")

    if len(lines) <= 3:
        lines.append("_No components detected yet. Install Ollama models, Kali, or the Docker lab "
                     "and refresh to see them here._")
    lines.append("\n_Each section is separate — big items are usually AI models and the WSL/Kali virtual disk._")
    return "\n".join(lines)
