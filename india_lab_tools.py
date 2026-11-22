"""
India Lab — the LIVE arsenal.  This is what makes the lab actually *do* things instead of
just showing text: every tool here runs for real on the connected Kali box (via the same
SSH shell the Kali tab uses), and when a command fails the AI auto-diagnoses and re-runs a
fixed version once — so the user gets a working result in one shot.

Everything targets the user's OWN lab / localhost — the same ethical boundary as the Kali tab.
"""

import re

import llm

# ---------------------------------------------------------------- the elite arsenal
# World-class tools. Each "demo" is a real command that produces real output immediately
# (proves the tool is installed and working); "gui" ones open in the Kali Desktop instead.
TOP_TOOLS = [
    {"id": "nmap",       "name": "Nmap",        "icon": "📡", "cat": "Recon / Scanning",
     "about": "The #1 network mapper — hosts, ports, services, versions, OS.",
     "demo": "nmap -sV -T4 127.0.0.1"},
    {"id": "metasploit", "name": "Metasploit",  "icon": "🎯", "cat": "Exploitation",
     "about": "The world's biggest exploit framework — 2000+ exploits & payloads.",
     "demo": "msfconsole -q -x 'version; db_status; exit'"},
    {"id": "sqlmap",     "name": "sqlmap",      "icon": "💉", "cat": "Web / Database",
     "about": "Automatic SQL-injection detection & database takeover.",
     "demo": "sqlmap --version && sqlmap --hh 2>&1 | head -20"},
    {"id": "burpsuite",  "name": "Burp Suite",  "icon": "🕷️", "cat": "Web proxy",
     "about": "The industry-standard web app proxy & scanner (GUI).",
     "gui": "burpsuite"},
    {"id": "hydra",      "name": "Hydra",       "icon": "🔑", "cat": "Password attacks",
     "about": "Fast network login brute-forcer — SSH, FTP, HTTP, 50+ protocols.",
     "demo": "hydra -h 2>&1 | head -25"},
    {"id": "hashcat",    "name": "Hashcat",     "icon": "🧮", "cat": "Password cracking",
     "about": "The fastest GPU/CPU password & hash cracker on earth.",
     "demo": "hashcat --version && hashcat -b -m 0 --quiet 2>&1 | head -15"},
    {"id": "wireshark",  "name": "Wireshark",   "icon": "🦈", "cat": "Sniffing",
     "about": "The world's foremost network protocol analyser (GUI).",
     "gui": "wireshark"},
    {"id": "nuclei",     "name": "Nuclei",      "icon": "⚡", "cat": "Vuln scanning",
     "about": "Fast, template-based vulnerability scanner (10k+ checks).",
     "demo": "nuclei -version && nuclei -tc 2>/dev/null; echo 'templates ready'"},
    {"id": "john",       "name": "John",        "icon": "🧵", "cat": "Password cracking",
     "about": "John the Ripper — the classic password cracker.",
     "demo": "john --list=build-info 2>&1 | head -12"},
    {"id": "aircrack",   "name": "Aircrack-ng", "icon": "📶", "cat": "Wireless",
     "about": "The complete Wi-Fi (WEP/WPA/WPA2) security auditing suite.",
     "demo": "aircrack-ng --help 2>&1 | head -18"},
]
TOOL_BY_ID = {t["id"]: t for t in TOP_TOOLS}

