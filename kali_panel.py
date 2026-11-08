"""
🐉 Kali — the dedicated Kali Linux workspace for Nanban.

One modern screen that combines:
  • a terminal that runs on your connected Kali box (or this PC) — editor-style, dark,
  • an AI helper: type what you want in Tanglish or English, it writes the exact command,
  • a live Command Reference: whatever command you run is auto-explained (EN + Tanglish),
    acting like a built-in man-page / dictionary for Kali tools.

Everything targets YOUR OWN lab / authorised machines — same boundary as the Security Tutor.
Running commands on Kali uses the existing SSH connection (servers.py, the 'kali' server).
"""

import re
import threading
import time

import gradio as gr

import cmd_dict
import config
import llm
import servers
import web_computer

KALI = "kali"

# a light safety net even on the user's own box (blocks obvious disk-wipes / fork bombs)
HARD_BLOCK = [
    r"\brm\s+-[a-zA-Z]*[rf][a-zA-Z]*\s+/(\s|$)", r"\bmkfs\b", r"\bdd\s+if=.*of=/dev/",
    r":\(\)\s*\{", r"\bshutdown\b", r"\breboot\b", r">\s*/dev/sda",
]

KALI_SYS = (
    "You are a Kali Linux command generator for the user's OWN lab and machines they are "
    "authorised to test. The user writes in English or Tanglish (Tamil in English letters). "
    "Output ONLY ONE line: the exact shell command to run — no explanation, no markdown, no "
    "backticks, no leading $ . Prefer tools that exist in Kali. If the request is unclear or is "
    "not a command, output a single line starting with '# ' briefly saying what you need. "
    "Assume targets are the user's own lab (e.g. 127.0.0.1) unless they give one."
)


# ---------------------------------------------------------------- connection

def _saved_kali() -> dict:
    """The saved Kali server entry (user/password), if any."""
    try:
        import json
        reg = json.loads((config.DATA_DIR / "servers.json").read_text("utf-8"))
        return reg.get(KALI, {}) or {}
    except Exception:
        return {}


def _known_kali_pass() -> str:
    """Saved Kali password, to prefill the connect form (local convenience)."""
    return (_saved_kali().get("password") or "")


def _known_kali_user() -> str:
    """Best guess for the Kali username, to prefill the connect form.
    Prefers the one already saved; otherwise asks WSL for its default user."""
    u = (_saved_kali().get("user") or "").strip()
    if u:
        return u
    try:
        import subprocess
        out = subprocess.run(["wsl.exe", "-d", "kali-linux", "--", "id", "-un"],
                             capture_output=True, text=True, timeout=12)
        name = (out.stdout or "").strip()
        if name and name != "root":
            return name
    except Exception:
        pass
    return ""


def connected() -> bool:
    if KALI not in servers.names():
        return False
    try:
        servers.connect(KALI)
        return True
    except Exception:
        return False


def status_line() -> str:
    if KALI not in servers.names():
        return ("⚪ **Kali not connected.** Install it once (Security tab → Kali setup), start SSH "
                "(`sudo service ssh start`), then connect below.")
    try:
        host = servers.connect(KALI)
        return f"🟢 **Kali connected** — {host.os_name} · `{host.user}@{host.host}`. Commands below run on Kali."
    except Exception as e:
        return f"🟠 **Kali registered but not reachable:** {e}  \nIn Kali run `sudo service ssh start`, then Re-check."


def connect_kali(username: str, password: str) -> str:
    username = (username or "").strip()
    if not username:
        return "⚠️ Type your Kali username first (the one you created during setup)."
    # Save the password so the local Kali login stays one-click (data/servers.json is gitignored).
    servers.add(KALI, f"{username}@127.0.0.1", password=password or "", save_password=bool(password))
    try:
        servers.disconnect(KALI)
        host = servers.connect(KALI, ask_password=lambda n: password or "")
        return f"🟢 **Connected to Kali** — {host.os_name} ({host.user}@{host.host}). You can run commands now."
    except Exception as e:
        return (f"🟠 Saved, but couldn't connect: {e}\n\n"
                "Check: Kali is open, and inside it `sudo service ssh start` was run.")


# ---------------------------------------------------------------- running commands

def _blocked(command: str) -> bool:
    return any(re.search(p, command, re.IGNORECASE) for p in HARD_BLOCK)


# The interactive shell is a real terminal, so its output carries ANSI colour codes,
# cursor moves and \r spinners. Clean them so the plain text box stays readable.
_ANSI_RE = re.compile(
    r"\x1b\[[0-9;?]*[ -/]*[@-~]"       # CSI … colour / cursor
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)"  # OSC … title
    r"|\x1b[=>]|\x1b[()][A-Za-z0-9]")     # misc two/three-char escapes


def _clean_term(text: str) -> str:
    text = _ANSI_RE.sub("", text).replace("\x1b", "")
    out = []
    for line in text.split("\n"):
        line = line.rstrip("\r")            # normal CRLF ending — just drop the trailing CR
        if "\r" in line:                    # a spinner / readline redraw overwrites in place:
            parts = [p for p in line.split("\r") if p]  # keep the final non-empty state
            line = parts[-1] if parts else ""
        # drop other control chars but keep tab
        line = "".join(ch for ch in line if ch == "\t" or ord(ch) >= 32)
        out.append(line)
    return "\n".join(out)


# One continuous terminal transcript (single-user local app), like a real terminal window.
_TERM = {"text": ""}
_TERM_CAP = 60000                           # keep the last ~60k chars


