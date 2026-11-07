"""
Nanban API: use your local AI from any app, script or bot.

OpenAI-compatible, so code written for ChatGPT's API works by changing the base URL:
    base_url = "http://<laptop>:8000/v1",  api_key = "<one of config.API_KEYS>"

Endpoints
  GET  /v1/models                      list of models (nanban, nanban:<mode>, and raw Ollama models)
  POST /v1/chat/completions            chat (stream=true supported). model "nanban:research" = Research mode with tools
  POST /api/agent                      {"message", "mode", "session_id"}  keeps a conversation per session_id
  GET  /api/servers                    registered servers (names only)
  GET  /api/servers/status             health of all servers
  POST /api/servers/{name}/run         {"command"} run a command on a server (risky commands refused)
  GET  /api/health                     is Ollama up, which model, VPN state
  GET  /docs                           interactive documentation (Swagger)

Auth: Authorization: Bearer <key>. With API_ALLOW_LOCAL_WITHOUT_KEY, requests from the laptop itself need no key.
Usage is logged to data/api_usage.jsonl.
"""

import json
import re
import threading
import time
import uuid
from collections import defaultdict, deque
from typing import Any

import ollama
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

import config
import llm
import servers
import tools
import vpn
from agent_core import Agent

app = FastAPI(title=f"{config.AGENT_NAME} API", version="1.0",
              description="Local AI agent API (OpenAI-compatible). Everything runs on your own machine.")

USAGE_FILE = config.DATA_DIR / "api_usage.jsonl"
_rate: dict[str, deque] = defaultdict(deque)
_sessions: dict[str, tuple[Agent, float]] = {}
_lock = threading.Lock()
SESSION_TTL = 3600 * 6
DANGEROUS = [
    r"\brm\s+-[a-zA-Z]*[rf]", r"\bmkfs", r"\bdd\s+if=", r":\(\)\s*\{", r"\bshutdown\b", r"\breboot\b",
    r"\bchmod\s+-R\s+777\s+/", r">\s*/dev/sd", r"\bgit\s+push\s+.*--force", r"\bgit\s+reset\s+--hard",
]


# ---------------------------------------------------------------- auth, rate limit, usage

def _client_is_local(request: Request) -> bool:
    host = request.client.host if request.client else ""
    return host in {"127.0.0.1", "::1", "localhost"}


def require_key(request: Request) -> str:
    header = request.headers.get("authorization", "")
    key = header[7:].strip() if header.lower().startswith("bearer ") else request.query_params.get("api_key", "")
    if key and key in config.API_KEYS:
        identity = "key:" + key[-4:]
    elif config.API_ALLOW_LOCAL_WITHOUT_KEY and _client_is_local(request):
        identity = "local"
    elif not config.API_KEYS and _client_is_local(request):
        identity = "local"
    else:
        raise HTTPException(401, "Missing or invalid API key. Send: Authorization: Bearer <key> "
                                 "(keys are set in config.py -> API_KEYS).")
    now = time.monotonic()
    window = _rate[identity]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= config.API_RATE_LIMIT:
        raise HTTPException(429, f"Rate limit: {config.API_RATE_LIMIT} requests per minute.")
    window.append(now)
    return identity


def log_usage(identity: str, endpoint: str, started: float, **extra: Any) -> None:
    record = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "who": identity, "endpoint": endpoint,
              "ms": int((time.time() - started) * 1000), **extra}
    try:
        with USAGE_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def recent_usage(limit: int = 50) -> list[dict]:
    try:
        lines = USAGE_FILE.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in lines]
    except (OSError, json.JSONDecodeError):
        return []


# ---------------------------------------------------------------- OpenAI-compatible

class ChatMessage(BaseModel):
    role: str
    content: Any = ""


class ChatRequest(BaseModel):
    model: str = "nanban"
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    user: str | None = None


def _split_model(model: str) -> tuple[str, str | None]:
    """'nanban' -> (MODEL, assistant) ; 'nanban:coding' -> (MODEL, coding) ; 'llama3.1:8b' -> raw, no agent."""
    if model == "nanban":
        return config.MODEL, config.DEFAULT_MODE
    if model.startswith("nanban:"):
        mode = model.split(":", 1)[1]
        return config.MODEL, (mode if mode in config.MODES else config.DEFAULT_MODE)
    return model, None


def _content_text(content: Any) -> str:
    if isinstance(content, list):
        return " ".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content or "")


def _agent_reply(mode: str, messages: list[ChatMessage], user: str):
    """Run a Nanban mode (with its tools) over the given history; yields text chunks."""
    agent = Agent(mode, user=user or "")
    history = [{"role": m.role, "content": _content_text(m.content)} for m in messages if m.role in {"user", "assistant"}]
    if not history or history[-1]["role"] != "user":
        raise HTTPException(400, "The last message must be from the user.")
    agent.history = history[:-1]
    for event in agent.stream(history[-1]["content"]):
        if event.kind == "text":
            yield event.data
        elif event.kind == "error":
            raise HTTPException(503, event.data)


def _raw_reply(model: str, messages: list[ChatMessage], temperature, max_tokens):
    """Raw passthrough to the active backend (whichever LLM_BACKEND is set)."""
    msgs = [{"role": m.role, "content": _content_text(m.content)} for m in messages]
    opts = {}
    if temperature is not None:
        opts["temperature"] = temperature
    if max_tokens:
        opts["num_predict"] = max_tokens
    try:
        for chunk in llm.chat(msgs, tools=None, options=opts):
            if chunk.message.content:
                yield chunk.message.content
    except Exception as e:
        raise HTTPException(503, llm.error_hint(e))


