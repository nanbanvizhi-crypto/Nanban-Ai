"""
Shell engine for the Nanban terminal.

Three backends:
  "linux"      - bash. On Windows this runs inside WSL (Ubuntu); on Linux/macOS it is the local bash.
  "powershell" - Windows PowerShell (Windows only).
  "cmd"        - classic Command Prompt, cmd.exe (Windows only).
("windows" is accepted as an alias of "powershell".)

Commands you type run attached to your real terminal, so interactive programs
(vim, nano, htop, python, ssh, sudo prompts) work normally. Commands the AI runs
are captured (output shown live and sent back to the AI) with a timeout.
"""

import os
import platform
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

IS_WINDOWS = os.name == "nt"
MAX_OUTPUT_CHARS = 6000

# Bundled BusyBox gives Linux commands on Windows with no install (no WSL, no Kali).
# It ships as a single busybox.exe in bin/. If missing, we fall back cleanly.
BUSYBOX_EXE = Path(__file__).resolve().parent / "bin" / "busybox.exe"


def busybox_available() -> bool:
    return IS_WINDOWS and BUSYBOX_EXE.exists()


def _decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def wsl_available() -> bool:
    if not IS_WINDOWS or not shutil.which("wsl"):
        return False
    try:
        return subprocess.run(["wsl.exe", "-e", "true"], capture_output=True, timeout=30).returncode == 0
    except Exception:
        return False


_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07|\r")


def _strip_ansi(text: str) -> str:
    text = _ANSI.sub("", text)
    # drop the header/footer lines that `script` adds
    return "\n".join(l for l in text.splitlines() if not l.startswith(("Script started on", "Script done on"))).strip()