def _term_append(chunk: str) -> str:
    _TERM["text"] = (_TERM["text"] + chunk)[-_TERM_CAP:]
    return _TERM["text"]


def run_on_kali(command: str):
    """Send a line to the persistent Kali shell and stream back the live output.
    Because the shell stays open, interactive tools (msfconsole, python, mysql…) keep
    running and your next lines go into them — and cd/env persist between commands."""
    command = (command or "").rstrip("\n")
    if _blocked(command):
        yield _term_append(f"\n⚠ Blocked: idhu disk wipe / crash maari dangerous. Run pannala.\n")
        return
    try:
        host = servers.connect(KALI)
    except Exception as e:
        yield (f"🟠 Kali not reachable: {e}\nStart SSH in Kali (`sudo service ssh start`) and reconnect.")
        return
    # first use: show the shell's banner / prompt
    banner = host.ensure_shell()
    if banner:
        yield _term_append(_clean_term(banner))
    host.shell_send(command)
    for chunk in host.shell_stream(idle=0.5, max_wait=config.COMMAND_TIMEOUT):
        yield _term_append(_clean_term(chunk))
    yield _TERM["text"]


def kali_interrupt():
    """Ctrl-C the running tool in the Kali shell, then show fresh output."""
    try:
        host = servers.connect(KALI)
    except Exception as e:
        yield f"🟠 Kali not reachable: {e}"
        return
    host.shell_interrupt()
    for chunk in host.shell_stream(idle=0.4, max_wait=10):
        yield _term_append(_clean_term(chunk))
    yield _TERM["text"]


def run(command: str, target: str):
    """Run on Kali or this PC, stream output, and auto-explain the command.
    Yields (output, reference_markdown)."""
    command = (command or "").strip()
    ref = reference_for(command)
    if not command:
        yield "", ref
        return
    if target == KALI:
        for out in run_on_kali(command):
            yield out, ref
    else:
        for out, _cwd in web_computer.run_command_stream(command, web_computer.shell.backend):
            yield out, ref


# ---------------------------------------------------------------- AI + reference

def ai_command(request: str) -> str:
    """Turn a natural-language (Tanglish/English) request into one command."""
    request = (request or "").strip()
    if not request:
        return ""
    messages = [{"role": "system", "content": KALI_SYS}, {"role": "user", "content": request}]
    text = ""
    try:
        for chunk in llm.chat(messages, tools=None, options={"temperature": 0.2}):
            if chunk.message.content:
                text += chunk.message.content
    except Exception as e:
        return f"# AI not reachable: {e}"
    line = next((l.strip() for l in text.splitlines() if l.strip()), "")
    line = line.strip("`").removeprefix("$ ").strip()      # strip stray backticks / prompt
    return line


_IP_RE = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
_PRIVATE_RE = re.compile(
    r"(127\.\d|10\.\d|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|0\.0\.0\.0|localhost"
    r"|\.lab\b|\.local\b|metasploitable|dvwa|juice[-\s]?shop)", re.I)
_EXT_DOMAIN_RE = re.compile(
    r"https?://([a-z0-9.\-]+)|\b([a-z0-9\-]+\.(?:com|net|org|io|in|co|gov|edu|me|dev|xyz|top|info|ru|cn|uk))\b",
    re.I)
_INSTALL_RE = re.compile(r"\b(apt|apt-get|pip3?|pipx|dpkg|snap|gem|cargo)\b")


def _target_in_scope(command: str) -> tuple[bool, str]:
    """True if the command targets a lab/local/private host (safe to auto-run).
    Returns (in_scope, found_public_target)."""
    c = command.lower()
    if _INSTALL_RE.search(c) or "git clone" in c or "go install" in c:
        return True, ""                       # package/setup commands are fine
    for m in _IP_RE.finditer(command):
        if not _PRIVATE_RE.search(m.group(0)):
            return False, m.group(0)          # a public IP → confirm needed
    md = _EXT_DOMAIN_RE.search(command)
    if md:
        host = md.group(1) or md.group(2) or ""
        if host and not _PRIVATE_RE.search(host) and "github.com" not in host and "gitlab" not in host:
            return False, host                # an external domain → confirm needed
    return True, ""


def ai_shell(prompt: str, auto_run: bool, target: str):
    """Tanglish/English prompt → command → (safety) → auto-run on Kali → output + reference.
    Yields (command_box, terminal_output, reference_markdown)."""
    prompt = (prompt or "").strip()
    if not prompt:
        yield "", "Oru request type pannu — e.g. '127.0.0.1 la open ports scan pannu'", ""
        return
    cmd = ai_command(prompt)
    if not cmd:
        yield "", "AI command generate panna mudiyala. Chat tab la oru model set pannu.", ""
        return
    if cmd.startswith("#"):                    # AI needs clarification
        yield "", "🤔 " + cmd.lstrip("# ").strip(), ""
        return
    ref = reference_for(cmd)
    if _blocked(cmd):
        yield cmd, f"$ {cmd}\n\n⚠ Blocked: idhu disk wipe / crash maari dangerous command. Run pannala.", ref
        return
    in_scope, tgt = _target_in_scope(cmd)
    if auto_run and not in_scope:
        msg = (f"$ {cmd}\n\n🟠 Idhu veliya target madhiri theriyudhu: '{tgt}'.\n"
               "Auto-run pannala (safety). Idhu un authorized target-aana, keela Run click pannu. "
               "Illaina un lab target (127.0.0.1 / 10.x / 192.168.x / Metasploitable) kudu.\n"
               "⚖️ Veliya real system scan/attack = illegal.")
        yield cmd, msg, ref
        return
    if not auto_run:
        yield cmd, f"$ {cmd}\n\n✍️ Command ready. Review panni keela **Run** click pannu.", ref
        return
    if target == KALI and not connected():
        yield cmd, (f"$ {cmd}\n\n🟠 Kali connect pannala. Right side la **Connect** pannu, "
                    "illa terminal la 🖥️ **This PC** select pannu."), ref
        return
    # safe + auto-run
    yield cmd, f"⏳ Running on {'Kali' if target == KALI else 'this PC'}…  ({cmd})", ref
    for out, r in run(cmd, target):
        # Kali's interactive shell already echoes the command in its transcript; the local
        # runner does not, so prefix only there.
        yield cmd, (out if target == KALI else f"$ {cmd}\n{out}"), r


