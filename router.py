"""
🏆 Nanban Best — one agent, many brains.

Instead of locking you to a single model, this routes EACH question to the strongest model for
that task, picking from whatever models your key exposes:
  • coding / bugs / SQL      -> a coder model (Qwen Coder, Codestral, DeepSeek)
  • hard reasoning / maths   -> a reasoning model (DeepSeek-R1, Nemotron, o-series)
  • images / diagrams        -> a vision model (Gemini, *-VL, Pixtral)
  • quick / short questions  -> the fastest model (gpt-oss-20b, *instant, *flash, 8B)
  • everything else          -> the biggest / best all-round model

If the picked model is busy or down, Nanban's auto-failover moves to the next best one. Result:
the best available answer, automatically, from one chat box.

One NVIDIA build.nvidia.com key already unlocks DeepSeek-R1, Llama 405B, Nemotron 120B, Qwen
Coder and Llama 70B, so routing works great with a single key. It also works on Groq, etc. —
it only ever routes among models the current key actually lists.
"""

import re

# category -> model-name substrings that indicate a good fit (checked in order)
_PREF = {
    "coding":    ["coder", "codestral", "qwen2.5-coder", "deepseek-v", "starcoder", "code"],
    "reasoning": ["deepseek-r1", "-r1", "nemotron", "reason", "think", "qwq", "o1", "o3"],
    "vision":    ["vision", "-vl", "llava", "pixtral", "gemini", "multimodal"],
    "fast":      ["instant", "gpt-oss-20b", "-8b", "flash", "mini", "-9b", "small", "lite"],
    "general":   [],   # falls through to the best-scoring model
}

_CODE_HINT = re.compile(
    r"```|def |class |function |import |SELECT |<\w+>|\bpython\b|\bjavascript\b|\breact\b|"
    r"\bcode\b|\bbug\b|\bfunction\b|\bapi\b|\bsql\b|\bregex\b|\bcompile\b|\berror\b", re.I)
_REASON_HINT = re.compile(
    r"\bwhy\b|\bprove\b|\bstep[- ]by[- ]step\b|\bcalculat|\bsolve\b|\bmath\b|\blogic\b|"
    r"\breason\b|\bplan\b|how many|\bpuzzle\b|\bstrategy\b|\banalyse\b|\banalyze\b", re.I)
_VISION_HINT = re.compile(
    r"\bimage\b|\bphoto\b|\bpicture\b|\bscreenshot\b|\bdiagram\b|\bchart\b|look at|\bpng\b|\bjpg\b", re.I)


def classify(text: str) -> str:
    t = text or ""
    if _VISION_HINT.search(t):
        return "vision"
    if _CODE_HINT.search(t):
        return "coding"
    if _REASON_HINT.search(t):
        return "reasoning"
    if len(t) < 120:
        return "fast"
    return "general"


def _last_user(messages) -> str:
    for m in reversed(messages or []):
        if m.get("role") == "user":
            return str(m.get("content", ""))
    return ""


def route_model(messages):
    """Return (model_id, category) — the best available model for this query, from the current
    key's model list. Falls back to the configured model if the list can't be fetched."""
    import config
    import llm
    avail = llm.list_models(200)
    cat = classify(_last_user(messages))
    if not avail:
        return getattr(config, "HOSTED_MODEL", ""), cat
    low = {m: m.lower() for m in avail}
    for sub in _PREF.get(cat, []):
        hits = [m for m in avail if sub in low[m]]
        if hits:
            return max(hits, key=llm._model_score), cat
    return max(avail, key=llm._model_score), cat
