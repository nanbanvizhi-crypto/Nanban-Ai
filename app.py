"""
Browser chat app for your local AI agent, also used from your phone.
Run:  python app.py   (or double-click start.bat)  ->  opens http://127.0.0.1:7860
      python app.py --no-browser   (used by the tray launcher)
"""

import io
import shutil
import sys
from pathlib import Path

import gradio as gr

import config
import docs_rag
import tools
import vpn
import llm
import security_hub
import web_computer
from agent_core import Agent

COMPUTER_MODE = {
    "label": "🖥️ Computer",
    "about": "Runs commands and edits files on the laptop, like the Nanban Terminal. Switch on 'Allow actions' first.",
}

EXAMPLES = {
    "vizhi": ["Vizhi, indha naal epdi irukku-nu sollu",
              "Enaku konjam encourage pannu, naan stress-la iruken",
              "Naalaiku enna plan pannalaam?"],
    "assistant": ["Naalaiku 5 manikku supplier-a call pannanum, task-a add pannu",
                  "En to-do list kaattu",
                  "1850 rupees-la 18% GST evlo?"],
    "coding": ["Python-la oru simple calculator program ezhudhi explain pannu",
               "What's the difference between a list and a tuple in Python?",
               "HTML + CSS-la oru login page design pannu"],
    "writing": ["Leave letter ezhudhu - 2 days fever, formal-a",
                "Write a LinkedIn post announcing my new restaurant app",
                "Indha paragraph-a Tamil-la translate pannu: Consistency beats talent."],
    "research": ["What are the latest developments in electric vehicles in India?",
                 "Chennai-la best co-working spaces evlo cost aagum?",
                 "Compare Ollama and LM Studio with sources"],
    "study": ["En documents-la enna irukku?",
              "Chapter 3-oda important points summary kudu",
              "Photosynthesis-la oru 5 question quiz vei"],
    "business": ["Oru chinna cloud kitchen start panna evlo selavu aagum?",
                 "Give me 5 marketing ideas for a small resort with a low budget",
                 "Price ₹120, cost ₹70, monthly 900 orders - profit evlo?"],
    "computer": ["Indha folder-la enna irukku?",
                 "Laptop-la disk space evlo free irukku?",
                 "Oru Python script ezhudhi run pannu: 1 to 100 prime numbers print pannanum"],
    "security": ["Explain SQL injection like a beginner",
                 "What nmap command to scan my lab, and explain each flag",
                 "How do I start privilege escalation on a Linux box I own?"],
}


# ---------------------------------------------------------------- side panels

def username_of(request) -> str:
    """Login name on the Nanban Server; '' when running without logins."""
    try:
        return (request.username or "") if request is not None else ""
    except Exception:
        return ""


def memory_markdown(user: str = "") -> str:
    facts = tools.load_memory(user)
    if not facts:
        return "_Nothing saved yet. Say “remember that…” in any chat._"
    return "\n".join(f"{i}. {fact}" for i, fact in enumerate(facts, 1))


def tasks_markdown(user: str = "") -> str:
    text = tools.list_tasks(user=user)
    return "_No pending tasks._" if text.startswith("The to-do list is empty") else text.replace("\n", "  \n")


def documents_markdown() -> str:
    files = [p.name for p in docs_rag.document_files()]
    return "\n".join(f"- {name}" for name in files) if files else "_No documents yet._"


def mode_markdown(mode: str) -> str:
    about = COMPUTER_MODE["about"] if mode == "computer" else config.MODES[mode]["about"]
    return about


def status_markdown() -> str:
    lines = [vpn.badge()]
    if getattr(web_computer, "SERVER_MODE", False):
        lines.append(f"🌐 `{web_computer.lan_ip()}:{config.SERVER_PORT}`")
        lines.append("🔌 API `/v1` · docs `/docs`")
    elif config.LAN_ACCESS:
        lines.append(f"📱 `{web_computer.lan_ip()}:{config.WEB_PORT}` · login **nanban**")
    else:
        lines.append("📱 Phone access off")
    lines.append(f"🧠 `{llm.describe()}`")
    return "  \n".join(lines)


