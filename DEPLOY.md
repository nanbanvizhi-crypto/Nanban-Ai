# 🚀 Taking Nanban live — the honest guide

Nanban was built to run on **your own machine** (local AI model, a terminal, SSH, Docker, VPN). That shapes what "live" can mean. Here's every real option, clearly.

## ⛔ What does NOT work: Vercel / Netlify / GitHub Pages

These host **static sites** or **short serverless functions** (10–60 sec, no persistent process, no GPU). Nanban needs a long-running server and a model. So the full app **cannot** run there — it's architectural, not a config you can tweak. (GitHub Pages is for static HTML only; Vercel/Netlify functions time out and reset.)

## ✅ The three options that DO work

| You want… | Use | Model runs on | Features | Cost |
|---|---|---|---|---|
| **My own Nanban, reachable anywhere** | Cloudflare Tunnel (laptop stays on) | your machine (local) | **everything** | free |
| **The code shared / backed up** | GitHub | — | — | free |
| **A public demo others can use** | HF Spaces / Render + model API | a cloud API | **chat only** | free tier |

---

## Option 1 — Public URL for YOUR Nanban (Cloudflare Tunnel) ⭐ best fit

Your laptop (or a mini-PC/always-on machine) runs the full Nanban; a free tunnel gives it a public `https://…` link. Model stays **local and free**, and **all** features work (terminal, lab, servers).

1. Start Nanban normally (double-click **Nanban** / `start_nanban.bat`). For multi-device use, set `USERS` + a password in `config.py` first.
2. Install **cloudflared**: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
3. Double-click **`tunnel.bat`**. It prints a public URL like `https://random-words.trycloudflare.com` — open that from your phone or share it.
4. Keep both windows open. The URL lasts while the tunnel runs. (For a permanent custom domain, set up a named Cloudflare Tunnel — their docs have the steps.)

**Alternative: Tailscale** (private, not public). Install on your laptop + phone with one account; reach Nanban at the laptop's Tailscale IP. Best when it's just for you and your own devices.

---

## Option 2 — Put the code on GitHub

Good for backup, version history, portfolio, and deploying to Render.

```bash
# in the local-ai-agent folder
git init
git add -A
git commit -m "Nanban — local AI agent"

# create an EMPTY repo on github.com first (no README), then:
git branch -M main
git remote add origin https://github.com/<your-username>/nanban.git
git push -u origin main
```

Already set up for you:
- **`.gitignore`** — excludes `.venv/`, `data/`, your documents, and any `.env`/keys. Your private data and secrets are never committed.
- **`LICENSE`** — MIT (change if you like).

> Double-check before the first push: never commit `config.py` if you've put real passwords/API keys in it. Either keep secrets out of it, or add `config.py` to `.gitignore` and ship `config.example.py` instead.

---

## Option 3 — A public cloud demo others can use

A **chat-only** Nanban on free hosting, using a hosted model API (no GPU, no your-machine). The terminal/lab/servers/VPN are intentionally left out — you can't safely hand strangers a shell on a public box.

Everything for this is in the **`deploy/`** folder:
- `deploy/app_cloud.py` — the chat-only app (6 modes, same Nanban look)
- `deploy/Dockerfile`, `deploy/requirements.txt`, `deploy/.env.example`
- **`deploy/README.md`** — step-by-step for **Hugging Face Spaces** (easiest) and **Render** (Docker)

Quick version: get a free **Groq** API key → create a Hugging Face **Gradio Space** → upload `app_cloud.py` (as `app.py`) + a requirements file → add `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` as secrets → it's live.

---

## Which should you pick?

- **Just you, all features, free:** Option 1 (Cloudflare Tunnel) or Tailscale.
- **Share the project / back it up:** Option 2 (GitHub).
- **Let the public try a chat demo:** Option 3 (HF Spaces).

You can do all three — they don't conflict. The full powerful Nanban always lives on your machine; the cloud demo is a lightweight shop window.
