# 🧠 Choosing Nanban's brain — free (and optional paid)

Nanban's intelligence depends on **which model** it runs. The free options are front-and-center; paid frontier models (Claude/GPT) are optional. You pick it in the app: **Admin tab → 🧠 AI model & settings** (no file editing). Two kinds:

- **Local** — Ollama on your machine. Free, private, offline. Limited by your hardware.
- **Hosted free tiers** — free cloud APIs. Much smarter & faster than a local 8B, and still $0 (they have rate limits, not charges).

Honest note: a local 8B model is fine for everyday help but isn't frontier-level. For much smarter replies at no cost, use a free hosted tier below.

---

## 🏆 Nanban Best — one agent, many brains (recommended)

The top preset in the dropdown. Instead of one fixed model, **Nanban routes each question to the strongest model for that task**, then auto-fails-over if it's busy:

| Your question is about… | Nanban uses |
|---|---|
| coding, bugs, SQL | a coder model (e.g. Qwen Coder) |
| hard reasoning, maths, planning | a reasoning model (e.g. DeepSeek-R1, Nemotron) |
| images / diagrams | a vision model (e.g. Gemini, *-VL) |
| quick / short questions | the fastest model (e.g. gpt-oss-20b, *instant) |
| everything else | the biggest all-round model (e.g. Llama 405B) |

**One key unlocks it:** get a free **NVIDIA** key at build.nvidia.com — it exposes DeepSeek-R1, Llama 405B, Nemotron 120B, Qwen Coder and Llama 70B, so routing works across all of them with a single key. Pick **🏆 Nanban Best** → paste the key → Save. If a model is down/slow, Nanban switches to the next best automatically — you always get the best available answer.

---

## Option A — Local models (free, private)

In the Settings screen pick **Local**, set the model name. Or by hardware:

| Your RAM | Model | Notes |
|---|---|---|
| 8 GB | `llama3.2:3b` | fast, light |
| 16 GB | `llama3.1:8b` (default) | good all-rounder |
| 16 GB | `qwen2.5:7b` | strong, good multilingual |
| 16 GB | `qwen2.5-coder:7b` | best local for coding |
| 24 GB+ | `qwen2.5:14b` | noticeably smarter |

---

## Option B — Free hosted tiers (smarter + faster, still free) ⭐

In the Settings screen, pick one of these, paste its free API key, Save. All are free to use.

| Provider | Free? | Model | Get a free key |
|---|---|---|---|
| **Groq** ⭐ | Free tier | `openai/gpt-oss-20b` (or `openai/gpt-oss-120b`) | console.groq.com → API Keys |
| **Google Gemini** | Free tier | `gemini-2.0-flash` | aistudio.google.com → Get API key |
| **Cerebras** | Free tier | `llama-3.3-70b` | cloud.cerebras.ai → API Keys |
| **OpenRouter (free models)** | Free models | `meta-llama/llama-3.3-70b-instruct:free` | openrouter.ai → Keys |

All run a **70B-class model** — far smarter and faster than your local 8B — for free.

### NVIDIA (build.nvidia.com) — top models, free key ⭐

NVIDIA hosts many frontier models with an OpenAI-compatible API. Get a free `nvapi-…` key at **build.nvidia.com** (open any model card → **Get API Key**). In Nanban, pick a **🟩 NVIDIA** preset → paste the key → **Save & apply**. The base URL (`https://integrate.api.nvidia.com/v1`) and model id are filled automatically — you change nothing.

| Preset | Model id | Best for |
|---|---|---|
| 🟩 NVIDIA → Nemotron Super 120B | `nvidia/nemotron-3-super-120b-a12b` | NVIDIA's flagship, all-round |
| 🟩 NVIDIA → Llama 3.1 405B | `meta/llama-3.1-405b-instruct` | the largest / smartest |
| 🟩 NVIDIA → Llama 3.3 70B | `meta/llama-3.3-70b-instruct` | fast all-rounder |
| 🟩 NVIDIA → DeepSeek-R1 | `deepseek-ai/deepseek-r1` | step-by-step reasoning |
| 🟩 NVIDIA → Qwen2.5 Coder 32B | `qwen/qwen2.5-coder-32b-instruct` | coding |

Model ids on build.nvidia.com change over time. If one is ever retired, Nanban **auto-switches to a working model** on your key — or click **🔎 Show my available models** to pick one.

### Setup (2 minutes, e.g. Groq)
1. Go to **console.groq.com** → sign in → **API Keys** → Create.
2. In Nanban: **Admin → 🧠 AI model & settings** → pick **Groq** → paste the key → **Save & apply**.
3. The model badge shows e.g. `☁️ openai/gpt-oss-20b`. Done — no restart, no file editing.

---

## Option C — Paid frontier models (optional, top intelligence)

Not needed — the free options above are great — but if you want the absolute best (Claude / GPT), Nanban supports them too. Pick a 💳 preset in Settings and use a paid key:

| Provider | Model | Where |
|---|---|---|
| OpenRouter → Claude | `anthropic/claude-3.5-sonnet` | openrouter.ai |
| OpenRouter → GPT-4o | `openai/gpt-4o` | openrouter.ai |
| OpenAI | `gpt-4o-mini` / `gpt-4o` | platform.openai.com |

These cost money per use. The free options cost nothing — use paid only if you specifically want frontier quality.

## Which to use?

- **Private / offline / zero accounts** → Local (`llama3.1:8b` or `qwen2.5:7b`).
- **Much smarter + faster, still free** → Groq or Cerebras free tier (70B).
- **Multimodal / Google ecosystem** → Google Gemini free tier.

Everything in Nanban — all chat modes, the terminal agent, tool-calling, the Security Tutor, the API — works identically on any of these. Switch any time in Settings.

## Privacy

Local keeps everything on your machine. Hosted free tiers send your prompts to that provider (like any cloud AI) — free, but not private. For sensitive work use Local; for general smarts use a free hosted tier. Your choice, per task.

## A note on "free"

Free tiers can change their limits over time, and all have rate limits (a cap on requests per minute/day). They're genuinely free to use within those limits. Local is free forever with no limits — just bounded by your hardware. Nanban itself, and every feature in it, is and stays free.