# A real, safe starter command for every tool a domain might list (localhost / lab targets).
LAB = "127.0.0.1"
STARTERS = {
    "nmap": f"nmap -sV -T4 {LAB}",
    "netcat": f"nc -zv {LAB} 1-100 2>&1 | head -20",
    "tshark": "tshark -D",
    "metasploit": "msfconsole -q -x 'version; exit'",
    "sqlmap": "sqlmap --version",
    "nikto": f"nikto -Version 2>&1 | head -5",
    "whatweb": "whatweb --version",
    "feroxbuster": "feroxbuster --version",
    "wfuzz": "wfuzz --version 2>&1 | head -3",
    "burpsuite": "echo 'Burp Suite is a GUI tool — open it from the 🐉 Kali Desktop (Kali tab).'",
    "hydra": "hydra -h 2>&1 | head -20",
    "medusa": "medusa -h 2>&1 | head -12",
    "ncrack": "ncrack --version 2>&1 | head -3",
    "ophcrack": "echo 'ophcrack is a GUI tool — open it from the Kali Desktop.'",
    "john": "john --list=build-info 2>&1 | head -10",
    "hashcat": "hashcat --version",
    "hashid": "hashid --help 2>&1 | head -8",
    "aircrack-ng": "aircrack-ng --help 2>&1 | head -15",
    "airodump-ng": "airodump-ng --help 2>&1 | head -12",
    "nuclei": "nuclei -version",
    "ffuf": "ffuf -V",
    "gobuster": "gobuster version",
    "wpscan": "wpscan --version 2>&1 | head -6",
    "wireshark": "echo 'Wireshark is a GUI tool — open it from the 🐉 Kali Desktop (Kali tab).'",
    "bettercap": "bettercap -version 2>&1 | head -3",
    "responder": "responder --version 2>&1 | head -3",
    "recon-ng": "recon-ng --version 2>&1 | head -3",
    "theharvester": "theHarvester --help 2>&1 | head -12",
    "binwalk": "binwalk --help 2>&1 | head -10",
    "volatility": "vol -h 2>&1 | head -10",
    "ghidra": "echo 'Ghidra is a GUI tool — open it from the 🐉 Kali Desktop (Kali tab).'",
    "radare2": "r2 -version",
    "impacket": "impacket-secretsdump -h 2>&1 | head -10",
    "netexec": "netexec --version 2>&1 | head -3",
    "bloodhound": "echo 'BloodHound is a GUI tool — open it from the Kali Desktop.'",
    "nmap-scripts": f"nmap --script vuln {LAB}",
}


def starter_for(tool: str) -> str:
    t = (tool or "").strip().lower()
    return STARTERS.get(t) or STARTERS.get(t.replace(" ", "-")) or f"{t} --help 2>&1 | head -15"


