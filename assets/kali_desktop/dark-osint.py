#!/usr/bin/env python3
"""
dark-osint — a Tor terminal browser + Dark Web OSINT toolkit (one file, Python stdlib only).

Browser (everything goes through the real Tor daemon, SOCKS5 127.0.0.1:9050, DNS resolved by Tor):
  * text-mode pages with numbered links, forms, back/forward, history, bookmarks
  * per-site circuit isolation + "new identity" (like Tor Browser), circuit display
  * no JavaScript, no plugins, no images loaded, session-only cookies (wiped on exit / new identity)
  * never falls back to a direct connection: if Tor is down, nothing is fetched

Toolkit — the 15 commands of the "Dark Web OSINT" cheat sheet as built-ins:
  start status verify port check head monitor | onions notes iocs | ftype meta hash | urls indicators

Use only for authorized research, education and threat intelligence.
"""

import atexit
import csv
import hashlib
import html
import os
import re
import secrets
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit

VERSION = "1.0"
SOCKS_HOST, SOCKS_PORT = "127.0.0.1", 9050
CONTROL_SOCKET = "/run/tor/control"
CONTROL_COOKIE = "/run/tor/control.authcookie"
# Same User-Agent Tor Browser sends, so the request blends in with other Tor users.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; rv:140.0) Gecko/20100101 Firefox/140.0"
ONION_RE = r"[a-z2-7]{56}\.onion"
AHMIA = "https://ahmia.fi/"
AHMIA_ONION = "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/"
HOME = os.path.expanduser("~/dark-osint")
MAX_PAGE = 25 * 1024 * 1024
MAX_DOWNLOAD = 500 * 1024 * 1024

TTY = sys.stdout.isatty()


def c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if TTY else s


def G(s): return c("92", s)            # green
def B(s): return c("1", s)             # bold
def D(s): return c("2", s)             # dim
def R(s): return c("91", s)            # red
def Y(s): return c("93", s)            # yellow
def CY(s): return c("96", s)           # cyan


def ok(label, value): print(f"  {G('[✓]')} {label}: {G(value)}")
def bad(label, value): print(f"  {R('[✗]')} {label}: {R(value)}")
def info(s): print(D(f"  {s}"))
def err(s): print(R(f"  ! {s}"))


# ───────────────────────────────────────────────────────────── Tor daemon

def socks_up() -> bool:
    try:
        with socket.create_connection((SOCKS_HOST, SOCKS_PORT), timeout=3):
            return True
    except OSError:
        return False


class Control:
    """Minimal Tor control-port client over the unix socket (cookie auth)."""

    def __init__(self):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.settimeout(10)
        self.s.connect(CONTROL_SOCKET)
        self.f = self.s.makefile("rwb")
        with open(CONTROL_COOKIE, "rb") as fh:
            cookie = fh.read().hex()
        self.cmd(f"AUTHENTICATE {cookie}")

    def cmd(self, line: str) -> list[str]:
        self.f.write(line.encode() + b"\r\n")
        self.f.flush()
        out, data = [], False
        while True:
            raw = self.f.readline()
            if not raw:
                raise OSError("control connection closed")
            ln = raw.decode("utf-8", "replace").rstrip("\r\n")
            if data:
                if ln == ".":
                    data = False
                else:
                    out.append(ln)
                continue
            code, sep, rest = ln[:3], ln[3:4], ln[4:]
            if sep == "+":
                data = True
                if rest.split("=", 1)[-1]:
                    out.append(rest.split("=", 1)[-1])
            elif sep == "-":
                out.append(rest)
            else:
                if not code.startswith("2"):
                    raise OSError(f"tor control: {ln}")
                return out

    def info(self, key: str) -> str:
        r = self.cmd(f"GETINFO {key}")
        if not r:
            return ""
        first = r[0]
        if first.startswith(key + "="):
            first = first[len(key) + 1:]
        return "\n".join([first] + r[1:]).strip()

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass


def control():
    try:
        return Control()
    except (OSError, PermissionError):
        return None


def bootstrap() -> int:
    ct = control()
    if not ct:
        return -1
    try:
        m = re.search(r"PROGRESS=(\d+)", ct.info("status/bootstrap-phase"))
        return int(m.group(1)) if m else -1
    except OSError:
        return -1
    finally:
        ct.close()


