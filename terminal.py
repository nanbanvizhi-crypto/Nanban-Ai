"""
Nanban Terminal: an AI agent and a real terminal in one window.

    python terminal.py [folder]       (or start_terminal.bat, or type `nanban` in any folder)

✦ AI mode     - talk in any language; the AI can run commands and edit files (you approve each step)
$ Shell mode  - a normal terminal: git, python, vim, htop, apt, ssh... (bash via WSL, or PowerShell)
Ctrl+T switches mode · !command runs once in the shell · ?question asks the AI once · /help
"""

import difflib
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import ollama
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

import config
import servers
import tools
import vpn
from agent_core import Agent
from editor import edit_file as open_editor
from shell import IS_WINDOWS, ShellSession

console = Console(highlight=False)

IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".idea", ".vscode",
                "dist", "build", ".next", ".cache", ".mypy_cache", ".pytest_cache", "target"}

DANGEROUS = [
    r"\brm\s+-[a-zA-Z]*[rf][a-zA-Z]*\s", r"\bmkfs", r"\bdd\s+if=", r"\bformat\s+[a-zA-Z]:",
    r":\(\)\s*\{", r"\bshutdown\b", r"\breboot\b", r"\b(del|erase)\s+/[sq]", r"\b(rd|rmdir)\s+/s",
    r"Remove-Item\b.*-Recurse", r"\bchmod\s+-R\s+777\s+/", r">\s*/dev/sd", r"\bgit\s+push\s+.*--force",
    r"\bgit\s+reset\s+--hard", r"\bgit\s+clean\s+-[a-z]*f", r"\bdiskpart\b", r"\bStop-Computer\b",
]

SLASH_COMMANDS = {
    "/help": "show help",
    "/ai": "switch to AI mode",
    "/shell": "switch to shell mode",
    "/linux": "use Linux bash (WSL)",
    "/powershell": "use Windows PowerShell",
    "/cmd": "use Command Prompt (cmd.exe)",
    "/vpn": "VPN status · /vpn on · /vpn off · /vpn ip",
    "/server": "servers: add · list · use · local · status · ssh · push · pull · remove",
    "/plan": "show the AI's current step plan",
    "/auto": "toggle auto-approve for AI actions",
    "/tree": "show the folder tree",
    "/view": "show a file with syntax highlighting",
    "/edit": "open a file in the built-in editor",
    "/new": "start a new AI conversation",
    "/model": "show or change the AI model",
    "/memory": "show what the AI remembers about you",
    "/clear": "clear the screen",
    "/exit": "quit",
}

HELP_TEXT = f"""
**Modes** (press **Ctrl+T** to switch)
- **✦ AI**: type normally in Tamil / English / Tanglish. {config.AGENT_NAME} can run commands, read and edit files. You approve every command and change.
- **$ Shell**: a real terminal. Interactive programs like `vim`, `nano`, `htop`, `python`, `ssh` work.

**Shortcuts**
- `!git status`: run one shell command while in AI mode
- `?why did that fail`: ask the AI once while in shell mode (it sees your last command and its output)
- `cmd: dir`, `ps: Get-Process`, `sh: ls -la`: run one command in a specific shell, from any mode
- When a command you type fails, the AI explains the error and suggests a fix automatically (`AUTO_EXPLAIN_ERRORS` in config.py)
- **Tab**: complete commands and file names · **↑/↓**: history · **Ctrl+C**: stop · **Ctrl+D**: quit

**Servers (SSH)**
- `/server add vps root@1.2.3.4` (or `user@host:port`, add `--key C:\\path\\id_ed25519` for key login)
- `/server use vps`: now the shell AND the AI work on that server · `/server local`: back to this laptop
- `/server status`: health of all servers · `/server ssh vps`: full interactive SSH session
- `/server push app.py /var/www/` · `/server pull /var/log/nginx/error.log .`
- In AI mode you can also just say: "vps-la nginx restart pannu" - the AI picks the server by name

**Commands**
""" + "\n".join(f"- `{cmd}`: {desc}" for cmd, desc in SLASH_COMMANDS.items())

TERMINAL_PROMPT = """You are {name}, an AI coding agent built into the user's terminal. You run locally on their laptop.
Today is {today}. System: {os_info}. Current directory: {cwd}.{last_command}
Language: reply in the language the user writes in (English, Tamil script, or Tanglish).

Shells available on this computer: {shells}. The default shell is {default_shell}.
{servers_text}
You can act on the computer with tools: run_command, read_file, write_file, edit_file, list_directory, search_files, server_status, transfer_file, set_plan, complete_step, web_search, fetch_webpage.
Every file/command tool has a `server` argument: leave it empty for the current target ({target}); give a server name to act on that server instead (its shell is always Linux bash, so use Linux commands there). For service work use systemctl/journalctl/docker/nginx/pm2 as appropriate; check logs before guessing.
How to work:
- Questions you can answer from knowledge (concepts, explanations, advice): just answer, no tools.
- Tasks on the computer: look first (list_directory, read_file, search_files), then act, then verify (run the code or tests) and fix any errors you see.
- Pick the right shell for each command with run_command's `shell` argument: Linux/Unix commands (ls, grep, apt, chmod, bash scripts, pip in Linux) -> "linux"; Windows admin, services, registry, Get-*/Set-* cmdlets, winget -> "powershell"; classic Windows commands (dir, ipconfig, netstat, tasklist, old .bat files) -> "cmd". Leave it empty to use the default shell. Never send PowerShell syntax to bash or vice versa.
- For a task with 3 or more steps, call set_plan first with the steps, then complete_step after each one, so the user can follow along.
- The user may ask about a command they just typed: you will be given that command and its output.
- To change an existing file, use edit_file with a small, exact old_text copied from the file. Use write_file for new files.
- Commands run without keyboard input and stop after {timeout} seconds. Use non-interactive flags (-y, --yes). Don't start servers, editors or programs that wait for input: tell the user to run those themselves by typing ! before the command.
- If a command needs sudo or a password, ask the user to run it with ! in front.
- The user approves every command and file change. If they decline, do what they say instead.
- Never delete files or run destructive commands unless the user clearly asked for it.
- Be brief: say what you did and the result. Use markdown code blocks for code the user should read."""