def phone_qr_image():
    if not config.LAN_ACCESS:
        return None
    import qrcode
    buffer = io.BytesIO()
    qrcode.make(f"http://{web_computer.lan_ip()}:{config.WEB_PORT}").save(buffer, format="PNG")
    buffer.seek(0)
    from PIL import Image
    return Image.open(buffer)


# ---------------------------------------------------------------- chat

ACTIVE: dict[str, float] = {}   # user -> last activity time (for the admin page)


def respond(user_text, display, agents, mode, allow_actions, image_path=None, request: gr.Request = None):
    user_text = (user_text or "").strip()
    images = None
    if image_path:
        import base64
        import mimetypes
        try:
            raw = open(image_path, "rb").read()
            mime = mimetypes.guess_type(image_path)[0] or "image/png"
            images = [f"data:{mime};base64," + base64.b64encode(raw).decode()]
            if not user_text:
                user_text = "Indha image-la enna irukku? Describe panni, question irundha answer pannu."
        except Exception:
            images = None
    if not user_text and not images:
        yield gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip()
        return

    user = username_of(request)
    ACTIVE[user or "local"] = __import__("time").time()
    agents = agents or {}
    if mode == "computer":
        if user and config.USERS and user not in config.ADMIN_USERS:
            display = list(display or []) + [{"role": "user", "content": user_text},
                                             {"role": "assistant", "content": "🔒 Computer mode is for admin users only on this server."}]
            yield "", display, display, agents, gr.skip(), gr.skip()
            return
        web_computer.host.allow_actions = bool(allow_actions)
        agent = agents.setdefault("computer", web_computer.WebComputerAgent(user))
    else:
        agent = agents.setdefault("chat", Agent(mode, user=user))
        agent.mode = mode
    shown_text = user_text + ("  🖼️ _(image attached)_" if images else "")
    display = list(display or []) + [{"role": "user", "content": shown_text}]
    yield gr.Textbox(value="", submit_btn=False, stop_btn=True), display, display, agents, gr.skip(), gr.skip()

    text_index = None
    tool_index = None
    stream = agent.stream(user_text, images=images) if mode != "computer" else agent.stream(user_text)
    for event in stream:
        if event.kind == "text":
            if text_index is None:
                display.append({"role": "assistant", "content": ""})
                text_index = len(display) - 1
            display[text_index]["content"] += event.data
        elif event.kind == "tool_start":
            text_index = None
            args = ", ".join(f"{k}={v!r}" for k, v in event.data.items())
            display.append({
                "role": "assistant",
                "content": f"`{event.tool}({args[:300]})`",
                "metadata": {"title": tools.TOOL_LABELS.get(event.tool, f"🔧 {event.tool}"), "status": "pending"},
            })
            tool_index = len(display) - 1
        elif event.kind == "tool_end" and tool_index is not None:
            preview = str(event.data)
            preview = preview[:1200] + ("…" if len(preview) > 1200 else "")
            display[tool_index]["content"] += "\n\n" + preview
            display[tool_index]["metadata"]["status"] = "done"
        elif event.kind == "error":
            display.append({"role": "assistant", "content": f"⚠️ {event.data}"})
        yield gr.skip(), display, display, agents, gr.skip(), gr.skip()

    if mode == "computer" and web_computer.host.plan:
        display.append({"role": "assistant", "content": web_computer.plan_markdown(),
                        "metadata": {"title": "📋 Plan", "status": "done"}})
    display = [m for m in display if m["content"].strip() or m.get("metadata")]
    try:
        import usage
        usage.record(user, mode, llm.model_name())
    except Exception:
        pass
    yield gr.Textbox(submit_btn=True, stop_btn=False), display, display, agents, memory_markdown(user), tasks_markdown(user)


def new_chat(agents):
    for agent in (agents or {}).values():
        agent.reset()
    return [], [], agents