def start_tor(quiet=False) -> bool:
    """Tool 01 — sudo systemctl start tor (and wait for the SOCKS port + bootstrap)."""
    if not socks_up():
        if not quiet:
            print(D("  $ sudo systemctl start tor"))
        if subprocess.call(["sudo", "-n", "systemctl", "start", "tor"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            subprocess.call(["sudo", "systemctl", "start", "tor"])
        for _ in range(40):
            if socks_up():
                break
            time.sleep(0.5)
    if not socks_up():
        return False
    last = None
    for _ in range(180):
        p = bootstrap()
        if p < 0 or p >= 100:
            break
        if p != last and not quiet:
            print(D(f"  Tor bootstrapping… {p}%"))
            last = p
        time.sleep(1)
    return True


def banner(full=True) -> bool:
    up = socks_up()
    p = bootstrap() if up else -1
    ready = up and (p < 0 or p >= 100)
    print()
    print(G(B("  ◉ dark-osint")) + D(f"  v{VERSION} — Tor terminal browser + Dark Web OSINT toolkit"))
    print()
    (ok if up else bad)("Tor", "Connected" if up else "Not running  (run: dark-osint start)")
    (ok if up else bad)("Proxy", f"{SOCKS_HOST}:{SOCKS_PORT}")
    ok("Search", "Onion Services")
    (ok if ready else bad)("Status", "Ready" if ready else (f"Bootstrapping {p}%" if up else "Offline"))
    print()
    return ready


# ───────────────────────────────────────────────────────────── HTML → text

BLOCK = {"p", "div", "section", "article", "header", "footer", "nav", "main", "aside", "ul", "ol", "table",
         "tr", "form", "fieldset", "blockquote", "dl", "dt", "dd", "figure", "figcaption", "hr", "details",
         "summary", "address", "center"}
SKIP = {"script", "style", "template", "svg", "head", "iframe", "object", "embed", "canvas", "audio", "video"}
PRE_MARK = "\x00"


class Renderer(HTMLParser):
    def __init__(self, base: str):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.buf: list[str] = []
        self.links: list[str] = []
        self.forms: list[dict] = []
        self.title = ""
        self._skip = 0
        self._pre = 0
        self._in_title = False
        self._a: list[int | None] = []
        self._form = None
        self._textarea = None
        self._lists: list[list] = []

    def _nl(self, n=1):
        self.buf.append("\n" * n)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
            return
        if tag == "base" and a.get("href"):
            self.base = urljoin(self.base, a["href"])
            return
        if tag in SKIP:
            self._skip += 1
            return
        if self._skip:
            return
        if tag in BLOCK:
            self._nl(2 if tag in ("p", "blockquote", "table", "form", "ul", "ol") else 1)
        if tag == "hr":
            self.buf.append("─" * 40 + "\n")
        elif tag == "br":
            self._nl()
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._nl(2)
            self.buf.append("\033[1;92m" if TTY else "")
            if tag in ("h1", "h2"):
                self.buf.append("# " if tag == "h1" else "## ")
        elif tag in ("b", "strong"):
            self.buf.append("\033[1m" if TTY else "")
        elif tag in ("ul", "ol"):
            self._lists.append([tag, 0])
        elif tag == "li":
            self._nl()
            if self._lists and self._lists[-1][0] == "ol":
                self._lists[-1][1] += 1
                self.buf.append(f"{'  ' * (len(self._lists) - 1)}{self._lists[-1][1]}. ")
            else:
                self.buf.append(f"{'  ' * max(0, len(self._lists) - 1)}• ")
        elif tag in ("td", "th"):
            self.buf.append("  ")
        elif tag == "pre":
            self._pre += 1
            self._nl()
        elif tag == "a":
            href = (a.get("href") or "").strip()
            if href and not href.lower().startswith(("javascript:", "#", "mailto:", "tel:", "data:")):
                self.links.append(urljoin(self.base, href))
                self._a.append(len(self.links))
            else:
                self._a.append(None)
        elif tag == "img":
            alt = (a.get("alt") or "").strip()
            self.buf.append(f"[img{': ' + alt if alt else ''}]")
        elif tag == "form":
            self._form = {"action": urljoin(self.base, a.get("action") or ""),
                          "method": (a.get("method") or "get").lower(), "fields": []}
        elif tag == "input":
            typ = (a.get("type") or "text").lower()
            name = a.get("name")
            if self._form is not None and name and typ not in ("submit", "button", "image", "reset", "file"):
                if typ in ("checkbox", "radio") and "checked" not in a:
                    return
                self._form["fields"].append({"name": name, "value": a.get("value") or "",
                                             "ask": typ not in ("hidden", "checkbox", "radio"),
                                             "label": a.get("placeholder") or name, "secret": typ == "password"})
                if typ not in ("hidden", "checkbox", "radio"):
                    self.buf.append(f"[{a.get('placeholder') or name}: ____] ")
        elif tag == "textarea":
            if self._form is not None and a.get("name"):
                self._textarea = {"name": a["name"], "value": "", "ask": True, "label": a["name"], "secret": False}
                self.buf.append(f"[{a['name']}: ____] ")
        elif tag == "select":
            if self._form is not None and a.get("name"):
                self._form["fields"].append({"name": a["name"], "value": "", "ask": True,
                                             "label": a["name"], "secret": False, "select": True})
        elif tag == "option":
            if self._form and self._form["fields"] and self._form["fields"][-1].get("select"):
                f = self._form["fields"][-1]
                if "selected" in a or not f.get("_set"):
                    f["value"], f["_set"] = a.get("value") or "", True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in SKIP:
            self._skip = max(0, self._skip - 1)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            return
        if tag in SKIP:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.buf.append("\033[0m" if TTY else "")
            self._nl(2)
        elif tag in ("b", "strong"):
            self.buf.append("\033[0m" if TTY else "")
        elif tag in ("ul", "ol"):
            if self._lists:
                self._lists.pop()
            self._nl()
        elif tag == "pre":
            self._pre = max(0, self._pre - 1)
            self._nl()
        elif tag == "a":
            n = self._a.pop() if self._a else None
            if n:
                self.buf.append(("\033[32m[%d]\033[0m" if TTY else "[%d]") % n)
        elif tag == "textarea":
            if self._textarea and self._form is not None:
                self._form["fields"].append(self._textarea)
            self._textarea = None
        elif tag == "form":
            if self._form is not None:
                self.forms.append(self._form)
                names = ", ".join(f["label"] for f in self._form["fields"] if f["ask"]) or "submit"
                self.buf.append(f"\n{'⟦'}form {len(self.forms)}: {names} — type: form {len(self.forms)}{'⟧'}\n")
            self._form = None
        elif tag in BLOCK:
            self._nl()
        elif tag in ("td", "th"):
            self.buf.append("  ")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
            return
        if self._skip:
            return
        if self._textarea is not None:
            self._textarea["value"] += data
            return
        if self._pre:
            self.buf.append("".join(PRE_MARK + ln + "\n" for ln in data.split("\n")) if "\n" in data
                            else PRE_MARK + data)
        else:
            self.buf.append(re.sub(r"\s+", " ", data))

    def lines(self, width: int) -> list[str]:
        out: list[str] = []
        for para in "".join(self.buf).split("\n"):
            if PRE_MARK in para:
                out.append(para.replace(PRE_MARK, ""))
                continue
            para = para.strip()
            if not para:
                if out and out[-1] != "":
                    out.append("")
                continue
            out.extend(textwrap.wrap(para, width, break_long_words=False, break_on_hyphens=False) or [""])
        while out and out[-1] == "":
            out.pop()
        return out


# ───────────────────────────────────────────────────────────── browser

class Page:
    def __init__(self, url):
        self.url = url
        self.status = 0
        self.ctype = ""
        self.headers = ""
        self.title = ""
        self.lines: list[str] = []
        self.links: list[str] = []
        self.forms: list[dict] = []
        self.body = b""
        self.is_text = True
        self.pos = 0


def site_of(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    if host.endswith(".onion"):
        return ".".join(host.split(".")[-2:])
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) > 2 and not host.replace(".", "").isdigit() else host


def normalise(url: str) -> str:
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        host = url.split("/")[0].lower()
        url = ("http://" if host.endswith(".onion") else "https://") + url
    return url


class Browser:
    def __init__(self, case_dir: str):
        self.case = os.path.abspath(os.path.expanduser(case_dir))
        self.tmp = tempfile.mkdtemp(prefix="dark-osint-")
        os.chmod(self.tmp, 0o700)
        atexit.register(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        self.nonce = secrets.token_hex(8)
        self.hist: list[Page] = []
        self.idx = -1
        self.visited: list[tuple[str, str, str]] = []

    # --- network (always through Tor; curl does the HTTP/TLS work) ---
    def _iso_user(self, url: str) -> str:
        return hashlib.sha256(site_of(url).encode()).hexdigest()[:16]

    def _curl(self, url: str, out_path: str, hdr_path: str, post: str | None, limit: int, head=False):
        scheme = urlsplit(url).scheme.lower()
        if scheme not in ("http", "https"):
            raise ValueError(f"blocked scheme '{scheme}:' — only http/https go through Tor")
        if not socks_up():
            raise ConnectionError("Tor is not running — nothing is fetched without Tor (type: start)")
        jar = os.path.join(self.tmp, "cookies-" + self._iso_user(url))
        proxy = f"socks5h://{self._iso_user(url)}:{self.nonce}@{SOCKS_HOST}:{SOCKS_PORT}"
        cmd = ["curl", "-sS", "-L", "--max-redirs", "8", "--compressed", "--connect-timeout", "75",
               "--max-time", "600" if limit > MAX_PAGE else "150", "--max-filesize", str(limit),
               "--proxy", proxy, "--noproxy", "", "--proto", "=http,https", "--proto-redir", "=http,https",
               "-A", USER_AGENT, "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "-H", "Accept-Language: en-US,en;q=0.5", "-b", jar, "-c", jar,
               "-D", hdr_path, "-o", out_path, "-w", "%{url_effective}\n%{http_code}\n%{content_type}"]
        if head:
            cmd.append("-I")
        if post is not None:
            cmd += ["--data", post]
        cmd += ["--", url]
        env = {k: v for k, v in os.environ.items() if not k.lower().endswith("_proxy")}
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            so, se = p.communicate()
        except KeyboardInterrupt:
            p.kill()
            p.wait()
            raise
        if p.returncode != 0:
            msg = se.decode("utf-8", "replace").strip().replace("curl: ", "")
            hint = ""
            if p.returncode in (7, 97):
                hint = " — onion service offline/unreachable, or Tor still building a circuit"
            elif p.returncode == 28:
                hint = " — timed out (the site is slow or blocks Tor; try: reload or newid)"
            elif p.returncode == 63:
                hint = " — file too large for a page (use: download)"
            raise ConnectionError(f"{msg}{hint}")
        eff, code, ctype = (so.decode("utf-8", "replace").split("\n") + ["", "", ""])[:3]
        return eff or url, int(code or 0), ctype

    def fetch(self, url: str, post: str | None = None) -> Page:
        url = normalise(url)
        body_p, hdr_p = os.path.join(self.tmp, "body"), os.path.join(self.tmp, "hdr")
        for f in (body_p, hdr_p):
            if os.path.exists(f):
                os.remove(f)
        eff, code, ctype = self._curl(url, body_p, hdr_p, post, MAX_PAGE)
        pg = Page(eff)
        pg.status, pg.ctype = code, ctype
        pg.headers = open(hdr_p, "rb").read().decode("iso-8859-1") if os.path.exists(hdr_p) else ""
        pg.body = open(body_p, "rb").read() if os.path.exists(body_p) else b""
        low = ctype.lower()
        sniff = pg.body[:600].lstrip().lower()
        is_html = "html" in low or sniff.startswith((b"<!doctype html", b"<html")) or b"<html" in sniff
        pg.is_text = is_html or low.startswith("text/") or "json" in low or "xml" in low or not low
        if pg.is_text and b"\x00" in pg.body[:2000]:
            pg.is_text = False
        if not pg.is_text:
            pg.title = os.path.basename(urlsplit(eff).path) or "download"
            pg.lines = [f"Binary content ({ctype or 'unknown type'}, {len(pg.body):,} bytes) — not displayed.",
                        "", "Type  save  to store it in the case folder with a SHA-256 evidence record."]
            return pg
        m = re.search(r"charset=([\w-]+)", low) or re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", pg.body[:3000], re.I)
        enc = (m.group(1).decode() if m and isinstance(m.group(1), bytes) else m.group(1)) if m else "utf-8"
        try:
            text = pg.body.decode(enc, "replace")
        except LookupError:
            text = pg.body.decode("utf-8", "replace")
        width = max(40, min(shutil.get_terminal_size((100, 30)).columns - 2, 110))
        if is_html:
            r = Renderer(eff)
            try:
                r.feed(text)
                r.close()
            except Exception:
                pass
            pg.title = re.sub(r"\s+", " ", r.title).strip()
            pg.links = [self._unwrap(u) for u in r.links]
            pg.forms = r.forms
            pg.lines = r.lines(width)
        else:
            pg.title = os.path.basename(urlsplit(eff).path) or eff
            pg.lines = text.splitlines()
        return pg

    @staticmethod
    def _unwrap(u: str) -> str:
        """Search engines wrap results in redirect links — show/visit the real target instead."""
        sp = urlsplit(u)
        q = parse_qs(sp.query)
        if "/search/redirect" in sp.path and q.get("redirect_url"):
            return q["redirect_url"][0]
        if sp.path.rstrip("/") == "/l" and "duckduckgo" in (sp.hostname or "") and q.get("uddg"):
            return q["uddg"][0]
        return u

    # --- navigation ---
    def cur(self) -> Page | None:
        return self.hist[self.idx] if 0 <= self.idx < len(self.hist) else None

    def go(self, url: str, post: str | None = None, push=True):
        host = urlsplit(normalise(url)).hostname or url
        print(D(f"  ⟳ {host} via Tor…"), end="", flush=True)
        t0 = time.time()
        try:
            pg = self.fetch(url, post)
        except KeyboardInterrupt:
            print("\r" + " " * 70 + "\r", end="")
            err("cancelled")
            return
        except (ConnectionError, ValueError, OSError) as e:
            print("\r" + " " * 70 + "\r", end="")
            err(str(e))
            return
        print("\r" + " " * 70 + "\r", end="")
        if push:
            self.hist = self.hist[: self.idx + 1] + [pg]
            self.idx = len(self.hist) - 1
        else:
            self.hist[self.idx] = pg
        self.visited.append((time.strftime("%H:%M:%S"), pg.url, pg.title))
        self.show(first=True, took=time.time() - t0)

    def show(self, first=False, took=None):
        pg = self.cur()
        if not pg:
            return self.home()
        h = max(8, shutil.get_terminal_size((100, 30)).lines - 6)
        if first:
            pg.pos = 0
            lock = G("🔒 onion") if (urlsplit(pg.url).hostname or "").endswith(".onion") else (
                G("🔒 https") if pg.url.startswith("https://") else Y("⚠ http (exit relay can read this)"))
            st = G(str(pg.status)) if 200 <= pg.status < 400 else R(str(pg.status))
            print(G("─" * 78))
            print(f" {B(pg.title or '(untitled)')}")
            print(f" {CY(pg.url)}")
            print(D(f" {lock}  ·  HTTP {st}  ·  {len(pg.body):,} bytes  ·  {len(pg.links)} links"
                    + (f"  ·  {took:.1f}s" if took else "")))
            m = re.search(r"^onion-location:\s*(\S+)", pg.headers, re.I | re.M)
            if m:
                print(Y(f" .onion available → open {m.group(1)}"))
            print(G("─" * 78))
        chunk = pg.lines[pg.pos: pg.pos + h]
        print("\n".join(chunk))
        pg.pos += len(chunk)
        if pg.pos < len(pg.lines):
            print(D(f"── more ({pg.pos}/{len(pg.lines)} lines) — press Enter · number = follow link · help ──"))
        else:
            print(D("── end — number = follow link · links · back · search <words> · help ──"))

    def home(self):
        banner()
        print(B("  Explore. Investigate. Analyze.") + D("   (no JavaScript · per-site circuits · session-only cookies)"))
        print()
        for k, d in (("search <words>", "search onion services (Ahmia)"),
                     ("open <url>", "open any http/https/.onion address"),
                     ("check", "verify traffic really goes through Tor"),
                     ("circuit / newid", "show the Tor circuit / get a new identity"),
                     ("tools", "the 15 OSINT terminal commands"),
                     ("help", "all commands")):
            print(f"  {G(k.ljust(18))}{d}")
        print()

    # --- evidence ---
    def _log(self, url, path, status):
        os.makedirs(self.case, exist_ok=True)
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        log = os.path.join(self.case, "evidence_log.csv")
        new = not os.path.exists(log)
        with open(log, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["utc_time", "url", "http_status", "file", "sha256", "bytes"])
            w.writerow([time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), url, status,
                        os.path.relpath(path, self.case), digest, os.path.getsize(path)])
        os.chmod(path, 0o440)
        print(f"  {G('saved')}  {path}")
        print(f"  {G('sha256')} {digest}")
        info(f"logged in {log}")

    def _name(self, url, default_ext=""):
        sp = urlsplit(url)
        base = os.path.basename(sp.path.rstrip("/")) or "index"
        base = re.sub(r"[^A-Za-z0-9._-]", "_", base)[:60]
        if default_ext and "." not in base:
            base += default_ext
        host = re.sub(r"[^A-Za-z0-9.-]", "_", sp.hostname or "site")[:24]
        return f"{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}_{host}_{base}"

    def save(self):
        pg = self.cur()
        if not pg:
            return err("no page open")
        d = os.path.join(self.case, "pages")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, self._name(pg.url, ".html" if "html" in pg.ctype.lower() else ""))
        with open(path, "wb") as fh:
            fh.write(pg.body)
        with open(path + ".headers.txt", "w", encoding="utf-8") as fh:
            fh.write(f"URL: {pg.url}\n{pg.headers}")
        self._log(pg.url, path, pg.status)

    def download(self, target: str):
        pg = self.cur()
        url = pg.links[int(target) - 1] if target.isdigit() and pg and 0 < int(target) <= len(pg.links) else target
        url = normalise(url)
        d = os.path.join(self.case, "downloads")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, self._name(url))
        print(D(f"  ⇣ downloading via Tor: {url}"))
        try:
            _, code, _ = self._curl(url, path, os.path.join(self.tmp, "dhdr"), None, MAX_DOWNLOAD)
        except KeyboardInterrupt:
            return err("cancelled")
        except (ConnectionError, ValueError) as e:
            return err(str(e))
        self._log(url, path, code)
        run(["file", path], show=False)
        print(Y("  ⚠ Unknown file: analyse it only inside this VM, never open it on your main PC."))

    # --- identity ---
    def newid(self):
        self.nonce = secrets.token_hex(8)
        for f in os.listdir(self.tmp):
            try:
                os.remove(os.path.join(self.tmp, f))
            except OSError:
                pass
        self.hist, self.idx, self.visited = [], -1, []
        ct = control()
        if ct:
            try:
                ct.cmd("SIGNAL NEWNYM")
            except OSError:
                pass
            ct.close()
        ok("New identity", "new circuits, cookies + history wiped")

    def circuit(self):
        ct = control()
        if not ct:
            return err(f"cannot read Tor control socket ({CONTROL_SOCKET}) — is your user in group debian-tor? "
                       "(re-run the installer, then open a new terminal)")
        try:
            pg = self.cur()
            want = self._iso_user(pg.url) if pg else None
            rows = [ln for ln in ct.info("circuit-status").splitlines() if " BUILT " in ln]
            mine = [ln for ln in rows if want and f'SOCKS_USERNAME="{want}"' in ln]
            target = mine[-1:] or [ln for ln in rows if "PURPOSE=GENERAL" in ln][-1:]
            if not target:
                return info("no built circuit yet — open a page first")
            path = target[0].split()[2].split(",")
            print(B(f"  Tor circuit{' for ' + site_of(pg.url) if mine else ' (latest general circuit)'}:"))
            print(f"    {G('●')} This browser")
            onion = bool(pg) and (urlsplit(pg.url).hostname or "").endswith(".onion")
            roles = ["Guard", "Middle", "Exit"] if len(path) <= 3 and not onion else ["Guard"] + ["Relay"] * (len(path) - 1)
            for i, hop in enumerate(path):
                fp, _, nick = hop.lstrip("$").partition("~")
                ip, cc = "?", "??"
                try:
                    m = re.search(r"^r \S+ \S+ \S+ \S+ \S+ (\S+)", ct.info(f"ns/id/{fp}"), re.M)
                    if m:
                        ip = m.group(1)
                        cc = ct.info(f"ip-to-country/{ip}") or "??"
                except OSError:
                    pass
                print(f"    {G('│')}\n    {G('●')} {roles[min(i, len(roles) - 1)]:<7}{nick or fp[:8]:<22}{ip:<17}{cc.upper()}")
            print(f"    {G('│')}\n    {G('●')} {'Onion service (3 more hidden relays)' if onion else (site_of(pg.url) if pg else 'Internet')}")
            info(f"{len(rows)} circuits built · Tor {ct.info('version')}")
        except OSError as e:
            err(str(e))
        finally:
            ct.close()

    def check(self):
        """Tool 05 — curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/"""
        print(D(f"  $ curl --socks5-hostname {SOCKS_HOST}:{SOCKS_PORT} https://check.torproject.org/"))
        try:
            pg = self.fetch("https://check.torproject.org/api/ip")
        except (ConnectionError, ValueError, OSError) as e:
            return bad("Tor check", str(e))
        txt = pg.body.decode("utf-8", "replace")
        ip = re.search(r'"IP"\s*:\s*"([^"]+)"', txt)
        if '"IsTor":true' in txt.replace(" ", ""):
            ok("Tor check", "Congratulations — this browser is using Tor")
            ok("Exit IP", ip.group(1) if ip else "?")
        else:
            bad("Tor check", f"NOT using Tor! ({txt.strip()[:120]})")

    def search_url(self, q: str) -> str | None:
        """Ahmia needs the hidden anti-bot token from its own search form, so read the form first."""
        for base in (AHMIA, AHMIA_ONION):
            try:
                home = self.fetch(base)
            except (ConnectionError, ValueError, OSError):
                continue
            form = next((f for f in home.forms if "search" in f["action"]), None)
            params = {f["name"]: f["value"] for f in form["fields"]} if form else {}
            qname = next((f["name"] for f in (form["fields"] if form else []) if f["ask"]), "q")
            params[qname] = q
            action = form["action"] if form else urljoin(base, "/search/")
            return action + ("&" if "?" in action else "?") + urlencode(params)
        return None

    def search(self, q: str):
        print(D("  ⟳ asking Ahmia via Tor…"), end="\r", flush=True)
        url = self.search_url(q)
        print(" " * 40, end="\r")
        if url:
            self.go(url)
        else:
            err("Ahmia is unreachable right now — try again in a moment (or: newid)")

    def form(self, n: str):
        pg = self.cur()
        if not pg or not pg.forms:
            return err("this page has no forms")
        i = int(n) if n.isdigit() else 1
        if not 0 < i <= len(pg.forms):
            return err(f"form number 1..{len(pg.forms)}")
        f = pg.forms[i - 1]
        data = {}
        for fld in f["fields"]:
            val = fld["value"]
            if fld["ask"]:
                try:
                    if fld["secret"]:
                        import getpass
                        val = getpass.getpass(f"  {fld['label']}: ")
                    else:
                        got = input(f"  {fld['label']}{' [' + val + ']' if val else ''}: ")
                        val = got if got else val
                except (EOFError, KeyboardInterrupt):
                    print()
                    return err("cancelled")
            data[fld["name"]] = val
        if f["method"] == "post":
            self.go(f["action"], post=urlencode(data))
        else:
            self.go(f["action"].split("?")[0] + "?" + urlencode(data))

    # --- bookmarks ---
    def _bm(self):
        return os.path.join(HOME, "bookmarks.txt")

    def bookmark(self):
        pg = self.cur()
        if not pg:
            return err("no page open")
        os.makedirs(HOME, exist_ok=True)
        with open(self._bm(), "a", encoding="utf-8") as fh:
            fh.write(f"{pg.url}\t{pg.title}\n")
        ok("Bookmarked", pg.url)

    def bookmarks(self, pick: str = ""):
        rows = [ln.rstrip("\n").split("\t") for ln in open(self._bm(), encoding="utf-8")] if os.path.exists(self._bm()) else []
        if pick.isdigit() and 0 < int(pick) <= len(rows):
            return self.go(rows[int(pick) - 1][0])
        if not rows:
            return info("no bookmarks yet — open a page and type: bookmark")
        for i, r in enumerate(rows, 1):
            print(f"  {G(str(i).rjust(3))}  {(r[1] if len(r) > 1 else '')[:40]:<40}  {D(r[0])}")
        info("open one with: bookmarks <number>")