def trim_output(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    """Keep the start and the end of long output (errors are usually at the end)."""
    if len(text) <= limit:
        return text
    head, tail = text[: limit // 4], text[-(limit * 3 // 4):]
    cut = text[len(head): len(text) - len(tail)].count("\n")
    return f"{head}\n... [{cut} lines cut] ...\n{tail}"


class ShellSession:
    def __init__(self, backend: str = "auto", start_dir: str | None = None):
        self.cwd = Path(start_dir or os.getcwd()).resolve()   # path Python can open
        self.prev_cwd = self.cwd
        self.linux_cwd = ""     # only used for WSL
        self.linux_home = ""
        self.has_wsl = False
        self.backend = ""
        self.powershell = (shutil.which("pwsh") or shutil.which("powershell") or "powershell") if IS_WINDOWS else ""
        self.posix_shell = "" if IS_WINDOWS else (shutil.which("bash") or os.environ.get("SHELL") or "/bin/sh")
        self.set_backend("linux" if backend == "auto" else backend)

    # ------------------------------------------------------------ backends

    @property
    def uses_wsl(self) -> bool:
        return IS_WINDOWS and self.backend == "linux"

    def set_backend(self, backend: str) -> str:
        """Switch between 'linux' (WSL or busybox), 'powershell' and 'cmd'. Returns a status message."""
        backend = {"windows": "powershell", "ps": "powershell", "bash": "linux", "wsl": "linux",
                   "busybox": "linux"}.get(backend, backend)
        if backend in {"powershell", "cmd"}:
            if not IS_WINDOWS:
                return f"{backend} mode is only available on Windows."
            self.backend = backend
            return ("Switched to Command Prompt (cmd.exe)." if backend == "cmd"
                    else f"Switched to Windows PowerShell ({Path(self.powershell).stem}).")

        if IS_WINDOWS:
            self.has_wsl = self.has_wsl or wsl_available()
            if self.has_wsl:
                self.backend = "linux"
                out = self._wsl_capture(["pwd"], cwd_override=str(self.cwd))
                self.linux_cwd = out.strip().splitlines()[-1] if out.strip() else "~"
                self.linux_home = self._wsl_capture(["bash", "-lc", "echo $HOME"]).strip()
                return "Switched to Linux (bash in WSL)."
            # No WSL — fall back to the bundled BusyBox for Linux-style commands,
            # so Nanban Portable has a usable Linux shell with zero install.
            if busybox_available():
                self.backend = "linux"
                return "Switched to Linux (BusyBox — bundled, no install needed)."
            if not self.backend:
                self.backend = "powershell"
            return ("Linux (WSL) is not installed. Nanban Portable bundles BusyBox for the same "
                    "commands with no install — this build is missing bin/busybox.exe.")

        self.backend = "linux"
        return f"Using {Path(self.posix_shell).name}."

    def _wsl_capture(self, args: list[str], cwd_override: str | None = None, timeout: int = 30) -> str:
        cd = cwd_override or self.linux_cwd or "~"
        try:
            result = subprocess.run(["wsl.exe", "--cd", cd, "--", *args], capture_output=True, timeout=timeout)
            return _decode(result.stdout)
        except Exception:
            return ""

    # ------------------------------------------------------------ display

    def label(self) -> str:
        if self.uses_wsl:
            return "bash · WSL"
        if IS_WINDOWS and self.backend == "linux" and busybox_available():
            return "sh · BusyBox"
        if self.backend == "powershell":
            return "PowerShell"
        if self.backend == "cmd":
            return "CMD"
        return Path(self.posix_shell).name

    def display_cwd(self) -> str:
        if self.uses_wsl:
            path = self.linux_cwd
            if self.linux_home and (path == self.linux_home or path.startswith(self.linux_home + "/")):
                path = "~" + path[len(self.linux_home):]
            return path
        home = str(Path.home())
        path = str(self.cwd)
        return "~" + path[len(home):] if path == home or path.startswith(home + os.sep) else path

    # ------------------------------------------------------------ cd

    def change_dir(self, target: str) -> str:
        """Change directory. Returns '' on success or an error message."""
        target = target.strip().strip('"').strip("'")
        if target.lower().startswith("/d "):     # cmd.exe style: cd /d D:\x
            target = target[3:].strip()
        if target == "-":
            target = str(self.prev_cwd)
        if not target:
            target = "~"

        if self.uses_wsl:
            script = ('t="$1"; case "$t" in "~"*) t="$HOME${t#\\~}";; esac; '
                      'cd -- "$t" 2>&1 && pwd && wslpath -w "$PWD"')
            out = self._wsl_capture(["bash", "-c", script, "_", target]).strip().splitlines()
            if len(out) < 2 or not out[-2].startswith("/"):
                return " ".join(out) or f"cd: {target}: No such directory"
            self.prev_cwd = self.cwd
            self.linux_cwd, self.cwd = out[-2], Path(out[-1])
            return ""

        if IS_WINDOWS and len(target) == 2 and target[1] == ":":
            target += "\\"
        path = Path(os.path.expandvars(os.path.expanduser(target)))
        path = (path if path.is_absolute() else self.cwd / path).resolve()
        if not path.is_dir():
            return f"cd: {target}: No such directory"
        self.prev_cwd, self.cwd = self.cwd, path
        return ""

    def resolve_path(self, p: str) -> Path:
        """Turn a path from the user or the AI into one Python can open.
        In WSL mode, Linux paths like /home/me/app.py or ~/app.py are converted with wslpath."""
        p = (p or ".").strip().strip('"').strip("'")
        if self.uses_wsl and (p.startswith("/") or p.startswith("~")):
            script = ('t="$1"; case "$t" in "~"*) t="$HOME${t#\\~}";; esac; '
                      'd=$(dirname "$t"); b=$(basename "$t"); w=$(wslpath -w "$d") && printf \'%s\\\\%s\' "$w" "$b"')
            out = self._wsl_capture(["bash", "-c", script, "_", p]).strip()
            if not out:
                raise ValueError(f"Can't find the folder for {p}")
            return Path(out)
        path = Path(os.path.expandvars(os.path.expanduser(p)))
        return path if path.is_absolute() else self.cwd / path

    # ------------------------------------------------------------ running

    def _command_args(self, command: str, interactive: bool, backend: str = "") -> list[str]:
        backend = backend or self.backend
        if IS_WINDOWS and backend == "linux":
            if self.has_wsl:
                if not self.linux_cwd:
                    out = self._wsl_capture(["pwd"], cwd_override=str(self.cwd))
                    self.linux_cwd = out.strip().splitlines()[-1] if out.strip() else "~"
                return ["wsl.exe", "--cd", self.linux_cwd or "~", "--", "bash", "-lic" if interactive else "-lc", command]
            # Zero-install Linux via bundled BusyBox (`busybox sh -c ...`):
            if busybox_available():
                return [str(BUSYBOX_EXE), "sh", "-c", command]
        if backend == "powershell":
            if interactive:
                return [self.powershell, "-NoLogo", "-Command", command]
            utf8 = "[Console]::OutputEncoding=[Text.Encoding]::UTF8; $ProgressPreference='SilentlyContinue'; "
            return [self.powershell, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", utf8 + command]
        if backend == "cmd":
            return ["cmd.exe", "/d", "/c", command if interactive else "chcp 65001>nul & " + command]
        return [self.posix_shell, "-lc", command]

    def available_backends(self) -> list[str]:
        if not IS_WINDOWS:
            return ["linux"]
        found = ["powershell", "cmd"]
        if not self.has_wsl and not getattr(self, "_wsl_checked", False):
            self._wsl_checked = True
            self.has_wsl = wsl_available()
        # "linux" is available via WSL (preferred) or the bundled BusyBox (no install).
        if self.has_wsl or busybox_available():
            found.insert(0, "linux")
        return found

    def run_interactive(self, command: str, backend: str = "") -> int:
        """Run a command typed by the user, attached to the real terminal."""
        backend = backend or self.backend
        try:
            return subprocess.run(self._command_args(command, interactive=True, backend=backend),
                                  cwd=None if (IS_WINDOWS and backend == "linux") else self.cwd).returncode
        except KeyboardInterrupt:
            return 130
        except FileNotFoundError as e:
            print(f"Shell not found: {e}")
            return 127

    # Programs that need the real console (no output recording): editors, REPLs, pagers, remote shells
    INTERACTIVE_PROGRAMS = {
        "vim", "vi", "nvim", "nano", "emacs", "micro", "less", "more", "man", "top", "htop", "btop", "ssh",
        "telnet", "ftp", "sftp", "mysql", "psql", "sqlite3", "irb", "bash", "sh", "zsh", "fish", "powershell",
        "pwsh", "cmd", "wsl", "tmux", "screen", "watch", "ipython", "gdb", "lazygit", "ranger", "mc", "ollama",
    }

    def _is_interactive(self, command: str) -> bool:
        words = command.strip().split()
        if not words:
            return False
        program = Path(words[0]).name.lower().removesuffix(".exe")
        if program in self.INTERACTIVE_PROGRAMS:
            return not (program == "ollama" and len(words) > 1 and words[1] not in {"run"})
        if program in {"python", "python3", "py", "node", "deno", "bun"}:
            return len(words) == 1 or words[1].startswith("-i")
        return False

    def run_user_command(self, command: str, backend: str = "") -> tuple[int, str]:
        """Run a command the user typed: attached to the real terminal (interactive programs work),
        while also recording the output so the AI can explain errors. Returns (exit code, output)."""
        backend = backend or self.backend
        env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
        if self._is_interactive(command):
            return self.run_interactive(command, backend=backend), ""

        if backend == "linux":
            # `script` gives the command a real terminal (colours, prompts) and records everything.
            quoted = command.replace("'", "'\\''")
            if IS_WINDOWS:
                log = f"/tmp/nanban_{os.getpid()}.log"
                # script shows the output on the terminal; we read the recording afterwards
                code = self.run_interactive(f"script -qfec '{quoted}' {log}", backend="linux")
                output = self._wsl_capture(["bash", "-c", f"cat {log} 2>/dev/null; rm -f {log}"])
                return code, _strip_ansi(output)
            if shutil.which("script"):
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as handle:
                    log = handle.name
                try:
                    code = subprocess.run(["script", "-qfec", command, log], cwd=self.cwd, env=env).returncode
                    output = Path(log).read_text(encoding="utf-8", errors="replace")
                finally:
                    Path(log).unlink(missing_ok=True)
                return code, _strip_ansi(output)
            return self.run_interactive(command, backend=backend), ""

        # Windows PowerShell / CMD: stream through Tee-Object so the user sees it live and we keep a copy.
        import tempfile
        log = Path(tempfile.gettempdir()) / f"nanban_{os.getpid()}.log"
        escaped = command.replace("'", "''")
        if backend == "cmd":
            runner = f"cmd /d /c '{escaped}' 2>&1 | Tee-Object -FilePath '{log}'; exit $LASTEXITCODE"
        else:
            runner = (f"try {{ & {{ {command} }} 2>&1 | Tee-Object -FilePath '{log}' }} "
                      f"catch {{ $_ | Out-String | Tee-Object -FilePath '{log}' -Append; exit 1 }}; "
                      f"if ($LASTEXITCODE) {{ exit $LASTEXITCODE }}; if (-not $?) {{ exit 1 }}")
        try:
            code = subprocess.run([self.powershell, "-NoLogo", "-NoProfile", "-Command", runner],
                                  cwd=self.cwd, env=env).returncode
        except KeyboardInterrupt:
            code = 130
        try:
            output = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
            log.unlink(missing_ok=True)
        except OSError:
            output = ""
        return code, _strip_ansi(output)

    def run_captured(self, command: str, timeout: int = 120, on_line=None, backend: str = "") -> tuple[int, str]:
        """Run a command for the AI: no keyboard input, output captured, stopped after `timeout` seconds.
        `backend` lets the AI pick 'linux', 'powershell' or 'cmd' for this one command."""
        backend = backend or self.backend
        if backend not in self.available_backends():
            return 127, f"The '{backend}' shell is not available on this computer. Available: {', '.join(self.available_backends())}"
        try:
            process = subprocess.Popen(
                self._command_args(command, interactive=False, backend=backend),
                cwd=None if (IS_WINDOWS and backend == "linux") else self.cwd,
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
        except FileNotFoundError as e:
            return 127, f"Shell not found: {e}"

        lines: list[str] = []

        def reader():
            for raw in iter(process.stdout.readline, b""):
                line = _decode(raw).rstrip("\n")
                lines.append(line)
                if on_line:
                    on_line(line)

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        deadline = time.monotonic() + timeout
        try:
            while process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.05)
            if process.poll() is None:
                process.kill()
                thread.join(2)
                return 124, trim_output("\n".join(lines)) + f"\n[stopped: took longer than {timeout}s]"
        except KeyboardInterrupt:
            process.kill()
            thread.join(2)
            return 130, trim_output("\n".join(lines)) + "\n[stopped by user]"
        thread.join(2)
        return process.returncode, trim_output("\n".join(lines))

    def os_description(self) -> str:
        if self.uses_wsl:
            distro = self._wsl_capture(["bash", "-lc", ". /etc/os-release 2>/dev/null; echo $PRETTY_NAME"]).strip()
            return f"Linux ({distro or 'WSL'}) inside Windows via WSL; shell: bash"
        if self.backend in {"powershell", "cmd"}:
            shells = ", ".join(self.available_backends())
            return f"Windows {platform.release()}; shell: {self.label()} (available: {shells})"
        return f"{platform.system()} {platform.release()}; shell: {Path(self.posix_shell).name}"
