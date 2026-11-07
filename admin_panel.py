"""
Admin tab for the web app / Nanban Server: machine stats, who is online, API usage,
server health, logs. Only admin users see it (config.ADMIN_USERS).
"""

import time
from pathlib import Path

import gradio as gr

import config
import servers
import vpn

LOG_FILE = config.DATA_DIR / "server.log"


def machine_stats() -> str:
    try:
        import psutil
    except ImportError:
        return "_psutil not installed_"
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage(str(Path.home().anchor or "/"))
    boot = time.time() - psutil.boot_time()
    lines = [
        f"**CPU** {psutil.cpu_percent(interval=0.3):.0f}% of {psutil.cpu_count()} cores",
        f"**RAM** {vm.used / 2**30:.1f} / {vm.total / 2**30:.1f} GB ({vm.percent:.0f}%)",
        f"**Disk** {disk.used / 2**30:.0f} / {disk.total / 2**30:.0f} GB ({disk.percent:.0f}%)",
        f"**Up** {boot / 3600:.1f} h",
        f"**{vpn.badge()}**",
    ]
    import llm
    lines.append(f"**AI engine:** {llm.describe()}")
    if llm.backend() == "local":
        try:
            import ollama
            running = ollama.ps().models
            lines.append("**Ollama loaded:** " + (", ".join(f"{m.model} ({(m.size or 0) / 2**30:.1f} GB)" for m in running) or "nothing loaded (idle)"))
        except Exception:
            lines.append("**Ollama:** not reachable")
    return "  \n".join(lines)


def online_users() -> str:
    import app
    now = time.time()
    rows = [(u, now - t) for u, t in sorted(app.ACTIVE.items(), key=lambda x: -x[1])]
    if not rows:
        return "_No activity yet._"
    return "\n".join(f"- **{u}** · {int(age // 60)} min ago" if age > 90 else f"- **{u}** · active now" for u, age in rows[:30])


def api_usage() -> str:
    import api
    rows = api.recent_usage(40)
    if not rows:
        return "_No API calls yet._"
    out = ["| time | who | endpoint | ms | details |", "|---|---|---|---|---|"]
    for r in reversed(rows):
        extra = ", ".join(f"{k}={v}" for k, v in r.items() if k not in {"time", "who", "endpoint", "ms"})
        out.append(f"| {r['time']} | {r['who']} | {r['endpoint']} | {r['ms']} | {extra} |")
    return "\n".join(out)


def servers_table() -> str:
    if not servers.names():
        return "_No servers registered. In the Nanban Terminal: `/server add <name> user@host`_"
    rows = servers.status_all()
    out = ["| server | status | OS | uptime | load | memory | disk |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("ok"):
            out.append(f"| **{r['name']}** | ✅ | {r.get('os', '')} | {r.get('up', '')} | {r.get('load', '')} | {r.get('mem', '')} | {r.get('disk', '')} |")
        else:
            out.append(f"| **{r['name']}** | ❌ {r.get('error', '')} | | | | | |")
    return "\n".join(out)


def logs_tail(lines: int = 60) -> str:
    try:
        text = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:]
        return "\n".join(text) or "(empty)"
    except OSError:
        return "(no log file yet: logs appear when you run server.py)"


def access_info() -> str:
    import web_computer
    ip = web_computer.lan_ip()
    port = config.SERVER_PORT
    users = ", ".join(config.USERS) if config.USERS else "none (no login)"
    return (f"**Wi-Fi** `http://{ip}:{port}`  \n**API** `http://{ip}:{port}/v1`  \n**Docs** `/docs`  \n"
            f"**Users** {users}  \n**API keys** {len(config.API_KEYS)}")


def outside_info() -> str:
    port = config.SERVER_PORT
    return (f"**Tailscale (recommended):** install it on this machine and on your phone/laptop with the same account, "
            f"then open `http://<this machine's Tailscale IP>:{port}`. Encrypted, no port forwarding.\n\n"
            f"**Cloudflare Tunnel (temporary public link):** run `cloudflared tunnel --url http://localhost:{port}` "
            f"and share the `https://….trycloudflare.com` URL. Use strong passwords and API keys first.")


