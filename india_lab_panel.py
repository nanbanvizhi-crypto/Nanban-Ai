"""🇮🇳 India Lab tab — futuristic red+blue team learning hub, Tanglish, hands-on.

Not just reading cards: every topic has live AI lab actions (attack walkthrough,
defense playbook, build-a-mini-lab, practice challenge), a graded quiz, and XP /
badges so it feels like a real lab you make progress in.
"""

import gradio as gr

import india_lab as il
import llm

MAXQ = 3   # how many quiz questions we render per topic

# Inline CSS loaded with the content — beats Gradio's .prose wrapper that otherwise
# forces block layout on gr.HTML children. Key layout props use !important.
_INLINE_CSS = """<style>
.prose .il-grid, .il-grid { display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)) !important; gap: 14px !important; margin-top: 4px; }
.prose .il-card, .il-card { border-radius: 16px !important; padding: 15px 15px 13px !important;
  background: var(--block-background-fill, #fff) !important; border: 1px solid var(--border-color-primary, #e5e7eb) !important;
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease; }
.il-card:hover { transform: translateY(-3px); box-shadow: 0 16px 34px rgba(28,32,20,.14); border-color: var(--nb-accent, #a9d31f) !important; }
.il-card-top { display: flex !important; justify-content: space-between; align-items: center; }
.il-ico { font-size: 1.7rem; }
.il-fut { font-size: .64rem; font-weight: 700; color: #4f6318; background: rgba(169,211,31,.16);
  border: 1px solid #d6ef9a; padding: 2px 7px; border-radius: 999px; }
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
.il-hero { border-radius: 24px !important; padding: 28px 26px !important; text-align: center; color: #1a1f17 !important;
  background: radial-gradient(760px 260px at 12% -36%, rgba(191,230,58,.45), transparent 60%),
    radial-gradient(760px 280px at 92% 134%, rgba(255,176,138,.42), transparent 60%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ef 55%, #ffffff 100%) !important;
  box-shadow: 0 14px 44px rgba(28,32,20,.10); border: 1px solid #ecefe2; position: relative; overflow: hidden; }
.il-hero-badge { display: inline-block; font-size: .72rem; letter-spacing: .14em; font-weight: 800;
  padding: 5px 12px; border-radius: 999px; margin-bottom: 10px; background: rgba(169,211,31,.16);
  border: 1px solid #d6ef9a; color: #4f6318 !important; }
.il-hero h1 { margin: 2px 0 8px !important; font-size: 2rem !important; font-weight: 800 !important;
  letter-spacing: -.03em !important; color: #141514 !important; }
.il-hero p { margin: 0 auto 12px; max-width: 640px; color: #5a6152 !important; font-size: .96rem; }
.il-hero .il-safe { font-size: .82rem; color: #7a5a2a !important; background: rgba(255,176,138,.16);
  border: 1px solid #f0d6b8; border-radius: 14px; padding: 9px 13px; max-width: 760px; margin: 0 auto; }
#il-progress { border-radius: 16px; padding: 12px 16px; margin-top: 10px;
  background: linear-gradient(135deg, rgba(191,230,58,.20), rgba(255,176,138,.16));
  border: 1px solid var(--border-color-primary, #ecefe2); font-size: .92rem; }
#il-workbench { border: 1px solid var(--border-color-primary, #e5e7eb); border-radius: 16px;
  padding: 14px 16px; margin-top: 12px; background: var(--block-background-fill, #fff); }
#il-actionbar button { font-size: .86rem !important; }
#il-actout { min-height: 1.5em; }
@media (max-width: 640px) { .il-hero h1 { font-size: 1.5rem !important; } }
</style>"""


def _quiz_updates(did: str):
    """Return (radio_update x MAXQ, submit_update, note_update) for a topic."""
    qs = il.quiz_for(did)
    radios = []
    for i in range(MAXQ):
        if i < len(qs):
            item = qs[i]
            radios.append(gr.update(visible=True, label=f"Q{i+1}. {item['q']}",
                                    choices=item["opts"], value=None))
        else:
            radios.append(gr.update(visible=False, value=None))
    if qs:
        submit = gr.update(visible=True)
        note = gr.update(value="", visible=False)
    else:
        submit = gr.update(visible=False)
        note = gr.update(
            value="_Indha topic-ku graded quiz innum varala. Keezha lab actions use pannu, "
                  "illa Tutor-kitta 'quiz kudu' nu kelu._", visible=True)
    return radios + [submit, note]


