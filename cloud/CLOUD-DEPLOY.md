# ☁️ Run Nanban in the cloud — phone works even when your laptop is OFF

This hosts Nanban on an always-on server, so your phone reaches it from **anywhere**, any time —
no laptop needed. The AI "brain" is a **free hosted model** (Groq or NVIDIA), so the server needs
**no GPU** and stays **cheap**.

- **Cost:** free model key + a small server (**free tier to ~₹400–1,000 / ~$5–12 a month**).
- **Privacy note:** your prompts go to the model provider (Groq/NVIDIA), not your own machine.
  For private work, keep using the laptop setup. This is the trade-off for laptop-off access.

---

## Step 1 — Get a free model key (2 minutes)

Pick one:
- **Groq** — https://console.groq.com → sign in → **API Keys** → Create. Key looks like `gsk_…`.
- **NVIDIA** — https://build.nvidia.com → open any model → **Get API Key**. Key looks like `nvapi-…`.

Keep the key handy for Step 2.

---

## Step 2 — Deploy. Pick ONE host.

All three run the **same** app from the `cloud/` folder. Railway is the easiest.

### Option A — Railway (easiest, git-based) ⭐

1. Put this project on **GitHub** (see the main `DEPLOY.md` for the git steps).
2. Go to **railway.app** → **New Project** → **Deploy from GitHub repo** → pick your repo.
3. Railway detects the Dockerfile. In the service **Settings → Build**, set
   **Dockerfile Path** = `cloud/Dockerfile`.
4. Open **Variables** and add (from `cloud/.env.example`):
   ```
   NANBAN_LLM_BACKEND   = hosted
   NANBAN_HOSTED_BASE_URL = https://api.groq.com/openai/v1
   NANBAN_HOSTED_MODEL  = openai/gpt-oss-20b
   NANBAN_HOSTED_API_KEY = gsk_your_key
   NANBAN_USERS         = dev:your-strong-password
   NANBAN_ADMIN_USERS   = dev
   NANBAN_WEB_COMPUTER_MODE = false
   NANBAN_SECURITY_TAB  = false
   ```
   (Railway injects `PORT` automatically — Nanban reads it.)
5. **Settings → Networking → Generate Domain.** You get a public URL like
   `https://nanban-production.up.railway.app`.

### Option B — Render (Blueprint)

1. Project on GitHub (includes `cloud/render.yaml`).
2. **render.com → New + → Blueprint →** connect the repo. It reads `render.yaml`.
3. In the dashboard set the two secrets: `NANBAN_HOSTED_API_KEY` and `NANBAN_USERS`.
4. Deploy. Render gives a public `https://nanban.onrender.com` URL.

### Option C — Your own VPS with Docker (Hetzner / DigitalOcean / Contabo)

1. Create the cheapest **CPU** server (1–2 GB RAM is plenty — no GPU). Ubuntu is fine.
2. Install Docker: `curl -fsSL https://get.docker.com | sh`
3. Copy this project to the server (git clone, or scp).
4. ```bash
   cd local-ai-agent/cloud
   cp .env.example .env
   nano .env            # paste your key + set a strong password
   docker compose up -d --build
   ```
5. Open `http://<server-ip>:8000`. For a real domain + HTTPS, put **Caddy** or **Nginx** in
   front (Caddy does automatic HTTPS in ~3 lines — ask and I'll give you the config).

---

## Step 3 — Use it on your phone (from anywhere)

1. Open the public URL in your phone browser.
2. Log in: the user + password you set in `NANBAN_USERS`.
3. **Add to Home Screen** (iPhone Safari: Share → Add to Home Screen) → opens full-screen like an app.

That's it — the laptop can be off. The server is always on.

---

## Good to know

- **Your data** (memory, to-dos, uploaded documents) lives in the server's `data/` and
  `documents/` volumes and persists across restarts and redeploys.
- **Change the model anytime** without redeploying: **Admin → 🧠 AI model & settings** in the app,
  or edit the env vars. The 🔎 *Show my available models* button lists what your key can use, and
  if a model id is ever retired Nanban auto-switches to a working one.
- **Security:** the login (`NANBAN_USERS`) is what keeps your public app private — use a strong
  password. The terminal/Computer/Security tabs are **off by default** on the cloud image so a
  public server can't be used to run commands. Only turn them on if you understand the risk.
- **The API** (`/v1`, OpenAI-compatible) is available too — give out `NANBAN_API_KEYS` to use it
  from your own code, e.g. your DineFlow app.
- **Cost control:** stick to free model tiers (Groq/NVIDIA) and a free/cheap server plan. Render's
  free web service sleeps when idle (wakes on the next request); a ~$5 plan or a cheap VPS stays on.

Want automatic HTTPS + your own domain, or a one-command deploy script for a specific host? Say
which host and I'll add it.