# ---------------------------------------------------------------- AI tools that act on the computer

class TerminalTools:
    """Tools bound to the live shell session. Each change asks the user first."""

    def __init__(self, app: "NanbanTerminal"):
        self.app = app

    @property
    def shell(self) -> ShellSession:
        return self.app.shell

    def remote_for(self, server: str):
        """RemoteHost for `server`, or for the current target; None means this laptop."""
        name = (server or "").strip() or getattr(self.app, "remote_name", "")
        if not name or name.lower() in {"local", "laptop", "this"}:
            return None
        return servers.connect(name, getattr(self.app, "ask_password", None))

    def run_command(self, command: str, shell: str = "", timeout_seconds: int = 0, server: str = "") -> str:
        """Run a command in the current directory and return its output and exit code.

        Args:
            command: The command to run, e.g. 'python app.py', 'git status', 'dir', 'systemctl status nginx'
            shell: Which shell runs it: 'linux' (bash), 'powershell', 'cmd', or empty for the default shell
            timeout_seconds: Optional time limit in seconds (default 120)
            server: Name of a registered server to run it on (empty = current target)
        """
        timeout = timeout_seconds if timeout_seconds and timeout_seconds > 0 else config.COMMAND_TIMEOUT
        try:
            remote = self.remote_for(server)
        except Exception as e:
            return f"Error: {e}"
        if remote is not None:
            dangerous = any(re.search(p, command, re.IGNORECASE) for p in DANGEROUS)
            body = Syntax(command, "bash", theme="monokai", word_wrap=True, background_color="default")
            decision = self.app.approve("run_command", f"▶ Run on {remote.name} ({remote.user}@{remote.host}) · {remote.display_cwd()}",
                                        body, dangerous)
            if decision is not True:
                return decision
            result = remote.run(command, timeout=min(timeout, 1800),
                                on_line=lambda line: console.print(Text("  │ " + line, style="grey58")))
            console.print(Text(f"  └─ exit code {result.code} · {result.seconds:.1f}s", style="green" if result.code == 0 else "red"))
            return f"[on server {remote.name}] exit code: {result.code}\n{result.output or '(no output)'}"
        shell = {"bash": "linux", "wsl": "linux", "windows": "powershell", "ps": "powershell"}.get(shell, shell or "")
        if shell and shell not in self.shell.available_backends():
            return (f"The '{shell}' shell is not available here. Available: "
                    f"{', '.join(self.shell.available_backends())}. Rewrite the command for one of those.")
        backend = shell or self.shell.backend
        dangerous = any(re.search(p, command, re.IGNORECASE) for p in DANGEROUS)
        body = Syntax(command, {"linux": "bash", "powershell": "powershell", "cmd": "bat"}[backend],
                      theme="monokai", word_wrap=True, background_color="default")
        label = {"linux": "bash", "powershell": "PowerShell", "cmd": "CMD"}[backend]
        decision = self.app.approve("run_command", f"▶ Run in {label} · {self.shell.display_cwd()}", body, dangerous)
        if decision is not True:
            return decision
        code, output = self.shell.run_captured(
            command, timeout=min(timeout, 1800), backend=backend,
            on_line=lambda line: console.print(Text("  │ " + line, style="grey58")),
        )
        style = "green" if code == 0 else "red"
        console.print(Text(f"  └─ exit code {code}", style=style))
        return f"exit code: {code}\n{output or '(no output)'}"

    def _read_any(self, path: str, server: str) -> tuple[str | None, object]:
        """(text or None if missing, remote) for local or remote files."""
        remote = self.remote_for(server)
        if remote is not None:
            return (remote.read_text(path) if remote.exists(path) else None), remote
        file = self.shell.resolve_path(path)
        return (file.read_text(encoding="utf-8", errors="replace") if file.exists() else None), None

    def _write_any(self, path: str, content: str, remote) -> None:
        if remote is not None:
            remote.write_text(path, content)
            return
        file = self.shell.resolve_path(path)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")

    def read_file(self, path: str, start_line: int = 1, end_line: int = 0, server: str = "") -> str:
        """Read a text file and return its lines with line numbers.

        Args:
            path: File path, relative to the current directory or absolute
            start_line: First line to read (starts at 1)
            end_line: Last line to read (0 means up to 400 lines from start_line)
            server: Name of a registered server to read from (empty = current target)
        """
        try:
            text, _ = self._read_any(path, server)
        except Exception as e:
            return f"Error: {e}"
        if text is None:
            return f"Error: {path} does not exist."
        if "\x00" in text[:2048]:
            return f"{path} is a binary file."
        lines = text.splitlines()
        start = max(1, start_line)
        end = min(len(lines), end_line if end_line and end_line >= start else start + 399)
        numbered = "\n".join(f"{n:>5}| {lines[n - 1]}" for n in range(start, end + 1))
        more = f"\n[file has {len(lines)} lines; showing {start}-{end}]" if end < len(lines) or start > 1 else ""
        return (numbered or "(empty file)") + more

    def write_file(self, path: str, content: str, server: str = "") -> str:
        """Create a new file or completely replace a file's content.

        Args:
            path: File path, relative to the current directory or absolute
            content: The complete new content of the file
            server: Name of a registered server to write on (empty = current target)
        """
        try:
            old, remote = self._read_any(path, server)
        except Exception as e:
            return f"Error: {e}"
        where = f" on {remote.name}" if remote is not None else ""
        if old is None:
            preview = "\n".join(content.splitlines()[:80]) + ("\n…" if content.count("\n") > 80 else "")
            body = Syntax(preview, Syntax.guess_lexer(Path(path).name, preview), theme="monokai",
                          line_numbers=True, background_color="default")
            title = f"✚ Create {path}{where}  ({len(content.splitlines())} lines)"
        else:
            body = _diff_view(old, content, path)
            title = f"✎ Overwrite {path}{where}"
        decision = self.app.approve("write_file", title, body)
        if decision is not True:
            return decision
        self._write_any(path, content, remote)
        console.print(Text(f"  └─ saved {path}{where}", style="green"))
        return f"Saved {path}{where} ({len(content.splitlines())} lines)."

    def edit_file(self, path: str, old_text: str, new_text: str, server: str = "") -> str:
        """Replace one exact piece of text in an existing file (old_text must appear exactly once).

        Args:
            path: File path, relative to the current directory or absolute
            old_text: The exact text to replace, copied from the file including indentation
            new_text: The text to put in its place
            server: Name of a registered server the file is on (empty = current target)
        """
        try:
            old, remote = self._read_any(path, server)
        except Exception as e:
            return f"Error: {e}"
        where = f" on {remote.name}" if remote is not None else ""
        if old is None:
            return f"Error: {path} does not exist. Use write_file to create it."
        count = old.count(old_text) if old_text else 0
        if count == 0:
            return "Error: old_text was not found in the file. Read the file again and copy the text exactly."
        if count > 1:
            return f"Error: old_text appears {count} times. Include more surrounding lines so it is unique."
        new = old.replace(old_text, new_text, 1)
        decision = self.app.approve("edit_file", f"✎ Edit {path}{where}", _diff_view(old, new, path))
        if decision is not True:
            return decision
        self._write_any(path, new, remote)
        console.print(Text(f"  └─ saved {path}{where}", style="green"))
        return f"Edited {path}{where}."

    def server_status(self, server: str = "") -> str:
        """Health check of your servers: uptime, load, memory, disk, top processes.

        Args:
            server: One server name, or empty for all registered servers
        """
        if not servers.names():
            return "No servers registered. Add one with: /server add <name> user@host"
        try:
            rows = [servers.connect(server, getattr(self.app, "ask_password", None)).status()] if server \
                else servers.status_all(getattr(self.app, "ask_password", None))
        except Exception as e:
            return f"Error: {e}"
        return "\n".join(_status_line(r) for r in rows)

    def transfer_file(self, direction: str, local_path: str, remote_path: str, server: str = "") -> str:
        """Copy a file between this laptop and a server (SFTP).

        Args:
            direction: 'push' (laptop -> server) or 'pull' (server -> laptop)
            local_path: Path on this laptop
            remote_path: Path on the server (a folder or a file path)
            server: Name of the server (empty = current target)
        """
        try:
            remote = self.remote_for(server)
        except Exception as e:
            return f"Error: {e}"
        if remote is None:
            return "Error: no server given and the current target is this laptop."
        local = self.shell.resolve_path(local_path)
        arrow = f"{local} → {remote.name}:{remote_path}" if direction == "push" else f"{remote.name}:{remote_path} → {local}"
        decision = self.app.approve("transfer_file", f"⇅ {direction} {arrow}", Text(arrow))
        if decision is not True:
            return decision
        try:
            if direction == "push":
                if not local.is_file():
                    return f"Error: {local_path} is not a file on this laptop."
                target = remote.upload(local, remote_path)
                return f"Uploaded {local.name} to {remote.name}:{target}"
            saved = remote.download(remote_path, local)
            return f"Downloaded {remote.name}:{remote_path} to {saved}"
        except Exception as e:
            return f"Error: {e}"

    def set_plan(self, steps: str) -> str:
        """Show the user a checklist of the steps you are about to do (for tasks with several steps).

        Args:
            steps: The steps, one per line, in order
        """
        items = [s.strip(" -*0123456789.)\t") for s in steps.splitlines() if s.strip()]
        if not items:
            return "Error: give at least one step."
        self.app.plan = [{"text": s, "done": False} for s in items]
        self.app.show_plan()
        return f"Plan set with {len(items)} steps. Call complete_step(n) after finishing each step."

    def complete_step(self, step_number: int) -> str:
        """Mark a step of the plan as finished.

        Args:
            step_number: The step number, starting at 1
        """
        plan = self.app.plan
        if not plan or not 1 <= int(step_number) <= len(plan):
            return "Error: no such step. Call set_plan first."
        plan[int(step_number) - 1]["done"] = True
        self.app.show_plan()
        left = sum(1 for s in plan if not s["done"])
        return f"Step {step_number} done. {left} step(s) left." if left else "All steps done."

    def list_directory(self, path: str = ".", server: str = "") -> str:
        """List files and folders (two levels deep), skipping folders like .git and node_modules.

        Args:
            path: Folder to list, relative to the current directory or absolute
            server: Name of a registered server to list on (empty = current target)
        """
        try:
            remote = self.remote_for(server)
        except Exception as e:
            return f"Error: {e}"
        if remote is not None:
            skip = " ".join(f"-name {d} -prune -o" for d in sorted(IGNORED_DIRS))
            result = remote.run(f"cd {servers._shell_quote(remote.resolve(path))} 2>/dev/null && "
                                f"find . -mindepth 1 -maxdepth 2 \\( {skip} -print \\) 2>/dev/null | sort | head -300",
                                timeout=30)
            if result.code != 0 and not result.output:
                return f"Error: {path} is not a folder on {remote.name}."
            return "\n".join(l[2:] for l in result.output.splitlines() if l.startswith("./")) or "(empty folder)"
        root = self.shell.resolve_path(path)
        if not root.is_dir():
            return f"Error: {path} is not a folder."
        lines, count = [], 0
        for entry in _sorted_entries(root):
            lines.append(entry.name + ("/" if entry.is_dir() else ""))
            count += 1
            if entry.is_dir() and entry.name not in IGNORED_DIRS:
                for child in _sorted_entries(entry)[:40]:
                    lines.append("    " + child.name + ("/" if child.is_dir() else ""))
                    count += 1
            if count > 300:
                lines.append("… (more not shown)")
                break
        return "\n".join(lines) or "(empty folder)"

    def search_files(self, pattern: str, path: str = ".", server: str = "") -> str:
        """Search text files for a word or regular expression and return matching lines.

        Args:
            pattern: Text or regular expression to find, e.g. 'def main' or 'TODO'
            path: Folder to search in, relative to the current directory or absolute
            server: Name of a registered server to search on (empty = current target)
        """
        try:
            remote = self.remote_for(server)
        except Exception as e:
            return f"Error: {e}"
        if remote is not None:
            excludes = " ".join(f"--exclude-dir={d}" for d in sorted(IGNORED_DIRS))
            result = remote.run(f"grep -rniI -E {excludes} -m 20 -e {servers._shell_quote(pattern)} "
                                f"{servers._shell_quote(remote.resolve(path))} 2>/dev/null | head -60", timeout=60)
            return result.output or "No matches."
        root = self.shell.resolve_path(path)
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            regex = re.compile(re.escape(pattern), re.IGNORECASE)
        matches = []
        for folder, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for name in files:
                file = Path(folder) / name
                try:
                    if file.stat().st_size > 1_000_000:
                        continue
                    data = file.read_bytes()
                    if b"\x00" in data[:2048]:
                        continue
                    for n, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
                        if regex.search(line):
                            matches.append(f"{file.relative_to(root)}:{n}: {line.strip()[:200]}")
                            if len(matches) >= 60:
                                return "\n".join(matches) + "\n… (first 60 matches)"
                except OSError:
                    continue
        return "\n".join(matches) or "No matches."


