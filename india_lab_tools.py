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