# ───────────────────────────────────────────────────────────── the 15 OSINT tools

def run(cmd: list[str], show=True, pipe_to: list[str] | None = None, out_file: str | None = None) -> int:
    """Run a command (no shell — file names from untrusted downloads are never interpreted)."""
    if show:
        s = " ".join(shlex.quote(x) for x in cmd)
        if pipe_to:
            s += " | " + " ".join(shlex.quote(x) for x in pipe_to)
        if out_file:
            s += " > " + shlex.quote(out_file)
        print(D(f"  $ {s}"))
    if not shutil.which(cmd[0]):
        err(f"'{cmd[0]}' is not installed — re-run the installer (dark-osint-install.sh)")
        return 127
    sys.stdout.flush()
    try:
        if pipe_to or out_file:
            p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            data = p1.communicate()[0]
            if pipe_to:
                data = subprocess.run(pipe_to, input=data, stdout=subprocess.PIPE).stdout
            if out_file:
                with open(out_file, "wb") as fh:
                    fh.write(data)
                n = len(data.splitlines())
                print(f"  {G('saved')} {n} line(s) → {out_file}")
            else:
                sys.stdout.write(data.decode("utf-8", "replace") or D("  (no matches)\n"))
            return 0
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print()
        return 130


def monitor(once=False):
    """Tool 07 fallback when nyx is not installed: live Tor monitor from the control socket."""
    ct = control()
    if not ct:
        return err(f"cannot read Tor control socket ({CONTROL_SOCKET}) — user must be in group debian-tor")

    def rate(n):
        return f"{n / 1024:,.1f} KiB/s"

    try:
        prev = None
        while True:
            rd, wr = int(ct.info("traffic/read") or 0), int(ct.info("traffic/written") or 0)
            circs = ct.info("circuit-status").splitlines()
            built = sum(1 for x in circs if " BUILT " in x)
            streams = [x for x in ct.info("stream-status").splitlines() if x.strip()]
            boot = re.search(r"PROGRESS=(\d+)", ct.info("status/bootstrap-phase"))
            guards = sum(1 for x in ct.info("entry-guards").splitlines() if " up" in x)
            dn, up = ((rd - prev[0]), (wr - prev[1])) if prev else (0, 0)
            prev = (rd, wr)
            rows = [G(B("  ▸ Tor Monitor")) + D("   (Ctrl-C to leave)"),
                    f"  Tor        v{ct.info('version')}  {G('(running)')}",
                    f"  Bootstrap  {boot.group(1) if boot else '?'}%",
                    f"  Circuits   {built} {G('(established)')}  /  {len(circs)} total",
                    f"  Streams    {len(streams)} open",
                    f"  Guards     {guards} up",
                    f"  Bandwidth  {G(rate(dn))} ↓   {G(rate(up))} ↑",
                    f"  Total      {rd / 1048576:,.1f} MiB ↓   {wr / 1048576:,.1f} MiB ↑"]
            if once:
                print("\n".join(rows[1:]))
                return
            sys.stdout.write("\033[2J\033[H" + "\n".join(rows) + "\n")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print()
    except OSError as e:
        err(str(e))
    finally:
        ct.close()