def _status_line(r: dict) -> str:
    if not r.get("ok"):
        return f"✖ {r['name']}: {r.get('error', 'unreachable')}"
    return (f"✔ {r['name']} ({r.get('host', '?')}, {r.get('os', '')}): {r.get('up', '')} · load {r.get('load', '?')} · "
            f"mem {r.get('mem', '?')} · disk {r.get('disk', '?')} · top: {r.get('top', '')}")


def _sorted_entries(folder: Path) -> list[Path]:
    try:
        return sorted(folder.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        return []


def _diff_view(old: str, new: str, name: str):
    diff = "".join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                        fromfile=f"a/{name}", tofile=f"b/{name}", n=2))
    lines = diff.splitlines()
    if len(lines) > 120:
        diff = "\n".join(lines[:120]) + f"\n… ({len(lines) - 120} more diff lines)"
    return Syntax(diff or "(no changes)", "diff", theme="monokai", background_color="default")


# ---------------------------------------------------------------- the agent

class TerminalAgent(Agent):
    def __init__(self, app: "NanbanTerminal"):
        super().__init__()
        self.app = app
        self.toolbox = TerminalTools(app)

    def active_tools(self) -> list:
        t = self.toolbox
        return [t.run_command, t.read_file, t.write_file, t.edit_file, t.list_directory, t.search_files,
                t.server_status, t.transfer_file, t.set_plan, t.complete_step,
                tools.web_search, tools.fetch_webpage, tools.for_user(tools.remember, self.user)]

    def system_prompt(self) -> str:
        last = self.app.last_command
        last_text = ""
        if last:
            last_text = f"\nThe user's last shell command was `{last[0]}` (exit code {last[1]})."
            if self.app.last_output:
                tail = "\n".join(self.app.last_output.splitlines()[-config.AUTO_EXPLAIN_MAX_LINES:])
                last_text += f" Its output ended with:\n```\n{tail}\n```"
        prompt = TERMINAL_PROMPT.format(
            name=config.AGENT_NAME,
            today=datetime.now().strftime("%A, %d %B %Y"),
            os_info=self.app.os_info,
            cwd=self.app.shell.display_cwd(),
            timeout=config.COMMAND_TIMEOUT,
            shells=", ".join(self.app.shell.available_backends()),
            default_shell=self.app.shell.backend,
            servers_text=self.app.servers_text(),
            target=(f"server '{self.app.remote_name}'" if self.app.remote_name else "this laptop"),
            last_command=last_text,
        )
        facts = tools.load_memory(self.user)
        if facts:
            prompt += "\n\nWhat you know about the user:\n" + "\n".join(f"- {f}" for f in facts)
        return prompt

    def repair_history(self) -> None:
        """After Ctrl+C, drop a half-finished tool exchange so the next question starts clean."""
        while self.history and self.history[-1]["role"] in {"tool", "assistant"} and (
                self.history[-1]["role"] == "tool" or self.history[-1].get("tool_calls")):
            self.history.pop()


