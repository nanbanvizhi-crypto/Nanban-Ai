"""📚 Learn tab — interactive security study: Sandbox, Guided Labs, SOC Sim, Progress."""

import gradio as gr

import guided_labs as gl
import progress
import sandbox
import soc_sim

_CSS = """<style>
#learn-wrap .lh-hero { border-radius:18px; padding:20px 22px; text-align:center; color:#eaf2ff !important;
  background: linear-gradient(135deg,#0b1020,#15223f 60%,#0b1428) !important; margin-bottom:6px; }
#learn-wrap .lh-hero h2 { margin:0 0 4px; color:#8ef5b0 !important; font-size:1.5rem; }
#learn-wrap .lh-hero p { margin:0; color:#b9c6e4 !important; font-size:.9rem; }
.sb-out, .lab-out, .soc-out { font-family: ui-monospace,Menlo,Consolas,monospace !important;
  white-space: pre-wrap; background:#0d1117 !important; color:#c9d1d9 !important; border-radius:12px;
  padding:14px 16px !important; font-size:12.5px; line-height:1.5; border:1px solid #30363d; }
.pg-wrap { max-width:720px; margin:0 auto; }
.pg-hero { display:flex; align-items:center; gap:18px; justify-content:center; padding:14px;
  border-radius:16px; background:linear-gradient(135deg,#1a2238,#0f1830); color:#eaf2ff; }
.pg-xp { font-size:2.4rem; font-weight:800; color:#8ef5b0; line-height:1; }
.pg-xp span { font-size:.9rem; color:#9fb3d9; margin-left:4px; }
.pg-badge { font-size:1.1rem; font-weight:700; color:#ffd27a; }
.pg-badge-d { font-size:.78rem; color:#9fb3d9; font-weight:400; }
.pg-next { text-align:center; color:var(--body-text-color-subdued); margin:8px 0; font-size:.88rem; }
.pg-stats { text-align:center; margin:4px 0 12px; font-size:.9rem; }
.pg-roadmap { display:flex; flex-direction:column; gap:8px; }
.pg-stage { border-radius:12px; padding:11px 14px; border:1px solid var(--border-color-primary);
  background:var(--block-background-fill); }
.pg-stage.pg-done { border-color:#1f8a4c; background:rgba(31,138,76,.08); }
.pg-stage.pg-active { border-color:#ff9a3c; background:rgba(255,154,60,.07); }
.pg-stage.pg-locked { opacity:.6; }
.pg-stage-head { display:flex; justify-content:space-between; font-size:.98rem; }
.pg-need { font-size:.74rem; color:var(--body-text-color-subdued); }
.pg-stage-desc { font-size:.8rem; color:var(--body-text-color-subdued); margin-top:3px; }
.pg-badgelist { display:flex; flex-wrap:wrap; gap:6px; justify-content:center; margin-top:14px; }
.pg-chip { font-size:.72rem; padding:4px 10px; border-radius:999px; border:1px solid var(--border-color-primary); }
.pg-chip.on { background:rgba(142,245,176,.15); border-color:#1f8a4c; font-weight:700; }
.pg-chip.off { opacity:.45; }
</style>"""


