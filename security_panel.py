"""
The 🛡️ Security tab for the Nanban web app: course + lab + Kali, in one screen.
"""

import gradio as gr

import security_hub as hub


def build() -> None:
    gr.Markdown("### 🛡️ Security Lab — learn pentesting, legally\n"
                "Everything in one place: the course, your practice lab, and Kali. "
                "**Tip:** switch 💬 Chat to **🛡️ Security Tutor** mode to ask the AI anything — it explains "
                "concepts, gives exact commands, and interprets your tool output. "
                "**Only test your own lab or targets you have written permission for** — start with the Ethics lesson.")

    with gr.Row(equal_height=False):
        # ---- left: course reader
        with gr.Column(scale=3):
            with gr.Group(elem_classes=["admin-card"]):
                lesson = gr.Dropdown(choices=[t for t, _ in hub.LESSONS], value=hub.LESSONS[0][0],
                                     label="📚 Course", interactive=True)
                reader = gr.Markdown(hub.read_lesson(hub.LESSONS[0][1]), elem_id="lesson-reader")

        # ---- right: lab + kali controls
        with gr.Column(scale=2):
            with gr.Group(elem_classes=["admin-card"]):
                gr.Markdown("#### 🧪 Practice lab")
                lab_view = gr.Markdown(hub.lab_status())
                with gr.Row():
                    start_btn = gr.Button("▶ Start lab", variant="primary", size="sm")
                    stop_btn = gr.Button("■ Stop", variant="secondary", size="sm")
                    refresh_btn = gr.Button("↻ Refresh", variant="secondary", size="sm")
            with gr.Group(elem_classes=["admin-card"]):
                gr.Markdown("#### 🐉 Kali Linux — Auto-Setup")
                import kali_wizard as kw
                state = kw.detect()
                ready_badge = gr.Markdown(
                    "**Status: ✅ Ready**" if state.fully_ready
                    else "**Status: ⏳ Not set up yet** — one click below installs everything.")
                kali_status_view = gr.Markdown(state.summary(), elem_id="kali-status")
                with gr.Accordion("One-click install (first time only)", open=not state.fully_ready):
                    gr.Markdown(
                        "This installs **WSL2 + Kali Linux + every security tool + SSH** and wires it into "
                        "Nanban automatically. **Windows admin rights needed on the first click** (one UAC "
                        "prompt + one restart). After that it's all automatic. ~20 minutes total."
                    )
                    with gr.Row():
                        kali_user = gr.Textbox(value="nanban", label="Pick a Kali username", scale=1)
                        kali_pass = gr.Textbox(value="", label="Pick a password", type="password", scale=1)
                    install_btn = gr.Button("🚀 Install / continue setup", variant="primary", size="sm")
                    check_btn = gr.Button("↻ Re-check status", variant="secondary", size="sm")
                    kali_log = gr.Markdown("", elem_id="kali-log")

    def _refresh_status():
        s = kw.detect()
        head = "**Status: ✅ Ready**" if s.fully_ready else "**Status: ⏳ Setup incomplete**"
        return head, s.summary()

    def _install(username, password):
        if not username or not password:
            yield "**Status: ⚠️ Enter a username and password first**", kw.detect().summary(), ""
            return
        log: list[str] = ["🚀 Starting Kali Auto-Setup…"]
        kw.run_async(username, password, log)
        # poll the shared list every second for 30 minutes max
        import time
        for _ in range(60 * 30):
            head, summary = _refresh_status()
            yield head, summary, "\n".join(f"- {line}" for line in log[-30:])
            if not kw.is_running():
                break
            time.sleep(1)
        head, summary = _refresh_status()
        yield head, summary, "\n".join(f"- {line}" for line in log[-30:])

    lookup = {title: path for title, path in hub.LESSONS}
    lesson.change(lambda t: hub.read_lesson(lookup[t]), lesson, reader)
    start_btn.click(hub.start_lab, None, lab_view)
    stop_btn.click(hub.stop_lab, None, lab_view)
    refresh_btn.click(hub.lab_status, None, lab_view)
    check_btn.click(_refresh_status, None, [ready_badge, kali_status_view])
    install_btn.click(_install, [kali_user, kali_pass], [ready_badge, kali_status_view, kali_log])
