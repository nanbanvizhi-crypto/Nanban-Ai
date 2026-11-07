"""
🚀 Getting Started — a live first-run checklist that tells you exactly what to do to set Nanban up.

Each item reflects real state (✅ done / ⬜ to do) with a one-line action. Nothing here changes
settings; it just guides you. Also runs a quick health self-test.
"""

import config


def _ollama_ok() -> bool:
    try:
        import llm
        return bool(getattr(llm, "_HAVE_OLLAMA", False))
    except Exception:
        return False


def _checks() -> list[dict]:
    items = []

    # 1) AI engine
    has_key = bool(getattr(config, "HOSTED_API_KEY", ""))
    has_ollama = _ollama_ok()
    engine_ok = has_key or has_ollama
    if has_key and has_ollama:
        detail = "Hosted key + local Ollama — full power."
    elif has_key:
        detail = "Hosted key set — cloud models ready."
    elif has_ollama:
        detail = "Local Ollama ready — runs offline & free."
    else:
        detail = "Admin → AI model settings la oru free key paste pannu (NVIDIA/Groq), illa Ollama install pannu."
    items.append({"ok": engine_ok, "title": "🧠 AI engine", "detail": detail})

    # 2) Voice (Vizhi) — browser feature, always available
    items.append({"ok": True, "title": "👁️ Vizhi voice",
                  "detail": "Bottom-right 👁️ orb press pannu → mic 'Allow' → hands-free. (Chrome best.)"})

    # 3) Documents (RAG)
    try:
        import docs_rag
        n = len(docs_rag.document_files())
    except Exception:
        n = 0
    items.append({"ok": n > 0, "title": "📄 Your documents",
                  "detail": (f"{n} document(s) added — ask Nanban about them in Study mode."
                             if n else "Sidebar → 📚 Documents la PDF/notes upload pannu (keyword search — no setup).")})

    # 4) Kali (optional, for security learning)
    try:
        import kali_panel
        kali_ok = kali_panel.connected()
    except Exception:
        kali_ok = False
    items.append({"ok": kali_ok, "title": "🐉 Kali (optional)",
                  "detail": ("Connected — AI Shell + tools ready." if kali_ok
                             else "Security tab la install → Kali tab la Connect (security learning-ku).")})

    # 5) Messaging / remote (optional)
    tg = wa = False
    try:
        import telegram_bot; tg = telegram_bot.configured()
    except Exception:
        pass
    try:
        import whatsapp; wa = whatsapp.configured()
    except Exception:
        pass
    items.append({"ok": tg or wa, "title": "📨 Phone alerts (optional)",
                  "detail": ("Messaging set up." if (tg or wa)
                             else "Admin → Messaging la Telegram/WhatsApp connect pannu (automation alerts-ku).")})

    return items


def onboarding_html() -> str:
    items = _checks()
    done = sum(1 for i in items if i["ok"])
    pct = int(done / len(items) * 100) if items else 0
    rows = "".join(
        f'<div class="gs-row {"gs-done" if i["ok"] else "gs-todo"}">'
        f'<span class="gs-mark">{"✅" if i["ok"] else "⬜"}</span>'
        f'<span class="gs-body"><b>{i["title"]}</b><br><span class="gs-detail">{i["detail"]}</span></span>'
        '</div>' for i in items)
    return (
        '<style>'
        '#gs-wrap{max-width:720px}'
        '.gs-bar{height:8px;border-radius:999px;background:var(--border-color-primary);overflow:hidden;margin:6px 0 12px}'
        '.gs-fill{height:100%;background:linear-gradient(90deg,#ff9a3c,#8ef5b0)}'
        '.gs-row{display:flex;gap:10px;padding:10px 12px;border:1px solid var(--border-color-primary);'
        'border-radius:11px;margin-bottom:7px;background:var(--block-background-fill)}'
        '.gs-row.gs-done{border-color:#1f8a4c;background:rgba(31,138,76,.06)}'
        '.gs-mark{font-size:1.05rem}'
        '.gs-detail{font-size:.82rem;color:var(--body-text-color-subdued);line-height:1.45}'
        '</style>'
        '<div id="gs-wrap">'
        f'<div style="font-size:.9rem">Setup progress — <b>{done}/{len(items)}</b></div>'
        f'<div class="gs-bar"><div class="gs-fill" style="width:{pct}%"></div></div>'
        f'{rows}'
        '<div style="font-size:.8rem;color:var(--body-text-color-subdued);margin-top:6px">'
        'Optional items (Kali, phone alerts) venaam-na skip pannalaam — Nanban core velai seiyum.</div>'
        '</div>')


def health_html() -> str:
    """Quick self-test using the doctor module."""
    try:
        import doctor
        doctor.run_all()
        return "<div style='font-size:.9rem'>" + doctor.quick_summary() + "</div>"
    except Exception as e:
        return f"<div style='font-size:.9rem'>Self-test skipped ({e}).</div>"
