"""
Zero-dependency local AI runtime for Nanban Portable.

Replaces Ollama with llama-cpp-python, so the app runs on any computer with
NO external install (no Ollama, no Docker, no model manager). The model file
sits next to the app in models/, and llama-cpp-python runs it directly.

Three ways a model gets here, tried in order:
  1. A .gguf file already in models/           (portable bundle)
  2. Auto-download on first run (small model)  (fresh install)
  3. Fallback: tell the user to pick cloud     (no internet)
"""
from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path
from typing import Iterator

import config

# ---------------------------------------------------------------- model location

MODEL_DIR = config.BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# Default bundled model — tuned for size, multilingual support (Tamil/English/Tanglish),
# tool calling, and smart enough for everyday help on a 16 GB laptop.
DEFAULT_MODEL_FILE = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
DEFAULT_MODEL_URL = (
    "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/"
    "qwen2.5-1.5b-instruct-q4_k_m.gguf"
)
DEFAULT_MODEL_SIZE_MB = 1000  # approx

# Alternative bigger model (optional, user can drop it in):
#   qwen2.5-7b-instruct-q4_k_m.gguf  (~4.4 GB) — much smarter


# ---------------------------------------------------------------- the engine

_llm = None  # lazy singleton, loaded on first use


def available_model() -> Path | None:
    """First .gguf file found in models/ — or None if the folder is empty."""
    for p in MODEL_DIR.glob("*.gguf"):
        return p
    return None


def download_default_model(progress=None) -> Path:
    """Fetch the default small model on first run. ~1 GB one-time download."""
    target = MODEL_DIR / DEFAULT_MODEL_FILE
    if target.exists() and target.stat().st_size > 10 * 1024 * 1024:
        return target
    tmp = target.with_suffix(".part")
    print(f"Downloading AI model (~{DEFAULT_MODEL_SIZE_MB} MB, one time)…", flush=True)
    def _hook(block, blocksize, total):
        if progress and total > 0:
            progress(min(1.0, (block * blocksize) / total))
    urllib.request.urlretrieve(DEFAULT_MODEL_URL, tmp, reporthook=_hook)
    tmp.rename(target)
    print("Model ready.", flush=True)
    return target


def ensure_model() -> Path:
    """Return a usable model path, downloading the default one if needed."""
    found = available_model()
    if found:
        return found
    return download_default_model()


def _load():
    """Load llama-cpp. Cached so we only pay the cost once per process."""
    global _llm
    if _llm is not None:
        return _llm
    try:
        from llama_cpp import Llama
    except ImportError as e:
        raise RuntimeError(
            "llama-cpp-python is not installed. Nanban Portable bundles it; "
            "if you installed manually, run:  pip install llama-cpp-python"
        ) from e
    model_path = ensure_model()
    n_threads = max(2, (os.cpu_count() or 4) - 1)
    _llm = Llama(
        model_path=str(model_path),
        n_ctx=getattr(config, "CONTEXT_WINDOW", 8192),
        n_threads=n_threads,
        n_gpu_layers=0,          # pure CPU so it works on any laptop
        verbose=False,
    )
    return _llm


def describe() -> str:
    path = available_model()
    return f"📦 {path.name} (portable)" if path else f"📦 {DEFAULT_MODEL_FILE} (portable, will download)"


def ping() -> tuple[bool, str]:
    try:
        _load()
        return True, describe()
    except Exception as e:
        return False, f"Portable model not ready: {e}"


# ---------------------------------------------------------------- chat streaming
# Returns chunks shaped like Ollama's, so agent_core.py / llm.py don't change.


class _Fn:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


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


def chat(messages, tools=None, options=None) -> Iterator[_Chunk]:
    """Stream a reply from the bundled local model."""
    llm = _load()
    # Convert the Ollama-style history into a single prompt the base model understands.
    # (The small portable model doesn't do structured tool-calling well; the agent's
    # tools still run via the hosted/full backends.)
    prompt_parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "") or ""
        if role == "system":
            prompt_parts.append(f"<|im_start|>system\n{content}<|im_end|>")
        elif role == "user":
            prompt_parts.append(f"<|im_start|>user\n{content}<|im_end|>")
        elif role == "assistant":
            prompt_parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")
        elif role == "tool":
            prompt_parts.append(f"<|im_start|>user\n[tool {m.get('tool_name','')} result]\n{content}<|im_end|>")
    prompt_parts.append("<|im_start|>assistant\n")
    prompt = "\n".join(prompt_parts)

    opts = options or {}
    stream = llm(
        prompt=prompt,
        max_tokens=1024,
        temperature=opts.get("temperature", getattr(config, "TEMPERATURE", 0.6)),
        top_p=0.9,
        stop=["<|im_end|>", "<|im_start|>"],
        stream=True,
    )
    for piece in stream:
        text = piece["choices"][0].get("text", "")
        if text:
            yield _Chunk(content=text)