# ---------------------------------------------------------------- completion

class NanbanCompleter(Completer):
    def __init__(self, app: "NanbanTerminal"):
        self.app = app
        self.paths = PathCompleter(get_paths=lambda: [str(app.shell.cwd)], expanduser=True)

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("/") and " " not in text:
            for cmd, desc in SLASH_COMMANDS.items():
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text), display_meta=desc)
            return
        if text.startswith("/server "):
            parts = text.split(" ")
            word = parts[-1]
            options = (["add", "list", "use", "local", "status", "ssh", "push", "pull", "remove", "test"]
                       if len(parts) == 2 else servers.names())
            for option in options:
                if option.startswith(word):
                    yield Completion(option, start_position=-len(word))
            return
        word = text.split(" ")[-1].lstrip("!?") if text else ""
        if word:
            yield from self.paths.get_completions(Document(word, len(word)), complete_event)


# ---------------------------------------------------------------- the app

class NanbanTerminal:
    def __init__(self, start_dir: str | None = None):
        console.print(Text("Starting Nanban terminal…", style="grey50"))
        self.shell = ShellSession(backend=config.TERMINAL_SHELL, start_dir=start_dir)
        self.os_info = self.shell.os_description()
        self.mode = config.TERMINAL_START_MODE if config.TERMINAL_START_MODE in {"ai", "shell"} else "ai"
        self.auto_approve = False
        self.last_command: tuple[str, int] | None = None
        self.last_output = ""
        self.plan: list[dict] = []
        self.explaining = False
        self.remote = None          # servers.RemoteHost when /server use <name> is active
        self.remote_name = ""
        self.agent = TerminalAgent(self)
        self.running = True

        bindings = KeyBindings()

        @bindings.add("c-t")
        def _toggle(event):
            self.mode = "shell" if self.mode == "ai" else "ai"
            event.app.invalidate()

        self.session = PromptSession(
            message=self.prompt_message,
            history=FileHistory(str(config.DATA_DIR / "terminal_history")),
            auto_suggest=AutoSuggestFromHistory(),
            completer=NanbanCompleter(self),
            complete_while_typing=False,
            key_bindings=bindings,
            bottom_toolbar=self.toolbar,
            style=Style.from_dict({
                "ai": "bg:#6d5dfc #ffffff bold",
                "shell": "bg:#1f9d55 #ffffff bold",
                "path": "#5fafff bold",
                "remote": "bg:#d9731a #ffffff bold",
                "arrow": "#d7af00 bold",
                "bottom-toolbar": "bg:#1c1c28 #a8a8c0",
                "bottom-toolbar.text": "",
            }),
        )

    # ------------------------------------------------------------ prompt bits

    def prompt_message(self):
        badge = [("class:ai", " ✦ AI ")] if self.mode == "ai" else [("class:shell", " $ SHELL ")]
        if self.remote is not None:
            return badge + [("", " "), ("class:remote", f" ⇅ {self.remote_name} "), ("", " "),
                            ("class:path", self.remote.display_cwd()), ("class:arrow", " ❯ ")]
        return badge + [("", " "), ("class:path", self.shell.display_cwd()), ("class:arrow", " ❯ ")]

    def ask_password(self, name: str) -> str:
        try:
            return console.input(f"  🔑 Password for server '{name}' (kept only for this session): ", password=True)
        except (KeyboardInterrupt, EOFError):
            return ""

    def servers_text(self) -> str:
        registry = servers.load()
        if not registry:
            return "Registered servers: none (the user can add one with /server add <name> user@host)."
        lines = [f"- {name}: {e['user']}@{e['host']}:{e['port']}" + (f" ({e['notes']})" if e.get("notes") else "")
                 for name, e in registry.items()]
        return "Registered servers (reach them with the `server` argument):\n" + "\n".join(lines)

    def toolbar(self):
        safety = "⚡ auto-approve ON" if self.auto_approve else "🔒 asks first"
        shells = "/".join({"linux": "bash", "powershell": "ps", "cmd": "cmd"}[b] for b in self.shell.available_backends())
        where = (f"⇅ {self.remote_name} ({self.remote.user}@{self.remote.host})" if self.remote is not None
                 else f"{self.shell.label()} [{shells}]")
        count = len(servers.names())
        return (f" {where}  ·  🧠 {config.MODEL}  ·  {safety}  ·  {vpn.badge()}  ·  🖧 {count} server(s)"
                f"  ·  Ctrl+T mode  ·  /help ")

    def show_plan(self) -> None:
        if not self.plan:
            console.print(Text("No plan yet. The AI makes one for multi-step tasks.", style="grey50"))
            return
        lines = Text()
        for i, step in enumerate(self.plan, 1):
            lines.append(f"  {'✔' if step['done'] else '○'} {i}. {step['text']}\n",
                         style="green" if step["done"] else "white")
        done = sum(1 for s in self.plan if s["done"])
        console.print(Panel(lines, title=f"📋 Plan · {done}/{len(self.plan)} done", title_align="left",
                            border_style="#6d5dfc", padding=(0, 1)))

    # ------------------------------------------------------------ approvals

    def approve(self, kind: str, title: str, body, dangerous: bool = False):
        """Show what the AI wants to do. Returns True, or a message for the AI explaining the refusal."""
        border = "red" if dangerous else ("yellow" if kind == "run_command" else "cyan")
        parts = [body]
        if dangerous:
            parts.append(Text("\n⚠  This command can delete data or change your system.", style="bold red"))
        console.print(Panel(Group(*parts), title=title, title_align="left", border_style=border, padding=(0, 1)))

        if self.auto_approve and not dangerous:
            return True
        try:
            answer = console.input("[bold]  Allow?[/] [green]y[/]es · [red]n[/]o · [cyan]a[/]lways"
                                   + ("" if dangerous else " (auto-approve)") + " › ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            answer = "n"
        if answer in {"", "y", "yes", "s", "sari", "ok"}:
            return True
        if answer in {"a", "always"} and not dangerous:
            self.auto_approve = True
            console.print(Text("  Auto-approve is ON for this session. Type /auto to switch it off.", style="yellow"))
            return True
        try:
            reason = console.input("  [grey58]Tell the AI what to do instead (optional) ›[/] ").strip()
        except (KeyboardInterrupt, EOFError):
            reason = ""
        return "The user declined this action." + (f" The user says: {reason}" if reason else " Ask them what to do.")

    # ------------------------------------------------------------ AI

    def ask_ai(self, text: str) -> None:
        live, buffer = None, ""
        quiet_tools = {"run_command", "write_file", "edit_file"}   # these show their own approval panel
        try:
            for event in self.agent.stream(text):
                if event.kind == "text":
                    if live is None:
                        buffer = ""
                        live = Live(Markdown(""), console=console, refresh_per_second=12,
                                    vertical_overflow="visible")
                        live.start()
                    buffer += event.data
                    live.update(Markdown(buffer))
                    continue
                if live is not None:
                    live.stop()
                    live = None
                if event.kind == "tool_start" and event.tool not in quiet_tools:
                    label = tools.TOOL_LABELS.get(event.tool, "")
                    detail = next(iter(event.data.values()), "") if event.data else ""
                    names = {"read_file": "📄 Reading", "list_directory": "📁 Listing", "search_files": "🔎 Searching"}
                    console.print(Text(f"  {names.get(event.tool, label or event.tool)} {str(detail)[:80]}",
                                       style="grey58"))
                elif event.kind == "tool_end" and str(event.data).startswith("Error"):
                    console.print(Text(f"  └─ {str(event.data)[:200]}", style="red"))
                elif event.kind == "error":
                    console.print(Text(f"⚠  {event.data}", style="bold red"))
        except KeyboardInterrupt:
            if live is not None:
                live.stop()
                live = None
            self.agent.repair_history()
            console.print(Text("  (stopped)", style="yellow"))
        finally:
            if live is not None:
                live.stop()
        console.print()

    # ------------------------------------------------------------ shell

    SHELL_PREFIXES = {"cmd:": "cmd", "ps:": "powershell", "powershell:": "powershell", "sh:": "linux",
                      "bash:": "linux", "linux:": "linux", "wsl:": "linux"}

    def run_shell(self, command: str) -> None:
        if not command:
            return
        backend = ""
        head = command.split(" ")[0].lower()
        if head in self.SHELL_PREFIXES:
            backend = self.SHELL_PREFIXES[head]
            command = command[len(head):].strip()
            if backend not in self.shell.available_backends():
                console.print(Text(f"{backend} is not available here. Available: "
                                   f"{', '.join(self.shell.available_backends())}", style="red"))
                return
            if not command:
                console.print(Text(self.shell.set_backend(backend), style="cyan"))
                self.os_info = self.shell.os_description()
                return
        first, _, rest = command.partition(" ")
        lower = first.lower()
        if self.remote is not None and not backend:
            self.run_remote_shell(command)
            return
        if lower == "cd" and "&&" not in rest and ";" not in rest:
            error = self.shell.change_dir(rest)
            if error:
                console.print(Text(error, style="red"))
            self.last_command = (command, 1 if error else 0)
            return
        if lower in {"clear", "cls"} and not rest:
            console.clear()
            return
        if lower in {"exit", "logout"} and not rest:
            self.running = False
            return
        code, output = self.shell.run_user_command(command, backend=backend)
        self.last_command = (command, code)
        self.last_output = output
        if code not in (0, None):
            console.print(Text(f"exit code {code}", style="grey50"))
            if config.AUTO_EXPLAIN_ERRORS and code not in (130,) and not self.explaining:
                self.explain_last_failure()

    def run_remote_shell(self, command: str) -> None:
        """A command typed in shell mode while /server use is active."""
        remote = self.remote
        first, _, rest = command.partition(" ")
        if first.lower() == "cd" and "&&" not in rest and ";" not in rest:
            error = remote.change_dir(rest)
            if error:
                console.print(Text(error, style="red"))
            self.last_command, self.last_output = (command, 1 if error else 0), error
            return
        if first.lower() in {"exit", "logout"} and not rest:
            self.leave_server()
            return
        if self.shell._is_interactive(command):
            console.print(Text(f"  (interactive program → opening a real SSH session for it)", style="grey50"))
            self.ssh_session(command)
            return
        try:
            result = remote.run(command, timeout=config.COMMAND_TIMEOUT * 5,
                                on_line=lambda line: console.print(Text(line)))
        except Exception as e:
            console.print(Text(f"Connection problem: {e}. Reconnecting…", style="red"))
            servers.disconnect(self.remote_name)
            try:
                self.remote = servers.connect(self.remote_name, self.ask_password)
            except Exception as e2:
                console.print(Text(str(e2), style="red"))
                self.leave_server()
            return
        self.last_command, self.last_output = (command, result.code), result.output
        if result.code != 0:
            console.print(Text(f"exit code {result.code}", style="grey50"))
            if config.AUTO_EXPLAIN_ERRORS and not self.explaining:
                self.explain_last_failure()

    def ssh_session(self, command: str = "") -> None:
        """Open the system ssh client attached to the terminal (for vim, htop, sudo prompts…)."""
        entry = servers.get(self.remote_name) if self.remote_name else None
        if not entry:
            console.print("Use /server use <name> first, or /server ssh <name>.")
            return
        args = ["ssh", "-p", str(entry["port"]), "-t", f"{entry['user']}@{entry['host']}"]
        if entry.get("key"):
            args[1:1] = ["-i", entry["key"]]
        if self.remote is not None and command:
            args.append(f"cd {servers._shell_quote(self.remote.cwd)} && {command}")
        elif self.remote is not None:
            args.append(f"cd {servers._shell_quote(self.remote.cwd)} && exec $SHELL -l")
        try:
            import subprocess
            subprocess.run(args)
        except FileNotFoundError:
            console.print(Text("The 'ssh' command is missing. On Windows: Settings → Apps → Optional features → OpenSSH Client.",
                               style="red"))

    def use_server(self, name: str) -> None:
        try:
            console.print(Text(f"Connecting to {name}…", style="grey58"))
            self.remote = servers.connect(name, self.ask_password)
            self.remote_name = name
            self.os_info = f"{self.remote.os_name} on server '{name}' ({self.remote.user}@{self.remote.host}); shell: bash"
            console.print(Text(f"✔ Connected. Shell and AI now work on '{name}'. Type /server local to come back.", style="green"))
        except Exception as e:
            console.print(Text(str(e), style="red"))

    def leave_server(self) -> None:
        self.remote, self.remote_name = None, ""
        self.os_info = self.shell.os_description()
        console.print(Text("Back on this laptop.", style="cyan"))

    def server_command(self, arg: str) -> None:
        action, _, rest = arg.strip().partition(" ")
        action, rest = action.lower(), rest.strip()
        parts = rest.split()
        if action in {"", "list", "ls"}:
            registry = servers.load()
            if not registry:
                console.print("No servers yet.  /server add <name> user@host[:port] [--key path] [--password xxx --save-password]")
                return
            for name, e in registry.items():
                mark = "⇅ " if name == self.remote_name else "  "
                console.print(f"{mark}[bold]{name}[/]  {e['user']}@{e['host']}:{e['port']}"
                              + ("  🔑key" if e.get("key") else "") + ("  🔒saved pw" if e.get("password") else "")
                              + (f"  · {e['notes']}" if e.get("notes") else ""))
        elif action == "add":
            if len(parts) < 2:
                console.print("Usage: /server add <name> user@host[:port] [--key C:\\path\\key] [--password xxx] [--save-password] [--notes text]")
                return
            name, target, key, password, save_pw, notes = parts[0], parts[1], "", "", False, ""
            i = 2
            while i < len(parts):
                flag = parts[i]
                if flag == "--key" and i + 1 < len(parts):
                    key, i = parts[i + 1], i + 2
                elif flag == "--password" and i + 1 < len(parts):
                    password, i = parts[i + 1], i + 2
                elif flag == "--save-password":
                    save_pw, i = True, i + 1
                elif flag == "--notes":
                    notes, i = " ".join(parts[i + 1:]), len(parts)
                else:
                    i += 1
            console.print(Text(servers.add(name, target, key, password, save_pw, notes), style="cyan"))
            if save_pw:
                console.print(Text("  Password saved in data/servers.json (plain text). Prefer SSH keys when you can.", style="yellow"))
            self.server_command(f"test {name}")
        elif action in {"remove", "rm", "delete"}:
            if self.remote_name == rest:
                self.leave_server()
            console.print(Text(servers.remove(rest), style="cyan"))
        elif action == "use":
            if rest in servers.names():
                self.use_server(rest)
            else:
                console.print(Text(f"No server '{rest}'. Known: {', '.join(servers.names()) or 'none'}", style="red"))
        elif action in {"local", "laptop", "off"}:
            self.leave_server()
        elif action == "test":
            name = rest or self.remote_name
            try:
                host = servers.connect(name, self.ask_password)
                console.print(Text(f"✔ {name}: connected ({host.os_name}, home {host.home})", style="green"))
            except Exception as e:
                console.print(Text(f"✖ {e}", style="red"))
        elif action == "status":
            console.print(Text("Checking servers…", style="grey58"))
            rows = [servers.connect(rest, self.ask_password).status()] if rest else servers.status_all(self.ask_password)
            table = Table(title="🖧 Servers", title_justify="left", border_style="#6d5dfc", show_lines=False)
            for col in ("Server", "Host", "OS", "Uptime", "Load", "Memory", "Disk", "Top CPU"):
                table.add_column(col, overflow="fold")
            for r in rows:
                if r.get("ok"):
                    table.add_row(f"[green]✔ {r['name']}[/]", r.get("host", ""), r.get("os", ""), r.get("up", ""),
                                  r.get("load", ""), r.get("mem", ""), r.get("disk", ""), r.get("top", ""))
                else:
                    table.add_row(f"[red]✖ {r['name']}[/]", f"[red]{r.get('error', 'unreachable')}[/]", "", "", "", "", "", "")
            console.print(table)
        elif action == "ssh":
            if rest and rest != self.remote_name:
                self.use_server(rest)
            self.ssh_session()
        elif action in {"push", "pull"}:
            if len(parts) < 2:
                console.print(f"Usage: /server {action} <local> <remote>  (on the current server)" if action == "push"
                              else f"Usage: /server pull <remote> <local>")
                return
            if self.remote is None:
                console.print("Pick a server first: /server use <name>")
                return
            try:
                if action == "push":
                    target = self.remote.upload(self.shell.resolve_path(parts[0]), parts[1])
                    console.print(Text(f"✔ uploaded → {self.remote_name}:{target}", style="green"))
                else:
                    saved = self.remote.download(parts[0], self.shell.resolve_path(parts[1]))
                    console.print(Text(f"✔ downloaded → {saved}", style="green"))
            except Exception as e:
                console.print(Text(f"✖ {e}", style="red"))
        else:
            console.print("Commands: /server add · list · use · local · test · status · ssh · push · pull · remove")

    def explain_last_failure(self) -> None:
        """Ask the AI, briefly, why the user's command failed and how to fix it."""
        self.explaining = True
        import llm
        if not llm.ping()[0]:
            self.explaining = False
            return
        console.print(Text("  ✦ Nanban:", style="bold #8f83ff"))
        try:
            self.ask_ai("The command I just typed failed. In 2-4 lines: why, and the exact fixed command. "
                        "Don't run anything.")
        finally:
            self.explaining = False

    # ------------------------------------------------------------ slash commands

    def slash(self, line: str) -> None:
        command, _, arg = line.partition(" ")
        arg = arg.strip()
        command = command.lower()

        if command in {"/exit", "/quit"}:
            self.running = False
        elif command == "/help":
            console.print(Markdown(HELP_TEXT))
        elif command == "/ai":
            self.mode = "ai"
        elif command == "/shell":
            self.mode = "shell"
        elif command in {"/linux", "/windows", "/powershell", "/cmd"}:
            message = self.shell.set_backend(command[1:])
            self.os_info = self.shell.os_description()
            console.print(Text(message, style="cyan"))
        elif command == "/plan":
            self.show_plan()
        elif command == "/vpn":
            self.vpn_command(arg)
        elif command == "/server":
            self.server_command(arg)
        elif command == "/auto":
            self.auto_approve = not self.auto_approve
            console.print(Text("Auto-approve ON: AI actions run without asking (risky commands still ask)."
                               if self.auto_approve else "Auto-approve OFF: the AI asks before every action.",
                               style="yellow"))
        elif command == "/tree":
            self.show_tree(arg or ".")
        elif command == "/view":
            self.view_file(arg)
        elif command == "/edit":
            if not arg:
                console.print("Usage: /edit <file>")
                return
            path = self.shell.resolve_path(arg)
            saved = open_editor(path)
            console.print(Text(f"Saved {arg}" if saved else "Closed without saving.", style="green" if saved else "grey50"))
        elif command == "/new":
            self.agent.reset()
            console.print(Text("New conversation started.", style="cyan"))
        elif command == "/model":
            import llm
            if arg and llm.backend() == "local":
                config.MODEL = arg
                console.print(Text(f"Model set to {arg}. (If it's not downloaded: !ollama pull {arg})", style="cyan"))
            elif arg:
                config.HOSTED_MODEL = arg
                console.print(Text(f"Hosted model set to {arg}.", style="cyan"))
            else:
                console.print(f"Engine: [bold]{llm.describe()}[/]")
                if llm.backend() == "local":
                    try:
                        names = [m.model for m in ollama.list().models]
                        console.print(f"Installed local models: {', '.join(names) or 'none'}")
                    except Exception:
                        console.print("(Ollama not reachable)")
        elif command == "/memory":
            facts = tools.load_memory()
            console.print("\n".join(f"{i}. {f}" for i, f in enumerate(facts, 1)) or "Nothing saved yet.")
        elif command == "/clear":
            console.clear()
        else:
            console.print(f"Unknown command {command}. Type /help")

    def vpn_command(self, arg: str) -> None:
        action, _, name = arg.partition(" ")
        action = action.lower()
        name = name.strip() or config.VPN_PROFILE
        if action == "on":
            console.print(Text("Connecting…", style="grey58"))
            console.print(Text(vpn.connect(name), style="cyan"))
        elif action == "off":
            console.print(Text(vpn.disconnect(name), style="cyan"))
        elif action == "ip":
            console.print(Text("Checking public IP…", style="grey58"))
            console.print(f"🌍 Public IP: [bold]{vpn.public_ip()}[/]")
        else:
            s = vpn.status(force=True)
            if s["connected"]:
                console.print(f"🛡️ VPN [bold green]ON[/] via {', '.join(s['names'])}")
            else:
                console.print("🛡️ VPN [bold red]OFF[/]")
            kill = "ON (AI internet tools blocked while VPN is off)" if config.REQUIRE_VPN else "off"
            console.print(f"   Require-VPN setting: {kill}  ·  change REQUIRE_VPN in config.py")
            names = [p["Name"] for p in vpn.profiles()]
            if names:
                console.print(f"   Windows VPN profiles: {', '.join(names)}  ·  /vpn on <name>")
            console.print(Text("   Everything Nanban does online already goes through whatever VPN your system "
                               "has on. /vpn ip shows how the internet sees you.", style="grey58"))

    def show_tree(self, path: str) -> None:
        root = self.shell.resolve_path(path)
        if not root.is_dir():
            console.print(Text(f"{path} is not a folder", style="red"))
            return
        tree = Tree(f"📁 [bold]{root.name or root}[/]")

        def add(node, folder, depth):
            entries = _sorted_entries(folder)
            for entry in entries[:60]:
                if entry.is_dir():
                    branch = node.add(f"📁 [bold #5fafff]{entry.name}[/]")
                    if depth < 2 and entry.name not in IGNORED_DIRS:
                        add(branch, entry, depth + 1)
                else:
                    node.add(f"[white]{entry.name}[/]")
            if len(entries) > 60:
                node.add(f"[grey50]… {len(entries) - 60} more[/]")

        add(tree, root, 1)
        console.print(tree)

    def view_file(self, path: str) -> None:
        if not path:
            console.print("Usage: /view <file>")
            return
        file = self.shell.resolve_path(path)
        if not file.is_file():
            console.print(Text(f"{path} not found", style="red"))
            return
        text = file.read_text(encoding="utf-8", errors="replace")
        console.print(Panel(
            Syntax(text, Syntax.guess_lexer(file.name, text), theme="monokai", line_numbers=True,
                   word_wrap=False, background_color="default"),
            title=f"📄 {path}", title_align="left", border_style="#6d5dfc",
        ))

    # ------------------------------------------------------------ main loop

    def handle(self, line: str) -> None:
        text = line.strip()
        if not text:
            return
        if re.fullmatch(r"/[a-zA-Z]+", text.split(" ")[0]):   # /help, /edit … (not paths like /usr/bin/x)
            self.slash(text)
        elif text.startswith("!"):
            self.run_shell(text[1:].strip())
        elif text.startswith("?"):
            self.ask_ai(text[1:].strip())
        elif self.mode == "shell":
            self.run_shell(text)
        else:
            self.ask_ai(text)

    def banner(self) -> None:
        body = Text.assemble(
            ("✦ AI mode ", "bold #8f83ff"), ("talk in Tamil / English / Tanglish. I can run commands and edit files: "
                                           "you approve each step.\n", ""),
            ("$ Shell mode ", "bold #3ecf7a"), ("a real terminal: git, python, vim, htop, apt, ssh…\n\n", ""),
            ("Ctrl+T", "bold"), (" switch mode   ", ""), ("!cmd", "bold"), (" run once   ", ""),
            ("?question", "bold"), (" ask once   ", ""), ("/server", "bold"), (" manage servers   ", ""),
            ("/help", "bold"), (" all commands", ""),
        )
        console.print(Panel(body, title=f"🤖 {config.AGENT_NAME} Terminal", subtitle=f"{self.os_info}",
                            border_style="#6d5dfc", padding=(1, 2)))
        if IS_WINDOWS and "linux" not in self.shell.available_backends():
            console.print(Text("Tip: for a full Linux terminal, install WSL (see README) then type /linux", style="grey50"))
        import llm
        ok, desc = llm.ping()
        if ok:
            console.print(Text(f"AI engine: {desc}", style="grey50"))
        else:
            console.print(Text(f"⚠  {desc} (shell mode works without it)", style="yellow"))

    def run(self) -> None:
        self.banner()
        while self.running:
            try:
                line = self.session.prompt()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            try:
                self.handle(line)
            except KeyboardInterrupt:
                console.print(Text("(stopped)", style="yellow"))
            except Exception as e:  # keep the terminal alive whatever happens
                console.print(Text(f"Error: {e}", style="red"))
        console.print(Text("Bye! 👋", style="bold #8f83ff"))


def main() -> None:
    start_dir = sys.argv[1] if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else None
    NanbanTerminal(start_dir).run()


if __name__ == "__main__":
    main()
