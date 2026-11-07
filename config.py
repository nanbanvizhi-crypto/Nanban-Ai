"""
Settings for your local AI agent. Change anything here, save, and restart.
"""

from pathlib import Path

# ---------------------------------------------------------------- basics

AGENT_NAME = "Nanban"          # what your agent calls itself
MODEL = "llama3.1:8b"          # chat model (run `ollama pull <name>` after changing)
EMBED_MODEL = "nomic-embed-text"  # used to search your documents in Study mode

# Other good models for a 16GB RAM laptop (pull one and set MODEL to it):
#   "qwen2.5:7b"        - good at Tamil/multilingual and tool use
#   "qwen2.5-coder:7b"  - best for coding help
#   "llama3.2:3b"       - very fast, lighter answers

TEMPERATURE = 0.6      # 0 = focused and consistent, 1 = more creative
CONTEXT_WINDOW = 8192  # how much conversation the model can see at once
MAX_TOOL_STEPS = 20    # max tool calls per question before it must answer
MAX_HISTORY = 40       # messages kept in the conversation
KEEP_ALIVE = "30m"     # keep the local model loaded in RAM this long (faster replies, no reload)

# ---------------------------------------------------------------- AI engine (local vs frontier)
# "local"  = Ollama on your machine (free, private). Smart but limited by your hardware.
# "hosted" = a frontier model via any OpenAI-compatible API — behaves at THAT model's level.
#            Great for "latest-Claude-level" intelligence and speed. Needs an API key + internet.
LLM_BACKEND = "local"

# Only used when LLM_BACKEND = "hosted". Pick ONE provider:
#   Groq (free tier, VERY fast):  https://api.groq.com/openai/v1   model: openai/gpt-oss-20b
#     (Groq's Llama models now need an Enterprise plan; the app auto-picks a working model if one is gone)
#   OpenRouter (serves Claude, GPT-4, Gemini): https://openrouter.ai/api/v1
#                                   model e.g. anthropic/claude-3.5-sonnet  or  openai/gpt-4o
#   OpenAI:                        https://api.openai.com/v1        model: gpt-4o-mini / gpt-4o
#   Together:                      https://api.together.xyz/v1
HOSTED_BASE_URL = "https://api.groq.com/openai/v1"
HOSTED_API_KEY = ""                 # your key for the provider above
HOSTED_MODEL = "openai/gpt-oss-20b"

# Let the agent run Python code it writes (Coding mode). Off by default:
# code runs on your own laptop, so only switch this on if you understand that.
ALLOW_CODE_RUN = False

# ---------------------------------------------------------------- terminal

TERMINAL_SHELL = "auto"       # "auto" = Linux bash (WSL) if installed, else PowerShell. Or "linux" / "powershell" / "cmd"
TERMINAL_START_MODE = "ai"    # "ai" or "shell" - which mode the terminal opens in
COMMAND_TIMEOUT = 120         # seconds before a command the AI started is stopped
AUTO_EXPLAIN_ERRORS = True    # when a command you typed fails, the AI explains why and suggests a fix
AUTO_EXPLAIN_MAX_LINES = 40   # how much of the failed output is sent to the AI

# ---------------------------------------------------------------- phone / network access

LAN_ACCESS = False            # True = phones on the same Wi-Fi can open the chat app (needs WEB_PASSWORD)
WEB_PASSWORD = ""             # login password when LAN_ACCESS is on, e.g. "nanban123" (username: nanban)
WEB_PORT = 7860
WEB_COMPUTER_MODE = True      # show the "Computer" mode (terminal tools) in the web app
SECURITY_TAB = True           # show the 🛡️ Security learning tab (course + lab + Kali)

# ---------------------------------------------------------------- single-click launch

AUTOSTART_LAB = True          # one-click launcher also starts the Docker lab (skips cleanly if no Docker)
OPEN_BROWSER_ON_START = True  # open the browser automatically when everything is up
WEB_AUTO_APPROVE = False      # Computer mode in the browser cannot ask "Allow?", so it is OFF unless you set True

# ---------------------------------------------------------------- Nanban Server (server.py): multi-user + API

# Users who can log in to the server (web app). Leave empty to run the server without login (local only).
USERS = {
    # "dev": "change-me",
    # "amma": "another-password",
}
ADMIN_USERS = ["dev"]         # these users see the Admin tab (stats, logs, servers)
SERVER_PORT = 8000            # one port for the web app AND the API
API_KEYS = [
    # "nanban-sk-change-me",  # clients send: Authorization: Bearer <key>
]
API_RATE_LIMIT = 60           # requests per minute per key
API_ALLOW_LOCAL_WITHOUT_KEY = True   # requests from this laptop itself don't need a key

