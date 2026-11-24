"""
🕶️ Dark Lab tab — the Kali Linux 2027 wishlist, made real.

Two separate menus in the left nav:
  🧅 Terminal   — the dark-osint Tor browser: onion search, open .onion pages over
                  Tor as text, Tor check, and the 15 OSINT terminal commands.
  🐉 Kali Tools — four live tools, each run on the real Kali box and explained by
                  Nanban's own AI:
                    🌐 OSINT & Threat Intel (kali-intel)
                    🗺️ Nmap 2.0 visual      (nmap2)
                    🔬 Digital Forensics     (kali-forensics)
                    🎯 Pentest Agent         (kali-pentest)

AI runs on this machine through the app's engine, so it uses the same model the
rest of Nanban uses. For authorized research and education only.
"""

import gradio as gr

import dark_lab_tools as dlt

_CSS = """<style>
#dl-hero { border-radius: 22px !important; padding: 24px 22px !important; text-align: center;
  background: radial-gradient(720px 240px at 15% -30%, rgba(255,59,78,.30), transparent 60%),
    radial-gradient(720px 260px at 90% 130%, rgba(120,20,30,.35), transparent 60%),
    linear-gradient(135deg, #0b0d12 0%, #15181f 60%, #0b0d12 100%) !important;
  border: 1px solid #2a1116; box-shadow: 0 16px 46px rgba(0,0,0,.45); color: #e7e9ee !important; }
#dl-hero .dl-badge { display:inline-block; font-size:.72rem; letter-spacing:.14em; font-weight:800;
  padding:5px 12px; border-radius:999px; margin-bottom:10px; background:rgba(255,59,78,.16);
  border:1px solid #5a1d24; color:#ff6b78 !important; }
#dl-hero h1 { margin:2px 0 8px !important; font-size:1.8rem !important; font-weight:800 !important;
  letter-spacing:-.02em !important; color:#fff !important; }
#dl-hero h1 b { color:#ff3b4e !important; }
#dl-hero p { margin:0 auto 4px; max-width:680px; color:#aab0be !important; font-size:.94rem; }
#dl-term textarea, #dl-oterm textarea { background:#0b0d12 !important; color:#cdd3df !important;
  font-family: ui-monospace, Menlo, Consolas, monospace !important; font-size:12.5px !important;
  border:1px solid #1f2430 !important; border-radius:12px !important; }
.dl-ai { border:1px solid #3a1d1d; border-radius:14px; padding:4px 18px; margin-top:6px;
  background:linear-gradient(135deg, rgba(255,59,78,.06), rgba(120,20,30,.05)); }
.dl-ai h3:first-child { color:#ff3b4e; }
.dl-safe { font-size:.82rem; color:#caa; background:rgba(255,59,78,.08);
  border:1px solid #3a1d1d; border-radius:12px; padding:9px 13px; margin-top:8px; }
.dl-run button { font-weight:700 !important; }
</style>"""

_HERO = _CSS + """
<div id="dl-hero">
  <span class="dl-badge">KALI 2027 · MADE REAL</span>
  <h1>🕶️ <b>Dark Lab</b></h1>
  <p>🧅 <b>Terminal</b> = dark-osint Tor browser &nbsp;·&nbsp; 🐉 <b>Kali Tools</b> = OSINT · Nmap 2.0 · Forensics · Pentest.
  Real Kali-la live run aagum, Nanban AI explain pannum.</p>
</div>"""

_KALI_CHOICES = [(f"{m['icon']} {m['label']}", k) for k, m in dlt.TOOLS.items()]
_TERM_CHOICES = [(f"{m['icon']} {m['label']}", k) for k, m in dlt.TERMINAL_ACTIONS.items()]


# ───────────────────────────────────────────── 🐉 Kali Tools

def _kali_target_update(tool_key):
    t = dlt.TOOLS.get(tool_key, dlt.TOOLS["intel"])
    return (gr.update(label=t["tlabel"], placeholder=t["ph"]),
            gr.update(visible=(tool_key == "pentest")))


def _kali_run(tool_key, target, authok):
    if tool_key == "pentest" and not authok:
        yield ("⛔ Pentest-ku: 'I have written authorization' box-a tick pannu, apram Run pannu.\n"
               "Scanning without permission is illegal.")
        return
    yield from dlt.run_tool(tool_key, target)