def build():
    sel = gr.State(il.DOMAINS[0]["id"])

    with gr.Column(elem_id="il-wrap"):
        gr.HTML(_INLINE_CSS +
            '<div class="il-hero">'
            '<div class="il-hero-badge">🇮🇳 INDIA LAB · red team + blue team</div>'
            '<h1>Future-ready Security Lab</h1>'
            '<p>Modern + future technologies — <b>attack epdi nadakudhu</b> purinjikaradhu, '
            '<b>defend epdi pandradhu</b> master pannradhu. Hands-on: actions, quiz, XP — ellame Tanglish la.</p>'
            '<div class="il-safe">⚖️ Practice = un sontha lab · permission irukkura target · '
            'practice-ku-made targets (Metasploitable, DVWA, TryHackMe, HTB, OWASP) mattum. '
            'Veliya real system = illegal — Nanban help pannadhu.</div>'
            '</div>')

        header = gr.Markdown(il.progress_header(), elem_id="il-progress")

        with gr.Row(elem_id="il-filters"):
            level = gr.Radio(choices=["All"] + il.levels_available() + [il.ERA_PAST], value="All",
                             show_label=False, container=False, scale=4)
            search = gr.Textbox(placeholder="🔍 Search… (web, cloud, ai, wifi, forensics)",
                                show_label=False, container=False, scale=3)

        with gr.Accordion("🎯 Full Black-hat Attack Lifecycle — attack + defend, stage by stage",
                          open=False, elem_id="il-killchain"):
            gr.Markdown(il.kill_chain_markdown())
            gr.Markdown(il.defense_stack_markdown())

        gr.Markdown("### 📚 Technology domains — pick one to open the hands-on workbench")
        grid = gr.HTML(il.cards_html(), elem_id="il-gridwrap")

        with gr.Row(elem_id="il-jump"):
            picker = gr.Dropdown(
                choices=[(f'{d["icon"]} {d["name"]}', d["id"]) for d in il.DOMAINS],
                value=il.DOMAINS[0]["id"], show_label=False, container=False,
                info="Oru topic thernedu — detail + lab actions + quiz open aagum")

        detail = gr.Markdown(il.detail_markdown(il.DOMAINS[0]["id"]), elem_id="il-detail")

        # ---------------- hands-on workbench ----------------
        with gr.Column(elem_id="il-workbench"):
            gr.Markdown("### 🧪 Lab actions — oru button press pannu, Nanban live-ah kathu tharum")
            with gr.Row(elem_id="il-actionbar"):
                act_btns = {}
                for label, key in il.action_labels():
                    act_btns[key] = gr.Button(label, size="sm",
                                              variant=("primary" if key == "defend" else "secondary"))
            act_out = gr.Markdown("", elem_id="il-actout")

            gr.Markdown("### ❓ Quick quiz — paathu purinjaacha nu check pannu (+XP)")
            _first_quiz = il.quiz_for(il.DOMAINS[0]["id"])
            quiz_note = gr.Markdown("", visible=not _first_quiz)
            radios = []
            for i in range(MAXQ):
                if i < len(_first_quiz):
                    item = _first_quiz[i]
                    radios.append(gr.Radio(choices=item["opts"], label=f"Q{i+1}. {item['q']}",
                                           value=None, visible=True))
                else:
                    radios.append(gr.Radio(choices=[], label=f"Q{i+1}", visible=False))
            quiz_btn = gr.Button("✅ Check answers", variant="primary", size="sm",
                                 visible=bool(_first_quiz))
            quiz_result = gr.Markdown("")

        with gr.Accordion("🧑‍🏫 Ask the Lab Tutor (Tanglish)", open=False, elem_id="il-tutor"):
            gr.Markdown("Entha doubt venaalum kelu — attack concept, defense, oru tool epdi "
                        "work aagudhu, un lab setup. Tanglish-la pesu.")
            q = gr.Textbox(placeholder="e.g. 'SQL injection epdi work aagudhu, epdi defend pannradhu?'",
                           show_label=False, lines=2)
            ask = gr.Button("🧠 Ask tutor", variant="primary")
            ans = gr.Markdown("", elem_id="il-ans")

        gr.Markdown(il.platforms_markdown(), elem_id="il-platforms")

    # ---------------- wiring ----------------
    def _refresh(lv, qy):
        return il.cards_html(lv, qy)

    level.change(_refresh, [level, search], grid)
    search.change(_refresh, [level, search], grid)

    def _pick(did):
        did = did or il.DOMAINS[0]["id"]
        il.credit_study(did)                       # small XP for studying (once per topic)
        quiz_bits = _quiz_updates(did)             # MAXQ radios + submit + note
        return ([il.detail_markdown(did), did, il.progress_header(), "", ""] + quiz_bits)

    picker.change(
        _pick, picker,
        [detail, sel, header, act_out, quiz_result] + radios + [quiz_btn, quiz_note])

    # live AI lab actions
    def _make_action(kind):
        def _run(did):
            did = did or il.DOMAINS[0]["id"]
            msgs = il.action_prompt(did, kind)
            if not msgs:
                yield "Oru topic select pannu."
                return
            acc = ""
            try:
                for chunk in llm.chat(msgs, tools=None, options={"temperature": 0.4}):
                    piece = getattr(getattr(chunk, "message", None), "content", "") or ""
                    if piece:
                        acc += piece
                        yield acc
                if not acc:
                    yield "Reply varala. Chat tab-la oru model select panni, apuram try pannu."
            except Exception as e:
                yield f"AI-ah reach panna mudiyala ({e}). Ollama / model running-ah nu paaru."
        return _run

    for key, btn in act_btns.items():
        btn.click(_make_action(key), sel, act_out)

    # quiz grading
    def _grade(did, *answers):
        did = did or il.DOMAINS[0]["id"]
        md, _passed = il.grade_quiz(did, list(answers))
        if not md:
            return gr.update(value="_Indha topic-ku quiz illa._"), gr.update()
        return gr.update(value=md), gr.update(value=il.progress_header())

    quiz_btn.click(_grade, [sel] + radios, [quiz_result, header])

    # tutor
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
