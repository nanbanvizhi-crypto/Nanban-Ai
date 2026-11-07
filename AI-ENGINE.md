# 🧠 AI Engine — making Nanban smarter and faster

Nanban can run on two kinds of brain. You choose in `config.py` → `LLM_BACKEND`.

## The honest picture

| | Local (Ollama) | Hosted (frontier model) |
|---|---|---|
| Intelligence | Good, limited by your laptop | **Top-tier** (Claude / GPT-4 / Llama-70B) |
| Speed | Depends on hardware | Very fast (esp. Groq) |
| Cost | **Free** | API usage (free tiers exist) |
| Privacy | **100% on your machine** | Goes to the provider |
| Internet | Not needed | Required |

A local 8B model is genuinely useful, but it **cannot** match a frontier model's reasoning — that's hardware, not settings. For "latest-Claude-level" intelligence and speed, use the **hosted** engine. Keep **local** when you want free + private. Switch any time.

---

## Option A — Make LOCAL as good as it gets (free)

In `config.py`:
- **Use a stronger model** your 16 GB laptop can run. Best picks:
  - `MODEL = "qwen2.5:14b"` — noticeably smarter than the 8B default (download: `ollama pull qwen2.5:14b`).
  - `MODEL = "qwen2.5:7b"` — great reasoning, lighter.
  - `MODEL = "qwen2.5-coder:14b"` — best for coding.
  - `MODEL = "llama3.2:3b"` — fastest, for snappy replies.
- **Speed:** `KEEP_ALIVE = "30m"` (already set) keeps the model warm in RAM so replies start instantly instead of reloading each time.
- Close other heavy apps; the model shares your RAM.

## Option B — Plug in a FRONTIER model (the real "Claude-level" upgrade)

In `config.py`, set `LLM_BACKEND = "hosted"` and pick a provider:

### Groq — free tier, extremely fast (recommended first try)
```python
LLM_BACKEND   = "hosted"
HOSTED_BASE_URL = "https://api.groq.com/openai/v1"
HOSTED_MODEL    = "llama-3.3-70b-versatile"   # a 70B model, instant responses
HOSTED_API_KEY  = "gsk_..."                    # free key from console.groq.com
```

### OpenRouter — serves Claude, GPT-4, Gemini (one key, any model)
```python
LLM_BACKEND   = "hosted"
HOSTED_BASE_URL = "https://openrouter.ai/api/v1"
HOSTED_MODEL    = "anthropic/claude-3.5-sonnet"   # or openai/gpt-4o, google/gemini-pro-1.5
HOSTED_API_KEY  = "sk-or-..."                      # key from openrouter.ai
```
This is how you get **actual Claude** driving Nanban — the exact "latest Claude agent" behaviour you want.

### OpenAI directly
```python
LLM_BACKEND   = "hosted"
HOSTED_BASE_URL = "https://api.openai.com/v1"
HOSTED_MODEL    = "gpt-4o"            # or gpt-4o-mini (cheaper)
HOSTED_API_KEY  = "sk-..."
```

Restart Nanban. The top bar and Admin tab now show `☁️ <model>` so you always know which brain is active. **Everything works the same** — all chat modes, the Security Tutor, the terminal agent, tool-calling — just smarter and faster.

---

## Which should you use?

- **Daily driver, private, free:** local with `qwen2.5:14b`.
- **Maximum intelligence / speed, or on a weak laptop:** hosted (Groq free, or OpenRouter→Claude).
- **Mix:** keep local as default, flip to hosted when you need heavy reasoning. It's one line in `config.py`.

## Privacy note
With the hosted engine, your prompts go to that provider under their terms. For sensitive work (or the security labs), prefer the local engine so nothing leaves your machine. The choice is always yours and always visible in the UI.
