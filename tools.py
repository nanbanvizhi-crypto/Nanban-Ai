"""
Tools the agent can use. Each tool is a normal Python function: the type hints and
docstring tell the model what it does and which arguments it takes.

To add your own tool: write a function here, add it to ALL_TOOLS at the bottom,
and add its name to a mode's "tools" list in config.py.
"""

import ast
import json
import operator
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import config
import docs_rag
import vpn

MEMORY_FILE = config.DATA_DIR / "memory.json"
TASKS_FILE = config.DATA_DIR / "tasks.json"
MAX_RESULT_CHARS = 6000

# ---------------------------------------------------------------- per-user data (Nanban Server)
# Memory and to-dos are kept per user when the server runs with logins. The user is passed
# explicitly (functions take `user=""`); "" means the laptop owner's default files.

def _safe_user(user: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", user or "")


def memory_file(user: str = "") -> Path:
    if not user:
        return MEMORY_FILE
    folder = config.DATA_DIR / "users" / _safe_user(user)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "memory.json"


def tasks_file(user: str = "") -> Path:
    if not user:
        return TASKS_FILE
    folder = config.DATA_DIR / "users" / _safe_user(user)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "tasks.json"


# ---------------------------------------------------------------- small helpers

def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _safe_path(filename: str) -> Path:
    """Keep all file access inside the workspace folder."""
    root = config.WORKSPACE_DIR.resolve()
    path = (root / filename).resolve()
    if root not in path.parents:
        raise ValueError("Only files inside the workspace folder are allowed")
    return path


# ---------------------------------------------------------------- time & math

def get_current_time() -> str:
    """Get the current local date and time."""
    return datetime.now().strftime("%A, %d %B %Y, %I:%M %p")


_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculate(expression: str) -> str:
    """Evaluate a math expression exactly, e.g. '1250 * 12 * 0.18' or '(45000 - 32000) / 45000 * 100'.

    Args:
        expression: The math expression using numbers and + - * / ** % ( )
    """
    try:
        expression = expression.replace(",", "").replace("^", "**").replace("x", "*")
        result = _eval(ast.parse(expression, mode="eval").body)
        if isinstance(result, float):
            result = round(result, 6)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------------------------------------- web

def web_search(query: str, max_results: int = 5) -> str:
    """Search the internet (DuckDuckGo) for current information. Returns titles, links and snippets.

    Args:
        query: What to search for, in a few keywords
        max_results: How many results to return (1-10)
    """
    allowed, reason = vpn.internet_allowed()
    if not allowed:
        return reason
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=max(1, min(int(max_results), 10)))
    except Exception as e:
        return f"Web search failed ({e}). Check your internet connection."
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r.get('title', '')}\n   {r.get('href', '')}\n   {r.get('body', '')}")
    return "\n".join(lines)


def fetch_webpage(url: str) -> str:
    """Download a web page and return its main text, to read a search result in full.

    Args:
        url: The full page address starting with http:// or https://
    """
    if not re.match(r"^https?://", url):
        return "Error: URL must start with http:// or https://"
    allowed, reason = vpn.internet_allowed()
    if not allowed:
        return reason
    try:
        import requests
        from bs4 import BeautifulSoup
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (LocalAIAgent)"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        return text[:MAX_RESULT_CHARS] or "The page had no readable text."
    except Exception as e:
        return f"Could not read the page: {e}"


# ---------------------------------------------------------------- files

def list_files() -> str:
    """List the files in the agent's workspace folder."""
    files = sorted(p.name for p in config.WORKSPACE_DIR.iterdir() if p.is_file())
    return "\n".join(files) if files else "The workspace folder is empty."


def read_file(filename: str) -> str:
    """Read a text file from the workspace folder.

    Args:
        filename: Name of the file, for example 'notes.txt'
    """
    try:
        return _safe_path(filename).read_text(encoding="utf-8")[:MAX_RESULT_CHARS]
    except Exception as e:
        return f"Error: {e}"


def write_file(filename: str, content: str) -> str:
    """Save text or code to a file in the workspace folder (overwrites it if it exists).

    Args:
        filename: Name of the file with extension, for example 'essay.md' or 'app.py'
        content: The full text to save
    """
    try:
        path = _safe_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Saved {filename} in the workspace folder."
    except Exception as e:
        return f"Error: {e}"


def run_python(code: str) -> str:
    """Run a Python script and return what it prints. Use it to test code or compute results.

    Args:
        code: The complete Python code to run
    """
    if not config.ALLOW_CODE_RUN:
        return ("Running code is switched off. The user can enable it by setting "
                "ALLOW_CODE_RUN = True in config.py.")
    script = config.WORKSPACE_DIR / "_agent_run.py"
    script.write_text(code, encoding="utf-8")
    try:
        result = subprocess.run([sys.executable, str(script)], cwd=config.WORKSPACE_DIR,
                                capture_output=True, text=True, timeout=30)
        output = (result.stdout + ("\n[stderr]\n" + result.stderr if result.stderr else "")).strip()
        return output[:MAX_RESULT_CHARS] or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: the code took longer than 30 seconds and was stopped."


# ---------------------------------------------------------------- tasks (to-do list)

def add_task(task: str, due: str = "", user: str = "") -> str:
    """Add an item to the user's to-do list.

    Args:
        task: What needs to be done
        due: Optional due date or time in words, e.g. 'tomorrow 5pm' or '2026-11-10'
    """
    tasks = _load_json(tasks_file(user), [])
    next_id = max((t["id"] for t in tasks), default=0) + 1
    tasks.append({"id": next_id, "task": task, "due": due, "done": False,
                  "added": datetime.now().strftime("%Y-%m-%d %H:%M")})
    _save_json(tasks_file(user), tasks)
    return f"Added task #{next_id}: {task}" + (f" (due {due})" if due else "")