def reference_for(command: str) -> str:
    """The reference card for a command, from the dictionary (AI note if unknown)."""
    if cmd_dict.base_tool(command).lower() in {"msfconsole", "msfvenom"} or cmd_dict.is_metasploit_query(command):
        return cmd_dict.metasploit_markdown(tanglish=True)
    info = cmd_dict.explain(command)
    if info:
        return cmd_dict.to_markdown(info, tanglish=True)
    tool = cmd_dict.base_tool(command)
    if not tool:
        return "_Run a command or search a tool on the left to see its reference here._"
    return (f"### `{tool}`\n\n_Not in the built-in dictionary yet._\n\n"
            f"Ask the AI helper above (e.g. “explain `{tool}`”), or switch 💬 Chat to **🛡️ Security Tutor** "
            f"for a full explanation. The dictionary covers the common Kali tools — more are added over time.")


def lookup(query: str) -> str:
    """Manual reference lookup from the search box: a command, a tool, or a keyword."""
    query = (query or "").strip()
    if not query:
        return "_Type a command (`nmap -sV`) or a keyword (`sql`, `password`, `wifi`, `metasploit`) to look it up._"
    if cmd_dict.is_metasploit_query(query):
        return cmd_dict.metasploit_markdown(tanglish=True)
    info = cmd_dict.explain(query) or cmd_dict.get(cmd_dict.base_tool(query))
    if info:
        return cmd_dict.to_markdown(info, tanglish=True)
    matches = cmd_dict.search(query)
    if matches:
        cards = "\n".join(f"- **`{m}`** — {cmd_dict.get(m)['purpose']}" for m in matches)
        return f"**Matches for “{query}”:**\n\n{cards}\n\n_Type a tool's exact name to see full details._"
    return f"_No match for “{query}” in the dictionary. Try the AI helper above — it explains anything._"


# ---------------------------------------------------------------- UI