# ================================================================ FULL NETHUNTER / KALIGPT ARSENAL
# Everything the Kali NetHunter 2026 cheat-sheets promise, grouped like the carousel. Each entry maps
# a tool to (1) the apt package that installs it and (2) the binary we check with `command -v` to prove
# it is really there. This is what makes the "100% work" promise true: install_all() installs them all,
# readiness() shows a green/red grid, and every tool has a safe starter command above.
#
#   {id, name, pkg (apt package), bin (binary to verify), cat (category), gui (bool)}
ARSENAL = [
    # ── Recon / Network scanning ───────────────────────────────────────────────
    {"id": "nmap",        "name": "Nmap",          "pkg": "nmap",                 "bin": "nmap",        "cat": "Recon / Scanning"},
    {"id": "masscan",     "name": "Masscan",       "pkg": "masscan",              "bin": "masscan",     "cat": "Recon / Scanning"},
    {"id": "netdiscover", "name": "Netdiscover",   "pkg": "netdiscover",          "bin": "netdiscover", "cat": "Recon / Scanning"},
    {"id": "netcat",      "name": "Netcat",        "pkg": "netcat-traditional",   "bin": "nc",          "cat": "Recon / Scanning"},
    {"id": "hping3",      "name": "hping3",        "pkg": "hping3",               "bin": "hping3",      "cat": "Recon / Scanning"},
    {"id": "dnsrecon",    "name": "DNSRecon",      "pkg": "dnsrecon",             "bin": "dnsrecon",    "cat": "Recon / Scanning"},
    {"id": "theharvester","name": "theHarvester",  "pkg": "theharvester",         "bin": "theHarvester","cat": "Recon / Scanning"},
    {"id": "recon-ng",    "name": "Recon-ng",      "pkg": "recon-ng",             "bin": "recon-ng",    "cat": "Recon / Scanning"},
    {"id": "enum4linux",  "name": "enum4linux",    "pkg": "enum4linux",           "bin": "enum4linux",  "cat": "Recon / Scanning"},
    # ── Vulnerability scanning ─────────────────────────────────────────────────
    {"id": "nikto",       "name": "Nikto",         "pkg": "nikto",                "bin": "nikto",       "cat": "Vuln scanning"},
    {"id": "nuclei",      "name": "Nuclei",        "pkg": "nuclei",               "bin": "nuclei",      "cat": "Vuln scanning"},
    {"id": "wpscan",      "name": "WPScan",        "pkg": "wpscan",               "bin": "wpscan",      "cat": "Vuln scanning"},
    {"id": "whatweb",     "name": "WhatWeb",       "pkg": "whatweb",              "bin": "whatweb",     "cat": "Vuln scanning"},
    {"id": "gobuster",    "name": "Gobuster",      "pkg": "gobuster",             "bin": "gobuster",    "cat": "Vuln scanning"},
    {"id": "ffuf",        "name": "ffuf",          "pkg": "ffuf",                 "bin": "ffuf",        "cat": "Vuln scanning"},
    {"id": "feroxbuster", "name": "feroxbuster",   "pkg": "feroxbuster",          "bin": "feroxbuster", "cat": "Vuln scanning"},
    {"id": "dirb",        "name": "dirb",          "pkg": "dirb",                 "bin": "dirb",        "cat": "Vuln scanning"},
    {"id": "wfuzz",       "name": "wfuzz",         "pkg": "wfuzz",                "bin": "wfuzz",       "cat": "Vuln scanning"},
    # ── Exploitation ───────────────────────────────────────────────────────────
    {"id": "metasploit",  "name": "Metasploit",    "pkg": "metasploit-framework", "bin": "msfconsole",  "cat": "Exploitation"},
    {"id": "searchsploit","name": "SearchSploit",  "pkg": "exploitdb",            "bin": "searchsploit","cat": "Exploitation"},
    {"id": "sqlmap",      "name": "sqlmap",        "pkg": "sqlmap",               "bin": "sqlmap",      "cat": "Exploitation"},
    {"id": "netexec",     "name": "NetExec",       "pkg": "netexec",              "bin": "netexec",     "cat": "Exploitation"},
    {"id": "impacket",    "name": "Impacket",      "pkg": "impacket-scripts",     "bin": "impacket-secretsdump", "cat": "Exploitation"},
    {"id": "evil-winrm",  "name": "Evil-WinRM",    "pkg": "evil-winrm",           "bin": "evil-winrm",  "cat": "Exploitation"},
    {"id": "setoolkit",   "name": "SET Toolkit",   "pkg": "set",                  "bin": "setoolkit",   "cat": "Exploitation"},
    # ── Password / hash cracking ───────────────────────────────────────────────
    {"id": "hydra",       "name": "Hydra",         "pkg": "hydra",                "bin": "hydra",       "cat": "Password attacks"},
    {"id": "john",        "name": "John the Ripper","pkg": "john",                "bin": "john",        "cat": "Password attacks"},
    {"id": "hashcat",     "name": "Hashcat",       "pkg": "hashcat",              "bin": "hashcat",     "cat": "Password attacks"},
    {"id": "medusa",      "name": "Medusa",        "pkg": "medusa",               "bin": "medusa",      "cat": "Password attacks"},
    {"id": "ncrack",      "name": "Ncrack",        "pkg": "ncrack",               "bin": "ncrack",      "cat": "Password attacks"},
    {"id": "crunch",      "name": "Crunch",        "pkg": "crunch",               "bin": "crunch",      "cat": "Password attacks"},
    {"id": "cewl",        "name": "CeWL",          "pkg": "cewl",                 "bin": "cewl",        "cat": "Password attacks"},
    {"id": "hashid",      "name": "hashid",        "pkg": "hashid",               "bin": "hashid",      "cat": "Password attacks"},
    # ── Wireless / Wi-Fi / Bluetooth / Wardriving ──────────────────────────────
    {"id": "aircrack-ng", "name": "Aircrack-ng",   "pkg": "aircrack-ng",          "bin": "aircrack-ng", "cat": "Wireless"},
    {"id": "wifite",      "name": "Wifite",        "pkg": "wifite",               "bin": "wifite",      "cat": "Wireless"},
    {"id": "reaver",      "name": "Reaver",        "pkg": "reaver",               "bin": "reaver",      "cat": "Wireless"},
    {"id": "pixiewps",    "name": "PixieWPS",      "pkg": "pixiewps",             "bin": "pixiewps",    "cat": "Wireless"},
    {"id": "kismet",      "name": "Kismet",        "pkg": "kismet",               "bin": "kismet",      "cat": "Wireless / Wardriving"},
    {"id": "gpsd",        "name": "GPSd (wardrive)","pkg": "gpsd",                "bin": "gpsd",        "cat": "Wireless / Wardriving"},
    {"id": "bluez",       "name": "BlueZ (Bluetooth)","pkg": "bluez",             "bin": "bluetoothctl","cat": "Bluetooth"},
    {"id": "spooftooph",  "name": "Spooftooph",    "pkg": "spooftooph",           "bin": "spooftooph",  "cat": "Bluetooth"},
    {"id": "macchanger",  "name": "macchanger",    "pkg": "macchanger",           "bin": "macchanger",  "cat": "Wireless"},
    # ── Sniffing / MITM ────────────────────────────────────────────────────────
    {"id": "tshark",      "name": "tshark",        "pkg": "tshark",               "bin": "tshark",      "cat": "Sniffing / MITM"},
    {"id": "tcpdump",     "name": "tcpdump",       "pkg": "tcpdump",              "bin": "tcpdump",     "cat": "Sniffing / MITM"},
    {"id": "bettercap",   "name": "Bettercap",     "pkg": "bettercap",            "bin": "bettercap",   "cat": "Sniffing / MITM"},
    {"id": "responder",   "name": "Responder",     "pkg": "responder",            "bin": "responder",   "cat": "Sniffing / MITM"},
    {"id": "ettercap",    "name": "Ettercap",      "pkg": "ettercap-text-only",   "bin": "ettercap",    "cat": "Sniffing / MITM"},
    # ── Forensics / Reversing ──────────────────────────────────────────────────
    {"id": "binwalk",     "name": "Binwalk",       "pkg": "binwalk",              "bin": "binwalk",     "cat": "Forensics / RE"},
    {"id": "radare2",     "name": "radare2",       "pkg": "radare2",              "bin": "r2",          "cat": "Forensics / RE"},
    {"id": "foremost",    "name": "Foremost",      "pkg": "foremost",             "bin": "foremost",    "cat": "Forensics / RE"},
    {"id": "exiftool",    "name": "ExifTool",      "pkg": "libimage-exiftool-perl","bin": "exiftool",   "cat": "Forensics / RE"},
    # ── GUI tools (install, but open from the 🐉 Kali Desktop) ──────────────────
    {"id": "wireshark",   "name": "Wireshark",     "pkg": "wireshark",            "bin": "wireshark",   "cat": "GUI", "gui": True},
    {"id": "burpsuite",   "name": "Burp Suite",    "pkg": "burpsuite",            "bin": "burpsuite",   "cat": "GUI", "gui": True},
]
ARSENAL_BY_ID = {t["id"]: t for t in ARSENAL}