TOOLS = [
    ("TOR NETWORK SETUP", [
        ("01", "start", "", "Start Tor service", "sudo systemctl start tor"),
        ("02", "status", "", "Check Tor service", "sudo systemctl status tor"),
        ("03", "verify", "", "Verify Tor configuration", "tor --verify-config"),
        ("04", "port", "", "Check SOCKS proxy port", "ss -lntp | grep 9050")]),
    ("SECURE CONNECTION TESTING", [
        ("05", "check", "", "Test Tor connectivity", "curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/"),
        ("06", "head", "[url]", "Fetch headers through Tor", "torsocks curl -I https://ahmia.fi"),
        ("07", "monitor", "", "Monitor Tor activity", "nyx")]),
    ("ONION INTELLIGENCE", [
        ("08", "onions", "[dir]", "Extract .onion addresses", "grep -RhoE '[a-z2-7]{56}\\.onion' ./case/ | sort -u"),
        ("09", "notes", "[dir] [terms]", "Search threat notes", "grep -RniE 'ransomware|breach|leak' ./case/"),
        ("10", "iocs", "[dir]", "Save unique onion IOCs", "grep -RhoE '[a-z2-7]{56}\\.onion' ./case/ | sort -u > onion_iocs.txt")]),
    ("EVIDENCE INVESTIGATION", [
        ("11", "ftype", "<file>", "Identify file type", "file ./case/sample.html"),
        ("12", "meta", "<file>", "Extract metadata", "exiftool ./case/sample.pdf"),
        ("13", "hash", "<file>", "Calculate file hash", "sha256sum ./case/sample.pdf")]),
    ("ADVANCED THREAT INTELLIGENCE", [
        ("14", "urls", "<file>", "Extract URLs & onion links", "strings -n 8 ./case/sample.bin | grep -Ei 'https?://|\\.onion'"),
        ("15", "indicators", "<json>", "Read threat indicators from JSON", "jq -r '.indicators[]?' ./case/report.json")]),
]
TOOL_NAMES = {t[1] for _, ts in TOOLS for t in ts}
TOOL_NUM = {t[0]: t[1] for _, ts in TOOLS for t in ts}