def change_mode(mode, agents):
    if agents and "chat" in agents and mode != "computer":
        agents["chat"].mode = mode
    return mode_markdown(mode), agents, gr.Dataset(samples=[[e] for e in EXAMPLES[mode]])


def run_terminal(command, backend):
    for output, cwd in web_computer.run_command_stream(command, backend):
        yield output, f"`{web_computer.shell.label()}` · `{cwd}`", gr.skip()
    yield gr.skip(), gr.skip(), ""


def explain_terminal(agents, allow_actions, request: gr.Request = None):
    """Ask the AI about the last command run in the Terminal tab."""
    agents = agents or {}
    web_computer.host.allow_actions = bool(allow_actions)
    agent = agents.setdefault("computer", web_computer.WebComputerAgent(username_of(request)))
    if not web_computer.host.last_command:
        return "Run a command first.", agents
    text = ""
    for event in agent.stream("Explain the result of the command I just ran in 2-5 lines. If it failed, give the "
                              "exact fixed command. Don't run anything."):
        if event.kind == "text":
            text += event.data
        elif event.kind == "error":
            text += f"⚠️ {event.data}"
    return text, agents


def upload_documents(files):
    for f in files or []:
        source = Path(f if isinstance(f, str) else f.name)
        if source.suffix.lower() in docs_rag.SUPPORTED:
            shutil.copy(source, config.DOCUMENTS_DIR / source.name)
    try:
        status = docs_rag.refresh_index()
    except Exception as e:
        status = f"Indexing failed: {e}. Is Ollama running and '{config.EMBED_MODEL}' downloaded?"
    return documents_markdown(), status, None


def clear_memory(request: gr.Request = None):
    user = username_of(request)
    tools.clear_memory(user)
    return memory_markdown(user)


def on_load(request: gr.Request = None):
    """Per-user refresh when the page opens: memory, tasks, status, admin tab visibility."""
    user = username_of(request)
    is_admin = (not config.USERS) or (user in config.ADMIN_USERS)
    show_security = getattr(config, "SECURITY_TAB", True) and security_hub.available()
    return (memory_markdown(user), tasks_markdown(user), status_markdown(), gr.update(visible=is_admin),
            gr.update(visible=is_admin), brand_html(user), topbar_html(), gr.update(visible=show_security),
            gr.update(visible=show_security), gr.update(visible=show_security), gr.update(visible=show_security))


# ---------------------------------------------------------------- layout

import base64

import ui_theme

CSS = ui_theme.CSS
ICON_B64 = base64.b64encode((config.BASE_DIR / "assets" / "nanban.png").read_bytes()).decode()

MODE_CHOICES = [(m["label"], key) for key, m in config.MODES.items()]
if config.WEB_COMPUTER_MODE:
    MODE_CHOICES.append((COMPUTER_MODE["label"], "computer"))


_SIDEBAR_CSS = """<style>
.sidebar .sidebar-content { display:flex !important; flex-direction:column !important; min-height:100dvh; }
.sidebar .sidebar-content > .column { flex:1 1 auto !important; display:flex !important; flex-direction:column !important; }
#status { margin-top:auto !important; border-top:1px solid var(--border-color-primary); padding:12px 10px 0 !important;
  font-size:12.5px; line-height:1.7; color:var(--body-text-color-subdued); }
</style>"""


def brand_html(user: str = "") -> str:
    who = f"<div class='sub'>👤 {user}</div>" if user else "<div class='sub'>Local · Private · Free</div>"
    # inline styles so the logo stays compact AND the status block pins to the sidebar bottom
    # (Gradio drops some css= rules in this build, so critical sidebar layout is inlined here)
    return (
        _SIDEBAR_CSS +
        "<div id='brand' style='display:flex;align-items:center;gap:10px;padding:0 2px 8px'>"
        f"<img src='data:image/png;base64,{ICON_B64}' alt='' "
        "style='width:42px;height:42px;min-width:42px;max-width:42px;border-radius:12px;margin:0;object-fit:cover'>"
        "<div style='display:flex;flex-direction:column;line-height:1.2'>"
        f"<div class='name' style='font-weight:700;font-size:17px'>{config.AGENT_NAME}</div>"
        f"{who}</div></div>")