_KALI_CSS = """<style>
#kali-wrap { max-width: 1200px; margin: 0 auto; width: 100%; }
#kali-wrap, #kali-wrap .gap { gap: 10px !important; }
#kali-title, #kali-title * { font-size: 1.15rem !important; margin: 0 !important; }
#kali-status, #kali-status * { font-size: .82rem !important; }
/* 🖥️ Kali Desktop launcher */
#kali-desk { border:1px solid rgba(43,212,189,.45) !important; border-radius:14px !important; padding:12px 16px !important;
  background:linear-gradient(135deg, #0e1a22 0%, #0b1118 60%, #12222a 100%) !important; margin-bottom:10px !important;
  color:#e3edf6 !important; box-shadow:0 6px 24px rgba(0,0,0,.25); }
#kali-desk * { color:#e3edf6; }
#kali-desk-bar { align-items:center !important; justify-content:space-between !important; flex-wrap:nowrap !important; gap:12px;
  background:transparent !important; border:none !important; }
#kali-desk-txt { flex:1 1 auto; background:transparent !important; }
.kd-txt { display:flex; align-items:center; gap:14px; }
.kd-ico { font-size:32px; line-height:1; }
.kd-title { font-weight:800; font-size:15px; color:#ffffff; letter-spacing:.1px; }
.kd-sub { font-size:12.5px; color:#9fb3c4; margin-top:3px; }
#kali-desk-btn { flex:0 0 auto !important; min-height:40px !important; border-radius:10px !important; font-weight:800 !important;
  padding:0 20px !important; white-space:nowrap; background:#2bd4bd !important; color:#06211e !important; border:none !important;
  box-shadow:0 4px 16px rgba(43,212,189,.35); }
#kali-desk-btn:hover { background:#3fe3cc !important; }
#kali-desk-status { font-size:12.5px; margin-top:8px; background:transparent !important; }
#kali-desk-status p { margin:0; color:#cfe3dd; }
#kali-desk-status a { color:#2bd4bd !important; font-weight:700; }
#kali-desk-url { display:none !important; }
@media (max-width:720px) { #kali-desk-bar { flex-wrap:wrap !important; } .kd-sub { display:none; } }

#kali-head { align-items:center !important; justify-content:space-between !important; flex-wrap:nowrap !important; gap:8px; }
#kali-head #kali-title { flex:1 1 auto; }
#kali-connect-toggle { flex:0 0 auto !important; min-height:32px !important; height:32px; border-radius:9px !important;
  font-size:12.5px !important; font-weight:600 !important; padding:0 14px !important; white-space:nowrap; }
.kali-ct.on button, #kali-connect-toggle.on { border-color:#27c93f !important; }

#kali-main { gap: 12px !important; align-items: flex-start !important;
  flex-direction: row !important; flex-wrap: nowrap !important; }
/* both panels ≈ full screen height: 5% gap at top, 5% gap at bottom */
#kali-term-col { flex: 3 1 0 !important; min-width: 0 !important; gap: 10px !important;
  position: sticky; top: 5vh; align-self: flex-start; }
#kali-ref-col { flex: 1.4 1 0 !important; min-width: 0 !important; gap: 10px !important;
  position: sticky; top: 5vh; align-self: flex-start; }
/* the terminal output grows tall; the Run box stays right under it (no floating gap) */
#kali-out textarea { height: calc(90vh - 220px) !important; min-height: 240px !important;
  max-height: none !important; resize: none !important; }
/* the Command Reference matches that height and scrolls inside */
#kali-ref-view { height: calc(90vh - 112px) !important; min-height: 240px !important;
  max-height: none !important; overflow-y: auto !important; }

/* terminal window */
#kali-term { background:#0c0a07 !important; border:1px solid #2a2420 !important; border-radius:14px !important;
  padding:0 !important; overflow:hidden; box-shadow:0 8px 28px rgba(0,0,0,.28); }
#kali-term-head { align-items:center !important; justify-content:space-between !important; padding:8px 12px !important;
  background:#161210 !important; border-bottom:1px solid #2a2420; gap:8px; }
#kali-term-head > *:first-child { flex:1 1 auto !important; min-width:0; width:auto !important; }
#kali-term-head #kali-target, #kali-term-head #kali-ctrlc { flex:0 0 auto !important; width:auto !important; }
#kali-ctrlc button, #kali-ctrlc { min-height:28px !important; height:28px !important; padding:0 12px !important;
  border-radius:8px !important; font-size:12px !important; font-weight:600 !important;
  background:#3a2a24 !important; color:#ffb4a0 !important; border:1px solid #5a3a30 !important; white-space:nowrap; }
#kali-ctrlc button:hover { background:#c0392b !important; color:#fff !important; }
.term-chrome { display:flex; align-items:center; gap:7px; }
.term-chrome .dot { width:11px; height:11px; border-radius:50%; display:inline-block; }
.term-chrome .dot.r{background:#ff5f56;} .term-chrome .dot.y{background:#ffbd2e;} .term-chrome .dot.g{background:#27c93f;}
.term-chrome .term-name { color:#8a8178; font-size:12px; font-family:ui-monospace,Menlo,Consolas,monospace; margin-left:4px; }
#kali-target .wrap { display:flex !important; gap:3px; background:#0c0a07; border:1px solid #2a2420; border-radius:9px; padding:3px; }
#kali-target label { display:inline-flex !important; align-items:center; height:26px; border-radius:7px !important;
  padding:0 11px !important; color:#b8afa2; font-size:12.5px !important; cursor:pointer; border:none !important; background:transparent !important; }
#kali-target label.selected { background:#d6552e !important; color:#fff !important; }
#kali-target input[type=radio]{ display:none !important; }
#kali-out { padding:0 !important; background:transparent !important; border:none !important; }
#kali-out textarea { font-family:ui-monospace,Menlo,Consolas,monospace !important; font-size:12.5px !important;
  background:#0c0a07 !important; color:#8ef5b0 !important; border:none !important; padding:12px 14px !important;
  line-height:1.5 !important; }
#kali-out .icon-button-wrapper { background:transparent !important; border:none !important; }
#kali-in { border-top:1px solid #2a2420 !important; padding:7px !important; background:#120f0b !important; }
#kali-in .input-container { display:flex !important; align-items:center; gap:7px; }
#kali-in textarea { font-family:ui-monospace,Menlo,Consolas,monospace !important; font-size:13px !important;
  background:#221d17 !important; color:#eee !important; border:1px solid #2a2420 !important; border-radius:8px !important; padding:8px 10px !important; }
#kali-in textarea::placeholder { color:#6f665a; }
#kali-in .submit-button { height:36px !important; padding:0 16px !important; border-radius:9px !important;
  background:#d6552e !important; color:#fff !important; border:none !important; }

/* AI shell + cards */
#kali-ai, #kali-connect, #kali-ref { border:1px solid var(--border-color-primary) !important; border-radius:13px !important;
  background:var(--block-background-fill) !important; }
#kali-ai { padding:14px !important; position:relative; overflow:hidden;
  background:linear-gradient(135deg, rgba(214,85,46,.07), rgba(214,85,46,.015)) !important;
  border:1px solid rgba(214,85,46,.28) !important; border-radius:16px !important; }
#kali-ai .block { border:none !important; background:transparent !important; padding:0 !important; }
.ais-head { display:flex; align-items:center; gap:11px; margin-bottom:11px; }
.ais-ico { flex:0 0 auto; width:40px; height:40px; border-radius:12px; display:flex; align-items:center;
  justify-content:center; font-size:20px; color:#fff;
  background:radial-gradient(circle at 50% 35%, #ff9a6a, #d6552e 70%); box-shadow:0 4px 14px rgba(214,85,46,.4); }
.ais-title { font-weight:700; font-size:1rem; display:flex; align-items:center; gap:7px; }
.ais-badge { font-size:.6rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:#d6552e;
  background:rgba(214,85,46,.14); border:1px solid rgba(214,85,46,.3); padding:2px 7px; border-radius:999px; }
.ais-sub { font-size:.78rem; color:var(--body-text-color-subdued); line-height:1.45; margin-top:2px; }
#kali-ai-in textarea { font-size:13.5px !important; border-radius:11px !important;
  border:1px solid var(--border-color-primary) !important; padding:10px 12px !important;
  background:var(--block-background-fill) !important; transition:border-color .15s, box-shadow .15s; }
#kali-ai-in textarea:focus { border-color:#d6552e !important; box-shadow:0 0 0 3px rgba(214,85,46,.14) !important; }
#kali-ai .gr-button, #kali-ai button.primary { border-radius:11px !important; font-weight:700 !important;
  background:linear-gradient(135deg, #ff8a5c, #d6552e) !important; border:none !important; color:#fff !important;
  box-shadow:0 4px 14px rgba(214,85,46,.32) !important; white-space:nowrap; }
/* checkbox → modern pill toggle */
#kali-ai label.svelte-1qxcj8f, #kali-ai .wrap label { font-size:12.5px !important; }
#kali-ai input[type=checkbox] { appearance:none; -webkit-appearance:none; width:38px !important; height:21px !important;
  border-radius:999px !important; background:var(--border-color-primary) !important; position:relative;
  cursor:pointer; transition:background .18s; border:none !important; flex:0 0 auto; }
#kali-ai input[type=checkbox]:checked { background:#d6552e !important; }
#kali-ai input[type=checkbox]::after { content:''; position:absolute; top:2px; left:2px; width:17px; height:17px;
  border-radius:50%; background:#fff; transition:transform .18s; box-shadow:0 1px 3px rgba(0,0,0,.3); }
#kali-ai input[type=checkbox]:checked::after { transform:translateX(17px); }
#kali-connect, #kali-ref { padding:0 !important; }
.ref-head { display:flex; align-items:center; gap:7px; padding:9px 12px !important; font-size:12.5px !important;
  font-weight:600; border-bottom:1px solid var(--border-color-primary); background:var(--background-fill-secondary); border-radius:13px 13px 0 0; }
.ref-head .ref-ico { font-size:14px; }
#kali-connect-body { padding:10px 12px !important; gap:6px !important; }
#kali-connect textarea, #kali-connect input { font-size:12.5px !important; border-radius:8px !important; }
#kali-connect-btns { gap:7px !important; flex-wrap:nowrap !important; }
#kali-connect-btns .gr-button { flex:1 1 0; min-height:32px !important; height:32px; border-radius:8px !important; }
#kali-connect-hint, #kali-connect-hint * { font-size:10.5px !important; color:var(--body-text-color-subdued); }
#kali-ref { padding:0 !important; display:flex !important; flex-direction:column !important; }
#kali-ref-search { padding:9px 11px 0 !important; }
#kali-ref-search textarea { font-size:12.5px !important; border-radius:9px !important; }
/* the reference scrolls on its own; JS keeps its height equal to the terminal */
#kali-ref-view { padding:4px 13px 13px !important; font-size:12.5px !important; overflow-y:auto; scrollbar-width:thin; }
#kali-ref-view::-webkit-scrollbar { width:9px; }
#kali-ref-view::-webkit-scrollbar-thumb { background:rgba(214,85,46,.35); border-radius:8px; }
.ref-hint { margin-left:auto; font-size:10px; font-weight:500; color:var(--body-text-color-subdued); white-space:nowrap; }
/* commands in the reference are clickable → load into the terminal input */
#kali-ref-view code { cursor:pointer; border:1px solid transparent; border-radius:5px; padding:1px 5px;
  background:rgba(214,85,46,.10); color:#d6552e; transition:background .12s, border-color .12s; }
#kali-ref-view code:hover { background:rgba(214,85,46,.22); border-color:rgba(214,85,46,.55); }
#kali-ref-view code:active { transform:translateY(1px); }

/* Connect Kali — modal dialog (hidden until the header button adds .kopen) */
#kali-connect-modal { display:none !important; }
#kali-connect-modal.kopen {
  display:flex !important; flex-direction:column !important;
  position:fixed !important; top:50%; left:50%; transform:translate(-50%,-50%);
  z-index:10002 !important; width:min(400px,92vw) !important; max-width:400px !important;
  height:auto !important; max-height:none !important; gap:0 !important;
  border:1px solid rgba(214,85,46,.5) !important; border-radius:16px !important;
  background:var(--background-fill-primary, #17130f) !important;
  box-shadow:0 24px 70px rgba(0,0,0,.6) !important; padding:0 !important;
  overflow:visible !important; animation:kali-pop .16s ease; }
#kali-connect-modal.kopen::before { content:''; position:fixed; inset:0;
  background:rgba(0,0,0,.6); backdrop-filter:blur(2px); z-index:-1; }
@keyframes kali-pop { from{opacity:0; transform:translate(-50%,-46%) scale(.97)} to{opacity:1; transform:translate(-50%,-50%) scale(1)} }
/* force every inner Gradio block to actually lay out (they otherwise collapse to a line) */
#kali-connect-modal.kopen > *, #kali-connect-modal.kopen .block,
#kali-connect-modal.kopen .form, #kali-connect-modal.kopen .gap, #kali-connect-modal.kopen .wrap {
  display:block !important; width:100% !important; min-height:0 !important; min-width:0 !important;
  background:transparent !important; border:none !important; box-shadow:none !important; }
#kali-connect-modal.kopen .ref-head { display:flex !important; align-items:center !important; gap:8px !important;
  padding:13px 15px !important; font-size:13.5px !important; font-weight:700 !important;
  border-bottom:1px solid var(--border-color-primary) !important;
  background:rgba(214,85,46,.12) !important; border-radius:16px 16px 0 0 !important; }
#kali-connect-body { display:flex !important; flex-direction:column !important; gap:11px !important; padding:15px !important; }
#kali-connect-body > * { width:100% !important; }
#kali-user textarea, #kali-user input, #kali-pass textarea, #kali-pass input {
  display:block !important; width:100% !important; min-height:42px !important; font-size:14px !important;
  border:1px solid var(--border-color-primary) !important; border-radius:9px !important;
  padding:9px 12px !important; box-sizing:border-box !important;
  background:var(--block-background-fill) !important; color:var(--body-text-color) !important; }
#kali-connect-btns { display:flex !important; gap:8px !important; flex-wrap:nowrap !important; }
#kali-connect-btns > * { flex:1 1 0 !important; }
#kali-connect-btns button { width:100% !important; min-height:40px !important; border-radius:9px !important; }
#kali-modal-close { margin-top:2px !important; }
#kali-modal-close button { width:100% !important; min-height:38px !important; border-radius:9px !important; }
#kali-connect-hint, #kali-connect-hint * { font-size:11px !important; color:var(--body-text-color-subdued) !important; }

/* most-powerful arsenal card */
#kali-power { border:1px solid #d6552e !important; border-radius:13px !important;
  background:linear-gradient(135deg, rgba(214,85,46,.08), rgba(214,85,46,.02)) !important; padding:13px 14px !important; }
#kali-power .block { border:none !important; background:transparent !important; padding:0 !important; }
.kp-head { display:flex; align-items:center; gap:11px; }
.kp-ico { font-size:1.6rem; }
.kp-title { font-weight:700; font-size:1rem; }
.kp-sub { font-size:.76rem; color:var(--body-text-color-subdued); margin-top:2px; line-height:1.45; }
#kali-power-btns { gap:8px !important; margin-top:10px; flex-wrap:wrap; }
#kali-power-btns .gr-button { flex:1 1 auto; min-height:34px !important; }

/* installer accordion */
#kali-installer { border-radius:13px !important; }

/* responsive — stacks on phones/tablets */
@media (max-width: 860px) {
  #kali-main { flex-direction:column !important; }
  #kali-term-col, #kali-ref-col { flex:1 1 100% !important; width:100% !important;
    position:static !important; height:auto !important; }
  #kali-out { flex:0 0 auto !important; }
  #kali-out textarea { font-size:12px !important; height:58vh !important; }
  #kali-ref { flex:0 0 auto !important; }
  #kali-ref-view { flex:0 0 auto !important; max-height:50vh !important; }
}
</style>"""


