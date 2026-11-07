# 📲 Nanban on WhatsApp (official Meta Cloud API — free tier)

Chat with Nanban from WhatsApp. This uses WhatsApp's **official** Cloud API (free for a generous
number of conversations), so it's safe — no risk of your number being banned.

**You need:** the Nanban **Server** running, and its webhook reachable on a **public https URL**.
Easiest URL: **Admin → 🌍 Remote access → Start** (gives a `https://….trycloudflare.com` link), or
deploy to the cloud (`cloud/CLOUD-DEPLOY.md`).

---

## Step 1 — Create a Meta app (free, ~10 min)

1. Go to **developers.facebook.com** → log in → **My Apps** → **Create App** → type **Business**.
2. In the app, add the **WhatsApp** product.
3. Open **WhatsApp → API Setup**. You'll see:
   - a **temporary access token** (copy it — call it `WHATSAPP_TOKEN`),
   - a **Phone number ID** (copy it — `WHATSAPP_PHONE_ID`),
   - a free **test number** to send from.
4. Under **"Send and receive messages"**, add **your own** phone number as a recipient and verify it
   (so Meta lets the test number message you).

## Step 2 — Put the values in Nanban

In `config.py` (or as env vars on the cloud):
```python
WHATSAPP_TOKEN        = "EAAG...your-token..."
WHATSAPP_PHONE_ID     = "123456789012345"
WHATSAPP_VERIFY_TOKEN = "nanban-secret-word"   # any word you choose
USERS = {"dev": "a-password"}                  # the server needs a login
```
Start the server: **`start_server.bat`** (or your cloud deploy).

## Step 3 — Get a public URL for the webhook

- **Admin → 🌍 Remote access → Start** → copy the `https://….trycloudflare.com` link, **or**
- use your cloud deploy URL.

Your webhook URL is that link **+ `/whatsapp/webhook`**, e.g.
`https://abc123.trycloudflare.com/whatsapp/webhook`

## Step 4 — Connect the webhook in Meta

1. In the Meta app: **WhatsApp → Configuration → Webhook → Edit**.
2. **Callback URL:** your webhook URL from Step 3.
3. **Verify token:** the same word you set as `WHATSAPP_VERIFY_TOKEN`.
4. Click **Verify and save** (Nanban answers the handshake automatically).
5. Under **Webhook fields**, subscribe to **messages**.

## Step 5 — Chat

Message the **test number** from your WhatsApp. Nanban replies. Each sender gets their own memory.

---

## Notes
- **Free tier:** Meta gives a large number of free conversations per month; beyond that it's paid.
  For personal use you'll likely stay free.
- The **temporary token** from Step 1 expires in ~24h. For always-on use, create a **System User**
  with a **permanent token** (Meta Business Settings → Users → System Users → generate token with
  `whatsapp_business_messaging` permission) and use that as `WHATSAPP_TOKEN`.
- The laptop/server and the public URL must stay up for WhatsApp to reach Nanban. The trycloudflare
  link changes each time you restart it — update the Meta webhook URL if you restart. For a stable
  URL, use the cloud deploy.
- **Prefer zero setup?** **Telegram** (see `telegram_bot.py`) is instant and 100% free — just a
  token from @BotFather, no webhooks. WhatsApp's official API simply needs more steps.