def topbar_html() -> str:
    v = vpn.status()
    vpn_badge = "<span class='badge ok'>🛡️ VPN on</span>" if v["connected"] else "<span class='badge'>🛡️ VPN off</span>"
    server_badge = ("<span class='badge ok hide-sm'>🌐 Server</span>" if getattr(web_computer, "SERVER_MODE", False)
                    else ("<span class='badge ok hide-sm'>📱 Phone access</span>" if config.LAN_ACCESS else ""))
    # Main-content spacing tightener — scoped to .contain (the main column), NEVER the sidebar
    # (.sidebar uses .sidebar-content, so these rules can't touch it). Inlined because this
    # Gradio build drops some css= rules.
    spacing = (
        "<style>"
        # --- base spacing (scoped to main content, never the sidebar) ---
        ".contain > .column { gap: 9px !important; }"
        ".contain > .column > .tabs { margin-top: 0 !important; }"
        ".contain .tabs > .tab-wrapper, .contain .tabitem { padding-top: 8px !important; }"
        ".contain .html-container { padding-top: 2px !important; padding-bottom: 2px !important; }"
        ".contain .form { gap: 8px !important; }"
        ".contain .gap { gap: 9px !important; }"
        "#topbar { margin: 0 !important; }"
        # (Gradio has a native tab overflow menu for narrow screens — don't fight it.)
        # --- tablet / small laptop ---
        "@media (max-width: 760px){"
        " #modes label{ flex:1 1 46% !important; }"           # mode chips 2-up
        " #kali-main{ flex-direction:column !important; }"
        " #kali-term-col, #kali-ref-col{ flex:1 1 100% !important; width:100% !important; }"
        "}"
        # --- phone / iPhone ---
        "@media (max-width: 560px){"
        " .contain > .column{ gap:8px !important; padding:0 2px; }"
        " #topbar{ flex-wrap:wrap; gap:4px; }"
        " #modes label{ flex:1 1 100% !important; }"          # mode chips full width
        " .contain textarea, .contain input[type=text]{ font-size:16px !important; }"  # no iOS zoom-on-focus
        " .il-grid, .ki-grid, .gs-row{ grid-template-columns:1fr !important; }"
        " #img-controls > *, #il-filters > *{ flex:1 1 100% !important; }"
        " .il-hero h1{ font-size:1.4rem !important; }"
        " #kali-out textarea{ font-size:12px !important; }"
        # keep the Vizhi orb + tools comfortably in reach on phones
        " #nb-tools{ right:10px !important; bottom:84px !important; gap:7px !important; }"
        " #nb-vizhi{ width:52px !important; height:52px !important; font-size:23px !important; }"
        " #nb-tools button:not(#nb-vizhi){ width:38px !important; height:38px !important; font-size:16px !important; }"
        " #nb-jcap{ right:62px !important; bottom:150px !important; max-width:190px !important; font-size:12px !important; }"
        "}"
        "</style>")
    return (spacing +
            f"<div id='topbar'><div class='title'>{config.AGENT_NAME}</div><div class='badges'>"
            f"<span class='badge hide-sm'>🧠 {llm.describe()}</span>{server_badge}{vpn_badge}</div></div>")


def toggle_allow(mode):
    return gr.update(visible=(mode == "computer") and config.WEB_COMPUTER_MODE)