_DESK = {}   # components of the Kali Desktop launcher (filled by build, used by wire_tab)

# Opens (or focuses) the desktop tab synchronously on the user's click — so pop-up blockers
# allow it — and shows a "starting…" screen until the real desktop URL arrives.
_DESK_OPEN_JS = """() => {
  const w = window.open('', 'nanban-kali-desktop');
  if (!w) { alert('Pop-up blocked. Allow pop-ups for Nanban, then click again.'); return; }
  let blank = false;
  try { blank = (!w.location.href || w.location.href === 'about:blank'); } catch (e) { blank = false; }
  if (blank) {
    w.document.open();
    w.document.write('<!doctype html><title>Kali Linux — starting…</title><body style="margin:0;background:radial-gradient(1200px 600px at 50% 40%,#0f1a22 0%,#05080b 70%);color:#d9e2ec;font:15px system-ui,Segoe UI,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;flex-direction:column;gap:12px;text-align:center"><div style="font-size:64px">\U0001F409</div><div style="font-size:20px;font-weight:700">Starting your Kali Linux desktop…</div><div style="color:#8a96a3;font-size:13px">Real Kali XFCE desktop · first start takes about 10 seconds</div><div style="width:26px;height:26px;border:3px solid #223040;border-top-color:#2bd4bd;border-radius:50%;animation:r 1s linear infinite"></div><style>@keyframes r{to{transform:rotate(360deg)}}</style></body>');
    w.document.close();
  }
  w.focus();
  window.__kaliDesk = w;
}"""