# Extra safe starter commands for the newly added tools (localhost / lab-only, non-interactive).
STARTERS.update({
    "masscan": "masscan --version 2>&1 | head -4",
    "netdiscover": "netdiscover -h 2>&1 | head -12",
    "hping3": "hping3 --version 2>&1 | head -4",
    "dnsrecon": "dnsrecon --version 2>&1 | head -3 || dnsrecon -h 2>&1 | head -8",
    "enum4linux": "enum4linux -h 2>&1 | head -12",
    "searchsploit": "searchsploit --version 2>&1 | head -4 && searchsploit -u 2>&1 | tail -3",
    "netexec": "netexec --version 2>&1 | head -3",
    "evil-winrm": "evil-winrm --version 2>&1 | head -3",
    "setoolkit": "echo 'SET is interactive — launch with: sudo setoolkit (own lab only).'",
    "crunch": "crunch 1 1 abc 2>&1 | head -6",
    "cewl": "cewl --help 2>&1 | head -10",
    "wifite": "wifite --help 2>&1 | head -15",
    "reaver": "reaver -h 2>&1 | head -12",
    "pixiewps": "pixiewps --help 2>&1 | head -10",
    "kismet": "kismet --version 2>&1 | head -4",
    "gpsd": "gpsd --version 2>&1 | head -4",
    "bluez": "bluetoothctl --version 2>&1 | head -3",
    "spooftooph": "spooftooph -h 2>&1 | head -10",
    "macchanger": "macchanger --help 2>&1 | head -10",
    "tcpdump": "tcpdump --version 2>&1 | head -4",
    "ettercap": "ettercap --version 2>&1 | head -4",
    "foremost": "foremost -V 2>&1 | head -3",
    "exiftool": "exiftool -ver",
    "dirb": "dirb 2>&1 | head -8",
})