def show_tools():
    print()
    for sec, ts in TOOLS:
        print(G(B(f"  {sec}")))
        for num, name, args, desc, cmd in ts:
            print(f"   {G(num)}  {B((name + ' ' + args).ljust(22))}{desc}")
            print(D(f"       $ {cmd}"))
        print()
    print(R("  ⚠ Use only on data you have legally obtained, for research, analysis or threat intelligence."))
    print()


def tool(br: Browser, name: str, args: list[str]) -> None:
    case = br.case
    name = TOOL_NUM.get(name.zfill(2), name) if name.isdigit() else name
    need_file = name in ("ftype", "meta", "hash", "urls", "indicators")
    if need_file:
        if not args:
            return err(f"usage: {name} <file>")
        path = os.path.expanduser(args[0])
        if not os.path.isfile(path) and os.path.isfile(os.path.join(case, args[0])):
            path = os.path.join(case, args[0])
        if not os.path.isfile(path):
            return err(f"file not found: {args[0]}")
    target = os.path.expanduser(args[0]) if args and not need_file else case
    if name in ("onions", "notes", "iocs"):
        os.makedirs(case, exist_ok=True)
        if not os.path.exists(target):
            return err(f"folder not found: {target}")
    if name == "start":
        (ok if start_tor() else bad)("Tor", "Connected" if socks_up() else "could not start")
    elif name == "status":
        run(["systemctl", "status", "tor", "tor@default", "--no-pager", "-n", "5"])
    elif name == "verify":
        run(["tor", "--verify-config"], pipe_to=["grep", "-vE", r"^\s*$"])
    elif name == "port":
        run(["ss", "-lntp"], pipe_to=["grep", str(SOCKS_PORT)])
    elif name == "check":
        br.check()
    elif name == "head":
        url = normalise(args[0]) if args else "https://ahmia.fi"
        run(["torsocks", "curl", "-sS", "-I", "-A", USER_AGENT, "--max-time", "120", "--", url])
    elif name == "monitor":
        if shutil.which("nyx") and sys.stdin.isatty():
            run(["nyx", "-s", CONTROL_SOCKET])
        else:
            monitor(once=not sys.stdout.isatty())
    elif name == "onions":
        run(["grep", "-RhoE", ONION_RE, target], pipe_to=["sort", "-u"])
    elif name == "notes":
        terms = args[1] if len(args) > 1 else "ransomware|breach|leak"
        run(["grep", "-RniE", "--color=always" if TTY else "--color=never", terms, target])
    elif name == "iocs":
        run(["grep", "-RhoE", "--exclude=onion_iocs.txt", ONION_RE, target], pipe_to=["sort", "-u"],
            out_file=os.path.join(case, "onion_iocs.txt"))
    elif name == "ftype":
        run(["file", path])
    elif name == "meta":
        run(["exiftool", path])
    elif name == "hash":
        run(["sha256sum", path])
    elif name == "urls":
        run(["strings", "-n", "8", path], pipe_to=["grep", "-aEi", r"https?://|\.onion"])
    elif name == "indicators":
        run(["jq", "-r", ".indicators[]?", path])


