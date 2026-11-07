"""🇮🇳 India Lab tab — futuristic red+blue team learning hub, Tanglish, easy UX."""

import gradio as gr

import india_lab as il
import llm

# Inline CSS loaded with the content — beats Gradio's .prose wrapper that otherwise
# forces block layout on gr.HTML children. Key layout props use !important.
_INLINE_CSS = """<style>
.prose .il-grid, .il-grid { display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)) !important; gap: 14px !important; margin-top: 4px; }
.prose .il-card, .il-card { border-radius: 16px !important; padding: 15px 15px 13px !important;
  background: var(--block-background-fill, #fff) !important; border: 1px solid var(--border-color-primary, #e5e7eb) !important;
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease; }
.il-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(20,30,60,.18); border-color: #ff9a3c !important; }
.il-card-top { display: flex !important; justify-content: space-between; align-items: center; }
.il-ico { font-size: 1.7rem; }
.il-fut { font-size: .64rem; font-weight: 700; color: #7c3aed; background: rgba(124,58,237,.12);
  border: 1px solid rgba(124,58,237,.30); padding: 2px 7px; border-radius: 999px; }
.il-past { font-size: .64rem; font-weight: 700; color: #9a6a00; background: rgba(214,158,46,.14);
  border: 1px solid rgba(214,158,46,.35); padding: 2px 7px; border-radius: 999px; margin-left: 4px; }
.il-run { font-size: .64rem; font-weight: 700; color: #0e7490; background: rgba(14,116,144,.12);
  border: 1px solid rgba(14,116,144,.30); padding: 2px 7px; border-radius: 999px; margin-left: 4px; }
.il-card-top > span:last-child { display: inline-flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }
.il-name { font-weight: 700 !important; margin: 8px 0 3px !important; font-size: 1.02rem; }
.il-lvl { font-size: .74rem; opacity: .8; margin-bottom: 7px; }
.il-what { font-size: .83rem; color: var(--body-text-color-subdued, #6b7280); line-height: 1.45; min-height: 3.2em; }
.il-tools { font-size: .74rem; margin-top: 8px; color: var(--body-text-color-subdued, #6b7280);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.il-row2 { display: flex !important; gap: 6px; margin-top: 10px; }
.il-tag { font-size: .7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.il-atk { color: #c0392b; background: rgba(192,57,43,.10); border: 1px solid rgba(192,57,43,.25); }
.il-def { color: #1f8a4c; background: rgba(31,138,76,.10); border: 1px solid rgba(31,138,76,.25); }
.il-empty { text-align: center; padding: 30px; color: var(--body-text-color-subdued, #6b7280); }
.il-hero { border-radius: 20px !important; padding: 26px 24px !important; text-align: center; color: #eaf2ff !important;
  background: radial-gradient(1200px 300px at 20% -40%, rgba(255,153,51,.30), transparent 60%),
    radial-gradient(1000px 320px at 90% 140%, rgba(19,136,8,.32), transparent 60%),
    linear-gradient(135deg, #0b1020 0%, #121a33 55%, #0b1428 100%) !important;
  box-shadow: 0 10px 40px rgba(10,18,40,.35); position: relative; overflow: hidden; }
.il-hero-badge { display: inline-block; font-size: .72rem; letter-spacing: .14em; font-weight: 700;
  padding: 5px 12px; border-radius: 999px; margin-bottom: 10px; background: rgba(255,255,255,.10);
  border: 1px solid rgba(255,255,255,.18); color: #cfe0ff !important; }
.il-hero h1 { margin: 2px 0 8px !important; font-size: 1.9rem !important; color: #ffd27a !important; }
.il-hero p { margin: 0 auto 12px; max-width: 640px; color: #b9c6e4 !important; font-size: .96rem; }
.il-hero .il-safe { font-size: .82rem; color: #ffe0b8 !important; background: rgba(255,153,51,.12);
  border: 1px solid rgba(255,153,51,.30); border-radius: 12px; padding: 9px 13px; max-width: 760px; margin: 0 auto; }
@media (max-width: 640px) { .il-hero h1 { font-size: 1.5rem !important; } }
</style>"""