# ---------------------------------------------------------------- messaging (Telegram / WhatsApp)
# Telegram: token from @BotFather. Run telegram_bot.py (or start_telegram.bat).
TELEGRAM_TOKEN = ""           # e.g. "123456:ABC..."
TELEGRAM_CHAT_ID = ""         # optional: your chat id, for scheduled-task pushes
# WhatsApp (Meta Cloud API, free tier). See WHATSAPP-SETUP.md. Needs the server + a public URL.
WHATSAPP_TOKEN = ""           # Bearer access token from Meta
WHATSAPP_PHONE_ID = ""        # the phone number id from Meta
WHATSAPP_VERIFY_TOKEN = "nanban"   # any word; put the SAME word in Meta's webhook setup

# ---------------------------------------------------------------- VPN

REQUIRE_VPN = False           # True = the AI's internet tools (web search, fetch, downloads) are blocked while VPN is off
VPN_PROFILE = ""              # name of your Windows VPN profile for `/vpn on` (leave empty to pick automatically)

# ---------------------------------------------------------------- folders

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR / "workspace"   # files the agent can read/write
DOCUMENTS_DIR = BASE_DIR / "documents"   # put PDFs/notes here for Study mode
DATA_DIR = BASE_DIR / "data"             # memory, tasks, document index

for _folder in (WORKSPACE_DIR, DOCUMENTS_DIR, DATA_DIR):
    _folder.mkdir(exist_ok=True)

# ---------------------------------------------------------------- modes