def build():
    with gr.Column(elem_id="learn-wrap"):
        gr.HTML(_CSS +
            '<div class="lh-hero"><h2>📚 Learn — hands-on security study</h2>'
            '<p>Practice safely: simulated sandbox, guided labs, SOC detection drills. '
            'Earn XP, climb the roadmap. No real target — 100% safe learning.</p></div>')

        with gr.Tabs():
            # ---------- 1. Sandbox ----------
            with gr.Tab("🧪 Sandbox"):
                gr.Markdown("Type any command — Nanban shows **simulated** output (fake practice target "
                            "`10.10.10.5`) + Tanglish explanation. Nothing runs for real.\n\n"
                            f"Try: `{'`, `'.join(sandbox.HELP[:8])}` …")
                sb_in = gr.Textbox(placeholder="nmap -sV 10.10.10.5", show_label=False, lines=1)
                sb_run = gr.Button("▶️ Run (simulated)", variant="primary", size="sm")
                sb_out = gr.Textbox(show_label=False, lines=10, interactive=False, elem_classes=["sb-out"])
                sb_expl = gr.Markdown()

                def _sb(cmd):
                    out, expl = sandbox.run(cmd)
                    return out, f"**💡 {expl}**"
                sb_run.click(_sb, sb_in, [sb_out, sb_expl])
                sb_in.submit(_sb, sb_in, [sb_out, sb_expl])
                gr.Examples([["nmap -sV 10.10.10.5"], ["nikto 10.10.10.5"],
                             ["sqlmap -u http://10.10.10.5/vuln?id=1 --dbs"], ["whoami"],
                             ["searchsploit vsftpd 2.3.4"]], inputs=sb_in, label="Examples")

            # ---------- 2. Guided Labs ----------
            with gr.Tab("🎓 Guided Labs"):
                lab_state = gr.State(("", 0))
                gr.Markdown("Step-by-step labs. Pick one, follow each step, run it, learn. Finish = XP.")
                lab_pick = gr.Dropdown(
                    choices=[(f'{l["level"]}  {l["title"]}', l["id"]) for l in gl.labs_list()],
                    label="Choose a lab", value=None)
                lab_goal = gr.Markdown()
                lab_body = gr.Markdown()
                with gr.Row():
                    lab_runbtn = gr.Button("▶️ Run step (sandbox)", variant="primary", size="sm")
                    lab_next = gr.Button("➡️ Next step", size="sm", variant="secondary")
                lab_out = gr.Textbox(show_label=False, lines=8, interactive=False,
                                     elem_classes=["lab-out"], visible=False)
                lab_teach = gr.Markdown()
                lab_award = gr.Markdown()

                def _lab_start(lid):
                    lab = gl.lab_by_id(lid)
                    if not lab:
                        return "", "", ("", 0), gr.update(visible=False), "", ""
                    goal = f"🎯 **Goal:** {lab['goal_ta']}"
                    return goal, gl.step_markdown(lid, 0), (lid, 0), gr.update(visible=False), "", ""
                lab_pick.change(_lab_start, lab_pick,
                                [lab_goal, lab_body, lab_state, lab_out, lab_teach, lab_award])

                def _lab_run(state):
                    lid, idx = state
                    if not lid:
                        return gr.update(visible=False), "Oru lab thernedu first."
                    out, teach = gl.run_step(lid, idx)
                    return gr.update(value=out, visible=True), f"**📘 {teach}**"
                lab_runbtn.click(_lab_run, lab_state, [lab_out, lab_teach])

                def _lab_next(state):
                    lid, idx = state
                    if not lid:
                        return "", (lid, idx), gr.update(visible=False), "", ""
                    idx += 1
                    lab = gl.lab_by_id(lid)
                    award = ""
                    if idx >= len(lab["steps"]):
                        msg = progress.award("labs", lid, lab["xp"])
                        if msg:
                            award = f"🎉 {msg}"
                    return gl.step_markdown(lid, idx), (lid, idx), gr.update(visible=False), "", award
                lab_next.click(_lab_next, lab_state,
                               [lab_body, lab_state, lab_out, lab_teach, lab_award])

            # ---------- 3. SOC Sim ----------
            with gr.Tab("🛡️ SOC Sim"):
                soc_state = gr.State(("", 0))
                gr.Markdown("You're a SOC analyst. Read the logs, answer the questions, learn to **detect** "
                            "attacks. Solve all = XP.")
                soc_pick = gr.Dropdown(
                    choices=[(f'{s["level"]}  {s["title"]}', s["id"]) for s in soc_sim.scenarios_list()],
                    label="Choose a scenario", value=None)
                soc_intro = gr.Markdown()
                soc_q = gr.Markdown()
                soc_opts = gr.Radio(choices=[], show_label=False)
                with gr.Row():
                    soc_submit = gr.Button("✅ Submit answer", variant="primary", size="sm")
                    soc_next = gr.Button("➡️ Next question", size="sm", variant="secondary")
                soc_fb = gr.Markdown()
                soc_award = gr.Markdown()

                def _soc_start(sid):
                    if not sid:
                        return "", "", gr.update(choices=[], value=None), ("", 0), "", ""
                    intro = soc_sim.intro_markdown(sid)
                    q, opts = soc_sim.question_markdown(sid, 0)
                    return intro, q, gr.update(choices=opts, value=None), (sid, 0), "", ""
                soc_pick.change(_soc_start, soc_pick,
                                [soc_intro, soc_q, soc_opts, soc_state, soc_fb, soc_award])

                def _soc_submit(state, choice):
                    sid, idx = state
                    if not sid:
                        return "Oru scenario thernedu."
                    ok, fb = soc_sim.check_answer(sid, idx, choice)
                    return fb
                soc_submit.click(_soc_submit, [soc_state, soc_opts], soc_fb)

                def _soc_next(state):
                    sid, idx = state
                    if not sid:
                        return "", gr.update(choices=[], value=None), (sid, idx), "", ""
                    idx += 1
                    sc = soc_sim.scenario_by_id(sid)
                    award = ""
                    if idx >= len(sc["questions"]):
                        msg = progress.award("soc", sid, sc["xp"])
                        if msg:
                            award = f"🎉 {msg}"
                        return (f"## ✅ Solved — {sc['title']}\n\nVera scenario try pannu.",
                                gr.update(choices=[], value=None), (sid, idx), "", award)
                    q, opts = soc_sim.question_markdown(sid, idx)
                    return q, gr.update(choices=opts, value=None), (sid, idx), "", award
                soc_next.click(_soc_next, soc_state, [soc_q, soc_opts, soc_state, soc_fb, soc_award])

            # ---------- 4. Progress ----------
            with gr.Tab("🗺️ Progress"):
                gr.Markdown("Un learning journey — XP, badges, roadmap. Labs + SOC solve pannina inga update aagum.")
                pg_view = gr.HTML(progress.roadmap_html())
                pg_refresh = gr.Button("🔄 Refresh", size="sm", variant="secondary")
                pg_refresh.click(progress.roadmap_html, None, pg_view)