_DESK_NAV_JS = """(u) => {
  const w = window.__kaliDesk;
  if (!u) {
    try { if (w && !w.closed) { w.document.body.innerHTML = '<div style="font-size:60px">\U0001F409</div><div style="font-size:18px;font-weight:700">Kali desktop could not start</div><div style="color:#8a96a3;max-width:520px">See the message in the Nanban \U0001F409 Kali tab (this window can be closed).</div>'; } } catch (e) {}
    return;
  }
  const full = u + (u.includes('?') ? '&' : '?') + 'back=' + encodeURIComponent(location.href);
  try { if (w && !w.closed) { w.location.replace(full); w.focus(); return; } } catch (e) {}
  const n = window.open(full, 'nanban-kali-desktop'); if (n) n.focus();
}"""


def open_desktop():
    """Start the real Kali desktop (idempotent) → (status markdown, url or '')."""
    import kali_desktop
    ok, msg = kali_desktop.start()
    if ok:
        return (f"🟢 Kali Desktop running — [open it ↗]({kali_desktop.url()}) "
                f"(real Kali XFCE in your browser · click inside to type)"), kali_desktop.url()
    return f"🔴 {msg}", ""


def wire_tab(tab) -> None:
    """Pressing the 🐉 Kali tab itself opens the full-page Kali desktop."""
    if not _DESK:
        return
    tab.select(open_desktop, None, [_DESK["status"], _DESK["url"]], js=_DESK_OPEN_JS).then(
        None, _DESK["url"], None, js=_DESK_NAV_JS)


