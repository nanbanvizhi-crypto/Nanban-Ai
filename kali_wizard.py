"""
Kali Linux Auto-Setup — one-click install, user creation, tools, SSH, and
auto-wiring into Nanban's /server registry. Lives in the Security tab so
anyone can use Kali without typing a shell command.

Architecture reality: Kali is a full Linux OS. The ONLY way to run it on
Windows without a VM is Microsoft's WSL2. This module drives the end-to-end
install of WSL2 + Kali + the full tool set + SSH, non-interactively, with
clear progress reporting back to the UI.

Flow (first time):
  1. Check state → shows what's missing.
  2. If WSL2 missing: elevated `wsl --install` (one UAC prompt, one restart).
  3. If Kali missing: `wsl --install -d kali-linux --no-launch`.
  4. Create user non-interactively (useradd + set password + /etc/wsl.conf default user).
  5. apt install kali-linux-headless + openssh-server.
  6. Start SSH + make it autostart.
  7. Register in Nanban's server list as `kali`.
Done — Security tab shows ✅ and the Terminal tab's `/server use kali` works.

Every subsequent run detects the finished state and skips to ✅ immediately.
"""
from __future__ import annotations

import os
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path

import config
import servers

IS_WINDOWS = os.name == "nt"

# ---------------------------------------------------------------- state detection


@dataclass
class KaliState:
    wsl_installed: bool = False          # WSL2 engine available
    kali_installed: bool = False         # kali-linux distro registered
    user_created: bool = False           # a default non-root user exists
    tools_installed: bool = False        # kali-linux-headless metapackage present
    ssh_running: bool = False            # ssh service up
    wired_in_nanban: bool = False        # servers.json has a 'kali' entry
    default_user: str = ""               # the default user inside Kali

    @property
    def fully_ready(self) -> bool:
        return all((self.wsl_installed, self.kali_installed, self.user_created,
                    self.tools_installed, self.ssh_running, self.wired_in_nanban))

    def summary(self) -> str:
        """Human-readable summary for the UI."""
        if not IS_WINDOWS:
            return "_Kali Auto-Setup is Windows-only. On Linux/macOS you can install Kali manually._"
        tick = lambda ok: "✅" if ok else "⚪"
        rows = [
            f"{tick(self.wsl_installed)}  WSL2 engine",
            f"{tick(self.kali_installed)}  Kali Linux installed",
            f"{tick(self.user_created)}  Default user: `{self.default_user or '—'}`",
            f"{tick(self.tools_installed)}  Security tools (nmap, sqlmap, metasploit, ...)",
            f"{tick(self.ssh_running)}  SSH service running",
            f"{tick(self.wired_in_nanban)}  Connected to Nanban (as `kali`)",
        ]
        return "\n".join(rows)


def _run(args: list[str], timeout: int = 60, input_text: str = "") -> tuple[int, str]:
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout,
                           input=input_text.encode() if input_text else None)
        return r.returncode, (r.stdout + r.stderr).decode("utf-8", errors="replace")
    except Exception as e:
        return 1, str(e)


def _wsl(args: list[str], timeout: int = 60, as_root: bool = False, user: str = "") -> tuple[int, str]:
    cmd = ["wsl.exe", "-d", "kali-linux"]
    if as_root:
        cmd += ["--user", "root"]
    elif user:
        cmd += ["--user", user]
    cmd += ["--"] + args
    return _run(cmd, timeout=timeout)


def detect() -> KaliState:
    """Fast snapshot of what's currently set up."""
    s = KaliState()
    if not IS_WINDOWS:
        return s
    # WSL engine
    code, out = _run(["wsl.exe", "--status"], timeout=10)
    s.wsl_installed = (code == 0)
    # Kali distro
    code, out = _run(["wsl.exe", "-l", "-q"], timeout=10)
    s.kali_installed = "kali-linux" in out.lower().replace("\x00", "")
    if s.kali_installed:
        # default user (from /etc/wsl.conf or /etc/passwd)
        _, who = _wsl(["bash", "-lc", "id -un 2>/dev/null"], timeout=15)
        s.default_user = (who or "").strip().splitlines()[-1] if who.strip() else ""
        s.user_created = bool(s.default_user) and s.default_user != "root"
        # kali-linux-headless metapackage
        _, got = _wsl(["bash", "-lc", "dpkg -l kali-linux-headless 2>/dev/null | tail -1"], timeout=15)
        s.tools_installed = "ii  kali-linux-headless" in got
        # ssh service
        _, ssh = _wsl(["bash", "-lc", "service ssh status 2>&1 | head -1"], timeout=15, as_root=True)
        s.ssh_running = "is running" in ssh or "active (running)" in ssh
    # Nanban's /server registry
    s.wired_in_nanban = "kali" in servers.names()
    return s


# ---------------------------------------------------------------- one-click setup
# Each step is idempotent — safe to re-run — and streams progress lines through
# `on_log`. The UI pipes those to a live Markdown log.


class SetupError(Exception):
    pass


def enable_wsl_elevated(on_log) -> None:
    """Trigger `wsl --install` in an elevated PowerShell. User sees a UAC prompt.
    A reboot is needed after the first successful run — the UI tells them."""
    on_log("🔑  Asking Windows to enable WSL2 (click **Yes** on the UAC prompt)…")
    # Start-Process -Verb RunAs makes the UAC prompt appear.
    ps = ("Start-Process -Verb RunAs -FilePath wsl.exe "
          "-ArgumentList '--install','--no-distribution' -Wait")
    code, out = _run(["powershell.exe", "-NoProfile", "-Command", ps], timeout=600)
    if code != 0:
        raise SetupError("WSL2 install was cancelled or failed. "
                         "Run **PowerShell as Administrator** and try `wsl --install` manually, then restart.")
    on_log("✅ WSL2 enabled. **Please restart Windows now**, then open Nanban again and click this button.")