def _kali_analyze(tool_key, target, transcript):
    if not (transcript or "").strip() or transcript.strip().startswith(("⛔", "🟠")):
        yield "_Run mudinjadhuma AI analysis inga varum._"
        return
    yield "🧠 _AI analysing the result…_"
    yield from dlt.ai_analyze(tool_key, target, transcript)


def _build_kali_tools():
    tool = gr.Radio(_KALI_CHOICES, value="intel", label="Tool")
    target = gr.Textbox(label=dlt.TOOLS["intel"]["tlabel"],
                        placeholder=dlt.TOOLS["intel"]["ph"], lines=1)
    authok = gr.Checkbox(False, label="🎯 I have WRITTEN authorization to test this target",
                         visible=False)
    with gr.Row():
        run_btn = gr.Button("▶ Run on Kali", variant="primary", elem_classes="dl-run", scale=2)
        clear_btn = gr.Button("Clear", scale=1)
    term = gr.Textbox(label="Live terminal (real Kali)", lines=16, elem_id="dl-term", interactive=False)
    with gr.Group(elem_classes="dl-ai"):
        gr.Markdown("### 🧠 AI Analysis")
        ai_md = gr.Markdown("_Tool run pannadhum, Nanban AI result-a inga explain pannum._")
    gr.HTML('<div class="dl-safe">⚖️ Authorized research & education mattum. Reports Kali-la '
            '<code>~/nanban-kit/case/reports/</code>-la (HTML + Markdown, SHA-256 logged) save aagum.</div>')

    tool.change(_kali_target_update, tool, [target, authok])
    run_evt = run_btn.click(_kali_run, [tool, target, authok], term)
    run_evt.then(_kali_analyze, [tool, target, term], ai_md)
    clear_btn.click(lambda: ("", "_Cleared._"), None, [term, ai_md])


# ───────────────────────────────────────────── 🧅 Terminal (dark-osint Tor browser)

def _term_input_update(action_key):
    a = dlt.TERMINAL_ACTIONS.get(action_key, dlt.TERMINAL_ACTIONS["search"])
    return gr.update(label=a["tlabel"] or "(no input needed)", placeholder=a["ph"],
                     visible=bool(a["need"]) or a["tlabel"] != "")


def _term_run(action_key, arg):
    yield from dlt.run_terminal(action_key, arg)


def _term_analyze(action_key, arg, transcript):
    if not (transcript or "").strip() or transcript.strip().startswith(("⛔", "🟠", "Give", "unknown")):
        yield "_Run mudinjadhuma AI explanation inga varum._"
        return
    yield "🧠 _AI explaining…_"
    yield from dlt.ai_analyze_terminal(action_key, arg, transcript)


def _build_terminal():
    gr.Markdown("#### 🧅 dark-osint — Tor terminal browser\n"
                "_Everything routes through the real Tor network. No JavaScript, session-only cookies._")
    action = gr.Radio(_TERM_CHOICES, value="search", label="Action")
    arg = gr.Textbox(label=dlt.TERMINAL_ACTIONS["search"]["tlabel"],
                     placeholder=dlt.TERMINAL_ACTIONS["search"]["ph"], lines=1)
    with gr.Row():
        run_btn = gr.Button("▶ Run over Tor", variant="primary", elem_classes="dl-run", scale=2)
        clear_btn = gr.Button("Clear", scale=1)
    out = gr.Textbox(label="Tor terminal (real Kali)", lines=16, elem_id="dl-oterm", interactive=False)
    with gr.Group(elem_classes="dl-ai"):
        gr.Markdown("### 🧠 AI Explanation")
        ai_md = gr.Markdown("_Run pannadhum, Nanban AI result-a inga explain pannum._")
    gr.HTML('<div class="dl-safe">🧅 For authorized dark-web research & threat intel only — '
            'avoid illegal markets/content. Full interactive browser venumna Kali desktop terminal-la '
            '<code>dark-osint</code> type pannu. Evidence <code>~/dark-osint/case/</code>-la save aagum.</div>')

    action.change(_term_input_update, action, arg)
    run_evt = run_btn.click(_term_run, [action, arg], out)
    run_evt.then(_term_analyze, [action, arg, out], ai_md)
    clear_btn.click(lambda: ("", "_Cleared._"), None, [out, ai_md])


def build():
    gr.HTML(_HERO)
    with gr.Tabs():
        with gr.TabItem("🧅 Terminal"):
            _build_terminal()
        with gr.TabItem("🐉 Kali Tools"):
            _build_kali_tools()
