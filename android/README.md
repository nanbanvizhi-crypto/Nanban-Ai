# 📱 Nanban Android (Nanban.apk)

A real native Android app that opens your Nanban server. First launch asks for the server URL (your laptop's address or a public tunnel URL), remembers it forever. The menu has "Change server URL" and "Reload."

**Why a thin WebView wrapper and not a full-native app?** A full native app that runs a 1–2 GB AI model on-device isn't realistic — phone hardware. This wrapper gives you a real Android app icon + full-screen launch + native feel, talking to the full-power Nanban on your laptop.

---

## 🚀 Three ways to get `Nanban.apk`

### Option 1 — GitHub Actions (easiest, zero install) ⭐ recommended
This repo already has `.github/workflows/build-android-apk.yml`. GitHub builds the APK for you, for free:

1. Push this folder to GitHub (any public or private repo).
2. Go to **Actions** → **Build Android APK** → wait ~4 minutes for the green check.
3. Click the finished run → scroll to **Artifacts** → download `nanban-apk` → unzip → `Nanban.apk`.
4. Email the `.apk` to your phone → tap to install.

(On your phone, enable "Install unknown apps" for your mail/file app — one-time toggle.)

### Option 2 — Local build with Android Studio
1. Install [Android Studio](https://developer.android.com/studio).
2. Open this `android/` folder as a project.
3. Menu: **Build → Build Bundle(s) / APK(s) → Build APK(s)**.
4. Pop-up gives you the APK path.

### Option 3 — Command line (any machine with Android SDK)
```bash
cd android
./gradlew assembleRelease
# APK is at: app/build/outputs/apk/release/app-release.apk
```

---

## 📲 Installing the APK

1. Copy `Nanban.apk` to your phone (email, Google Drive, USB).
2. Tap it → Android asks permission the first time → Install.
3. Open the Nanban app → it asks for your server URL.
4. Type your laptop's address — e.g. `http://192.168.1.4:7860` (same Wi-Fi) or `https://your-tunnel.trycloudflare.com` (public).
5. Tap **Connect**. Done — Nanban is now on your phone's home screen.

Change the URL any time: menu (⋮ top right) → **Change server URL**.

---

## 🔒 About signing

The release build is signed with Android's standard debug keystore, which is universally installable but **not** for the Play Store. For Play Store publishing, create a real keystore and point `signingConfig` at it in `app/build.gradle`.

---

## 💡 Easiest alternative — no `.apk` file needed

Nanban is already a full PWA (Progressive Web App). On your phone's Chrome → open the Nanban URL → menu → **"Install app"** → home-screen icon that launches full-screen. Takes 10 seconds. Looks and behaves like a native app with no build step.