def build() -> None:
    import kali_desktop
    kali_desktop.start_background()           # warm the real desktop up while the app loads
    with gr.Column(elem_id="kali-wrap"):
        gr.HTML(_KALI_CSS)
        _is_on = connected()

        # ---- 🖥️ Kali Desktop — the real Kali OS, full page ----
        with gr.Group(elem_id="kali-desk"):
            with gr.Row(elem_id="kali-desk-bar"):
                gr.HTML('<div class="kd-txt"><div class="kd-ico">🖥️</div><div>'
                        '<div class="kd-title">Kali Desktop — the real Kali Linux OS, full screen</div>'
                        '<div class="kd-sub">Top panel, app menu, File Manager, Terminal, every tool — '
                        'opens in its own browser tab. Press the 🐉 Kali tab or this button.</div></div></div>',
                        elem_id="kali-desk-txt")
                desk_btn = gr.Button("🖥️ Open Kali Desktop ↗", variant="primary", size="sm", elem_id="kali-desk-btn")
            desk_status = gr.Markdown("", elem_id="kali-desk-status")
            desk_url = gr.Textbox(visible=False, elem_id="kali-desk-url")
        _DESK.update(btn=desk_btn, status=desk_status, url=desk_url)
        desk_btn.click(open_desktop, None, [desk_status, desk_url], js=_DESK_OPEN_JS).then(
            None, desk_url, None, js=_DESK_NAV_JS)

        with gr.Row(elem_id="kali-head"):
            gr.Markdown("### 🐉 Kali Linux — terminal + AI, together", elem_id="kali-title")
            connect_toggle = gr.Button(
                "🟢 Kali connected" if _is_on else "🔌 Connect Kali",
                size="sm", elem_id="kali-connect-toggle",
                elem_classes=["kali-ct", "on"] if _is_on else ["kali-ct"])
        status = gr.Markdown(status_line(), elem_id="kali-status")

        # ---- Connect Kali — modal dialog (opened from the header button) ----
        with gr.Group(elem_id="kali-connect-modal") as connect_modal:
            gr.HTML('<div class="ref-head"><span class="ref-ico">🔌</span>'
                    '<span>Connect Kali</span></div>', elem_id="kali-connect-title")
            with gr.Column(elem_id="kali-connect-body"):
                k_user = gr.Textbox(show_label=False, container=False, value=_known_kali_user(),
                                    placeholder="Kali username (e.g. nanbanlinux)", elem_id="kali-user")
                k_pass = gr.Textbox(show_label=False, container=False, type="password", value=_known_kali_pass(),
                                    placeholder="Password", elem_id="kali-pass")
                with gr.Row(elem_id="kali-connect-btns"):
                    connect_btn = gr.Button("🔌 Connect", variant="primary", size="sm")
                    recheck_btn = gr.Button("↻ Re-check", variant="secondary", size="sm")
                close_btn = gr.Button("✕ Close", variant="secondary", size="sm", elem_id="kali-modal-close")
                gr.Markdown("Install Kali in the 🛡️ **Security** tab → `sudo service ssh start` → connect.",
                            elem_id="kali-connect-hint")

        with gr.Row(equal_height=False, elem_id="kali-main"):
            # ---- left: terminal (bigger) + AI ----
            with gr.Column(scale=5, elem_id="kali-term-col"):
                with gr.Group(elem_id="kali-term"):
                    with gr.Row(elem_id="kali-term-head"):
                        gr.HTML('<div class="term-chrome"><span class="dot r"></span>'
                                '<span class="dot y"></span><span class="dot g"></span>'
                                '<span class="term-name">nanban — terminal</span></div>',
                                elem_id="kali-term-chrome")
                        target = gr.Radio(choices=[("🐉 Kali", KALI), ("🖥️ This PC", "local")],
                                          value=KALI if connected() else "local", show_label=False,
                                          container=False, elem_id="kali-target")
                        ctrlc_btn = gr.Button("■ Stop", size="sm", elem_id="kali-ctrlc")
                    term_out = gr.Textbox(show_label=False, lines=13, max_lines=26, interactive=False,
                                          elem_id="kali-out", buttons=["copy"], container=False,
                                          value="# Type a command below, or ask the AI (Tanglish). Output appears here.")
                    term_in = gr.Textbox(placeholder="command…  (e.g. nmap -sV 127.0.0.1)", show_label=False,
                                         container=False, submit_btn="Run", lines=1, elem_id="kali-in")
                with gr.Group(elem_id="kali-ai"):
                    gr.HTML(
                        '<div class="ais-head">'
                        '<div class="ais-ico">🤖</div>'
                        '<div class="ais-txt"><div class="ais-title">AI Shell '
                        '<span class="ais-badge">Tanglish</span></div>'
                        '<div class="ais-sub">Sollu → Nanban command convert panni run pannum. '
                        'Lab/local auto · veliya target confirm kekkum.</div></div></div>',
                        elem_id="kali-ai-label")
                    with gr.Row():
                        ai_in = gr.Textbox(placeholder="e.g. 127.0.0.1 la open ports scan pannu  /  ella tools install pannu",
                                           show_label=False, container=False, scale=4, elem_id="kali-ai-in")
                        ai_btn = gr.Button("⚡ Run", variant="primary", scale=1, size="sm")
                    ai_auto = gr.Checkbox(value=True, label="⚡ Auto-run on safe/lab targets", container=False)

            # ---- right: command dictionary (same height as the terminal, scrollable) ----
            with gr.Column(scale=2, elem_id="kali-ref-col"):
                with gr.Group(elem_id="kali-ref"):
                    gr.HTML('<div class="ref-head"><span class="ref-ico">📖</span>'
                            '<span>Command Reference</span>'
                            '<span class="ref-hint">👆 tap a command to load it</span></div>',
                            elem_id="kali-ref-title")
                    ref_search = gr.Textbox(placeholder="🔍  Look up a tool…  (nmap, sql, wifi, metasploit)",
                                            show_label=False, container=False, elem_id="kali-ref-search")
                    ref_view = gr.Markdown(
                        "_Every command you run is explained here automatically — in English and Tanglish. "
                        "Or search any tool above. **Tap any command to drop it into the terminal.**_",
                        elem_id="kali-ref-view")

        # ---- Toolset installer ----
        import kali_installer
        with gr.Group(elem_id="kali-power"):
            gr.HTML(
                '<div class="kp-head"><span class="kp-ico">⭐</span>'
                '<div><div class="kp-title">Most Powerful Arsenal — one click</div>'
                f'<div class="kp-sub">{kali_installer.POWERFUL_TOOLS}</div></div></div>')
            with gr.Row(elem_id="kali-power-btns"):
                power_btn = gr.Button("🚀 Install full arsenal on Kali", variant="primary", size="sm")
                power_copy = gr.Button("📋 Just show the command", variant="secondary", size="sm")
        with gr.Accordion("🧰 Toolset Installer — pick bundles / categories (official metapackages)",
                          open=False, elem_id="kali-installer"):
            gr.HTML(kali_installer.installer_html())

        # ---- wiring ----
        def _toggle_update():
            on = connected()
            return gr.update(value="🟢 Kali connected" if on else "🔌 Connect Kali",
                             elem_classes=["kali-ct", "on"] if on else ["kali-ct"])

        # Opening/closing the dialog is done in the browser (INIT_JS) via a CSS class —
        # instant, and it can't miss. The buttons below only do the actual work.
        _close_js = "() => { const m = document.querySelector('#kali-connect-modal'); if (m) m.classList.remove('kopen'); }"
        connect_btn.click(connect_kali, [k_user, k_pass], status).then(
            lambda: gr.update(value=KALI if connected() else "local"), None, target).then(
            _toggle_update, None, connect_toggle).then(None, None, None, js=_close_js)
        recheck_btn.click(status_line, None, status).then(_toggle_update, None, connect_toggle)
        term_in.submit(run, [term_in, target], [term_out, ref_view]).then(lambda: "", None, term_in)
        ctrlc_btn.click(kali_interrupt, None, term_out)
        ai_btn.click(ai_shell, [ai_in, ai_auto, target], [term_in, term_out, ref_view]).then(
            lambda: "", None, ai_in)
        ai_in.submit(ai_shell, [ai_in, ai_auto, target], [term_in, term_out, ref_view]).then(
            lambda: "", None, ai_in)
        ref_search.change(lookup, ref_search, ref_view)

        def _install_arsenal():
            import kali_installer
            import kali_desktop
            cmd = kali_installer.POWERFUL_CMD
            # Preferred: WSL Kali on this PC → run detached inside Kali (keeps going even if this
            # tab is closed) and stream its log here. Falls back to the SSH command otherwise.
            if kali_desktop.available():
                ok, msg = kali_desktop.arsenal_start()
                head = "$ nanban-arsenal   (kali-linux-large · seclists · nuclei · bloodhound · netexec)"
                if not ok:
                    yield cmd, f"{head}\n\n🔴 {msg}", ""
                    return
                note = ("⏳ Already running — showing live progress." if msg == "already running"
                        else "⏳ Started inside Kali (detached). Periya download — 20-40 min aagum. "
                             "Tab close pannaalum install nikkaadhu.")
                yield cmd, f"{head}\n{note}\n", ""
                for _ in range(1800):          # up to ~90 min of live log
                    time.sleep(3)
                    log = kali_desktop.arsenal_log(45)
                    yield cmd, f"{head}\n{note}\n\n{log}", ""
                    if "=== DONE" in log:
                        yield cmd, (f"{head}\n\n{log}\n\n✅ Full arsenal installed. Ella tools-um 🖥️ Kali Desktop "
                                    "menu-la (01 Information Gathering … 13 Social Engineering) ready."), ""
                        return
                    if not kali_desktop.arsenal_running() and "=== DONE" not in log:
                        yield cmd, f"{head}\n\n{log}\n\n🟠 Installer stopped before finishing — press the button again to resume.", ""
                        return
                return
            if not connected():
                yield (cmd, f"$ {cmd}\n\n🟠 Kali connect pannala. Right side la **Connect** pannu, "
                       "apuram indha button press pannu — illa indha command-ah copy panni un Kali la "
                       "manual-ah paste pannu.", "")
                return
            yield cmd, f"$ {cmd}\n⏳ Installing the full arsenal on Kali… (periya download — konja neram aagum)", ""
            for out in run_on_kali(cmd):
                yield cmd, f"$ {cmd}\n{out}", ""

        def _show_arsenal():
            import kali_installer
            cmd = kali_installer.POWERFUL_CMD
            return (cmd, f"$ {cmd}\n\n📋 Indha command-ah copy panni un Kali / WSL terminal la paste pannu. "
                    "Ella powerful tools-um install aagidum.", "")

        power_btn.click(_install_arsenal, None, [term_in, term_out, ref_view])
        power_copy.click(_show_arsenal, None, [term_in, term_out, ref_view])
