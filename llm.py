"""
The AI backend for Nanban. One interface, two engines:

  • "local"  — Ollama on your own machine (free, private, offline). Default.
  • "hosted" — any OpenAI-compatible API (Groq, OpenAI, OpenRouter, Together, Mistral…).
               Point it at a frontier model and Nanban behaves at THAT model's level.
               OpenRouter even serves Claude and GPT-4 through this same interface.

Set the engine in config.py (LLM_BACKEND + the HOSTED_* values). Everything else in
Nanban — chat modes, the terminal agent, tool calling — works the same either way,
because this module makes both engines look identical to the rest of the app.

Honest note: a local 8B model can't match a frontier hosted model's intelligence.
For "latest-Claude-level" responses, use the hosted backend with a top model; for
free + private, use local. You can switch any time.
"""

import json

try:
    import ollama  # optional: only used when LLM_BACKEND == "local" (Ollama runtime)
    _HAVE_OLLAMA = True
except ImportError:  # pragma: no cover
    ollama = None   # type: ignore
    _HAVE_OLLAMA = False

import config

# ---------------------------------------------------------------- adapter objects
# These mimic Ollama's streaming chunk shape so agent_core.py needs no changes:
#   chunk.message.content            -> str | None
#   chunk.message.tool_calls         -> [call, ...] | None
#   call.function.name               -> str
#   call.function.arguments          -> dict


class _Fn:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments      # dict


class _ToolCall:
    def __init__(self, name, arguments):
        self.function = _Fn(name, arguments)


class _Msg:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class _Chunk:
    def __init__(self, content=None, tool_calls=None):
        self.message = _Msg(content, tool_calls)


# ---------------------------------------------------------------- backend info

def backend() -> str:
    """One of 'hosted', 'local' (Ollama), or 'portable' (bundled llama.cpp, no install)."""
    value = getattr(config, "LLM_BACKEND", "local")
    if value == "hosted":
        return "hosted"
    if value == "router":
        return "router"
    if value == "council":
        return "council"
    if value == "portable":
        return "portable"
    # value == "local" (default) → use Ollama if it's here, otherwise fall back to portable
    return "local" if _HAVE_OLLAMA else "portable"


def model_name() -> str:
    b = backend()
    if b == "hosted":
        return config.HOSTED_MODEL
    if b in ("router", "council"):
        return "auto"
    if b == "portable":
        import local_runtime
        return local_runtime.describe()
    return config.MODEL


def describe() -> str:
    b = backend()
    host = (getattr(config, "HOSTED_BASE_URL", "") or "").split("//")[-1].split("/")[0]
    if b == "hosted":
        return f"☁️ {config.HOSTED_MODEL} ({host})"
    if b == "router":
        return f"🏆 Nanban Best — auto-routing ({host})"
    if b == "council":
        return f"🏛️ Nanban Council — several models combined ({host})"
    if b == "portable":
        import local_runtime
        return local_runtime.describe()
    return f"🖥️ {config.MODEL} (local)"


def error_hint(e: Exception) -> str:
    """A helpful message for the agent to show when a call fails."""
    if backend() in ("hosted", "router", "council"):
        msg = str(getattr(e, "message", e))
        if "api_key" in msg.lower() or "authentication" in msg.lower() or "401" in msg:
            return "Hosted model auth failed — check HOSTED_API_KEY in config.py."
        return f"Can't reach the hosted model ({msg}). Check HOSTED_BASE_URL / your internet."
    error = getattr(e, "error", str(e))
    if "not found" in str(error).lower():
        return f"Model not downloaded. Run in Command Prompt:  ollama pull {config.MODEL}"
    return f"Can't reach Ollama ({error}). Open the Ollama app and try again."


# ---------------------------------------------------------------- hosted translation

_client = None


def _openai_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(base_url=config.HOSTED_BASE_URL, api_key=config.HOSTED_API_KEY or "missing-key")
    return _client