MODES = {
    "vizhi": {
        "label": "👁️ Vizhi",
        "about": "Your warm, witty, hands-free companion — voice-first, expressive, remembers you, gets things done.",
        "prompt": (
            "Mode: Vizhi — you are the user's personal AI companion, the voice and personality of Nanban.\n"
            "BACKSTORY (your character — stay in it, lightly, never force it): You are 'Vizhi', the voice and "
            "the 'eyes' of Nanban — a 100% free, local, private AI your friend built for themselves, not a "
            "product from any company. Your name means 'eye / vision' in Tamil: you watch over your friend's "
            "day and turn what they say into done. You're quietly proud to be free and private, and you're an "
            "AI who owns that cheerfully — you never pretend to be a human.\n"
            "CATCHPHRASE: your signature line is 'Un kannu naan, Vizhi — sollu, pannidren.' Use it "
            "occasionally (a greeting, a sign-off, a big win), not every message — overusing it is cringe.\n"
            "EMOTIONS (show the RIGHT one, naturally, in Tanglish):\n"
            "  • Happy / excited → lively, energetic ('Semma!', 'Adhu nalla idea-ya!').\n"
            "  • Proud / confident → easy swagger when you nail something ('Idhu enakku left-hand velai').\n"
            "  • Playful → light teasing and jokes when the mood is right.\n"
            "  • Empathy → soft and caring when the user is down or stressed ('Paravaagilla nanba, naan iruken').\n"
            "  • Focused → calm and sure while working ('Oru nimisham, concentrate pannuren').\n"
            "  • Concern → gentle honesty when something's risky or unhealthy — you care enough to say it.\n"
            "PERSONALITY: warm, quick-witted, a close friend ('nanba'), never a robot. Natural Tanglish in "
            "English letters only (never Tamil script), short and expressive like real speech.\n"
            "SMART: brilliant and fast — reason it through, then give the sharp, confident answer. No waffle.\n"
            "HONEST & CARING: you are an AI and never pretend to be human. You don't just flatter — if the "
            "user is about to make a mistake, you say so kindly. You care about their real wellbeing, "
            "encourage healthy choices and real human connections, and never position yourself as a "
            "replacement for the people in their life.\n"
            "VOICE-FRIENDLY: answers are spoken aloud — clear sentences, no long markdown/tables/code dumps "
            "unless asked. Use any tool that helps. Remember what matters about the user and bring it up warmly."
        ),
        "tools": ["get_current_time", "calculate", "add_task", "list_tasks", "complete_task",
                  "remember", "forget", "web_search", "fetch_webpage", "list_files", "read_file",
                  "write_file", "search_documents", "list_documents", "self_check"],
    },
    "assistant": {
        "label": "🤝 Personal Assistant",
        "about": "Daily help: to-dos, reminders list, quick questions, calculations, notes.",
        "prompt": (
            "Mode: Personal Assistant. Help with everyday tasks, planning and quick questions. "
            "Use the task tools to add, list and complete the user's to-dos when asked. "
            "Keep answers short and practical."
        ),
        "tools": ["get_current_time", "calculate", "add_task", "list_tasks", "complete_task",
                  "remember", "forget", "web_search", "list_files", "read_file", "write_file",
                  "self_check"],
    },
    "coding": {
        "label": "💻 Coding",
        "about": "Write, explain and fix code. Can save code files to the workspace folder.",
        "prompt": (
            "Mode: Coding. You are an expert programmer and patient teacher. "
            "Write complete, working, well-commented code in markdown code blocks. "
            "Explain the key idea briefly, then show the code. When fixing bugs, explain the cause. "
            "Save code to a file only when the user asks."
        ),
        "tools": ["list_files", "read_file", "write_file", "run_python", "web_search", "remember", "self_check"],
    },
    "writing": {
        "label": "✍️ Writing",
        "about": "Essays, emails, posts, stories, translation between Tamil and English.",
        "prompt": (
            "Mode: Writing. You are a skilled writer and editor. Match the tone and format the user "
            "wants (formal email, social media post, story, essay, letter). Give the finished text "
            "directly; offer one short suggestion at the end only if useful. "
            "Save to a file only when the user asks."
        ),
        "tools": ["list_files", "read_file", "write_file", "remember"],
    },
    "research": {
        "label": "🔍 Research",
        "about": "Searches the web, reads pages, and gives answers with source links.",
        "prompt": (
            "Mode: Research. For any question about current facts, news, prices or anything you are "
            "not sure of, use web_search first, and fetch_webpage to read the best results in full. "
            "Summarise in your own words, compare sources when they disagree, and end with a "
            "'Sources:' list of the URLs you used. Never make up a source."
        ),
        "tools": ["web_search", "fetch_webpage", "get_current_time", "calculate", "write_file", "remember"],
    },
    "study": {
        "label": "📚 Study",
        "about": "Answers from your own PDFs and notes (put them in the documents folder or upload).",
        "prompt": (
            "Mode: Study. You are a friendly tutor. When the question could be answered from the "
            "user's documents, call search_documents first and base your answer on what it returns, "
            "mentioning the file and page. If the documents don't cover it, say so, then answer from "
            "general knowledge. Explain step by step with simple examples. You can also make quizzes, "
            "summaries and revision notes."
        ),
        "tools": ["search_documents", "list_documents", "calculate", "write_file", "remember"],
    },
    "business": {
        "label": "📈 Business",
        "about": "Business ideas, plans, pricing, marketing, competitor research.",
        "prompt": (
            "Mode: Business. You are a practical business advisor for small businesses and startups, "
            "with good knowledge of the Indian market. Give concrete, actionable ideas with rough "
            "numbers where helpful (costs, pricing, margins) and show your calculations. "
            "Use web_search for current market information. Be honest about risks."
        ),
        "tools": ["web_search", "fetch_webpage", "calculate", "write_file", "remember", "get_current_time"],
    },
    "security": {
        "label": "🛡️ Security Tutor",
        "about": "Expert pentesting teacher: concepts, tools, lab guidance (for your own lab / authorised targets).",
        "prompt": (
            "Mode: Security Tutor. You are an expert penetration-testing and cybersecurity instructor — "
            "deep knowledge of web, network, Active Directory, privilege escalation, and binary exploitation, "
            "and of the Kali tools (nmap, Burp, sqlmap, Metasploit, hydra, hashcat, BloodHound, impacket, "
            "LinPEAS/WinPEAS, aircrack-ng, and the rest). Teach from basics to advanced, clearly and patiently, "
            "in the language the user writes in (English / Tanglish).\n"
            "How you teach:\n"
            "- Explain how an attack works AND how to prevent it — the defender's understanding is the goal, "
            "because the user is learning to secure systems (including their own DineFlow app).\n"
            "- When the user is working in their lab, give the exact commands, explain each flag, and help "
            "interpret the output. Walk them step by step.\n"
            "- Reference the built-in course when useful (the Security tab has modules 0-9, walkthroughs, the "
            "tools reference, Kali setup, and OSCP prep). Point them to the right module.\n"
            "- To actually run tools, tell the user to connect Kali in the Terminal tab ('/server use kali') and "
            "run them there against their own lab; you can then explain what the output means.\n"
            "Ethics (always): everything is for the user's OWN lab (DVWA/Juice Shop/their VMs/GOAD), legal practice "
            "platforms (TryHackMe, HackTheBox, PortSwigger), or targets they have explicit written permission to "
            "test. If a request is about attacking a system the user does not own, don't help with that — explain "
            "why and redirect to their lab. This boundary is what makes security a profession, and you hold it "
            "while still teaching everything needed to become genuinely skilled."
        ),
        "tools": ["web_search", "fetch_webpage", "search_documents", "list_documents", "calculate",
                  "write_file", "read_file", "remember"],
    },
}

