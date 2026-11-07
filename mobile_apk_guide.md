# 📱 Install Nanban on Android (two paths)

**The honest reality first:** a real native Android app that runs a 1–2 GB AI model locally **cannot be made** — phone CPUs/RAM aren't built for it, even the fanciest flagship. Every "AI app" you see on Android is either calling a cloud model, or using a tiny (<100 MB) model with far weaker answers. So the realistic Nanban-on-Android story is:

> **Nanban runs on your laptop.** Your phone opens it over Wi-Fi (same network) or over the internet (via Cloudflare Tunnel / Tailscale). You get the whole app on your phone — chat, terminal, security, admin — talking to the full-power Nanban on the laptop.

Two ways to make that feel like a native app on your phone:

---

## Path A — PWA install (30 seconds, zero build) ⭐ recommended

Nanban is already a **Progressive Web App**. Modern Android treats PWAs exactly like native apps: home-screen icon, full-screen launch, push notifications possible.

1. On the **laptop**: start Nanban (`start_nanban.bat`). In the Admin tab, turn on **Phone access** (`LAN_ACCESS=true`), set a password.
2. On your **phone**: connect to the same Wi-Fi.
3. Open **Chrome** on the phone → type the laptop's address shown in the Admin tab (e.g. `http://192.168.1.4:7860`).
4. Log in → open the ⋮ menu → **"Install app"** (or "Add to Home Screen").
5. Done. There's now a **Nanban icon** on your home screen. Tap it — launches full-screen with no browser bars. Looks and feels like a native app.

That's it. iOS is the same: Safari → Share → "Add to Home Screen".

**You never leave the phone's local network?** Install [Tailscale](https://tailscale.com) on both devices (free). It gives your laptop a private IP your phone can reach from anywhere.

---

## Path B — Real signed `.apk` file (if you specifically want one)

If you want an actual `Nanban.apk` file to install / share, use **PWABuilder.com** — Microsoft's free, open-source tool that turns any PWA into a signed native Android APK (and iOS / Windows too).

**Steps (one time, ~5 minutes):**

1. Make Nanban publicly reachable, so PWABuilder can see it. Simplest free way:
   - On the laptop: `cloudflared tunnel --url http://localhost:7860`
   - Copy the `https://...trycloudflare.com` URL it prints.
2. Open https://www.pwabuilder.com — paste that URL → **Start**.
3. It analyses Nanban's PWA manifest and shows a report. Click **Package for Stores → Android**.
4. Settings:
   - **Package ID**: `com.nanban.app`
   - **App Name**: `Nanban`
   - **Launcher Name**: `Nanban`
   - Leave the rest as defaults.
5. Click **Download Package** → you get `nanban.apk` (plus a signed key — keep it for future updates).
6. Email / sideload the `.apk` to your phone → tap to install → **Nanban is now a real Android app**.

The resulting APK is a thin WebView wrapper that opens your Nanban. All UI, chat, terminal, security features work the same as in the browser. Updates to your Nanban reflect immediately — no re-build needed unless the app manifest changes.

---

## iOS (iPhone/iPad)

iOS does not allow sideloading `.apk`-style files unless the developer pays for an Apple Developer account ($99/year). PWA install (Path A) is the only sensible way — but it works beautifully on iOS Safari (Share → Add to Home Screen). The result is a full-screen app on the home screen.