def build():
    sel = gr.State("")

    with gr.Column(elem_id="il-wrap"):
        gr.HTML(_INLINE_CSS +
            '<div class="il-hero">'
            '<div class="il-hero-badge">🇮🇳 INDIA LAB · red team + blue team</div>'
            '<h1>Future-ready Security Lab</h1>'
            '<p>Modern + future technologies — <b>attack epdi nadakudhu</b> purinjikaradhu, '
            '<b>defend epdi pandradhu</b> master pannradhu. Ellame Tanglish la, easy-ah.</p>'
            '<div class="il-safe">⚖️ Practice = un sontha lab · permission irukkura target · '
            'practice-ku-made targets (Metasploitable, DVWA, TryHackMe, HTB, OWASP) mattum. '
            'Veliya real system = illegal — Nanban help pannadhu.</div>'
            '</div>')

        with gr.Row(elem_id="il-filters"):
            level = gr.Radio(choices=["All"] + il.levels_available() + [il.ERA_PAST], value="All",
                             show_label=False, container=False, scale=4)
            search = gr.Textbox(placeholder="🔍 Search… (web, cloud, ai, wifi, forensics)",
                                show_label=False, container=False, scale=3)

        with gr.Accordion("🎯 Full Black-hat Attack Lifecycle — attack + defend, stage by stage",
                          open=False, elem_id="il-killchain"):
            gr.Markdown(il.kill_chain_markdown())
            gr.Markdown(il.defense_stack_markdown())

        gr.Markdown("### 📚 Technology domains — attack + defend by area")
        grid = gr.HTML(il.cards_html(), elem_id="il-gridwrap")

        with gr.Row(elem_id="il-jump"):
            picker = gr.Dropdown(
                choices=[(f'{d["icon"]} {d["name"]}', d["id"]) for d in il.DOMAINS],
                value=None, show_label=False, container=False,
                info="Oru topic thernedu — full attack + defend + practice paaru")

        detail = gr.Markdown(il.detail_markdown(il.DOMAINS[0]["id"]), elem_id="il-detail")

        with gr.Accordion("🧑‍🏫 Ask the Lab Tutor (Tanglish)", open=False, elem_id="il-tutor"):
            gr.Markdown("Entha doubt venaalum kelu — attack concept, defense, oru tool epdi "
                        "work aagudhu, un lab setup. Tanglish-la pesu.")
            q = gr.Textbox(placeholder="e.g. 'SQL injection epdi work aagudhu, epdi defend pannradhu?'",
                           show_label=False, lines=2)
            ask = gr.Button("🧠 Ask tutor", variant="primary")
            ans = gr.Markdown("", elem_id="il-ans")

        gr.Markdown(il.platforms_markdown(), elem_id="il-platforms")

    # ---- wiring
    def _refresh(lv, qy):
        return il.cards_html(lv, qy)

    level.change(_refresh, [level, search], grid)
    search.change(_refresh, [level, search], grid)

    def _pick(did):
        return il.detail_markdown(did), (did or "")

    picker.change(_pick, picker, [detail, sel])

    def _ask(question, did):
        question = (question or "").strip()
        if not question:
            yield "✍️ Oru kelvi type pannu."
            return
        msgs = il.tutor_prompt(question, did)
        acc = ""
        try:
            for chunk in llm.chat(msgs, tools=None, options={"temperature": 0.3}):
                piece = getattr(getattr(chunk, "message", None), "content", "") or ""
                if piece:
                    acc += piece
                    yield acc
            if not acc:
                yield "Tutor-la bathil varala. Chat tab-la oru model select pannu, apuram try pannu."
        except Exception as e:
            yield f"Tutor-ah reach panna mudiyala ({e}). Chat tab-la oru model select pannu."

    ask.click(_ask, [q, sel], ans)
    q.submit(_ask, [q, sel], ans)