def _tools_to_openai(tool_list):
    """Python callables -> OpenAI tool schemas (reusing Ollama's converter)."""
    from ollama._utils import convert_function_to_tool
    out = []
    for f in tool_list or []:
        spec = convert_function_to_tool(f).model_dump()["function"]
        params = {k: v for k, v in (spec.get("parameters") or {}).items() if v is not None}
        # strip the per-property nulls Ollama leaves in
        for prop in (params.get("properties") or {}).values():
            for k in [k for k, v in list(prop.items()) if v is None]:
                prop.pop(k, None)
        out.append({"type": "function", "function": {
            "name": spec["name"], "description": spec.get("description") or "", "parameters": params}})
    return out


def _history_to_openai(messages):
    """Ollama-style history -> OpenAI format, synthesising tool_call ids so tool
    results line up with the assistant calls that produced them."""
    out, pending = [], []
    counter = 0
    for m in messages:
        role = m.get("role")
        if role == "assistant" and m.get("tool_calls"):
            calls, pending = [], []
            for tc in m["tool_calls"]:
                fn = tc["function"]
                cid = f"call_{counter}"
                counter += 1
                pending.append(cid)
                args = fn.get("arguments", {})
                calls.append({"id": cid, "type": "function", "function": {
                    "name": fn["name"], "arguments": args if isinstance(args, str) else json.dumps(args)}})
            out.append({"role": "assistant", "content": m.get("content") or None, "tool_calls": calls})
        elif role == "tool":
            cid = pending.pop(0) if pending else f"call_{counter}"
            counter += 1
            out.append({"role": "tool", "tool_call_id": cid, "content": str(m.get("content", ""))})
        elif m.get("images_data"):
            parts = []
            if m.get("content"):
                parts.append({"type": "text", "text": m["content"]})
            for url in m["images_data"]:
                parts.append({"type": "image_url", "image_url": {"url": url}})
            out.append({"role": role, "content": parts})
        else:
            out.append({"role": role, "content": m.get("content", "")})
    return out


def _model_not_found(e: Exception) -> bool:
    """True when the provider rejected the *model id* (vs auth / network / rate limit)."""
    msg = str(getattr(e, "message", e)).lower()
    status = getattr(e, "status_code", None)
    hits = ("does not exist", "model_not_found", "no such model", "not a valid model",
            "do not have access", "model not found", "decommission", "unknown model")
    return any(h in msg for h in hits) or (status == 404 and "model" in msg)


def _should_failover(e: Exception) -> bool:
    """True when the error means 'this model/provider is unavailable right now' — so we should
    switch to another model. Covers missing model, rate limits, overload, server errors, timeouts
    and connection drops. NOT auth errors (a bad key won't be fixed by another model)."""
    msg = str(getattr(e, "message", e)).lower()
    status = getattr(e, "status_code", None)
    if "api_key" in msg or "authentication" in msg or "invalid key" in msg or status == 401:
        return False
    if _model_not_found(e):
        return True
    if status in (408, 409, 425, 429, 500, 502, 503, 504):
        return True
    hits = ("rate limit", "rate_limit", "overloaded", "over capacity", "capacity", "timeout",
            "timed out", "temporarily", "unavailable", "connection", "bad gateway", "try again",
            "service error", "server error", "too many requests", "econnreset", "reset by peer")
    return any(h in msg for h in hits)


def _remember_model(new_model: str) -> None:
    """Persist an auto-chosen model so the fix sticks across restarts."""
    config.HOSTED_MODEL = new_model
    try:
        import settings
        settings.save({"HOSTED_MODEL": new_model})   # also rebuilds the client
    except Exception:
        global _client
        _client = None


