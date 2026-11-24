"""
kitlib — shared engine for the Nanban Kali Kit CLI tools
(kali-intel, kali-pentest, nmap2, kali-forensics).

Everything here is Python standard library only, so the tools run on a plain
Kali / Debian box with nothing pip-installed. It gives every tool the same:
  * AI bridge     — one ai() call that reaches the SAME engine the Nanban app uses
                    (local Ollama first, optional hosted model as fallback); fully
                    offline-aware, never crashes a tool when AI is unavailable.
  * command runner — run()/stream() with no shell by default (safe for untrusted
                    file names), live line callback, timeouts.
  * reporting     — Markdown + self-contained HTML reports, SHA-256 evidence log.
  * small helpers — colour, which(), json read/write, redaction.

Use only for authorized security research, education and threat intelligence.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

KIT_VERSION = "1.0"
KIT_HOME = Path(os.path.expanduser("~/.nanban-kit"))
CASE_DEFAULT = Path(os.path.expanduser("~/nanban-kit/case"))
TTY = sys.stdout.isatty()
UA = "NanbanKit/1.0 (+security-research)"   # generic — never carries the user's identity


# ───────────────────────────────────────────────────────────── colour / print

def _c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if TTY else s


def red(s):  return _c("91", s)
def grn(s):  return _c("92", s)
def ylw(s):  return _c("93", s)
def cyn(s):  return _c("96", s)
def bold(s): return _c("1", s)
def dim(s):  return _c("2", s)


def ok(label, value=""):  print(f"  {grn('[+]')} {label}" + (f": {value}" if value else ""))
def warn(label, value=""): print(f"  {ylw('[!]')} {label}" + (f": {value}" if value else ""))
def bad(label, value=""):  print(f"  {red('[-]')} {label}" + (f": {value}" if value else ""))
def info(s):  print(dim(f"  {s}"))
def step(s):  print(f"  {cyn('==>')} {bold(s)}")


def title(name: str, sub: str = ""):
    line = red("━" * 70)
    print(f"\n{line}\n  {bold(red(name))}" + (f"   {dim(sub)}" if sub else "") + f"\n{line}")


def rule(s=""):
    print(dim("  " + "─" * 66) + (f" {s}" if s else ""))


# ───────────────────────────────────────────────────────────── fs / json

def load_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text("utf-8"))
    except (OSError, ValueError):
        return default


def save_json(path: Path, obj) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), "utf-8")
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass


def which(tool: str) -> bool:
    return shutil.which(tool) is not None


def ensure_case(path) -> Path:
    p = Path(os.path.expanduser(str(path))) if path else CASE_DEFAULT
    p.mkdir(parents=True, exist_ok=True)
    return p


# ───────────────────────────────────────────────────────────── command runner

def run(cmd, timeout: int = 180, on_line=None, shell=False, inp: str | None = None):
    """Run a command. cmd is a list (no shell — safe for untrusted names) unless shell=True.
    Returns (returncode, combined_output). Streams each line to on_line if given."""
    if isinstance(cmd, str) and not shell:
        cmd = shlex.split(cmd)
    if not shell:
        exe = cmd[0]
        if not which(exe):
            return 127, f"__missing__ {exe}"
    try:
        p = subprocess.Popen(
            cmd, shell=shell, stdin=subprocess.PIPE if inp is not None else None,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            bufsize=1, errors="replace",
            env={**os.environ, "DEBIAN_FRONTEND": "noninteractive"})
    except (OSError, ValueError) as e:
        return 1, str(e)
    out = []
    try:
        if inp is not None:
            p.stdin.write(inp)
            p.stdin.close()
        start = time.time()
        for line in p.stdout:
            out.append(line)
            if on_line:
                on_line(line.rstrip("\n"))
            if time.time() - start > timeout:
                p.kill()
                out.append(f"\n[timed out after {timeout}s]\n")
                break
        p.wait(timeout=5)
    except KeyboardInterrupt:
        p.kill()
        out.append("\n[cancelled]\n")
        return 130, "".join(out)
    except subprocess.TimeoutExpired:
        p.kill()
    return (p.returncode or 0), "".join(out)


def tool_or_hint(name: str, pkg: str = "") -> bool:
    """True if a tool is present; otherwise print how to get it and return False."""
    if which(name):
        return True
    warn(f"'{name}' not installed", f"skipping — install with: sudo apt install -y {pkg or name}")
    return False


# ───────────────────────────────────────────────────────────── HTTP (stdlib)

def http_json(url: str, headers: dict | None = None, data: bytes | None = None,
              timeout: int = 25):
    """GET/POST and parse JSON. Returns (ok, parsed_or_error_string)."""
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", "replace")
        return True, (json.loads(body) if body.strip() else {})
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            pass
        return False, f"HTTP {e.code} {e.reason} {detail}".strip()
    except (urllib.error.URLError, ValueError, OSError) as e:
        reason = getattr(e, "reason", e)
        return False, f"{reason}"


def http_text(url: str, headers: dict | None = None, timeout: int = 25):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, r.read().decode("utf-8", "replace")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        return False, str(getattr(e, "reason", e))


# ───────────────────────────────────────────────────────────── AI bridge

def ai_config() -> dict:
    """AI settings. Precedence: process env (set by the Nanban app) → ~/.nanban-kit/ai.json."""
    cfg = load_json(KIT_HOME / "ai.json", {}) or {}
    env = os.environ
    if env.get("NANBAN_AI_URL"):
        cfg["ollama_url"] = env["NANBAN_AI_URL"]
    if env.get("NANBAN_AI_MODEL"):
        cfg["model"] = env["NANBAN_AI_MODEL"]
    if env.get("NANBAN_HOSTED_URL"):
        cfg["hosted_url"] = env["NANBAN_HOSTED_URL"]
    if env.get("NANBAN_HOSTED_KEY"):
        cfg["hosted_key"] = env["NANBAN_HOSTED_KEY"]
    if env.get("NANBAN_HOSTED_MODEL"):
        cfg["hosted_model"] = env["NANBAN_HOSTED_MODEL"]
    cfg.setdefault("model", "llama3.1:8b")
    return cfg


def _ollama_hosts(cfg: dict) -> list[str]:
    hosts = []
    if cfg.get("ollama_url"):
        hosts.append(cfg["ollama_url"].rstrip("/"))
    hosts.append("http://127.0.0.1:11434")
    # Windows host from inside WSL: the nameserver and the default gateway
    for src in ("/etc/resolv.conf",):
        try:
            for ln in Path(src).read_text().splitlines():
                m = re.match(r"\s*nameserver\s+([\d.]+)", ln)
                if m:
                    hosts.append(f"http://{m.group(1)}:11434")
        except OSError:
            pass
    try:
        rc, out = run(["ip", "route"], timeout=5)
        m = re.search(r"default via ([\d.]+)", out)
        if m:
            hosts.append(f"http://{m.group(1)}:11434")
    except Exception:
        pass
    seen, uniq = set(), []
    for h in hosts:
        if h not in seen:
            seen.add(h)
            uniq.append(h)
    return uniq


def ai_status() -> tuple[bool, str]:
    """(available, human description of which engine answers)."""
    cfg = ai_config()
    for host in _ollama_hosts(cfg):
        okk, data = http_json(host + "/api/tags", timeout=4)
        if okk:
            names = [m.get("name", "") for m in (data.get("models") or [])]
            model = cfg["model"] if cfg["model"] in names else (names[0] if names else cfg["model"])
            return True, f"Ollama {model} @ {host}"
    if cfg.get("hosted_key") and cfg.get("hosted_url"):
        return True, f"hosted {cfg.get('hosted_model', '?')}"
    return False, "no AI engine reachable (start Ollama, or set a hosted key in the app)"


def ai(prompt: str, system: str | None = None, context: str = "",
       temperature: float = 0.3, max_chars: int = 16000) -> str | None:
    """One call to the same AI the Nanban app uses. Returns text, or None if no engine.
    Local Ollama is tried first; a configured hosted model is the fallback."""
    cfg = ai_config()
    sysmsg = system or ("You are a precise cybersecurity analyst helping with authorized, "
                        "legal security research and education. Be concise, technical and practical. "
                        "Never provide instructions for illegal intrusion; focus on analysis, "
                        "explanation, risk and defensive/next-step guidance.")
    user = (context[:max_chars] + "\n\n" if context else "") + prompt
    messages = [{"role": "system", "content": sysmsg}, {"role": "user", "content": user}]

    for host in _ollama_hosts(cfg):
        payload = json.dumps({"model": cfg["model"], "messages": messages, "stream": False,
                              "options": {"temperature": temperature}}).encode()
        okk, data = http_json(host + "/api/chat",
                              headers={"Content-Type": "application/json"},
                              data=payload, timeout=180)
        if okk and isinstance(data, dict):
            txt = (data.get("message") or {}).get("content", "").strip()
            if txt:
                return txt

    url, key = cfg.get("hosted_url"), cfg.get("hosted_key")
    if url and key:
        payload = json.dumps({"model": cfg.get("hosted_model") or "gpt-4o-mini",
                              "messages": messages, "temperature": temperature}).encode()
        okk, data = http_json(url.rstrip("/") + "/chat/completions",
                              headers={"Content-Type": "application/json",
                                       "Authorization": f"Bearer {key}"},
                              data=payload, timeout=180)
        if okk and isinstance(data, dict):
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError):
                pass
    return None


def ai_box(text: str, heading: str = "AI Analysis"):
    """Print an AI answer in a tidy box (or a friendly note when AI is offline)."""
    if not text:
        avail, desc = ai_status()
        warn("AI unavailable", desc)
        return
    print(f"\n  {red('🧠 ' + heading)}")
    for ln in text.splitlines():
        for wrapped in _wrap(ln, 86):
            print(f"  {wrapped}")
    print()


def _wrap(s: str, width: int) -> list[str]:
    import textwrap
    if not s.strip():
        return [""]
    return textwrap.wrap(s, width, break_long_words=False, break_on_hyphens=False) or [""]


# ───────────────────────────────────────────────────────────── evidence + reports

def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def evidence_log(case: Path, kind: str, ref: str, path: Path | None = None, note: str = ""):
    """Append a chain-of-custody row to the case's evidence log (CSV)."""
    import csv
    case = Path(case)
    case.mkdir(parents=True, exist_ok=True)
    log = case / "evidence_log.csv"
    new = not log.exists()
    digest = sha256_file(path) if path and Path(path).is_file() else ""
    size = Path(path).stat().st_size if path and Path(path).is_file() else ""
    with open(log, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["utc_time", "kind", "reference", "file", "sha256", "bytes", "note"])
        w.writerow([time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), kind, ref,
                    os.path.relpath(path, case) if path else "", digest, size, note])
    return digest