with gr.Blocks(title=f"{config.AGENT_NAME}", fill_height=True) as demo:
    agent_state = gr.State(None)
    display_state = gr.State([])

    with gr.Sidebar(open=True, width=280):
        hello_view = gr.HTML(brand_html())
        new_btn = gr.Button("＋  New chat", variant="secondary", elem_id="new-chat")
        with gr.Accordion("📚 Documents", open=False):
            gr.Markdown("_Study mode answers from these files._")
            docs_view = gr.Markdown(documents_markdown())
            upload = gr.File(label="Add PDF / Word / text", file_count="multiple", file_types=sorted(docs_rag.SUPPORTED), height=90)
            docs_status = gr.Markdown()
        with gr.Accordion("✅ To-do", open=False):
            tasks_view = gr.Markdown(tasks_markdown())
        with gr.Accordion("🧠 Memory", open=False):
            memory_view = gr.Markdown(memory_markdown())
            clear_mem_btn = gr.Button("Clear memory", size="sm")
        with gr.Accordion("📱 Phone", open=False, visible=config.LAN_ACCESS):
            gr.Image(value=phone_qr_image(), show_label=False, interactive=False, height=200, container=False)
            gr.Markdown("Scan on the same Wi-Fi, then **Add to Home Screen**.")
        status_view = gr.Markdown(status_markdown(), elem_id="status")

    topbar = gr.HTML(topbar_html())
    with gr.Tabs():
        with gr.Tab("💬 Chat"):
            with gr.Column(elem_id="chat-col"):
                mode = gr.Radio(choices=MODE_CHOICES, value=config.DEFAULT_MODE, show_label=False, container=False, elem_id="modes")
                mode_info = gr.Markdown(mode_markdown(config.DEFAULT_MODE), elem_id="mode-info")
                allow_actions = gr.Checkbox(label="⚡ Allow actions: the AI may run commands and edit files on this laptop",
                                            value=False, visible=False, elem_id="allow-actions", container=False)
                chatbot = gr.Chatbot(
                    elem_id="chat", show_label=False, height="calc(100dvh - 372px)", min_height=300,
                    placeholder=f"### Vanakkam 👋\nNaan {config.AGENT_NAME}. Ketkanum nu irukkadha edhuvum kelunga — Tamil, English or Tanglish.",
                    buttons=["copy"], feedback_options=None, layout="bubble",
                )
                image_in = gr.Image(sources=["upload"], type="filepath", height=96,
                                    show_label=False, elem_id="img-in", container=False)
                with gr.Column(elem_id="composer"):
                    msg = gr.Textbox(placeholder="Message…", show_label=False, container=False, autofocus=True,
                                     submit_btn=True, stop_btn=False, lines=1, max_lines=6)
                    examples = gr.Examples(examples=[[e] for e in EXAMPLES[config.DEFAULT_MODE]], inputs=msg,
                                           label="", elem_id="examples")

        with gr.Tab("🎨 Images"):
            import images_panel
            images_panel.build()

        with gr.Tab("💻 Terminal", visible=False) as terminal_tab:
            shells = web_computer.shell.available_backends()
            shell_names = {"linux": "🐧 Linux", "powershell": "🪟 PowerShell", "cmd": "⬛ CMD"}
            with gr.Column(elem_id="term-card"):
                with gr.Row():
                    term_shell = gr.Radio(choices=[(shell_names[s], s) for s in shells], value=web_computer.shell.backend,
                                          show_label=False, container=False, elem_id="term-shell", scale=2)
                    term_cwd = gr.Markdown(f"`{web_computer.shell.label()}` · `{web_computer.shell.display_cwd()}`",
                                           elem_id="term-cwd")
                term_out = gr.Textbox(label="Output", lines=14, max_lines=30, interactive=False, elem_id="term-out",
                                      buttons=["copy"])
                term_in = gr.Textbox(placeholder="$  command…",
                                     show_label=False, container=False, submit_btn="Run", lines=1, elem_id="term-in")
                explain_btn = gr.Button("✦ Ask AI about this result", size="sm", variant="secondary", elem_id="explain-btn")
                gr.Markdown(f"Commands run without keyboard input and stop after {config.COMMAND_TIMEOUT}s. "
                            "Risky commands (rm -rf, format…) are refused here.", elem_id="term-note")
            explain_out = gr.Markdown()

        with gr.Tab("🛡️ Security", visible=False) as security_tab:
            import security_hub
            import security_panel
            if security_hub.available():
                security_panel.build()
            else:
                gr.Markdown("_Security pack not found. Keep the `security/` folder next to the app._")

        with gr.Tab("🐉 Kali", visible=False) as kali_tab:
            import kali_panel
            kali_panel.build()
        kali_panel.wire_tab(kali_tab)        # pressing the tab opens the full-page Kali desktop

        with gr.Tab("🇮🇳 India Lab", visible=False) as india_tab:
            import india_lab_panel
            india_lab_panel.build()

        with gr.Tab("📚 Learn", visible=False) as learn_tab:
            import learn_panel
            learn_panel.build()

        with gr.Tab("🛠️ Admin", visible=False) as admin_tab:
            import admin_panel
            admin_panel.build()

    chat_event = msg.submit(
        respond, [msg, display_state, agent_state, mode, allow_actions, image_in],
        [msg, chatbot, display_state, agent_state, memory_view, tasks_view],
    ).then(lambda: None, None, image_in)
    msg.stop(lambda: gr.Textbox(submit_btn=True, stop_btn=False), None, msg, cancels=[chat_event])
    new_btn.click(new_chat, agent_state, [chatbot, display_state, agent_state])
    mode.change(change_mode, [mode, agent_state], [mode_info, agent_state, examples.dataset])
    mode.change(toggle_allow, mode, allow_actions)
    upload.upload(upload_documents, upload, [docs_view, docs_status, upload])
    clear_mem_btn.click(clear_memory, None, memory_view)
    term_in.submit(run_terminal, [term_in, term_shell], [term_out, term_cwd, term_in])
    explain_btn.click(explain_terminal, [agent_state, allow_actions], [explain_out, agent_state])
    import web_extras
    demo.load(on_load, None, [memory_view, tasks_view, status_view, admin_tab, terminal_tab, hello_view, topbar, security_tab, kali_tab, india_tab, learn_tab],
              js=web_extras.INIT_JS)