def list_tasks(include_done: bool = False, user: str = "") -> str:
    """Show the user's to-do list.

    Args:
        include_done: Also show completed tasks
    """
    tasks = [t for t in _load_json(tasks_file(user), []) if include_done or not t["done"]]
    if not tasks:
        return "The to-do list is empty."
    return "\n".join(
        f"#{t['id']} [{'x' if t['done'] else ' '}] {t['task']}" + (f" (due {t['due']})" if t.get("due") else "")
        for t in tasks
    )


def complete_task(task_id: int, user: str = "") -> str:
    """Mark a to-do item as done.

    Args:
        task_id: The task number shown in the list, e.g. 3
    """
    tasks = _load_json(tasks_file(user), [])
    for t in tasks:
        if t["id"] == int(task_id):
            t["done"] = True
            _save_json(tasks_file(user), tasks)
            return f"Marked task #{t['id']} as done: {t['task']}"
    return f"No task #{task_id} found."


# ---------------------------------------------------------------- long-term memory

def load_memory(user: str = "") -> list[str]:
    return _load_json(memory_file(user), [])


def remember(fact: str, user: str = "") -> str:
    """Save a lasting fact or preference about the user to long-term memory, when the user asks you
    to remember something or shares something useful for future chats (their name, job, goals, likes).

    Args:
        fact: The fact in one short sentence, e.g. 'User's name is Dev'
    """
    facts = load_memory(user)
    if fact.strip() and fact.strip() not in facts:
        facts.append(fact.strip())
        _save_json(memory_file(user), facts)
    return f"Remembered: {fact}"


def forget(fact_number: int, user: str = "") -> str:
    """Remove a saved fact from long-term memory.

    Args:
        fact_number: The number of the fact as shown in the memory list (starting at 1)
    """
    facts = load_memory(user)
    index = int(fact_number) - 1
    if 0 <= index < len(facts):
        removed = facts.pop(index)
        _save_json(memory_file(user), facts)
        return f"Forgot: {removed}"
    return f"No fact #{fact_number} in memory."


def clear_memory(user: str = "") -> None:
    _save_json(memory_file(user), [])


USER_SCOPED = {"add_task", "list_tasks", "complete_task", "remember", "forget"}


def for_user(func, user: str):
    """Bind the hidden `user` argument of a user-scoped tool, keeping its name/docstring/signature
    (minus `user`) so the model still sees the same tool."""
    if not user or func.__name__ not in USER_SCOPED:
        return func
    import functools
    import inspect

    @functools.wraps(func)
    def bound(*args, **kwargs):
        kwargs.pop("user", None)
        return func(*args, user=user, **kwargs)

    sig = inspect.signature(func)
    bound.__signature__ = sig.replace(parameters=[p for p in sig.parameters.values() if p.name != "user"])
    return bound


# ---------------------------------------------------------------- documents (Study mode)

def search_documents(query: str) -> str:
    """Search the user's own documents (PDFs, notes) for passages that answer a question.

    Args:
        query: The question or topic to look for
    """
    try:
        docs_rag.refresh_index()
        hits = docs_rag.search(query)
    except Exception as e:
        return (f"Document search hit an error ({e}). Try re-uploading the file. "
                "Documents work without any model via built-in keyword search; "
                f"for best results you can also install embeddings (ollama pull {config.EMBED_MODEL}).")
    if not hits:
        return "No documents found. Put PDF/Word/text files in the documents folder or upload them."
    return "\n\n".join(f"[{h['file']}, page {h['page']}]\n{h['text']}" for h in hits)


def list_documents() -> str:
    """List the documents available for Study mode."""
    files = [p.name for p in docs_rag.document_files()]
    return "\n".join(files) if files else "No documents yet."


# ---------------------------------------------------------------- registry

def self_check() -> str:
    """Diagnose and automatically fix common Nanban problems.

    Use this whenever the user says the app is broken, slow, not working, erroring, the AI
    isn't responding, the model is missing, or anything similar. It checks folders, settings,
    dependencies, the AI engine (Ollama / cloud), disk space, and fixes the safe issues on its
    own, then reports what it fixed and anything that still needs the user.
    """
    import doctor
    return doctor.quick_summary()


ALL_TOOLS = {f.__name__: f for f in [
    get_current_time, calculate, web_search, fetch_webpage,
    list_files, read_file, write_file, run_python,
    add_task, list_tasks, complete_task,
    remember, forget,
    search_documents, list_documents,
    self_check,
]}

TOOL_LABELS = {
    "get_current_time": "🕒 Checking the time",
    "calculate": "🧮 Calculating",
    "web_search": "🔍 Searching the web",
    "fetch_webpage": "🌐 Reading a web page",
    "list_files": "📁 Listing files",
    "read_file": "📄 Reading a file",
    "write_file": "💾 Saving a file",
    "run_python": "▶️ Running code",
    "add_task": "✅ Adding a task",
    "list_tasks": "📋 Checking tasks",
    "complete_task": "☑️ Completing a task",
    "remember": "🧠 Saving to memory",
    "forget": "🧹 Removing from memory",
    "search_documents": "📚 Searching your documents",
    "self_check": "🩺 Checking & fixing Nanban",
    "set_plan": "📋 Making a plan",
    "complete_step": "✔ Step done",
    "run_command": "▶️ Running a command",
    "edit_file": "✎ Editing a file",
    "list_directory": "📁 Listing folder",
    "search_files": "🔎 Searching files",
    "list_documents": "📚 Listing documents",
}
