# Nanban Cloud — deploy the chat demo

A public, chat-only Nanban that runs on free/cheap hosting and uses a **hosted model API** (no GPU, no local machine). The Terminal, Computer mode, SSH servers, Docker lab and VPN are **not** in this version — those are local-only features (run the full Nanban on your own machine for them, and expose it with Cloudflare Tunnel; see `../DEPLOY.md`).

## 1. Get a model API key (free option)

**Groq** has a fast free tier and is OpenAI-compatible:
1. Sign up at console.groq.com → **API Keys** → create one.
2. You'll use: `LLM_BASE_URL=https://api.groq.com/openai/v1`, `LLM_MODEL=llama-3.1-8b-instant`.

(Any OpenAI-compatible provider works — OpenAI, Together, OpenRouter — just change the three env vars.)

## 2a. Deploy on Hugging Face Spaces (easiest, free)

1. Create a **Space** at huggingface.co → SDK: **Gradio**.
2. Upload `app_cloud.py` (rename it to `app.py` in the Space) and a `requirements.txt` containing:
   ```
   gradio>=6,<7
   openai>=1.40
   ```
3. Space **Settings → Variables and secrets** → add secrets:
   `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, and optionally `APP_PASSWORD`.
4. The Space builds and goes live at `https://huggingface.co/spaces/<you>/<name>`.

> For the exact Nanban look, also upload `ui_theme.py` from the repo root; the app imports it automatically if present.

## 2b. Deploy on Render (free web service)

1. Push this repo to GitHub (see `../DEPLOY.md`).
2. Render.com → **New → Web Service** → connect the repo.
3. Environment: **Docker** (it uses `deploy/Dockerfile`), or **Python** with:
   - Build: `pip install -r deploy/requirements.txt`
   - Start: `python deploy/app_cloud.py`
4. Add env vars: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `APP_PASSWORD` (optional).
5. Deploy → live at `https://<name>.onrender.com`.

(Railway and Fly.io work the same way with the Dockerfile.)

## 3. Test locally first

```bash
pip install -r deploy/requirements.txt
LLM_BASE_URL=https://api.groq.com/openai/v1 LLM_API_KEY=your-key LLM_MODEL=llama-3.1-8b-instant \
  python deploy/app_cloud.py
# open http://localhost:7860
```

## Notes

- **Security:** set `APP_PASSWORD` so the public URL isn't open to the whole internet. Never commit your API key — use the host's secrets/env vars.
- **Cost:** the model runs on the provider; free tiers have rate limits. Watch usage if you add a paid key.
- **Why not Vercel/Netlify?** They run short serverless functions and can't host a persistent Gradio server. Use HF Spaces, Render, Railway, Fly.io, or a VPS.