def _hosted_stream(messages, tool_list, options):
    """Stream from the hosted model with automatic failover: if the current model is missing,
    down, rate-limited, overloaded or timing out, switch to another working model on the same key
    and retry — up to a few alternates — so the user keeps getting answers. Only switches before
    any text has been produced (so a reply is never duplicated)."""
    tried: set[str] = set()
    routing = backend() == "router"
    if routing:                                 # 🏆 Nanban Best: pick the best model for THIS query
        try:
            import router
            model = router.route_model(messages)[0] or config.HOSTED_MODEL
        except Exception:
            model = config.HOSTED_MODEL
    else:
        model = config.HOSTED_MODEL
    # 📷 if the message has an image, automatically use a vision-capable model
    if any(m.get("images_data") for m in messages):
        vm = pick_vision_model()
        if vm:
            model = vm
    last_error = None
    for _attempt in range(4):
        tried.add(model)
        state = {"started": False}
        try:
            yield from _hosted_once(model, messages, tool_list, options, state)
            if not routing and model != config.HOSTED_MODEL:
                _remember_model(model)          # the alternate worked — keep it (single-model mode)
            return
        except Exception as e:
            last_error = e
            if state["started"] or not _should_failover(e):
                raise                            # mid-stream, or a real error (e.g. bad key)
            nxt = pick_available_model(exclude=tried)
            if not nxt or nxt in tried:
                raise
            model = nxt                          # try the next-best available model
    if last_error:
        raise last_error


def _hosted_once(model, messages, tool_list, options, state=None):
    client = _openai_client()
    kwargs = dict(
        model=model,
        messages=_history_to_openai(messages),
        stream=True,
        temperature=(options or {}).get("temperature", getattr(config, "TEMPERATURE", 0.6)),
    )
    oai_tools = _tools_to_openai(tool_list)
    if oai_tools:
        kwargs["tools"] = oai_tools
    acc = {}  # index -> {name, args}
    for chunk in client.chat.completions.create(**kwargs):
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if getattr(delta, "content", None):
            if state is not None:
                state["started"] = True
            yield _Chunk(content=delta.content)
        for tc in (getattr(delta, "tool_calls", None) or []):
            if state is not None:
                state["started"] = True
            slot = acc.setdefault(tc.index, {"name": "", "args": ""})
            if tc.function and tc.function.name:
                slot["name"] = tc.function.name
            if tc.function and tc.function.arguments:
                slot["args"] += tc.function.arguments
    if acc:
        calls = []
        for slot in acc.values():
            try:
                args = json.loads(slot["args"]) if slot["args"].strip() else {}
            except json.JSONDecodeError:
                args = {}
            calls.append(_ToolCall(slot["name"], args))
        yield _Chunk(tool_calls=calls)


# ---------------------------------------------------------------- the one entry point

def _ollama_chat(messages, tools=None, options=None):
    opts = {"temperature": getattr(config, "TEMPERATURE", 0.6), "num_ctx": getattr(config, "CONTEXT_WINDOW", 8192)}
    opts.update(options or {})
    # convert any attached images into Ollama's per-message `images` (base64) — needs a vision model
    oll_msgs = []
    for m in messages:
        mm = {k: v for k, v in m.items() if k != "images_data"}
        if m.get("images_data"):
            mm["images"] = [u.split(",", 1)[1] if u.startswith("data:") else u for u in m["images_data"]]
        oll_msgs.append(mm)
    for chunk in ollama.chat(
        model=config.MODEL, messages=oll_msgs, tools=tools or None, stream=True,
        options=opts, keep_alive=getattr(config, "KEEP_ALIVE", "30m"),
    ):
        yield chunk