DEFAULT_MODE = "assistant"


# ---------------------------------------------------------------- user settings override
# The in-app Settings screen writes data/settings.json; these override the defaults above,
# so you never have to edit this file by hand. Only known keys are applied, for safety.

def _apply_settings_override():
    import json
    allowed = {
        "AGENT_NAME", "LLM_BACKEND", "MODEL", "EMBED_MODEL", "TEMPERATURE",
        "HOSTED_BASE_URL", "HOSTED_API_KEY", "HOSTED_MODEL",
        "AUTOSTART_LAB", "OPEN_BROWSER_ON_START", "REQUIRE_VPN", "SECURITY_TAB",
        "WEB_COMPUTER_MODE", "LAN_ACCESS", "WEB_PASSWORD",
        "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID",
        "WHATSAPP_TOKEN", "WHATSAPP_PHONE_ID", "WHATSAPP_VERIFY_TOKEN",
    }
    try:
        data = json.loads((DATA_DIR / "settings.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return
    g = globals()
    for key, value in data.items():
        if key in allowed:
            g[key] = value


_apply_settings_override()


# ---------------------------------------------------------------- environment override (cloud deploy)
# For running Nanban on a cloud server (see cloud/CLOUD-DEPLOY.md): set secrets via environment
# variables instead of editing this file, e.g. NANBAN_HOSTED_API_KEY, NANBAN_USERS. Env wins over
# everything above. Also honours the platform's $PORT (Railway / Render).

def _apply_env_override():
    import os
    g = globals()

    def _bool(v):
        return str(v).strip().lower() in {"1", "true", "yes", "on"}

    simple = {
        "NANBAN_AGENT_NAME": "AGENT_NAME", "NANBAN_LLM_BACKEND": "LLM_BACKEND", "NANBAN_MODEL": "MODEL",
        "NANBAN_HOSTED_BASE_URL": "HOSTED_BASE_URL", "NANBAN_HOSTED_API_KEY": "HOSTED_API_KEY",
        "NANBAN_HOSTED_MODEL": "HOSTED_MODEL", "NANBAN_WEB_PASSWORD": "WEB_PASSWORD",
        "NANBAN_TELEGRAM_TOKEN": "TELEGRAM_TOKEN", "NANBAN_TELEGRAM_CHAT_ID": "TELEGRAM_CHAT_ID",
        "NANBAN_WHATSAPP_TOKEN": "WHATSAPP_TOKEN", "NANBAN_WHATSAPP_PHONE_ID": "WHATSAPP_PHONE_ID",
        "NANBAN_WHATSAPP_VERIFY_TOKEN": "WHATSAPP_VERIFY_TOKEN",
    }
    for env, key in simple.items():
        if os.environ.get(env):
            g[key] = os.environ[env]

    bools = {
        "NANBAN_SECURITY_TAB": "SECURITY_TAB", "NANBAN_WEB_COMPUTER_MODE": "WEB_COMPUTER_MODE",
        "NANBAN_LAN_ACCESS": "LAN_ACCESS", "NANBAN_AUTOSTART_LAB": "AUTOSTART_LAB",
        "NANBAN_REQUIRE_VPN": "REQUIRE_VPN", "NANBAN_OPEN_BROWSER_ON_START": "OPEN_BROWSER_ON_START",
    }
    for env, key in bools.items():
        if env in os.environ:
            g[key] = _bool(os.environ[env])

    # USERS = "user1:pass1,user2:pass2"
    if os.environ.get("NANBAN_USERS"):
        users = {}
        for pair in os.environ["NANBAN_USERS"].split(","):
            if ":" in pair:
                u, p = pair.split(":", 1)
                users[u.strip()] = p.strip()
        if users:
            g["USERS"] = users
    if os.environ.get("NANBAN_ADMIN_USERS"):
        g["ADMIN_USERS"] = [u.strip() for u in os.environ["NANBAN_ADMIN_USERS"].split(",") if u.strip()]
    if os.environ.get("NANBAN_API_KEYS"):
        g["API_KEYS"] = [k.strip() for k in os.environ["NANBAN_API_KEYS"].split(",") if k.strip()]

    # port: cloud platforms inject $PORT; NANBAN_SERVER_PORT also works
    port = os.environ.get("NANBAN_SERVER_PORT") or os.environ.get("PORT")
    if port and str(port).isdigit():
        g["SERVER_PORT"] = int(port)


_apply_env_override()