# ───────────────────────────────────────────────────────────── shell

HELP = """
  BROWSE
    open <url> | <url>      open a page (http, https, .onion)        search <words>   onion search (Ahmia)
    <number>                follow link number                        form [n]         fill in + submit a form
    Enter                   next screen of the page                   links [filter]   list links on the page
    back / forward / reload
    top / page              re-show the page from the top             find <text>      search inside the page
    history                 pages visited this session                bookmark / bookmarks [n]
    info / source           response headers / raw HTML               home             start screen

  IDENTITY
    check                   am I really on Tor? (exit IP)             circuit          relays used for this site
    newid                   new identity: new circuits, wipe cookies + history

  EVIDENCE
    save                    save current page + headers to the case folder, SHA-256 logged
    download <n|url>        download a file through Tor into the case folder
    case [dir]              show / change the case folder

  OSINT TOOLS               tools  = list all 15       (use the name or the number:  hash file.pdf  /  13 file.pdf)
    start status verify port check head monitor · onions notes iocs · ftype meta hash · urls indicators

    quit                    exit (cookies and history are wiped)
"""


def repl(br: Browser, first_url: str | None):
    try:
        import readline
        hist = os.path.join(HOME, ".cmd_history")
        os.makedirs(HOME, exist_ok=True)
        try:
            readline.read_history_file(hist)
        except OSError:
            pass
        readline.set_history_length(300)
        atexit.register(lambda: readline.write_history_file(hist))
    except ImportError:
        pass
    if not socks_up():
        print(D("  Tor is not running — starting it…"))
        start_tor()
    if first_url:
        br.go(first_url)
    else:
        br.home()
    while True:
        pg = br.cur()
        where = (urlsplit(pg.url).hostname or "")[:28] if pg else "home"
        if len(where) > 27:
            where = where[:12] + "…" + where[-12:]
        try:
            raw = input(f"{G('dark-osint')} {D('[' + where + ']')} {G('›')} ").strip()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        try:
            if not raw:
                if pg and pg.pos < len(pg.lines):
                    br.show()
                continue
            cmd, _, rest = raw.partition(" ")
            rest = rest.strip()
            low = cmd.lower()
            if low in ("q", "quit", "exit"):
                break
            if raw.isdigit() and pg:
                n = int(raw)
                if 0 < n <= len(pg.links):
                    br.go(pg.links[n - 1])
                else:
                    err(f"no link {n} on this page (1..{len(pg.links)})")
            elif low in ("o", "open", "go"):
                br.go(rest) if rest else err("usage: open <url>")
            elif low in ("s", "search"):
                br.search(rest) if rest else err("usage: search <words>")
            elif low in ("b", "back"):
                if br.idx > 0:
                    br.idx -= 1
                    br.show(first=True)
                else:
                    info("no previous page")
            elif low in ("f", "forward"):
                if br.idx < len(br.hist) - 1:
                    br.idx += 1
                    br.show(first=True)
                else:
                    info("no next page")
            elif low in ("r", "reload"):
                br.go(pg.url, push=False) if pg else br.home()
            elif low in ("top", "page"):
                br.show(first=True)
            elif low == "home":
                br.home()
            elif low in ("l", "links"):
                if not pg:
                    info("no page open")
                for i, u in enumerate(pg.links if pg else [], 1):
                    if not rest or rest.lower() in u.lower():
                        print(f"  {G(str(i).rjust(3))}  {u}")
            elif low == "find":
                hits = [ln for ln in (pg.lines if pg else []) if rest.lower() in ln.lower()] if rest else []
                print("\n".join(f"  {h}" for h in hits) if hits else D("  (not found)"))
            elif low == "history":
                for t, u, ti in br.visited:
                    print(f"  {D(t)}  {ti[:36]:<36}  {D(u)}")
            elif low == "bookmark":
                br.bookmark()
            elif low == "bookmarks":
                br.bookmarks(rest)
            elif low == "info":
                print(pg.headers.strip() if pg else D("  no page open"))
            elif low == "source":
                print(pg.body.decode("utf-8", "replace") if pg and pg.is_text else D("  no text page open"))
            elif low == "form":
                br.form(rest)
            elif low == "save":
                br.save()
            elif low in ("download", "dl"):
                br.download(rest) if rest else err("usage: download <link number | url>")
            elif low == "case":
                if rest:
                    br.case = os.path.abspath(os.path.expanduser(rest))
                    os.makedirs(br.case, exist_ok=True)
                ok("Case folder", br.case)
            elif low in ("newid", "newnym", "identity"):
                br.newid()
            elif low in ("circuit", "circ"):
                br.circuit()
            elif low in ("ip",):
                br.check()
            elif low == "tools":
                show_tools()
            elif low in ("help", "?", "h"):
                print(HELP)
            elif low in TOOL_NAMES or (low.isdigit() and low.zfill(2) in TOOL_NUM):
                tool(br, low, shlex.split(rest) if rest else [])
            elif " " not in raw and ("." in raw or raw.startswith(("http://", "https://"))):
                br.go(raw)
            else:
                err(f"unknown command '{cmd}' — type help   (to search: search {raw})")
        except KeyboardInterrupt:
            print()
        except Exception as e:  # keep the browser alive whatever a hostile page does
            err(f"{type(e).__name__}: {e}")
    print(D("  session closed — cookies and history wiped."))