def _pkg_list() -> list:
    """Unique apt packages for the whole arsenal, in a stable order."""
    seen, out = set(), []
    for t in ARSENAL:
        p = t["pkg"]
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def install_all_command() -> str:
    """One non-interactive command that updates apt and installs the ENTIRE arsenal.
    `DEBIAN_FRONTEND=noninteractive` + `|| true` on update so a slow mirror never blocks the install,
    and `--no-install-recommends` keeps it lean. Works on Kali and NetHunter (both Debian/apt)."""
    pkgs = " ".join(_pkg_list())
    return (
        "sudo DEBIAN_FRONTEND=noninteractive apt-get update -y || true; "
        "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "
        f"{pkgs}; "
        "echo '---DONE---'; echo 'Arsenal install attempted. Run the readiness check to confirm.'"
    )


def ensure_command(tool_id: str) -> str:
    """Install ONE tool if its binary is missing, then prove it's there."""
    t = ARSENAL_BY_ID.get(tool_id)
    if not t:
        return f"echo 'Unknown tool: {tool_id}'"
    return (f"command -v {t['bin']} >/dev/null 2>&1 || "
            f"sudo DEBIAN_FRONTEND=noninteractive apt-get install -y {t['pkg']}; "
            f"command -v {t['bin']} && echo 'READY: {t['name']}' || echo 'MISSING: {t['name']}'")


# A single marker line per tool: "<id>|<name>|<cat>|OK" or "...|NO". Easy to parse from one SSH run.
def readiness_command() -> str:
    checks = []
    for t in ARSENAL:
        checks.append(
            f"command -v {t['bin']} >/dev/null 2>&1 "
            f"&& echo '{t['id']}|{t['name']}|{t['cat']}|OK' "
            f"|| echo '{t['id']}|{t['name']}|{t['cat']}|NO'"
        )
    return "; ".join(checks)


def parse_readiness(output: str) -> list:
    """Turn the readiness_command output into [{id,name,cat,ok}] rows."""
    rows = []
    for line in (output or "").splitlines():
        line = line.strip()
        if line.count("|") == 3 and line.endswith(("|OK", "|NO")):
            tid, name, cat, state = line.split("|")
            rows.append({"id": tid, "name": name, "cat": cat, "ok": state == "OK"})
    return rows