def _ensure_ai_ready():
    """Wake the local AI engine (Ollama) before launch so every tab's AI works on
    first open. No-op when the engine is already up or a hosted backend is used.
    Best-effort only — never blocks the app from starting."""
    try:
        if llm.backend() != "local":
            return
        import time
        import ollama
        try:
            ollama.list()           # already awake → nothing to do
            return
        except Exception:
            pass
        print("⏳ Waking the local AI engine (Ollama)…")
        try:
            import doctor
            doctor._try_start_ollama()
        except Exception:
            pass
        for _ in range(30):         # wait up to ~15s for it to answer
            time.sleep(0.5)
            try:
                ollama.list()
                print("✅ Local AI engine is ready.")
                return
            except Exception:
                continue
        print("⚠  Ollama still not responding. Open the Ollama app (llama icon in the "
              "system tray); AI replies will work once it is running.")
    except Exception:
        pass


if __name__ == "__main__":
    _ensure_ai_ready()
    open_browser = "--no-browser" not in sys.argv
    host, auth = "127.0.0.1", None
    if config.LAN_ACCESS:
        if config.WEB_PASSWORD:
            host, auth = "0.0.0.0", ("nanban", config.WEB_PASSWORD)
            print(f"📱 Phone access ON: http://{web_computer.lan_ip()}:{config.WEB_PORT}  (login: nanban)")
        else:
            print("⚠  LAN_ACCESS is on but WEB_PASSWORD is empty: staying local-only. Set a password in config.py.")
    print(f"\n{config.AGENT_NAME} is running at http://127.0.0.1:{config.WEB_PORT}")
    print("Keep this window open while you use it. Close it to stop the agent.\n")
    demo.queue().launch(
        inbrowser=open_browser, server_name=host, server_port=config.WEB_PORT, auth=auth,
        auth_message=f"{config.AGENT_NAME}: user is 'nanban', password is WEB_PASSWORD from config.py" if auth else None,
        theme=ui_theme.theme(), css=CSS, footer_links=[], pwa=True,
        favicon_path=str(config.BASE_DIR / "assets" / "nanban.png"),
    )
