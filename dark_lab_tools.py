"""
Backend for the 🕶️ Dark Lab tab — drives the four Nanban Kali Kit tools
(kali-intel, nmap2, kali-forensics, kali-pentest) live on the Kali WSL box and
adds an AI analysis layer that runs on THIS machine through the app's own engine
(llm.chat) — so the same model the rest of Nanban uses explains every result,
with zero WSL↔Ollama networking needed.

The tools themselves run with --no-ai (fast data-gathering + report) and stream
their output into the panel; then ai_analyze() summarizes the transcript.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import time
from pathlib import Path

import config
import llm

DISTRO = "kali-linux"
ASSETS = Path(config.BASE_DIR) / "assets" / "kali_desktop"
KIT_SRC = ASSETS / "nanban-kit"
KIT_FILES = ("kitlib.py", "kali_intel.py", "kali_pentest.py", "nmap2.py",
             "kali_forensics.py", "install.sh")
CASE = "~/nanban-kit/case"
_FLAGS = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0

# tool_key -> (label, icon, command builder(target)->str, target label, placeholder, needs_target)
TOOLS = {
    "intel": {
        "label": "OSINT & Threat Intel", "icon": "🌐", "cmd": "kali-intel",
        "tlabel": "Domain, IP, file hash or email",
        "ph": "example.com   ·   104.21.56.123   ·   44d88612fea8a8f36de82e1278abb02f",
        "build": lambda t: f"kali-intel --no-ai --case {CASE} {shlex.quote(t)}",
    },
    "nmap": {
        "label": "Nmap 2.0 (visual)", "icon": "🗺️", "cmd": "nmap2",
        "tlabel": "Host, IP or CIDR you are authorized to scan",
        "ph": "127.0.0.1   ·   192.168.1.0/24   ·   scanme.nmap.org",
        "build": lambda t: f"nmap2 --no-ai --case {CASE} {shlex.quote(t)}",
    },
    "forensics": {
        "label": "Digital Forensics", "icon": "🔬", "cmd": "kali-forensics",
        "tlabel": "Path to a file INSIDE Kali (e.g. ~/samples/x.bin)",
        "ph": "~/samples/suspicious.bin",
        "build": lambda t: f"kali-forensics --no-ai --case {CASE} {shlex.quote(t)}",
    },
    "pentest": {
        "label": "Pentest Agent", "icon": "🎯", "cmd": "kali-pentest",
        "tlabel": "Target you have WRITTEN authorization to test",
        "ph": "127.0.0.1   ·   192.168.56.0/24",
        "build": lambda t: f"kali-pentest --no-ai --authorized --case {CASE} --target {shlex.quote(t)}",
    },
}


# ───────────────────────────────────────────── install / ensure kit present

def _wsl_root(cmd: str, stdin: bytes | None = None, timeout: int = 180) -> tuple[int, str]:
    try:
        p = subprocess.run(["wsl.exe", "-d", DISTRO, "-u", "root", "--", "bash", "-c", cmd],
                           input=stdin, capture_output=True, timeout=timeout, creationflags=_FLAGS)
        return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")
    except FileNotFoundError:
        return 127, "wsl.exe not found"
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except Exception as e:  # pragma: no cover
        return 1, str(e)


def _kali_user() -> str:
    try:
        import kali_panel
        return kali_panel._known_kali_user() or "nanbanlinux"
    except Exception:
        return "nanbanlinux"


def installed() -> bool:
    code, _ = _wsl_root("test -x /usr/local/bin/kali-intel && test -x /usr/local/bin/nmap2", timeout=30)
    return code == 0


def ensure_kit():
    """Yield status lines while making sure the kit is installed/updated inside Kali."""
    yield "🔧 Nanban Kali Kit check panren…"
    for f in KIT_FILES:
        src = KIT_SRC / f
        if not src.exists():
            yield f"⛔ missing source file: {f} (reinstall the app)"
            return
        data = src.read_bytes().replace(b"\r\n", b"\n")
        code, out = _wsl_root(f"mkdir -p /opt/nanban-kit-src && cat > /opt/nanban-kit-src/{f}", stdin=data)
        if code != 0:
            yield f"⛔ could not copy {f}: {out}"
            return
    yield "📦 Installing / updating the kit on Kali (tools + deps)…"
    code, out = _wsl_root(f"bash /opt/nanban-kit-src/install.sh {shlex.quote(_kali_user())} 2>&1 | tail -6",
                          timeout=600)
    yield out.strip() or ("✅ done" if code == 0 else "install returned an error")


# ───────────────────────────────────────────── run a tool live on Kali

def run_tool(tool_key: str, target: str):
    """Generator yielding the growing terminal transcript as the tool runs on Kali."""
    t = TOOLS.get(tool_key)
    if not t:
        yield "unknown tool"
        return
    target = (target or "").strip()
    if not target:
        yield f"Give a {t['tlabel'].lower()} first."
        return

    try:
        import india_lab_tools as ilt
        import kali_panel as kp
        import servers
    except Exception as e:
        yield f"⛔ cannot load Kali bridge: {e}"
        return

    if not installed():
        acc = []
        for line in ensure_kit():
            acc.append(line)
            yield "\n".join(acc)
        yield "\n".join(acc) + "\n"

    try:
        host = servers.connect(kp.KALI)
    except Exception:
        host = None
    if host is None:
        yield ("🟠 Kali connect aagala. 🐉 **Kali** tab-a oru thadava open pannu "
               "(desktop start aagum), apram thirumba Run pannu.")
        return

    command = t["build"](target)
    header = f"$ {command}\n\n"
    final = ""
    for grow, done in ilt._stream_exec(host, command, timeout=1800):
        if done is None:
            yield header + grow
        else:
            final = done
    yield header + (final or "(no output)")


# ───────────────────────────────────────────── AI analysis (runs on THIS machine)

_SYS = ("You are a precise cybersecurity analyst helping with authorized, legal security "
        "research, education and threat intelligence. You explain tool output clearly for an "
        "analyst or student, highlight the real risks, and give concrete, prioritized next steps. "
        "You never provide step-by-step intrusion or exploit payloads — analysis, risk and "
        "defensive/next-step guidance only. Keep it tight and well-structured with short headings.")

_PROMPTS = {
    "intel": ("This is an OSINT / threat-intelligence collection for the indicator '{t}'. "
              "Summarize what the indicator appears to be, the key risks or red flags, and 3-5 "
              "concrete next investigation steps."),
    "nmap": ("This is an Nmap service/version scan of '{t}'. Identify outdated or risky services, "
             "name the likely CVE(s)/weakness for each, flag the single highest-priority finding, "
             "and give one-line remediation per item. If versions look current, say so."),
    "forensics": ("This is a digital-forensics triage of a file ('{t}'). Explain what the file is, "
                  "whether anything is suspicious, what the notable artifacts/indicators mean, and "
                  "3-5 next DFIR steps (dump, sandbox, pivot on an IOC, etc.)."),
    "pentest": ("This is an authorized penetration-test recon of '{t}'. Give a concise attack-surface "
                "summary, the top risks ranked by severity with the likely weakness/CVE, and the "
                "recommended NEXT manual checks naming the Kali tool for each (no exploit payloads)."),
}


def ai_analyze(tool_key: str, target: str, transcript: str):
    """Stream an AI analysis of the tool's transcript using the app's own engine."""
    transcript = (transcript or "").strip()
    if not transcript:
        yield "_Run a tool first — then I'll analyse the result._"
        return
    # keep the model focused on the real data, trimmed to a sane size
    body = transcript[-9000:]
    prompt = _PROMPTS.get(tool_key, "Analyse these security tool results for an analyst.").format(t=target)
    messages = [{"role": "system", "content": _SYS},
                {"role": "user", "content": f"{prompt}\n\n--- TOOL OUTPUT ---\n{body}"}]
    text = ""
    try:
        for chunk in llm.chat(messages, tools=None, options={"temperature": 0.3}):
            piece = getattr(getattr(chunk, "message", None), "content", "") or ""
            if piece:
                text += piece
                yield text
    except Exception as e:
        yield (text + "\n\n") if text else "" + (
            f"⚠️ AI engine reach aagala: {e}\n\n"
            "Local-a: 🐉 Ollama app open pannu (`ollama serve`), illa 🛠️ Admin-la oru hosted key set pannu. "
            "Tool-oda data + report ready-a irukku.")
    if not text:
        yield ("⚠️ AI engine ippo offline. Tool-oda full output mela irukku, HTML/Markdown report-um "
               "Kali-la `~/nanban-kit/case/reports/`-la save aagirukku.")


# ───────────────────────────────────────────── 🧅 Terminal (dark-osint Tor browser)

# Quick actions for the Terminal menu. key -> (label, icon, builds a dark-osint command, hint)
TERMINAL_ACTIONS = {
    "search": {"label": "Onion Search (Ahmia)", "icon": "🔎",
               "tlabel": "Words to search on the dark web", "ph": "ransomware leak site",
               "build": lambda a: f"dark-osint search {shlex.quote(a)}", "need": True},
    "open": {"label": "Open .onion / URL", "icon": "🌐",
             "tlabel": ".onion address or https URL (fetched over Tor as text)",
             "ph": "http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion/",
             "build": lambda a: f"dark-osint dump {shlex.quote(a)}", "need": True},
    "check": {"label": "Tor Check (am I on Tor?)", "icon": "✅",
              "tlabel": "", "ph": "", "build": lambda a: "dark-osint check", "need": False},
    "onions": {"label": "Extract .onion IOCs from case", "icon": "🧅",
               "tlabel": "", "ph": "", "build": lambda a: "dark-osint iocs", "need": False},
    "cmd": {"label": "Run any dark-osint command", "icon": "🧰",
            "tlabel": "dark-osint command (e.g. 'notes', 'hash file.pdf', 'head ahmia.fi')",
            "ph": "notes   ·   onions   ·   hash ~/case/pages/x.html", "need": True,
            "build": lambda a: "dark-osint " + a},
}

DARK_OSINT_FILES = ("dark-osint.py", "dark-osint-install.sh")


def dark_osint_installed() -> bool:
    code, _ = _wsl_root("test -x /usr/local/bin/dark-osint", timeout=30)
    return code == 0


def ensure_dark_osint():
    """Yield status lines while installing/updating the dark-osint Tor browser inside Kali."""
    yield "🔧 dark-osint (Tor browser) check panren…"
    for f in DARK_OSINT_FILES:
        src = ASSETS / f
        if not src.exists():
            yield f"⛔ missing source: {f}"
            return
        data = src.read_bytes().replace(b"\r\n", b"\n")
        code, out = _wsl_root(f"mkdir -p /opt/dark-osint-src && cat > /opt/dark-osint-src/{f}", stdin=data)
        if code != 0:
            yield f"⛔ copy failed {f}: {out}"
            return
    yield "📦 Installing dark-osint + Tor on Kali (first time konja neram)…"
    code, out = _wsl_root(f"bash /opt/dark-osint-src/dark-osint-install.sh {shlex.quote(_kali_user())} 2>&1 | tail -6",
                          timeout=600)
    yield out.strip() or ("✅ done" if code == 0 else "install returned an error")


def run_terminal(action_key: str, arg: str):
    """Generator yielding the growing dark-osint output as it runs on Kali over Tor."""
    a = TERMINAL_ACTIONS.get(action_key)
    if not a:
        yield "unknown action"
        return
    arg = (arg or "").strip()
    if a["need"] and not arg:
        yield f"Give: {a['tlabel'].lower()}"
        return
    try:
        import india_lab_tools as ilt
        import kali_panel as kp
        import servers
    except Exception as e:
        yield f"⛔ cannot load Kali bridge: {e}"
        return
    if not dark_osint_installed():
        acc = []
        for line in ensure_dark_osint():
            acc.append(line)
            yield "\n".join(acc)
        yield "\n".join(acc) + "\n"
    try:
        host = servers.connect(kp.KALI)
    except Exception:
        host = None
    if host is None:
        yield ("🟠 Kali connect aagala. 🐉 **Kali** tab-a oru thadava open pannu, apram thirumba Run pannu.")
        return
    command = a["build"](arg)
    header = f"$ {command}\n\n"
    final = ""
    for grow, done in ilt._stream_exec(host, command, timeout=600):
        if done is None:
            yield header + grow
        else:
            final = done
    yield header + (final or "(no output)")


_TERM_PROMPTS = {
    "search": "These are dark-web (onion) search results from Ahmia for '{t}'. Summarize the kinds of "
              "sites found, which look relevant for threat-intel research, and safe next steps. "
              "Do not encourage accessing illegal content.",
    "open": "This is the text of a page fetched over Tor ('{t}'). Summarize what the page is and any "
            "noteworthy indicators or links. Analysis only.",
    "check": "This is a Tor connectivity check result. In one or two lines say whether Tor is working "
             "and what the exit IP means for anonymity.",
    "onions": "These are .onion indicators extracted from collected research files. Briefly explain what "
              "this IOC list is useful for in threat intelligence.",
    "cmd": "Explain this dark-osint command output for a security learner and note any useful findings.",
}


def ai_analyze_terminal(action_key: str, arg: str, transcript: str):
    transcript = (transcript or "").strip()
    if not transcript:
        yield "_Run something first — then I'll explain it._"
        return
    body = transcript[-9000:]
    prompt = _TERM_PROMPTS.get(action_key, "Explain this Tor/OSINT output for an analyst.").format(t=arg)
    messages = [{"role": "system", "content": _SYS},
                {"role": "user", "content": f"{prompt}\n\n--- OUTPUT ---\n{body}"}]
    text = ""
    try:
        for chunk in llm.chat(messages, tools=None, options={"temperature": 0.3}):
            piece = getattr(getattr(chunk, "message", None), "content", "") or ""
            if piece:
                text += piece
                yield text
    except Exception as e:
        yield (text + f"\n\n⚠️ AI reach aagala: {e}") if text else f"⚠️ AI engine offline: {e}"
    if not text:
        yield "⚠️ AI engine ippo offline — output mela irukku. (Ollama start pannu, illa Admin-la hosted key set pannu.)"


def latest_report() -> str:
    """Path of the newest report written by any kit tool (for the 'open report' hint)."""
    code, out = _wsl_root(
        f"ls -1t $(eval echo {CASE})/reports/*.html 2>/dev/null | head -1", timeout=20)
    return out.strip().splitlines()[0] if out.strip() else ""
