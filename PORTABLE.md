# 📦 Nanban Portable — zero install, zero dependencies

Nanban Portable is the same app as regular Nanban, but **nothing is installed on your computer**. Everything lives in this one folder. Double-click, and it just runs.

## What's inside (first run fills these automatically)

```
Nanban/
├── Nanban-Portable.bat      ← double-click this to start
├── runtime/                 ← embedded Python (downloads on first run, ~50 MB)
├── models/                  ← AI model (downloads on first run, ~1 GB)
├── bin/busybox.exe          ← Linux commands for Windows (~1 MB)
├── data/                    ← your memory, settings, to-dos (stays here)
├── documents/               ← your PDFs and notes for Study mode
└── everything else          ← Nanban's code
```

## What you do NOT need

| Dependency | Why Nanban doesn't need it |
|---|---|
| **Python install** | Bundled. Embedded Python 3.13 sits in `runtime/`. |
| **Ollama** | Replaced by `llama-cpp-python` (bundled). A small Qwen 2.5 model runs directly. |
| **WSL / Kali Linux** | `busybox.exe` (bundled, ~1 MB) gives Linux commands: `ls`, `grep`, `cat`, `sed`, `awk`, `curl`, `tar`, and 300+ more. |
| **Docker** | The practice lab is replaced by links to free public targets (TryHackMe, PortSwigger). No container runtime needed. |
| **Any admin rights** | Everything installs inside this folder, not system-wide. |
| **Internet after setup** | Only needed on first run for the model download. Once set up, works offline. |

## First run

1. **Internet needed for setup** (downloads Python runtime + AI model, ~1.1 GB total).
2. Double-click **`Nanban-Portable.bat`**.
3. Wait a few minutes while it unpacks everything. Progress shows in the black window.
4. Your browser opens automatically. Done.

## Every run after

1. Double-click **`Nanban-Portable.bat`**.
2. Browser opens. No checks, no waits.

## Moving it to another computer / USB stick

Just copy the whole folder. Everything travels with it — runtime, model, your memory, your to-dos. On the new machine, double-click `Nanban-Portable.bat` and it runs. No install, no setup. (If you move between Windows, Mac and Linux, re-download each OS's runtime — Python embedded is Windows-only.)

## Want a smarter AI?

The bundled Qwen 2.5 1.5B is fast and multilingual but small. For much smarter replies:

- **Free cloud upgrade:** Admin tab → 🧠 AI model & settings → pick **Groq / Cerebras / Gemini** → paste the free API key. 70B-class models, no cost, works everywhere.
- **Bigger local model:** drop any `.gguf` file into `models/` (e.g. `qwen2.5-7b-instruct-q4_k_m.gguf` from Hugging Face). Nanban picks it up automatically.

## Delete it

Delete the folder. Nothing left on your computer — no registry entries, no system files. That's the whole point of portable.