def chat(messages, tools=None, options=None):
    """Stream a reply. Yields chunk objects shaped like Ollama's (see adapter classes).

    Master-class reliability for 🏆 Best / 🏛️ Council / hosted: if the hosted side can't work
    (no key yet, or it fails before producing any text) and Ollama is available, it transparently
    falls back to the local model — so these modes never dead-end on an error."""
    b = backend()
    if b in ("hosted", "router", "council"):
        # no key yet but Ollama is here → just answer locally so nothing breaks
        if not config.HOSTED_API_KEY and _HAVE_OLLAMA:
            yield from _ollama_chat(messages, tools, options)
            return
        produced = {"any": False}
        try:
            source = (__import__("council").run(messages, options) if b == "council"
                      else _hosted_stream(messages, tools, options))
            for chunk in source:
                produced["any"] = True
                yield chunk
            return
        except Exception:
            if produced["any"] or not _HAVE_OLLAMA:
                raise                       # mid-reply, or no local fallback → surface the error
            yield from _ollama_chat(messages, tools, options)   # hosted failed cold → use local
            return
    if b == "portable":
        import local_runtime
        yield from local_runtime.chat(messages, tools, options)
        return
    yield from _ollama_chat(messages, tools, options)


# model ids that aren't text-chat models (audio, embeddings, safety, etc.)
_NON_CHAT = ("whisper", "tts", "embed", "guard", "moderation", "rerank",
             "distil-whisper", "speech", "audio", "transcribe", "clip")


def _is_chat_model(mid: str) -> bool:
    m = mid.lower()
    return not any(bad in m for bad in _NON_CHAT)


def _model_score(mid: str) -> int:
    """Rough 'how good a general chat model' score, to auto-pick a sensible default."""
    m = mid.lower()
    score = 0
    for kw, pts in (("405b", 60), ("120b", 55), ("90b", 50), ("70b", 48), ("72b", 48),
                    ("large", 35), ("versatile", 28), ("instruct", 22), ("gpt-oss", 25),
                    ("32b", 30), ("27b", 26), ("20b", 24), ("flash", 20), ("8b", 18),
                    ("9b", 16), ("instant", 16), ("mini", 10), ("pro", 14)):
        if kw in m:
            score += pts
    for kw, pen in (("preview", 6), ("deprecated", 40), ("nano", 6), ("1b", 20), ("3b", 10)):
        if kw in m:
            score -= pen
    return score


def list_models(limit: int = 40) -> list[str]:
    """Usable chat model ids from the current hosted provider (empty for local)."""
    if backend() not in ("hosted", "router", "council"):
        return []
    try:
        models = _openai_client().models.list()
        ids = [m.id for m in getattr(models, "data", []) if _is_chat_model(m.id)]
        return sorted(ids)[:limit]
    except Exception:
        return []


_VISION_HINTS = ("vision", "-vl", "vl-", "llava", "pixtral", "gemini", "multimodal", "qwen2-vl", "qwen2.5-vl")


def _is_vision_model(mid: str) -> bool:
    m = mid.lower()
    return any(v in m for v in _VISION_HINTS)


def pick_vision_model(exclude=()) -> str:
    """Best available image-capable model on the current key (empty if none)."""
    excl = {exclude} if isinstance(exclude, str) and exclude else set(exclude)
    vis = [m for m in list_models(200) if _is_vision_model(m) and m not in excl]
    return max(vis, key=_model_score) if vis else ""


def pick_available_model(preferred: str = "", exclude=()) -> str:
    """Return a model id this key can actually use: `preferred` if it's available, otherwise the
    best-scoring available chat model, never one in `exclude` (a single id or a set/list). Falls
    back to whatever was asked for if the list can't be fetched."""
    excl = {exclude} if isinstance(exclude, str) and exclude else set(exclude)
    avail = [m for m in list_models(200) if m not in excl]
    if not avail:
        return preferred or config.HOSTED_MODEL
    if preferred and preferred in avail:
        return preferred
    return max(avail, key=_model_score)


def ping() -> tuple[bool, str]:
    """Quick health check for the current backend."""
    try:
        b = backend()
        if b in ("hosted", "router", "council"):
            if not config.HOSTED_API_KEY:
                return False, "No HOSTED_API_KEY set in config.py."
            _openai_client().models.list()
            return True, describe()
        if b == "portable":
            import local_runtime
            return local_runtime.ping()
        ollama.list()
        return True, describe()
    except Exception as e:
        return False, error_hint(e)
