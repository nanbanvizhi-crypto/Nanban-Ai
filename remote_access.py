"""
🌍 One-tap Remote Access for Nanban.

Starts a Cloudflare Tunnel (no account needed) so your phone can reach Nanban from anywhere,
grabs the public https://…trycloudflare.com link, and shows it as a QR code to scan. Stop it
with one click too. No editing tunnel.bat, no typing IPs.

Safety: the tunnel exposes Nanban to the public internet, so this refuses to start unless a
login is set (WEB_PASSWORD for the web app, or USERS for the Nanban Server). It also reminds
you to use a strong password.
"""

import base64
import io
import re
import shutil
import subprocess
import threading
import time

import config

_proc = None
_url = ""
_lock = threading.Lock()


def _port() -> int:
    try:
        import web_computer
        if getattr(web_computer, "SERVER_MODE", False):
            return config.SERVER_PORT
    except Exception:
        pass
    return getattr(config, "WEB_PORT", 7860)


def _has_auth() -> bool:
    return bool(getattr(config, "WEB_PASSWORD", "") or getattr(config, "USERS", {}))


def available() -> bool:
    return shutil.which("cloudflared") is not None


def tunnel_url() -> str:
    return _url


def is_running() -> bool:
    return _proc is not None and _proc.poll() is None


def start() -> str:
    """Launch the tunnel and return the public URL (waits up to ~25s), or '' if it failed."""
    global _proc, _url
    with _lock:
        if is_running() and _url:
            return _url
        if not available():
            return ""
        port = _port()
        try:
            _proc = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        except Exception:
            _proc = None
            return ""
        _url = ""

        def reader():
            global _url
            try:
                for line in _proc.stdout:
                    m = re.search(r"https://[-\w]+\.trycloudflare\.com", line)
                    if m:
                        _url = m.group(0)
                        break
            except Exception:
                pass

        threading.Thread(target=reader, daemon=True).start()
    for _ in range(50):
        if _url:
            break
        time.sleep(0.5)
    return _url


def stop() -> None:
    global _proc, _url
    with _lock:
        if _proc:
            try:
                _proc.terminate()
            except Exception:
                pass
        _proc = None
        _url = ""


# ---------------------------------------------------------------- rendering

def _qr_data_uri(url: str) -> str:
    try:
        import qrcode
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


def _link_html(url: str) -> str:
    qr = _qr_data_uri(url)
    qr_img = f'<img class="ra-qr" src="{qr}" alt="QR">' if qr else ""
    pw = "a strong password" if not config.WEB_PASSWORD else f"<code>{config.WEB_PASSWORD}</code>"
    return (
        '<div class="ra-live">'
        '<div class="ra-badge">🟢 Remote access ON — reachable from anywhere</div>'
        f'{qr_img}'
        '<div class="ra-scan">📱 Scan this with your iPhone camera, or open the link:</div>'
        f'<a class="ra-url" href="{url}" target="_blank">{url}</a>'
        f'<div class="ra-note">Login: user <b>nanban</b> · password {pw}. '
        'Anyone with this link can reach the login page — keep it private. '
        'The link changes each time you start it.</div>'
        '</div>')


def _install_html() -> str:
    return (
        '<div class="ra-warn"><b>Cloudflare Tunnel isn\'t installed yet</b> (one-time, free).<br>'
        'Install it on this laptop, then click the button again:<br><br>'
        '• <b>Easiest:</b> open <b>Command Prompt</b> and run '
        '<code>winget install --id Cloudflare.cloudflared</code><br>'
        '• Or download <code>cloudflared.exe</code> from '
        'github.com/cloudflare/cloudflared/releases and put it in this folder.</div>')


def _no_auth_html() -> str:
    return (
        '<div class="ra-warn"><b>Set a password first</b> — remote access would put Nanban on the '
        'public internet, so a login is required.<br><br>'
        'In <code>config.py</code> set <code>LAN_ACCESS = True</code> and '
        '<code>WEB_PASSWORD = "your-strong-password"</code>, restart Nanban, then try again. '
        '(On the Nanban Server, adding <code>USERS</code> also counts.)</div>')


def _idle_html() -> str:
    return ('<div class="ra-idle">Remote access is <b>off</b>. Click <b>Start remote access</b> '
            'to get a private link + QR code you can open on your phone from anywhere. '
            'Your laptop must stay on and awake.</div>')


def current_render() -> str:
    return _link_html(_url) if (is_running() and _url) else _idle_html()


def start_and_render() -> str:
    if not _has_auth():
        return _no_auth_html()
    if not available():
        return _install_html()
    url = start()
    if not url:
        return ('<div class="ra-warn">Couldn\'t get a link. Make sure Nanban is running and you '
                'have internet, then try again.</div>')
    return _link_html(url)


def stop_and_render() -> str:
    stop()
    return ('<div class="ra-idle">🔴 Remote access <b>stopped</b>. Your phone can no longer reach '
            'Nanban from outside your Wi-Fi.</div>')
