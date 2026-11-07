"""
🩺 Nanban self-repair ("doctor").

Checks Nanban for the common problems and AUTO-FIXES the safe ones, so the app can heal
itself. Used two ways:
  • Admin tab → "🩺 Self-check & auto-fix" button
  • the AI tool `self_check` — when the user says "Nanban is broken / slow / not working",
    the agent runs this and reports what it fixed.

Safe auto-fixes (done without asking): create missing folders, reset a corrupt settings.json
(backed up first), (re)install missing Python packages, pull a missing local model, switch a
hosted model that your key can't use to one it can, and wake Ollama. Anything risky (deleting
files, freeing disk, killing ports) is only *reported* with clear instructions — never done
automatically.
"""

import json
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import config

_ICON = {"ok": "✅", "fixed": "🛠️", "warn": "⚠️", "fail": "❌"}


def _bg(fn):
    threading.Thread(target=fn, daemon=True).start()


# ---------------------------------------------------------------- individual checks

def _check_folders():
    made = []
    for p in (config.WORKSPACE_DIR, config.DOCUMENTS_DIR, config.DATA_DIR):
        if not Path(p).exists():
            try:
                Path(p).mkdir(parents=True, exist_ok=True)
                made.append(Path(p).name)
            except Exception:
                pass
    if made:
        return ("Folders", "fixed", f"Created missing folders: {', '.join(made)}.")
    return ("Folders", "ok", "workspace / documents / data folders present.")


def _check_writable():
    try:
        t = config.DATA_DIR / ".write_test"
        t.write_text("ok", encoding="utf-8")
        t.unlink()
        return ("Permissions", "ok", "Data folder is writable.")
    except Exception as e:
        return ("Permissions", "fail",
                f"Can't write to the data folder ({e}). Move Nanban to a folder you own "
                f"(e.g. Documents), not Program Files, and run again.")


def _check_settings():
    f = config.DATA_DIR / "settings.json"
    if not f.exists():
        return ("Settings file", "ok", "Using defaults (no custom settings).")
    try:
        json.loads(f.read_text(encoding="utf-8"))
        return ("Settings file", "ok", "settings.json is valid.")
    except Exception:
        try:
            bak = f.with_name("settings.json.bak")
            shutil.copy(f, bak)
            f.unlink()
            return ("Settings file", "fixed",
                    f"settings.json was corrupt — backed it up to {bak.name} and reset to defaults.")
        except Exception as e:
            return ("Settings file", "fail", f"settings.json is corrupt and couldn't be reset: {e}")


def _check_deps():
    missing = []
    for mod in ("gradio", "fastapi", "uvicorn", "paramiko", "psutil", "openai"):
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)
    if not missing:
        return ("Dependencies", "ok", "All required Python packages are installed.")

    def job():
        pip = [sys.executable, "-m", "pip", "install", "-q", "-r", str(config.BASE_DIR / "requirements.txt")]
        try:
            subprocess.run(pip, cwd=config.BASE_DIR, capture_output=True, timeout=900)
        except Exception:
            pass

    _bg(job)
    return ("Dependencies", "fixed",
            f"Missing packages ({', '.join(missing)}) — installing them now in the background. "
            f"Restart Nanban after a minute.")


def _try_start_ollama():
    try:
        if sys.platform == "win32":
            subprocess.Popen("start \"\" ollama app", shell=True)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def _check_ai():
    import llm
    if llm.backend() == "hosted":
        ok, desc = llm.ping()
        if ok:
            return ("AI engine", "ok", f"Cloud AI reachable — {desc}.")
        # try to self-heal a bad model id
        try:
            avail = llm.list_models()
            if avail and config.HOSTED_MODEL not in avail:
                new = llm.pick_available_model()
                import settings
                settings.save({"HOSTED_MODEL": new})
                return ("AI engine", "fixed",
                        f"The model '{config.HOSTED_MODEL}' isn't on your key — switched to '{new}'.")
        except Exception:
            pass
        return ("AI engine", "fail",
                f"Cloud AI not reachable ({desc}). Check your API key and internet, "
                f"or switch provider in Admin → AI model & settings.")

    # local (Ollama)
    try:
        import ollama
        installed = [m.model for m in ollama.list().models]
    except Exception:
        _try_start_ollama()
        return ("AI engine", "warn",
                "Ollama isn't responding — I tried to start it. If this persists, open the Ollama "
                "app (you'll see a llama icon in the system tray).")
    bases = {m.split(":")[0] for m in installed}
    if config.MODEL not in installed and config.MODEL.split(":")[0] not in bases:
        def job():
            try:
                subprocess.run(["ollama", "pull", config.MODEL], capture_output=True, timeout=3600)
            except Exception:
                pass
        _bg(job)
        return ("AI engine", "fixed",
                f"The model '{config.MODEL}' isn't installed — pulling it now in the background. "
                f"It'll be ready in a few minutes (big download).")
    return ("AI engine", "ok", f"Local AI ready — {config.MODEL}.")


def _check_disk():
    try:
        import psutil
        d = psutil.disk_usage(str(Path.home().anchor or "/"))
        free_gb = d.free / 2 ** 30
        if free_gb < 2:
            return ("Disk space", "warn",
                    f"Low disk space — only {free_gb:.1f} GB free. Open Admin → 💾 Storage to see "
                    f"what's using space (usually AI models or the Kali/WSL disk) and how to free it.")
        return ("Disk space", "ok", f"{free_gb:.0f} GB free.")
    except Exception:
        return ("Disk space", "ok", "skipped.")


def run_all() -> list[tuple[str, str, str]]:
    """Run every check (auto-fixing the safe ones). Returns [(label, status, message)]."""
    return [
        _check_folders(),
        _check_writable(),
        _check_settings(),
        _check_deps(),
        _check_ai(),
        _check_disk(),
    ]


# ---------------------------------------------------------------- outputs

def doctor_html() -> str:
    checks = run_all()
    fixed = sum(1 for _l, s, _m in checks if s == "fixed")
    bad = sum(1 for _l, s, _m in checks if s in ("warn", "fail"))
    if fixed == 0 and bad == 0:
        head = "✅ Everything looks healthy — no problems found."
    elif bad == 0:
        head = f"🛠️ Fixed {fixed} issue(s) automatically. You're good to go."
    else:
        head = f"🛠️ Fixed {fixed}; ⚠️ {bad} need a quick action from you (see below)."
    rows = []
    for label, status, msg in checks:
        rows.append(f'<div class="doc-item doc-{status}"><span class="doc-ico">{_ICON[status]}</span>'
                    f'<span class="doc-txt"><b>{label}</b> — {msg}</span></div>')
    return f'<div class="doc-wrap"><div class="doc-head">{head}</div>{"".join(rows)}</div>'


def quick_summary() -> str:
    """Plain-text report for the AI tool."""
    checks = run_all()
    lines = [f"{_ICON[s]} {label}: {m}" for label, s, m in checks]
    bad = [label for label, s, _m in checks if s in ("warn", "fail")]
    header = ("Nanban self-check — I checked everything and fixed what I safely could.\n"
              if not bad else
              "Nanban self-check — I fixed what I could; a couple of things need you (marked ⚠️/❌).\n")
    return header + "\n".join(lines)