def write_report(case: Path, slug: str, title_text: str, sections: list[tuple[str, str]],
                 ai_summary: str = "", meta: dict | None = None) -> dict:
    """Write both a Markdown and a standalone dark-themed HTML report. Returns the paths + hashes."""
    case = ensure_case(case)
    rep_dir = case / "reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    base = rep_dir / f"{stamp}_{slug}"
    meta = meta or {}
    when = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    # --- Markdown
    md = [f"# {title_text}", "", f"*Generated by Nanban Kali Kit v{KIT_VERSION} — {when}*", ""]
    for k, v in meta.items():
        md.append(f"- **{k}:** {v}")
    if ai_summary:
        md += ["", "## AI Summary", "", ai_summary]
    for head, body in sections:
        md += ["", f"## {head}", "", "```", body.rstrip(), "```"]
    md += ["", "---", "*For authorized research and educational use only.*", ""]
    md_path = base.with_suffix(".md")
    md_path.write_text("\n".join(md), "utf-8")

    # --- HTML (self-contained, dark)
    def esc(x): return html.escape(str(x))
    rows = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in meta.items())
    secs = ""
    for head, body in sections:
        secs += f"<h2>{esc(head)}</h2><pre>{esc(body.rstrip())}</pre>"
    ai_html = f"<div class='ai'><h2>🧠 AI Summary</h2><pre>{esc(ai_summary)}</pre></div>" if ai_summary else ""
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title_text)}</title><style>
:root{{color-scheme:dark}}
body{{background:#0b0d12;color:#e7e9ee;font:15px/1.6 ui-sans-serif,system-ui,Segoe UI,Roboto,sans-serif;margin:0;padding:32px;max-width:980px;margin-inline:auto}}
h1{{color:#ff3b4e;font-size:26px;margin:0 0 4px}}
h2{{color:#ff6b78;border-bottom:1px solid #22262f;padding-bottom:6px;margin-top:32px}}
.meta{{color:#8b93a7;font-size:13px}}
table{{border-collapse:collapse;margin:14px 0;width:100%}}
th,td{{text-align:left;padding:6px 10px;border-bottom:1px solid #1b1f28;vertical-align:top}}
th{{color:#9aa3b5;font-weight:600;width:190px}}
pre{{background:#12151c;border:1px solid #1f2430;border-radius:10px;padding:14px;overflow:auto;white-space:pre-wrap;word-break:break-word;font:13px/1.5 ui-monospace,Menlo,Consolas,monospace;color:#cdd3df}}
.ai{{background:#17110f;border:1px solid #3a1d1d;border-radius:12px;padding:4px 18px;margin:18px 0}}
.ai h2{{color:#ff3b4e;border:0}}
footer{{margin-top:40px;color:#6a7284;font-size:12px}}
.badge{{display:inline-block;background:#ff3b4e;color:#fff;border-radius:6px;padding:2px 8px;font-size:12px;font-weight:700}}
</style></head><body>
<h1>{esc(title_text)}</h1>
<div class="meta"><span class="badge">Nanban Kali Kit v{KIT_VERSION}</span> &nbsp; {esc(when)}</div>
<table>{rows}</table>
{ai_html}
{secs}
<footer>For authorized research and educational use only. This report contains indicators that should be verified before action.</footer>
</body></html>"""
    html_path = base.with_suffix(".html")
    html_path.write_text(doc, "utf-8")

    ok("Report (Markdown)", str(md_path))
    ok("Report (HTML)", str(html_path))
    evidence_log(case, "report", title_text, html_path, "auto-generated")
    return {"md": str(md_path), "html": str(html_path),
            "md_sha256": sha256_file(md_path), "html_sha256": sha256_file(html_path)}


# ───────────────────────────────────────────────────────────── misc

def is_ip(s: str) -> bool:
    return bool(re.fullmatch(r"(\d{1,3}\.){3}\d{1,3}", s)) and all(0 <= int(x) < 256 for x in s.split("."))


def is_hash(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Fa-f0-9]{32}|[A-Fa-f0-9]{40}|[A-Fa-f0-9]{64}", s))


def is_email(s: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", s))


def is_domain(s: str) -> bool:
    return bool(re.fullmatch(r"(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}", s))


def classify(target: str) -> str:
    t = target.strip().rstrip("/")
    t = re.sub(r"^https?://", "", t).split("/")[0]
    if is_ip(t):
        return "ip"
    if is_hash(target.strip()):
        return "hash"
    if is_email(t):
        return "email"
    if is_domain(t):
        return "domain"
    return "unknown"


def banner(tool_name: str, tagline: str):
    dragon = red("🐉")
    print(f"\n{dragon} {bold(red('Nanban Kali Kit'))} {dim('·')} {bold(tool_name)}  {dim('v' + KIT_VERSION)}")
    print(dim(f"   {tagline}"))
    avail, desc = ai_status()
    print(f"   AI: {grn(desc) if avail else dim(desc)}\n")
