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

def _known_kali_user() -> str:
    """Best guess for the Kali username, to prefill the connect form.
    Prefers the one already saved; otherwise asks WSL for its default user."""
    try:
        import json
        reg = json.loads((config.DATA_DIR / "servers.json").read_text("utf-8"))
        u = (reg.get(KALI, {}).get("user") or "").strip()
        if u:
            return u
    except Exception:
        pass
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
    servers.add(KALI, f"{username}@127.0.0.1", password=password or "", save_password=False)
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


def run_on_kali(command: str):
    """Stream output from a command executed on the Kali box over SSH."""
    command = (command or "").strip()
    if not command:
        yield ""
        return
    if _blocked(command):
        yield "⚠ Blocked: this looks like it could wipe the disk or crash the box. Not run."
        return
    try:
        host = servers.connect(KALI)
    except Exception as e:
        yield f"🟠 Kali not reachable: {e}\nStart SSH in Kali (`sudo service ssh start`) and reconnect."
        return
    lines: list[str] = []
    result: dict = {}

    def worker():
        r = host.run(command, timeout=config.COMMAND_TIMEOUT, on_line=lines.append)
        result["code"] = r.code

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    shown = 0
    while t.is_alive():
        if len(lines) != shown:
            shown = len(lines)
            yield "\n".join(lines)
        time.sleep(0.12)
    t.join()
    code = result.get("code", 0)
    yield "\n".join(lines) + f"\n\n[exit code {code}]  ·  {host.display_cwd()}"


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
    yield cmd, f"$ {cmd}\n⏳ Running on {'Kali' if target == KALI else 'this PC'}…", ref
    for out, r in run(cmd, target):
        yield cmd, f"$ {cmd}\n{out}", r


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
#kali-head { align-items:center !important; justify-content:space-between !important; flex-wrap:nowrap !important; gap:8px; }
#kali-head #kali-title { flex:1 1 auto; }
#kali-connect-toggle { flex:0 0 auto !important; min-height:32px !important; height:32px; border-radius:9px !important;
  font-size:12.5px !important; font-weight:600 !important; padding:0 14px !important; white-space:nowrap; }
.kali-ct.on button, #kali-connect-toggle.on { border-color:#27c93f !important; }

#kali-main { gap: 12px !important; align-items: flex-start !important;
  flex-direction: row !important; flex-wrap: nowrap !important; }
#kali-term-col { flex: 3 1 0 !important; min-width: 0 !important; gap: 10px !important;
  position: sticky; top: 8px; align-self: flex-start; }
#kali-ref-col { flex: 1.4 1 0 !important; min-width: 0 !important; gap: 10px !important;
  position: sticky; top: 8px; align-self: flex-start; }

/* terminal window */
#kali-term { background:#0c0a07 !important; border:1px solid #2a2420 !important; border-radius:14px !important;
  padding:0 !important; overflow:hidden; box-shadow:0 8px 28px rgba(0,0,0,.28); }
#kali-term-head { align-items:center !important; justify-content:space-between !important; padding:8px 12px !important;
  background:#161210 !important; border-bottom:1px solid #2a2420; gap:8px; }
#kali-term-head > *:first-child { flex:1 1 auto !important; min-width:0; width:auto !important; }
#kali-term-head > *:last-child { flex:0 0 auto !important; width:auto !important; }
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
#kali-connect-modal.kopen { display:block !important; position:fixed !important; top:50%; left:50%;
  transform:translate(-50%,-50%); z-index:10002 !important; width:min(392px,92vw) !important; max-width:392px !important;
  border:1px solid var(--border-color-primary) !important; border-radius:16px !important;
  background:var(--block-background-fill) !important; box-shadow:0 24px 70px rgba(0,0,0,.55) !important;
  padding:0 !important; overflow:visible; animation:kali-pop .16s ease; }
#kali-connect-modal.kopen::before { content:''; position:fixed; inset:0; background:rgba(0,0,0,.55);
  backdrop-filter:blur(2px); z-index:-1; }
@keyframes kali-pop { from{opacity:0; transform:translate(-50%,-46%) scale(.97)} to{opacity:1; transform:translate(-50%,-50%) scale(1)} }
#kali-modal-close { margin-top:4px !important; }
#kali-modal-close button { width:100% !important; }

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
    position:static !important; }
  #kali-out textarea { font-size:12px !important; }
  #kali-ref-view { max-height:420px !important; }
}
</style>"""


def build() -> None:
    with gr.Column(elem_id="kali-wrap"):
        gr.HTML(_KALI_CSS)
        _is_on = connected()
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
                k_pass = gr.Textbox(show_label=False, container=False, type="password",
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
        ai_btn.click(ai_shell, [ai_in, ai_auto, target], [term_in, term_out, ref_view]).then(
            lambda: "", None, ai_in)
        ai_in.submit(ai_shell, [ai_in, ai_auto, target], [term_in, term_out, ref_view]).then(
            lambda: "", None, ai_in)
        ref_search.change(lookup, ref_search, ref_view)

        def _install_arsenal():
            import kali_installer
            cmd = kali_installer.POWERFUL_CMD
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
