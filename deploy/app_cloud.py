"""
Nanban Cloud — a chat-only version that runs on public hosting (Hugging Face Spaces,
Render, Railway, Fly.io, or any VPS). It uses a HOSTED model API instead of local
Ollama, so it needs no GPU and no local machine.

What's included: the chat, the 6 assistant modes, memory, and the clean Nanban UI.
What's NOT here (on purpose — these are local/host features that can't be public):
the Terminal, Computer mode, SSH servers, the Docker lab, and VPN. For those, run
the full Nanban on your own machine (see the main README) and expose it with
Cloudflare Tunnel (see ../DEPLOY.md).

Model: any OpenAI-compatible API. Set these environment variables on your host:
    LLM_BASE_URL   e.g. https://api.groq.com/openai/v1   (Groq has a free tier)
                   or   https://api.openai.com/v1
    LLM_API_KEY    your key for that provider
    LLM_MODEL      e.g. llama-3.1-8b-instant (Groq) or gpt-4o-mini (OpenAI)
    APP_PASSWORD   (optional) a password to gate the public app (user: nanban)

Run locally to test:  LLM_BASE_URL=... LLM_API_KEY=... LLM_MODEL=... python app_cloud.py
"""

import os

import gradio as gr
from openai import OpenAI

AGENT_NAME = os.environ.get("AGENT_NAME", "Nanban")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
API_KEY = os.environ.get("LLM_API_KEY", "")
MODEL = os.environ.get("LLM_MODEL", "llama-3.1-8b-instant")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
PORT = int(os.environ.get("PORT", "7860"))

client = OpenAI(base_url=BASE_URL, api_key=API_KEY or "missing-key")

MODES = {
    "assistant": ("🤝 Personal Assistant", "Help with everyday tasks, planning and quick questions. Be concise and practical."),
    "coding": ("💻 Coding", "You are an expert programmer and patient teacher. Give complete, working, commented code and explain the key idea briefly."),
    "writing": ("✍️ Writing", "You are a skilled writer and editor. Match the tone and format requested; give the finished text directly."),
    "research": ("🔍 Research", "You are a careful researcher. Answer clearly, note uncertainty, and distinguish facts from opinion. (No live web access in the cloud demo.)"),
    "study": ("📚 Study", "You are a friendly tutor. Explain step by step with simple examples, and offer quizzes and summaries."),
    "business": ("📈 Business", "You are a practical business advisor for small businesses and startups, with good knowledge of the Indian market. Be concrete and honest about risks."),
}
DEFAULT_MODE = "assistant"

SYSTEM = ("You are {name}, a helpful AI assistant. Reply in the same language the user writes in "
          "(English, Tamil script, or Tanglish — Tamil in English letters). Be clear, warm and honest.\n\n{mode}")

# Reuse the main app's theme + CSS if present (same look); otherwise fall back to Soft.
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import ui_theme
    THEME, CSS = ui_theme.theme(), ui_theme.CSS
except Exception:
    THEME, CSS = gr.themes.Soft(), "footer {display:none !important}"

EXAMPLES = {
    "assistant": ["1850 rupees-la 18% GST evlo?", "Naalaiku panna 5 tasks plan pannu"],
    "coding": ["Python-la fibonacci function ezhudhi explain pannu", "What's the difference between a list and a tuple?"],
    "writing": ["Leave letter ezhudhu - 2 days fever, formal-a", "Write a LinkedIn post announcing my new app"],
    "research": ["Explain how solar panels work", "Compare electric vs petrol cars for a city commute"],
    "study": ["Explain photosynthesis simply", "Make a 5-question quiz on the water cycle"],
    "business": ["Cloud kitchen start panna evlo selavu?", "5 low-budget marketing ideas for a small resort"],
}


def respond(message, history, mode):
    message = (message or "").strip()
    if not message:
        yield history
        return
    if not API_KEY:
        history = history + [{"role": "user", "content": message},
                             {"role": "assistant", "content": "⚠️ No model API key set. The host needs LLM_API_KEY (and LLM_BASE_URL, LLM_MODEL) configured."}]
        yield history
        return

    system = SYSTEM.format(name=AGENT_NAME, mode=MODES[mode][1])
    msgs = [{"role": "system", "content": system}]
    for m in history[-20:]:
        msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": message})

    history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": ""}]
    yield history
    try:
        stream = client.chat.completions.create(model=MODEL, messages=msgs, stream=True, temperature=0.6)
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                history[-1]["content"] += delta
                yield history
    except Exception as e:
        history[-1]["content"] = f"⚠️ Model error: {e}"
        yield history


def change_mode(mode):
    return MODES[mode][1] if False else gr.Dataset(samples=[[e] for e in EXAMPLES[mode]])


with gr.Blocks(title=AGENT_NAME, fill_height=True) as demo:
    gr.HTML(f"<div id='topbar'><div class='title' style='display:block'>{AGENT_NAME}</div>"
            f"<div class='badges'><span class='badge'>☁️ Cloud · {MODEL}</span></div></div>")
    mode = gr.Radio(choices=[(label, key) for key, (label, _) in MODES.items()],
                    value=DEFAULT_MODE, show_label=False, container=False, elem_id="modes")
    chatbot = gr.Chatbot(elem_id="chat", show_label=False, height="calc(100dvh - 300px)",
                         min_height=300, placeholder=f"### Vanakkam 👋\nNaan {AGENT_NAME}. Tamil, English, Tanglish — kelunga.")
    with gr.Column(elem_id="composer"):
        msg = gr.Textbox(placeholder="Message…", show_label=False, container=False, submit_btn=True, autofocus=True)
        ex = gr.Examples(examples=[[e] for e in EXAMPLES[DEFAULT_MODE]], inputs=msg, label="", elem_id="examples")

    msg.submit(respond, [msg, chatbot, mode], chatbot).then(lambda: "", None, msg)
    mode.change(change_mode, mode, ex.dataset)


if __name__ == "__main__":
    auth = ("nanban", APP_PASSWORD) if APP_PASSWORD else None
    demo.queue().launch(server_name="0.0.0.0", server_port=PORT, auth=auth, theme=THEME, css=CSS, footer_links=[], pwa=True)
