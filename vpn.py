"""
VPN awareness for Nanban.

Nanban runs on your own laptop, so whatever VPN you switch on in Windows (or Linux)
already carries all of Nanban's internet traffic: web search, page fetches, downloads,
terminal commands. This module only *detects* that VPN, shows it, can connect or
disconnect a Windows VPN profile, and (optionally) blocks internet tools when the VPN
is off (a "kill switch" for the AI's web access).

It does not create a VPN and cannot make one faster: speed depends on the VPN server
and your connection.
"""

import json
import os
import re
import subprocess
import time

import config

IS_WINDOWS = os.name == "nt"
_cache = {"time": 0.0, "status": None}
CACHE_SECONDS = 5

VPN_ADAPTER_WORDS = re.compile(
    r"wireguard|openvpn|tap-windows|tap adapter|tun|proton|nord|express|surfshark|mullvad|windscribe|"
    r"cloudflare warp|tailscale|zerotier|vpn|cisco anyconnect|fortinet|globalprotect|pulse",
    re.IGNORECASE,
)


def _run(args: list[str], timeout: int = 15) -> str:
    try:
        flags = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
        result = subprocess.run(args, capture_output=True, timeout=timeout, creationflags=flags)
        return result.stdout.decode("utf-8", errors="replace")
    except Exception:
        return ""


def _powershell(command: str, timeout: int = 15) -> str:
    return _run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                 "[Console]::OutputEncoding=[Text.Encoding]::UTF8; " + command], timeout)


# ---------------------------------------------------------------- detection

def status(force: bool = False) -> dict:
    """Return {'connected': bool, 'names': [...], 'kind': 'windows-vpn'|'adapter'|'linux'|'none'}."""
    now = time.monotonic()
    if not force and _cache["status"] and now - _cache["time"] < CACHE_SECONDS:
        return _cache["status"]

    names, kind = [], "none"
    if IS_WINDOWS:
        out = _powershell("Get-VpnConnection -ErrorAction SilentlyContinue | "
                          "Where-Object {$_.ConnectionStatus -eq 'Connected'} | "
                          "Select-Object -ExpandProperty Name")
        names = [line.strip() for line in out.splitlines() if line.strip()]
        if names:
            kind = "windows-vpn"
        else:
            out = _powershell("Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object {$_.Status -eq 'Up'} | "
                              "ForEach-Object { $_.Name + '|' + $_.InterfaceDescription }")
            for line in out.splitlines():
                if VPN_ADAPTER_WORDS.search(line):
                    names.append(line.split("|")[0].strip())
            if names:
                kind = "adapter"
    else:
        out = _run(["ip", "-o", "link", "show", "up"])
        for line in out.splitlines():
            match = re.match(r"\d+:\s*([^:@]+)", line)
            if match and re.match(r"(tun|tap|wg|ppp|proton|nordlynx|tailscale)", match.group(1)):
                names.append(match.group(1))
        if names:
            kind = "linux"

    result = {"connected": bool(names), "names": names, "kind": kind}
    _cache.update(time=now, status=result)
    return result


def is_connected() -> bool:
    return status()["connected"]


def profiles() -> list[dict]:
    """Windows VPN profiles the user has set up (Settings > Network > VPN)."""
    if not IS_WINDOWS:
        return []
    out = _powershell("Get-VpnConnection -ErrorAction SilentlyContinue | "
                      "Select-Object Name, ServerAddress, ConnectionStatus | ConvertTo-Json -Compress")
    try:
        data = json.loads(out) if out.strip() else []
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        return []


# ---------------------------------------------------------------- connect / disconnect

def connect(name: str = "") -> str:
    if not IS_WINDOWS:
        return "Connecting is only automated on Windows. Use your VPN app or `nmcli`/`wg-quick` here."
    available = profiles()
    if not name:
        if len(available) == 1:
            name = available[0]["Name"]
        elif not available:
            return ("No Windows VPN profile found. Either open your VPN app (ProtonVPN, WireGuard, etc.) and "
                    "connect there, or add a profile in Settings > Network & internet > VPN.")
        else:
            return "Which one? " + ", ".join(p["Name"] for p in available) + "  (e.g. /vpn on " + available[0]["Name"] + ")"
    out = _run(["rasdial", name], timeout=60)
    _cache["status"] = None
    if "Successfully connected" in out or "already connected" in out.lower():
        return f"Connected to VPN '{name}'."
    return f"Could not connect '{name}': {out.strip() or 'unknown error'}"


def disconnect(name: str = "") -> str:
    if not IS_WINDOWS:
        return "Disconnecting is only automated on Windows."
    out = _run(["rasdial", name, "/disconnect"] if name else ["rasdial", "/disconnect"], timeout=30)
    _cache["status"] = None
    return "Disconnected." if "Command completed" in out or not out.strip() else out.strip()


def public_ip() -> str:
    """Public IP as the internet sees you (uses the internet). Handy to confirm the VPN is working."""
    try:
        import requests
        data = requests.get("https://ipinfo.io/json", timeout=8).json()
        where = ", ".join(x for x in [data.get("city"), data.get("country")] if x)
        return f"{data.get('ip', '?')} ({where})" + (f" · {data.get('org')}" if data.get("org") else "")
    except Exception as e:
        return f"Could not check public IP ({e})"


# ---------------------------------------------------------------- kill switch for AI internet tools

def internet_allowed() -> tuple[bool, str]:
    """(allowed, reason). When REQUIRE_VPN is on, internet tools are blocked while the VPN is off."""
    if not getattr(config, "REQUIRE_VPN", False):
        return True, ""
    if is_connected():
        return True, ""
    return False, ("Blocked: VPN is OFF and the 'require VPN for internet' setting is on. "
                   "Turn on your VPN (or /vpn on), or set REQUIRE_VPN = False in config.py.")


def badge() -> str:
    s = status()
    if s["connected"]:
        return "🛡️ VPN ON" + (f" ({s['names'][0]})" if s["names"] else "")
    return "🛡️ VPN off" + (" · internet blocked" if getattr(config, "REQUIRE_VPN", False) else "")