def readiness_html(rows: list) -> str:
    """A compact green/red grid of the arsenal, grouped by category."""
    if not rows:
        return ("<div class='nh-ready-empty'>Readiness innum check pannala. "
                "'✅ Check readiness' press pannu — Kali-la ella tool-um irukka nu grid kaamikum.</div>")
    ok = sum(1 for r in rows if r["ok"])
    total = len(rows)
    pct = int(round(ok * 100 / total)) if total else 0
    bar = (f"<div class='nh-ready-bar'><div class='nh-ready-fill' style='width:{pct}%'></div></div>"
           f"<div class='nh-ready-pct'>{ok}/{total} ready · <b>{pct}%</b></div>")
    cats, order = {}, []
    for r in rows:
        if r["cat"] not in cats:
            cats[r["cat"]] = []
            order.append(r["cat"])
        cats[r["cat"]].append(r)
    blocks = []
    for cat in order:
        chips = "".join(
            f"<span class='nh-chip {'ok' if r['ok'] else 'no'}'>"
            f"{'✅' if r['ok'] else '⬇️'} {r['name']}</span>"
            for r in cats[cat])
        blocks.append(f"<div class='nh-cat'><div class='nh-cat-t'>{cat}</div>"
                      f"<div class='nh-chips'>{chips}</div></div>")
    missing = [r["name"] for r in rows if not r["ok"]]
    foot = ("<div class='nh-ready-foot ok'>🎉 Ella tool-um ready — 100%. Sollu, Nanban run pannidum.</div>"
            if not missing else
            f"<div class='nh-ready-foot no'>⬇️ {len(missing)} tool install aaganum: "
            f"{', '.join(missing[:12])}{'…' if len(missing) > 12 else ''}. "
            "'🔧 Install &amp; verify ALL' press pannu.</div>")
    return f"<div class='nh-ready'>{bar}{''.join(blocks)}{foot}</div>"


def install_all(auto_fix: bool = False):
    """Stream the whole-arsenal install on Kali (reuses smart_run — same safety + one-shot exec)."""
    yield ("🔧 **Full arsenal install** starting on Kali… idhu konja neram edukkum "
           "(apt download). Mudinjadhum readiness check panni confirm pannu.\n")
    for out in smart_run(install_all_command(), auto_fix=auto_fix):
        yield out


def check_readiness():
    """Run the readiness probe on Kali and return parsed rows (for the HTML grid)."""
    import kali_panel as kp
    import servers
    try:
        host = servers.connect(kp.KALI)
    except Exception:
        return None
    try:
        r = host.run(readiness_command(), timeout=90)
        return parse_readiness(kp._clean_term(r.output))
    except Exception:
        return None


# ---------------------------------------------------------------- AI command + auto-fix

_LAB_SYS = (
    "You are an elite Kali Linux operator for the user's OWN lab and localhost (127.0.0.1) only. "
    "Turn the request into ONE single shell command that runs non-interactively and finishes. "
    "Prefer real Kali tools. If a target is not given, use 127.0.0.1 or a local lab target. "
    "Output ONLY the command — no explanation, no markdown, no backticks, no leading $."
)
_FIX_SYS = (
    "A Kali Linux command just FAILED. Given the command and its error output, reply with ONE "
    "corrected shell command that will succeed. If a tool was 'not found', install it first with "
    "'sudo apt-get install -y <package> && <original command>'. Fix wrong flags, wrong paths, or "
    "add non-interactive flags as needed. Output ONLY the command — no explanation, no backticks."
)

# Strong, unambiguous failure signatures (avoid matching tools that merely print the word 'error').
_FAIL_RE = re.compile(
    r"(command not found|not found|no such file|permission denied|could not resolve|"
    r"could not open|unable to (?:open|connect|resolve|locate)|unknown option|unrecognized option|"
    r"invalid option|not installed|traceback \(most recent|ModuleNotFoundError|"
    r"E: Unable to locate|E: Could not|segmentation fault|fatal error)",
    re.I,
)


