"""
🏛️ Nanban Council — ask several models, combine the best answer.

For each question Nanban asks 2–3 strong, *different* models in parallel (e.g. a reasoning model,
a big all-rounder and a coder), then a lead "editor" model merges their answers into ONE superior
reply — keeping what's right, fixing mistakes, resolving disagreements. This is the highest-quality
mode, at the cost of being slower and using more of your quota (3–4 calls per question).

Council mode answers directly (it doesn't run tools during the debate — it's for best-quality
answers, not tool actions). It only runs on a hosted/NVIDIA key that lists several models.
"""

import threading

import config


def pick_panel(avail: list[str], n: int = 3) -> list[str]:
    """Choose up to n strong, diverse models: a reasoning one, a big all-rounder, a coder."""
    import llm
    import router
    picks: list[str] = []

    def best_for(cat):
        for sub in router._PREF.get(cat, []):
            hits = [m for m in avail if sub in m.lower() and m not in picks]
            if hits:
                return max(hits, key=llm._model_score)
        return None

    for cat in ("reasoning", "coding"):
        m = best_for(cat)
        if m:
            picks.append(m)
    # add the best overall all-rounder not already picked
    rest = [m for m in avail if m not in picks]
    if rest:
        picks.append(max(rest, key=llm._model_score))
    # fill up to n with the next best
    for m in sorted(avail, key=llm._model_score, reverse=True):
        if len(picks) >= n:
            break
        if m not in picks:
            picks.append(m)
    return picks[:n]


def _answer(model, messages, options, out, idx):
    import llm
    try:
        client = llm._openai_client()
        r = client.chat.completions.create(
            model=model,
            messages=llm._history_to_openai(messages),
            temperature=(options or {}).get("temperature", 0.5),
            stream=False,
            timeout=55,                     # a slow expert never holds up the panel
        )
        out[idx] = (model, (r.choices[0].message.content or "").strip())
    except Exception:
        out[idx] = (model, "")


def _stream_text(text):
    import llm
    for word in text.split(" "):
        yield llm._Chunk(content=word + " ")


def run(messages, options=None):
    """Gather several experts in parallel, then stream one synthesised best answer."""
    import llm
    import router

    avail = llm.list_models(200)
    if not avail:
        yield from llm._hosted_once(config.HOSTED_MODEL, messages, None, options, None)
        return

    # 📷 image question → skip the debate, answer with a vision model
    if any(m.get("images_data") for m in messages):
        vm = llm.pick_vision_model() or max(avail, key=llm._model_score)
        yield from llm._hosted_once(vm, messages, None, options, None)
        return

    panel = pick_panel(avail, 3)
    if len(panel) < 2:
        yield from llm._hosted_once(panel[0] if panel else config.HOSTED_MODEL, messages, None, options, None)
        return

    # ---- ask every expert in parallel ----
    out = [None] * len(panel)
    threads = [threading.Thread(target=_answer, args=(m, messages, options, out, i), daemon=True)
               for i, m in enumerate(panel)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(60)                          # proceed with whoever answered within a minute
    answers = [(m, a) for item in out if item for (m, a) in [item] if a]

    if not answers:                                    # everyone failed → normal path with failover
        yield from llm._hosted_stream(messages, None, options)
        return
    if len(answers) == 1:                              # only one replied → just use it
        yield from _stream_text(answers[0][1])
        return

    # ---- synthesise one best answer ----
    user_q = router._last_user(messages)
    blocks = "\n\n".join(f"--- Expert {i} answer ---\n{a}" for i, (_m, a) in enumerate(answers, 1))
    synth = [
        {"role": "system", "content":
            "You are the lead editor of an expert panel. Several expert AI models independently "
            "answered the user's question. Merge them into ONE superior final answer: keep what is "
            "correct and useful, fix any mistakes, resolve disagreements, and be clear and well "
            "organised. Do NOT mention the experts or that answers were combined — just give the "
            "single best answer, in the same language the user used."},
        {"role": "user", "content":
            f"User's question:\n{user_q}\n\n{blocks}\n\nWrite the single best final answer now."},
    ]
    judge = max((m for m, _a in answers), key=llm._model_score)
    tried = set()
    model = judge
    for _ in range(3):
        tried.add(model)
        state = {"started": False}
        try:
            yield from llm._hosted_once(model, synth, None, options, state)
            return
        except Exception as e:
            if state["started"] or not llm._should_failover(e):
                raise
            nxt = llm.pick_available_model(exclude=tried)
            if not nxt or nxt in tried:
                best = max(answers, key=lambda x: llm._model_score(x[0]))[1]
                yield from _stream_text(best)           # fall back to the best single answer
                return
            model = nxt