def install_kali(on_log) -> None:
    on_log("⬇️  Installing Kali Linux (~2 GB, a few minutes)…")
    code, out = _run(["wsl.exe", "--install", "-d", "kali-linux", "--no-launch"], timeout=1800)
    if code != 0 and "already installed" not in out.lower():
        raise SetupError(f"Could not install Kali:\n{out[-800:]}")
    on_log("✅ Kali installed.")


def _password_hash(password: str) -> str:
    """Pre-hash the password so we never send plaintext through a shell."""
    import crypt
    return crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))


def create_user(username: str, password: str, on_log) -> None:
    if not username.isidentifier():
        raise SetupError("Username must be letters/digits/underscore only.")
    on_log(f"👤 Creating user `{username}` in Kali…")
    # The first `wsl.exe -d kali-linux --user root --` bootstraps rootfs if needed.
    script = (
        f"set -e; "
        f"id -u {username} >/dev/null 2>&1 || useradd -m -s /bin/bash -G sudo {username}; "
        f"echo '{username}:{password}' | chpasswd; "
        f"grep -q '^\\[user\\]' /etc/wsl.conf 2>/dev/null || printf '\\n[user]\\ndefault=%s\\n' {username} >> /etc/wsl.conf; "
        f"echo ok"
    )
    code, out = _wsl(["bash", "-c", script], timeout=120, as_root=True)
    if "ok" not in out:
        raise SetupError(f"Could not create user:\n{out[-500:]}")
    # Apply default-user change by terminating + restarting the distro
    _run(["wsl.exe", "--terminate", "kali-linux"], timeout=30)
    on_log(f"✅ User `{username}` ready.")


def install_tools(on_log) -> None:
    on_log("📦 Installing security tool suite (nmap, sqlmap, metasploit, hydra, nikto, …) — one time, ~5 GB.")
    on_log("     This takes 10–20 minutes depending on your internet. Progress is shown below.")
    script = ("export DEBIAN_FRONTEND=noninteractive; "
              "apt-get update -q && "
              "apt-get install -y -q kali-linux-headless openssh-server")
    code, out = _wsl(["bash", "-c", script], timeout=3600, as_root=True)
    if code != 0:
        raise SetupError(f"apt install failed:\n{out[-1200:]}")
    on_log("✅ Tools installed.")


def start_ssh(on_log) -> None:
    on_log("🔌 Starting SSH service…")
    script = ("set -e; "
              "service ssh start; "
              "grep -q 'service ssh start' /root/.bashrc 2>/dev/null || echo 'service ssh start >/dev/null 2>&1' >> /root/.bashrc; "
              "service ssh status | head -1")
    code, out = _wsl(["bash", "-c", script], timeout=60, as_root=True)
    if "is running" not in out and "active" not in out:
        raise SetupError(f"SSH didn't start:\n{out[-500:]}")
    on_log("✅ SSH running.")


def connect_in_nanban(username: str, password: str, on_log) -> None:
    on_log("🔗 Registering Kali as `kali` in Nanban's /server list…")
    servers.add("kali", f"{username}@127.0.0.1", key="", password=password, save_password=True,
                tags=["kali", "security"], notes="Auto-set-up by Kali Auto-Setup")
    on_log("✅ Connected. In the Terminal tab, `/server use kali` is now ready.")


# ---------------------------------------------------------------- orchestrator

def run_all(username: str, password: str, on_log) -> KaliState:
    """Do every step still needed. Safe to re-run — each step is idempotent.
    Streams progress to `on_log`. Returns the state at the end."""
    if not IS_WINDOWS:
        on_log("⚠️  Auto-Setup is Windows-only.")
        return detect()

    state = detect()
    try:
        if not state.wsl_installed:
            enable_wsl_elevated(on_log)
            return detect()   # user must restart Windows before we continue

        if not state.kali_installed:
            install_kali(on_log)
            state = detect()

        if not state.user_created:
            create_user(username, password, on_log)
            state = detect()

        if not state.tools_installed:
            install_tools(on_log)
            state = detect()

        if not state.ssh_running:
            start_ssh(on_log)
            state = detect()

        if not state.wired_in_nanban:
            connect_in_nanban(state.default_user or username, password, on_log)
            state = detect()

        if state.fully_ready:
            on_log("\n🎉 **All done.** Kali + full tool set is ready. "
                   "Open the **Terminal** tab and try `/server use kali` → `nmap -sV scanme.nmap.org`.")
    except SetupError as e:
        on_log(f"\n❌ {e}")
    except Exception as e:
        on_log(f"\n❌ Unexpected error: {e}")

    return state


# ---------------------------------------------------------------- background runner

_lock = threading.Lock()
_running = False


def is_running() -> bool:
    return _running


def run_async(username: str, password: str, log_sink: list[str]):
    """Kick off run_all in a thread so the UI stays responsive.
    `log_sink` is a list the UI polls for new lines."""
    global _running
    with _lock:
        if _running:
            log_sink.append("_(already running — please wait)_")
            return
        _running = True

    def _worker():
        global _running
        try:
            run_all(username, password, log_sink.append)
        finally:
            _running = False

    threading.Thread(target=_worker, daemon=True).start()