@app.get("/v1/models")
def list_models(identity: str = Depends(require_key)):
    data = [{"id": "nanban", "object": "model", "owned_by": "local"}]
    data += [{"id": f"nanban:{m}", "object": "model", "owned_by": "local"} for m in config.MODES]
    try:
        data += [{"id": m.model, "object": "model", "owned_by": "ollama"} for m in ollama.list().models]
    except Exception:
        pass
    return {"object": "list", "data": data}


@app.post("/v1/chat/completions")
def chat_completions(body: ChatRequest, request: Request, identity: str = Depends(require_key)):
    started = time.time()
    model, mode = _split_model(body.model)
    chunks = _agent_reply(mode, body.messages, body.user) if mode else _raw_reply(model, body.messages, body.temperature, body.max_tokens)
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())

    if body.stream:
        def events():
            total = 0
            try:
                for piece in chunks:
                    total += len(piece)
                    data = {"id": completion_id, "object": "chat.completion.chunk", "created": created, "model": body.model,
                            "choices": [{"index": 0, "delta": {"role": "assistant", "content": piece}, "finish_reason": None}]}
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                done = {"id": completion_id, "object": "chat.completion.chunk", "created": created, "model": body.model,
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
                yield f"data: {json.dumps(done)}\n\ndata: [DONE]\n\n"
            except HTTPException as e:
                yield f"data: {json.dumps({'error': {'message': e.detail}})}\n\n"
            finally:
                log_usage(identity, "chat.completions", started, model=body.model, chars=total, stream=True)
        return StreamingResponse(events(), media_type="text/event-stream")

    text = "".join(chunks)
    log_usage(identity, "chat.completions", started, model=body.model, chars=len(text))
    prompt_chars = sum(len(_content_text(m.content)) for m in body.messages)
    return {
        "id": completion_id, "object": "chat.completion", "created": created, "model": body.model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": prompt_chars // 4, "completion_tokens": len(text) // 4,
                  "total_tokens": (prompt_chars + len(text)) // 4},
    }


# ---------------------------------------------------------------- Nanban-native agent endpoint

class AgentRequest(BaseModel):
    message: str
    mode: str = config.DEFAULT_MODE
    session_id: str = Field(default="", description="Reuse to continue a conversation")
    user: str = ""


@app.post("/api/agent")
def agent_endpoint(body: AgentRequest, identity: str = Depends(require_key)):
    started = time.time()
    now = time.time()
    with _lock:
        for sid in [s for s, (_, seen) in _sessions.items() if now - seen > SESSION_TTL]:
            del _sessions[sid]
        session_id = body.session_id or uuid.uuid4().hex[:16]
        agent, _ = _sessions.get(session_id, (None, 0))
        if agent is None:
            agent = Agent(body.mode, user=body.user)
        agent.mode = body.mode if body.mode in config.MODES else agent.mode
        _sessions[session_id] = (agent, now)
    text, tool_calls = "", []
    for event in agent.stream(body.message):
        if event.kind == "text":
            text += event.data
        elif event.kind == "tool_start":
            tool_calls.append({"tool": event.tool, "args": event.data})
        elif event.kind == "error":
            raise HTTPException(503, event.data)
    log_usage(identity, "agent", started, mode=agent.mode, chars=len(text), tools=len(tool_calls))
    return {"session_id": session_id, "mode": agent.mode, "reply": text, "tool_calls": tool_calls}


# ---------------------------------------------------------------- servers (DevOps)

class RunRequest(BaseModel):
    command: str
    timeout: int = 120


@app.get("/api/servers")
def servers_list(identity: str = Depends(require_key)):
    return {"servers": [{"name": n, "host": e["host"], "user": e["user"], "port": e["port"], "notes": e.get("notes", "")}
                        for n, e in servers.load().items()]}


@app.get("/api/servers/status")
def servers_status(identity: str = Depends(require_key)):
    started = time.time()
    rows = servers.status_all()
    log_usage(identity, "servers.status", started, count=len(rows))
    return {"servers": rows}


@app.post("/api/servers/{name}/run")
def servers_run(name: str, body: RunRequest, identity: str = Depends(require_key)):
    started = time.time()
    if any(re.search(p, body.command, re.IGNORECASE) for p in DANGEROUS):
        raise HTTPException(403, "Refused: this looks destructive. Run it yourself in the Nanban Terminal.")
    try:
        host = servers.connect(name)
    except Exception as e:
        raise HTTPException(502, str(e))
    result = host.run(body.command, timeout=min(max(body.timeout, 1), 900))
    log_usage(identity, "servers.run", started, server=name, code=result.code)
    return {"server": name, "command": body.command, "exit_code": result.code, "output": result.output,
            "seconds": round(result.seconds, 2)}


# ---------------------------------------------------------------- health

@app.get("/api/health")
def health():
    try:
        models = [m.model for m in ollama.list().models]
        ollama_ok = True
    except Exception:
        models, ollama_ok = [], False
    ok, desc = llm.ping()
    return {"ok": ok, "agent": config.AGENT_NAME, "backend": llm.backend(), "model": llm.model_name(), "engine": desc, "model_installed": (config.MODEL in models) if llm.backend()=="local" else True,
            "ollama_models": models, "vpn": vpn.status(), "servers": servers.names(), "time": time.strftime("%Y-%m-%d %H:%M:%S")}


@app.exception_handler(HTTPException)
async def _openai_style_errors(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": {"message": exc.detail, "type": "error", "code": exc.status_code}})