def build() -> None:
    import getting_started
    with gr.Accordion("🚀 Getting Started — set up Nanban (live checklist)", open=True, elem_classes=["admin-acc"]):
        gs_view = gr.HTML(getting_started.onboarding_html())
        with gr.Row():
            gs_refresh = gr.Button("🔄 Re-check setup", size="sm", variant="secondary")
            gs_health = gr.Button("🩺 Run health self-test", size="sm", variant="secondary")
        gs_health_view = gr.HTML()
        gs_refresh.click(getting_started.onboarding_html, None, gs_view)
        gs_health.click(getting_started.health_html, None, gs_health_view)

    with gr.Row(equal_height=True):
        with gr.Column(elem_classes=["admin-card"]):
            gr.Markdown("#### 💻 This machine")
            stats = gr.Markdown(machine_stats)
        with gr.Column(elem_classes=["admin-card"]):
            gr.Markdown("#### 🔗 Access")
            gr.Markdown(access_info)
        with gr.Column(elem_classes=["admin-card"]):
            gr.Markdown("#### 👥 Users online")
            online = gr.Markdown(online_users)
    with gr.Row():
        refresh = gr.Button("🔄 Refresh", size="sm", variant="secondary", elem_id="admin-refresh")

    # ---- One-tap remote access (Cloudflare Tunnel + QR) ----
    import remote_access as ra
    with gr.Accordion("🌍 Remote access — use Nanban on your phone from anywhere", open=False, elem_classes=["admin-acc"]):
        gr.Markdown("One tap starts a private link to this laptop and shows a **QR code** — scan it "
                    "with your phone and use Nanban from mobile data or any Wi-Fi. (Laptop must stay on.)")
        with gr.Row():
            ra_start = gr.Button("🌍 Start remote access", variant="primary", size="sm")
            ra_stop = gr.Button("⏹ Stop", variant="secondary", size="sm")
        ra_view = gr.HTML(ra.current_render, elem_id="ra-view")
        ra_start.click(ra.start_and_render, None, ra_view)
        ra_stop.click(ra.stop_and_render, None, ra_view)

    # ---- Messaging: Telegram + WhatsApp, no file editing ----
    with gr.Accordion("💬 Messaging — chat with Nanban on Telegram / WhatsApp", open=False, elem_classes=["admin-acc"]):
        gr.Markdown("**Telegram (easiest, 100% free):** in Telegram message **@BotFather** → `/newbot` → "
                    "copy the token → paste below → **Start**. That's it — open your bot and chat.")
        tg_token = gr.Textbox(label="Telegram bot token", type="password", placeholder="123456:ABC-...")
        with gr.Row():
            tg_start = gr.Button("▶ Start Telegram bot", variant="primary", size="sm")
            tg_check = gr.Button("↻ Status", variant="secondary", size="sm")
        tg_status = gr.Markdown()

        def _tg_start(tok):
            import settings as _st, telegram_bot, config as _cfg
            if tok:
                _st.save({"TELEGRAM_TOKEN": tok})
                _cfg.TELEGRAM_TOKEN = tok
            if not telegram_bot.configured():
                return "⚠️ Paste your bot token first (from @BotFather)."
            telegram_bot.start_background()
            return "🟢 **Telegram bot is running.** Open your bot in Telegram and send a message."

        def _tg_check():
            import telegram_bot
            return ("🟢 Running." if telegram_bot.is_running()
                    else ("⚪ Not started. Paste the token and press Start."
                          if telegram_bot.configured() else "⚪ No token yet."))

        tg_start.click(_tg_start, tg_token, tg_status)
        tg_check.click(_tg_check, None, tg_status)

        gr.Markdown("---\n**WhatsApp (official Meta Cloud API):** paste the three values from "
                    "**developers.facebook.com → WhatsApp → API Setup**, Save, then connect the webhook "
                    "(the URL is shown after Save). Full guide: `WHATSAPP-SETUP.md`.")
        with gr.Row():
            wa_token = gr.Textbox(label="WhatsApp access token", type="password", scale=2)
            wa_phone = gr.Textbox(label="Phone number id", scale=1)
        with gr.Row():
            wa_verify = gr.Textbox(label="Verify word (you choose)", value="nanban", scale=1)
            wa_save = gr.Button("💾 Save WhatsApp", variant="primary", size="sm", scale=1)
        wa_status = gr.Markdown()

        def _wa_save(tok, phone, verify):
            import settings as _st, config as _cfg, remote_access as _ra
            if not tok or not phone:
                return "⚠️ Paste the access token and phone number id."
            _st.save({"WHATSAPP_TOKEN": tok, "WHATSAPP_PHONE_ID": phone,
                      "WHATSAPP_VERIFY_TOKEN": verify or "nanban"})
            _cfg.WHATSAPP_TOKEN, _cfg.WHATSAPP_PHONE_ID, _cfg.WHATSAPP_VERIFY_TOKEN = tok, phone, (verify or "nanban")
            base = _ra.tunnel_url() if _ra.is_running() else "https://YOUR-PUBLIC-URL"
            hook = base.rstrip("/") + "/whatsapp/webhook"
            note = ("" if _ra.is_running() else
                    "\n\n_(Start **🌍 Remote access** above to get your real public URL.)_")
            return (f"✅ Saved. In Meta → WhatsApp → Configuration → Webhook, set:\n\n"
                    f"- **Callback URL:** `{hook}`\n- **Verify token:** `{verify or 'nanban'}`\n\n"
                    f"Then subscribe to **messages**. Message your test number to chat.{note}")

        wa_save.click(_wa_save, [wa_token, wa_phone, wa_verify], wa_status)

    # ---- Self-repair: check Nanban and auto-fix common problems ----
    import doctor
    with gr.Accordion("🩺 Self-check & auto-fix — if anything's broken", open=False, elem_classes=["admin-acc"]):
        gr.Markdown("Nanban checks itself and **fixes the safe problems automatically** "
                    "(missing folders, corrupt settings, missing model or packages, a cloud model "
                    "your key can't use, Ollama asleep). Anything risky is only flagged with steps.")
        doctor_btn = gr.Button("🩺 Run self-check & fix", variant="primary", size="sm")
        doctor_view = gr.HTML(elem_id="doctor-view")
        doctor_btn.click(doctor.doctor_html, None, doctor_view)

    # ---- Storage: what's installed and using disk, separated by component ----
    import storage
    with gr.Accordion("💾 Storage — what's installed & using disk", open=True, elem_classes=["admin-acc"]):
        storage_view = gr.HTML(storage.storage_html, elem_id="storage-view")
        storage_btn = gr.Button("🔄 Refresh storage", size="sm", variant="secondary")
        storage_btn.click(storage.storage_html, None, storage_view)

    # ---- Usage dashboard ----
    import usage
    with gr.Accordion("📊 Usage — models & modes you've used", open=False, elem_classes=["admin-acc"]):
        usage_view = gr.HTML(usage.usage_html, elem_id="usage-view")
        usage_btn = gr.Button("🔄 Refresh usage", size="sm", variant="secondary")
        usage_btn.click(usage.usage_html, None, usage_view)

    # ---- Backup & restore ----
    import backup
    with gr.Accordion("🗄️ Backup & restore — your memory, to-dos, settings, documents", open=False, elem_classes=["admin-acc"]):
        gr.Markdown("Save everything to one file you can keep, or move to another laptop.")
        with gr.Row():
            bk_btn = gr.Button("⬇️ Create backup", variant="primary", size="sm")
            bk_file = gr.File(label="Your backup (download it)", interactive=False)
        bk_btn.click(backup.make_backup, None, bk_file)
        rs_up = gr.File(label="Restore: upload a Nanban backup .zip", file_types=[".zip"])
        rs_status = gr.Markdown()
        rs_up.upload(backup.restore_backup, rs_up, rs_status)

    # ---- Scheduled tasks ----
    import scheduler
    scheduler.start()
    with gr.Accordion("🔔 Automation jobs — Nanban runs things by itself on a schedule", open=False, elem_classes=["admin-acc"]):
        gr.Markdown("Set up jobs Nanban runs automatically: **Daily**, **Every N hours**, **Weekly** (chosen "
                    "days), or **Once**. A job can be a single **prompt**, a multi-step **chain** (one prompt "
                    "per line — each step sees the previous answer), or a safe **action** (self-check, backup, "
                    "or a daily India Lab exercise). Output saves to `data/scheduled/` and can ping your "
                    "Telegram / WhatsApp. The laptop/server must be running at that time.")

        sc_name = gr.Textbox(label="Job name", placeholder="Morning security brief", scale=1)
        with gr.Row():
            sc_type = gr.Radio(["daily", "interval", "weekly", "once"], value="daily",
                               label="Schedule", scale=2)
            sc_mode = gr.Dropdown(choices=list(config.MODES.keys()), value="assistant", label="Mode", scale=1)
        with gr.Row():
            sc_time = gr.Textbox(label="Time (HH:MM)", placeholder="08:30", scale=1)
            sc_every = gr.Number(label="Every N hours (interval)", value=4, scale=1)
            sc_date = gr.Textbox(label="Date (once — YYYY-MM-DD)", placeholder="2026-11-10", scale=1)
        sc_days = gr.CheckboxGroup(scheduler.WEEKDAYS, label="Weekdays (weekly only)")

        sc_kind = gr.Radio(["prompt", "chain", "action"], value="prompt", label="Job kind")
        sc_prompt = gr.Textbox(label="Prompt (chain = one step per line)",
                               placeholder="Give me a short security news brief for today", lines=3)
        sc_action = gr.Dropdown(choices=[(v, k) for k, v in scheduler.ACTIONS.items()],
                                value="self_check", label="Action (for 'action' kind)")
        with gr.Row():
            sc_tg = gr.Checkbox(label="📨 Notify Telegram", value=True, scale=1)
            sc_wa = gr.Checkbox(label="💬 Notify WhatsApp", value=False, scale=1)

        with gr.Row():
            sc_add = gr.Button("➕ Add job", variant="primary", size="sm")
            sc_refresh = gr.Button("🔄 Refresh", variant="secondary", size="sm")
        sc_status = gr.Markdown()
        sc_list = gr.Markdown(scheduler.list_text())
        with gr.Row():
            sc_id = gr.Textbox(label="Job id (for the buttons below)", placeholder="the number after id:", scale=2)
            sc_run = gr.Button("🚀 Run now", size="sm", scale=1)
            sc_tog = gr.Button("⏯️ Pause/Resume", size="sm", variant="secondary", scale=1)
            sc_rm_btn = gr.Button("🗑️ Remove", size="sm", variant="secondary", scale=1)

        def _sc_add(name, typ, t, every, days, date, kind, prompt, action, mode, tg, wa):
            msg = scheduler.add(name, typ, t, every, days, date, kind, prompt, action, mode, tg, wa)
            return msg, scheduler.list_text()

        def _sc_id_action(fn, i):
            try:
                out = fn(int(str(i).strip()))
            except Exception as e:
                out = f"⚠️ Enter a valid id ({e})."
            return out, scheduler.list_text()

        sc_add.click(_sc_add,
                     [sc_name, sc_type, sc_time, sc_every, sc_days, sc_date, sc_kind, sc_prompt, sc_action, sc_mode, sc_tg, sc_wa],
                     [sc_status, sc_list])
        sc_refresh.click(scheduler.list_text, None, sc_list)
        sc_run.click(lambda i: _sc_id_action(scheduler.run_now, i), sc_id, [sc_status, sc_list])
        sc_tog.click(lambda i: _sc_id_action(scheduler.toggle, i), sc_id, [sc_status, sc_list])
        sc_rm_btn.click(lambda i: _sc_id_action(scheduler.remove, i), sc_id, [sc_status, sc_list])

    # ---- Settings: change the AI brain with no file editing ----
    import settings as st
    with gr.Accordion("🧠 AI model & settings", open=True, elem_classes=["admin-acc"]):
        gr.Markdown("Pick Nanban's brain. **🆓 Free options** (top of the list): Local — free & private; or free "
                    "cloud tiers (Groq, Gemini, Cerebras, OpenRouter free) — 70B models, much smarter/faster than "
                    "local, just a free API key. **💳 Paid options** (optional): Claude / GPT for top frontier "
                    "intelligence. Saved instantly, no file editing. Not sure of the model name? Click "
                    "**Show my available models** below.")
        cur = st.load()
        provider = gr.Dropdown(choices=list(st.PROVIDERS.keys()),
                               value=list(st.PROVIDERS.keys())[0], label="Provider / model preset")
        with gr.Row():
            model_box = gr.Textbox(value=config.MODEL, label="Model name",
                                   info="Local: an Ollama model (e.g. llama3.1:8b). Hosted: the provider's model id.")
            key_box = gr.Textbox(value=cur.get("HOSTED_API_KEY", ""), label="API key (hosted only)",
                                 type="password", info="From your provider's dashboard. Stored locally, never shared.")
        base_box = gr.Textbox(value=cur.get("HOSTED_BASE_URL", config.HOSTED_BASE_URL),
                              label="Hosted API base URL", visible=False)
        with gr.Row():
            save_btn = gr.Button("💾 Save & apply", variant="primary", size="sm")
            list_btn = gr.Button("🔎 Show my available models", variant="secondary", size="sm")
        settings_status = gr.Markdown(f"Current brain: **{__import__('llm').describe()}**")

        def _on_provider(name):
            p = st.PROVIDERS[name]
            if p["backend"] in ("local", "portable"):
                default_model = "(bundled)" if p["backend"] == "portable" else config.MODEL
                return gr.update(value=default_model), gr.update(visible=False), gr.update(value="")
            return gr.update(value=p["model"]), gr.update(visible=True, value=p["base"]), gr.update()

        def _list_models(name, key, base):
            """Show the exact model ids this provider+key can use, so the user picks a valid one."""
            p = st.PROVIDERS[name]
            if p["backend"] == "local":
                try:
                    import ollama
                    names = [m.model for m in ollama.list().models]
                    return ("**Installed local models:** " + ", ".join(f"`{n}`" for n in names)
                            + "\n\n_Add more with_ `ollama pull <name>`." if names
                            else "No local models yet. In Command Prompt: `ollama pull llama3.1:8b`")
                except Exception as e:
                    return f"Can't reach Ollama ({e}). Open the Ollama app."
            if not key:
                return "⚠️ Paste your API key first, then click this again."
            # temporarily point llm at this provider+key to list models
            import llm
            old = (config.LLM_BACKEND, config.HOSTED_BASE_URL, config.HOSTED_API_KEY)
            config.LLM_BACKEND, config.HOSTED_BASE_URL, config.HOSTED_API_KEY = "hosted", (base or p["base"]), key
            llm._client = None
            avail = llm.list_models()
            config.LLM_BACKEND, config.HOSTED_BASE_URL, config.HOSTED_API_KEY = old
            llm._client = None
            if not avail:
                return ("Couldn't list models — check the API key is correct and you have internet. "
                        "You can also see them at your provider's models page.")
            return ("**Models your key can use** (copy one into the Model name box, then Save):\n\n"
                    + "\n".join(f"- `{m}`" for m in avail[:30]))

        def _save_settings(name, model, key, base):
            p = st.PROVIDERS[name]
            if p["backend"] == "portable":
                st.save({"LLM_BACKEND": "portable"})
            elif p["backend"] == "local":
                st.save({"LLM_BACKEND": "local", "MODEL": model or config.MODEL})
            else:
                if not key:
                    return "⚠️ This provider needs an API key. Paste one and Save again."
                backend = p["backend"]           # "hosted" or "router"
                updates = {"LLM_BACKEND": backend, "HOSTED_BASE_URL": base or p["base"],
                           "HOSTED_API_KEY": key}
                updates["HOSTED_MODEL"] = "auto" if backend in ("router", "council") else (model or p["model"])
                st.save(updates)
            import llm
            ok, desc = llm.ping()
            if not ok:
                return f"Saved, but the provider isn't reachable: {desc}"
            # For hosted: make sure the chosen model id actually works on this key.
            # If not, auto-pick the best available one so the user never hits a dead 404.
            if p["backend"] == "hosted":
                chosen = (model or p["model"]).strip()
                avail = llm.list_models()
                if avail and chosen not in avail:
                    fixed = llm.pick_available_model()
                    st.save({"HOSTED_MODEL": fixed})
                    desc = llm.describe()
                    return (f"ℹ️ `{chosen}` isn't available on your key, so I switched you to "
                            f"`{fixed}` (which is). Current brain: **{desc}**. "
                            f"To choose another, click **🔎 Show my available models**.")
            return f"✅ Saved. Current brain: **{desc}**"

        provider.change(_on_provider, provider, [model_box, base_box, key_box])
        save_btn.click(_save_settings, [provider, model_box, key_box, base_box], settings_status)
        list_btn.click(_list_models, [provider, key_box, base_box], settings_status)

    # ---- One-button update ----
    with gr.Accordion("⬆️ Update Nanban", open=False, elem_classes=["admin-acc"]):
        gr.Markdown(f"Version: `{st.current_version()}`. One click pulls the latest version and updates everything.")
        update_btn = gr.Button("⬆️ Check for updates & update", variant="secondary", size="sm")
        update_status = gr.Markdown()
        update_btn.click(lambda: st.update(), None, update_status)

    with gr.Accordion("🖧 Servers health", open=False, elem_classes=["admin-acc"]):
        srv = gr.Markdown("_Click the button to check every registered server._")
        srv_btn = gr.Button("Check all servers", size="sm", variant="secondary")
    with gr.Accordion("🌍 Access from outside", open=False, elem_classes=["admin-acc"]):
        gr.Markdown(outside_info)
    with gr.Accordion("📊 API usage (last 40)", open=False, elem_classes=["admin-acc"]):
        usage = gr.Markdown(api_usage)
    with gr.Accordion("📜 Server log", open=False, elem_classes=["admin-acc"]):
        logs = gr.Code(logs_tail(), language=None, lines=20, interactive=False)
    refresh.click(lambda: (machine_stats(), online_users(), api_usage(), logs_tail()), None, [stats, online, usage, logs])
    srv_btn.click(servers_table, None, srv)