def _one_line(messages) -> str:
    text = ""
    try:
        for chunk in llm.chat(messages, tools=None, options={"temperature": 0.1}):
            piece = getattr(getattr(chunk, "message", None), "content", "") or ""
            text += piece
    except Exception as e:
        return f"# AI not reachable: {e}"
    line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    return line.strip("`").removeprefix("$ ").strip()


def ai_to_command(request: str) -> str:
    request = (request or "").strip()
    if not request:
        return ""
    return _one_line([{"role": "system", "content": _LAB_SYS}, {"role": "user", "content": request}])


def ai_fix_command(command: str, output: str) -> str:
    out = (output or "")[-1600:]
    return _one_line([{"role": "system", "content": _FIX_SYS},
                      {"role": "user", "content": f"Command:\n{command}\n\nError output:\n{out}"}])


def looks_failed(output: str) -> bool:
    return bool(_FAIL_RE.search((output or "")[-2000:]))


def _stream_exec(host, command: str, timeout: int = 180):
    """Run ONE command on Kali as an independent one-shot (no shared interactive shell, so the
    India Lab never queues behind the Kali tab). Yields (growing_output, final_output)."""
    import queue
    import threading

    import kali_panel as kp
    q: "queue.Queue" = queue.Queue()
    done = {}

    def worker():
        try:
            r = host.run(command, timeout=timeout, on_line=lambda ln: q.put(ln))
            done["out"] = r.output
        except Exception as e:
            q.put(f"[error: {e}]")
            done["out"] = ""
        finally:
            q.put(None)

    threading.Thread(target=worker, daemon=True).start()
    acc = []
    while True:
        item = q.get()
        if item is None:
            break
        acc.append(kp._clean_term(item))
        yield "\n".join(acc), None
    yield "\n".join(acc), kp._clean_term(done.get("out", "\n".join(acc)))


def smart_run(command: str, auto_fix: bool = True):
    """Run a command on Kali; if it clearly fails, ask the AI for a fix and run that ONCE.
    Yields the growing terminal transcript (strings). Independent one-shot exec + the Kali safety net."""
    import kali_panel as kp
    import servers

    command = (command or "").strip()
    if not command:
        yield "Oru command type pannu (illa ⚡ tool button press pannu)."
        return
    if kp._blocked(command):
        yield f"$ {command}\n\n⛔ Blocked: idhu disk-wipe / crash maadhiri dangerous command."
        return
    try:
        host = servers.connect(kp.KALI)
    except Exception:
        yield ("🟠 Kali connect aagala. 🐉 **Kali** tab-la konja neram wait pannu (desktop start aagum), "
               "illa Kali-la `sudo service ssh start` run pannu. Aprama thirumba try pannu.")
        return

    head = f"$ {command}\n"
    final = ""
    for grow, fin in _stream_exec(host, command):
        yield head + grow
        if fin is not None:
            final = fin

    if auto_fix and looks_failed(final):
        yield head + final + "\n\n🤖 Error vandhuchu — AI automatic-ah fix panni thirumba run pannudhu…"
        fix = ai_fix_command(command, final)
        if fix and not fix.startswith("#") and fix.strip() != command.strip() and not kp._blocked(fix):
            prefix = head + final + f"\n\n🔧 Fix: {fix}\n$ {fix}\n"
            yield prefix
            fix_final = ""
            for grow, fin in _stream_exec(host, fix, timeout=300):
                yield prefix + grow
                if fin is not None:
                    fix_final = fin
            if looks_failed(fix_final):
                yield prefix + fix_final + "\n\n🤖 Innum error iruku — Kali tab-la manual-ah paaru."
        else:
            yield head + final + "\n\n🤖 Auto-fix: oru clean fix generate panna mudiyala. Mela error-ah paaru."
