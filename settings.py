"""
User settings: read/write data/settings.json and apply changes live, so the in-app
Settings screen can change the model/backend/etc. with no file editing and (mostly)
no restart. config.py loads this file's overrides at startup too.
"""

import json
import subprocess
import sys
from pathlib import Path

import config

SETTINGS_FILE = config.DATA_DIR / "settings.json"
APP_DIR = config.BASE_DIR

# Keys the Settings screen is allowed to change (must match config._apply_settings_override)
EDITABLE = {
    "AGENT_NAME", "LLM_BACKEND", "MODEL", "EMBED_MODEL", "TEMPERATURE",
    "HOSTED_BASE_URL", "HOSTED_API_KEY", "HOSTED_MODEL", "HOSTED_KEYS",
    "AUTOSTART_LAB", "OPEN_BROWSER_ON_START", "REQUIRE_VPN", "SECURITY_TAB",
    "WEB_COMPUTER_MODE", "LAN_ACCESS", "WEB_PASSWORD",
    "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID",
    "WHATSAPP_TOKEN", "WHATSAPP_PHONE_ID", "WHATSAPP_VERIFY_TOKEN",
}

# Ready-made providers for the dropdown. FREE ones first (local + free hosted tiers),
# then optional PAID frontier ones (Claude / GPT). Free tiers have rate limits but cost nothing.
PROVIDERS = {
    # ---- 🏆 BEST: one agent, auto-routes each question to the strongest model ----
    "🏆 Nanban Best — auto-picks the strongest model per task": {
        "backend": "router", "base": "https://integrate.api.nvidia.com/v1", "model": "auto"},
    "🏛️ Nanban Council — asks several models, combines the best (slower)": {
        "backend": "council", "base": "https://integrate.api.nvidia.com/v1", "model": "auto"},
    # ---- FREE ----
    "📦 Portable (bundled) — zero install, no Ollama": {"backend": "portable"},
    "🆓 Local (Ollama) — free & private": {"backend": "local"},
    "🆓 Groq — free & fast": {
        "backend": "hosted", "base": "https://api.groq.com/openai/v1", "model": "openai/gpt-oss-20b"},
    "🆓 Google Gemini — free tier": {
        "backend": "hosted", "base": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.0-flash"},
    "🆓 Cerebras — free, very fast 70B": {
        "backend": "hosted", "base": "https://api.cerebras.ai/v1", "model": "llama-3.3-70b"},
    "🆓 OpenRouter — free models only": {
        "backend": "hosted", "base": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.3-70b-instruct:free"},
    # ---- NVIDIA (build.nvidia.com — free nvapi- key, top models, OpenAI-compatible) ----
    # Base URL for all: https://integrate.api.nvidia.com/v1 . Get a free key at build.nvidia.com.
    # If a model id ever changes, Nanban auto-switches to a working one on your key.
    "🟩 NVIDIA → Nemotron Super 120B (flagship)": {
        "backend": "hosted", "base": "https://integrate.api.nvidia.com/v1",
        "model": "nvidia/nemotron-3-super-120b-a12b"},
    "🟩 NVIDIA → Llama 3.1 405B (largest)": {
        "backend": "hosted", "base": "https://integrate.api.nvidia.com/v1",
        "model": "meta/llama-3.1-405b-instruct"},
    "🟩 NVIDIA → Llama 3.3 70B (fast all-rounder)": {
        "backend": "hosted", "base": "https://integrate.api.nvidia.com/v1",
        "model": "meta/llama-3.3-70b-instruct"},
    "🟩 NVIDIA → DeepSeek V4.1 Flash (reasoning)": {
        "backend": "hosted", "base": "https://integrate.api.nvidia.com/v1",
        "model": "deepseek-ai/deepseek-v4.1-flash"},
    "🟩 NVIDIA → Qwen2.5 Coder 32B (coding)": {
        "backend": "hosted", "base": "https://integrate.api.nvidia.com/v1",
        "model": "qwen/qwen2.5-coder-32b-instruct"},
    "🟩 NVIDIA → MiniMax M3.1 Flash (vision, slower)": {
        "backend": "hosted", "base": "https://integrate.api.nvidia.com/v1",
        "model": "minimaxai/minimax-m3.1-flash"},
    # ---- PAID (optional, top frontier intelligence) ----
    "💳 OpenRouter → Claude 3.5 Sonnet (paid)": {
        "backend": "hosted", "base": "https://openrouter.ai/api/v1", "model": "anthropic/claude-3.5-sonnet"},
    "💳 OpenRouter → GPT-4o (paid)": {
        "backend": "hosted", "base": "https://openrouter.ai/api/v1", "model": "openai/gpt-4o"},
    "💳 OpenAI → GPT-4o mini (paid)": {
        "backend": "hosted", "base": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
}


def load() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


# ---- per-model API keys ----
# Each AI model (each dropdown preset) keeps its OWN key, under its own name.
# Nothing is shared between models, so saving one never erases another.

def get_key_for(slot: str) -> str:
    """The saved API key for one model/preset, or '' if none saved yet."""
    keys = load().get("HOSTED_KEYS", {}) or {}
    return keys.get((slot or "").strip(), "")


def set_key_for(slot: str, key: str) -> None:
    """Store one model's key under its own name (never touches any other model's key)."""
    slot = (slot or "").strip()
    if not slot:
        return
    keys = dict(load().get("HOSTED_KEYS", {}) or {})
    if key:
        keys[slot] = key
    else:
        keys.pop(slot, None)
    save({"HOSTED_KEYS": keys})


def save(updates: dict) -> None:
    """Persist and apply live. None values are ignored."""
    current = load()
    for key, value in updates.items():
        if key in EDITABLE and value is not None:
            current[key] = value
    SETTINGS_FILE.write_text(json.dumps(current, indent=2), encoding="utf-8")
    _apply_live(current)


def _apply_live(settings: dict) -> None:
    """Update the running config so changes take effect without a restart."""
    for key, value in settings.items():
        if key in EDITABLE and hasattr(config, key):
            setattr(config, key, value)
    try:
        import llm
        llm._client = None   # force the hosted client to be rebuilt with new base/key
    except Exception:
        pass


# ---------------------------------------------------------------- one-button update

def update() -> str:
    """Pull the latest version and reinstall dependencies. Returns a status report."""
    git_dir = APP_DIR / ".git"
    lines = []
    if git_dir.exists():
        pull = subprocess.run(["git", "pull", "--ff-only"], cwd=APP_DIR, capture_output=True, text=True, timeout=120)
        out = (pull.stdout + pull.stderr).strip()
        lines.append("🔄 " + (out or "git pull done"))
        if "Already up to date" in out:
            return "✅ Already up to date — you have the latest version."
        if pull.returncode != 0:
            return "⚠️ Update failed:\n" + out + "\n\nFix any local changes (or git stash) and try again."
    else:
        return ("ℹ️ This copy isn't linked to a Git repo yet, so there's nothing to pull from. "
                "To enable one-click updates: put Nanban on GitHub (see DEPLOY.md), then clone that repo "
                "and run from the clone. After that, this button pulls the latest automatically.")
    # reinstall dependencies in the venv
    pip = APP_DIR / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / ("pip.exe" if sys.platform == "win32" else "pip")
    pip = str(pip) if pip.exists() else sys.executable + " -m pip"
    try:
        subprocess.run(pip.split() + ["install", "-q", "-r", str(APP_DIR / "requirements.txt")],
                       cwd=APP_DIR, capture_output=True, text=True, timeout=600)
        lines.append("📦 Dependencies up to date.")
    except Exception as e:
        lines.append(f"📦 Dependency install skipped: {e}")
    lines.append("\n**Restart Nanban to finish the update.**")
    return "\n".join(lines)


def current_version() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=APP_DIR, capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return "local copy"