def main(argv: list[str]) -> int:
    case = os.path.join(HOME, "case")
    if "--case" in argv:
        i = argv.index("--case")
        if i + 1 >= len(argv):
            err("--case needs a folder")
            return 2
        case = argv[i + 1]
        del argv[i:i + 2]
    br = Browser(case)
    if not argv:
        repl(br, None)
        return 0
    a = argv[0]
    if a in ("-h", "--help", "help"):
        banner()
        print("  Usage:")
        print("    dark-osint                    start the Tor terminal browser")
        print("    dark-osint <url>              start and open a page")
        print("    dark-osint dump <url>         print a page as text and exit (scripts)")
        print("    dark-osint search <words>     print onion search results and exit")
        print("    dark-osint tools              list the 15 OSINT commands")
        print("    dark-osint <tool> [args]      run one tool, e.g.  dark-osint hash sample.pdf")
        print("    dark-osint --case <dir> …     use another case folder (default ~/dark-osint/case)")
        print(HELP)
        return 0
    if a in ("-V", "--version"):
        print(f"dark-osint {VERSION}")
        return 0
    if a == "tools":
        show_tools()
        return 0
    if a in ("dump", "search"):
        if len(argv) < 2:
            err(f"usage: dark-osint {a} <{'url' if a == 'dump' else 'words'}>")
            return 2
        if not start_tor(quiet=True):
            err("Tor is not running")
            return 1
        try:
            url = argv[1] if a == "dump" else br.search_url(" ".join(argv[1:]))
            if not url:
                err("Ahmia is unreachable right now")
                return 1
            pg = br.fetch(url)
        except (ConnectionError, ValueError, OSError) as e:
            err(str(e))
            return 1
        print(f"{pg.title}\n{pg.url}  [HTTP {pg.status}]\n")
        print("\n".join(pg.lines))
        if pg.links:
            print("\nLinks:")
            for i, u in enumerate(pg.links, 1):
                print(f"  [{i}] {u}")
        return 0
    if a in TOOL_NAMES or (a.isdigit() and a.zfill(2) in TOOL_NUM):
        tool(br, a, argv[1:])
        return 0
    repl(br, a)
    return 0


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)   # `dark-osint … | head` exits quietly
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print()
        sys.exit(130)
