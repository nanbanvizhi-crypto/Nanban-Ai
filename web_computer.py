"""
"Computer" mode for the browser app (and the phone): the same terminal tools the
Nanban Terminal has, driven from the chat, plus a simple command runner.

The browser cannot pop up an "Allow?" question in the middle of a reply, so actions
only run while the "Allow actions" switch in the sidebar is on; every action is still
shown in the chat as it happens, and risky commands are always refused here.
"""

import re
import socket
import threading
import time
from pathlib import Path

import config
import terminal
from shell import ShellSession

shell = ShellSession(backend=config.TERMINAL_SHELL, start_dir=str(Path.home()))


class WebHost:
    """What TerminalTools needs from its host, for the web version."""

    def __init__(self):
        self.shell = shell
        self.os_info = shell.os_description()
        self.plan: list[dict] = []
        self.last_command: tuple[str, int] | None = None
        self.last_output = ""
        self.allow_actions = False
        self.auto_approve = False

    def approve(self, kind: str, title: str, body, dangerous: bool = False):
        if dangerous:
            return ("Refused: this command could delete data or change the system, and risky commands never "
                    "run from the browser. The user can run it themselves in the Nanban Terminal.")
        if self.allow_actions:
            return True
        return ("Not allowed yet: the user has to switch on 'Allow actions' in the sidebar before you can "
                "run commands or change files. Tell them that in one line and wait.")

    def show_plan(self) -> None:
        pass

    remote = None
    remote_name = ""

    def servers_text(self) -> str:
        import servers
        registry = servers.load()
        if not registry:
            return "Registered servers: none."
        return "Registered servers (use the `server` argument):\n" + "\n".join(
            f"- {n}: {e['user']}@{e['host']}:{e['port']}" + (f" ({e['notes']})" if e.get("notes") else "")
            for n, e in registry.items())

    def ask_password(self, name: str) -> str:
        return ""   # no prompt possible in the browser; use a key or a saved password


host = WebHost()


class WebComputerAgent(terminal.TerminalAgent):
    def __init__(self, user: str = ""):
        super().__init__(host)
        self.user = user


def plan_markdown() -> str:
    if not host.plan:
        return ""
    return "\n".join(f"- {'✅' if s['done'] else '⬜'} {s['text']}" for s in host.plan)


# ---------------------------------------------------------------- command runner for the Terminal tab

def run_command_stream(command: str, backend: str):
    """Generator: yields (output_so_far, cwd_label) while a command runs."""
    command = (command or "").strip()
    if not command:
        yield "", shell.display_cwd()
        return
    if backend and backend != shell.backend:
        shell.set_backend(backend)
    first, _, rest = command.partition(" ")
    if first.lower() == "cd" and "&&" not in rest and ";" not in rest:
        error = shell.change_dir(rest)
        host.last_command = (command, 1 if error else 0)
        yield (error or f"→ {shell.display_cwd()}"), shell.display_cwd()
        return
    if any(re.search(p, command, re.IGNORECASE) for p in terminal.DANGEROUS):
        yield ("⚠ This command can delete data or change the system, so it is not run from the browser. "
               "Run it in the Nanban Terminal on the laptop if you really want it."), shell.display_cwd()
        return
    lines: list[str] = []
    result: dict = {}

    def worker():
        code, output = shell.run_captured(command, timeout=config.COMMAND_TIMEOUT, on_line=lines.append)
        result["code"], result["output"] = code, output

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    shown = 0
    while thread.is_alive():
        if len(lines) != shown:
            shown = len(lines)
            yield "\n".join(lines), shell.display_cwd()
        time.sleep(0.15)
    thread.join()
    code = result.get("code", 1)
    output = "\n".join(lines) or result.get("output", "")
    host.last_command = (command, code)
    host.last_output = output
    yield output + f"\n\n[exit code {code}]", shell.display_cwd()


def lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"
