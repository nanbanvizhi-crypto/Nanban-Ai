"""
🧰 Kali Toolset Installer — official Kali metapackages, one copy-paste command each.

These are Kali Linux's OWN tool groups (apt metapackages). Run a command in your own Kali / WSL
and that whole category of tools installs. This is the standard, legitimate way pentesters set up
their lab — the same powerful tools, used ethically on your own / authorised / practice targets.

Nothing is installed by Nanban; this just shows you the exact commands to run in your Kali.
"""

# (title, apt/pipx command, what you get, note)
BUNDLES = [
    {
        "icon": "⭐", "title": "Top 10 essentials", "size": "~2 GB",
        "cmd": "sudo apt update && sudo apt install -y kali-tools-top10",
        "tools": "nmap · metasploit · burpsuite · wireshark · aircrack-ng · john · hydra · sqlmap · nikto · wpscan",
        "note": "Start here — the 10 most-used tools.",
    },
    {
        "icon": "📦", "title": "Large set (recommended)", "size": "~9 GB",
        "cmd": "sudo apt update && sudo apt install -y kali-linux-large",
        "tools": "Most of the Kali arsenal — recon, web, exploitation, passwords, wireless, forensics…",
        "note": "Best single choice for serious learning — nearly everything.",
    },
    {
        "icon": "🌌", "title": "Everything", "size": "~40+ GB",
        "cmd": "sudo apt update && sudo apt install -y kali-linux-everything",
        "tools": "Every packaged Kali tool. Huge download + disk — only if you have space.",
        "note": "Overkill for most; kali-linux-large is usually enough.",
    },
]

CATEGORIES = [
    {"icon": "🔎", "title": "Information Gathering", "pkg": "kali-tools-information-gathering",
     "tools": "nmap · amass · theharvester · dnsenum · recon-ng · fierce · netdiscover"},
    {"icon": "🎯", "title": "Vulnerability Analysis", "pkg": "kali-tools-vulnerability",
     "tools": "nikto · nuclei · legion · unix-privesc-check"},
    {"icon": "🌐", "title": "Web Applications", "pkg": "kali-tools-web",
     "tools": "sqlmap · ffuf · gobuster · wpscan · zaproxy · wfuzz · whatweb"},
    {"icon": "💥", "title": "Exploitation", "pkg": "kali-tools-exploitation",
     "tools": "metasploit · searchsploit · commix · exploitdb · set"},
    {"icon": "🔑", "title": "Password Attacks", "pkg": "kali-tools-passwords",
     "tools": "hashcat · john · hydra · medusa · crunch · cewl · wordlists"},
    {"icon": "📡", "title": "Wireless", "pkg": "kali-tools-wireless",
     "tools": "aircrack-ng · wifite · kismet · reaver · bettercap · hcxtools"},
    {"icon": "🪤", "title": "Post-Exploitation", "pkg": "kali-tools-post-exploitation",
     "tools": "mimikatz · powersploit · weevely · evil-winrm · crackmapexec"},
    {"icon": "🧬", "title": "Forensics", "pkg": "kali-tools-forensics",
     "tools": "volatility3 · autopsy · binwalk · foremost · sleuthkit · bulk-extractor"},
    {"icon": "🔬", "title": "Reverse Engineering", "pkg": "kali-tools-reverse-engineering",
     "tools": "ghidra · radare2 · gdb · edb-debugger · jadx"},
    {"icon": "🕵️", "title": "Sniffing & Spoofing", "pkg": "kali-tools-sniffing-spoofing",
     "tools": "wireshark · tcpdump · mitmproxy · responder · ettercap · bettercap"},
    {"icon": "📱", "title": "Mobile / Android", "pkg": "kali-tools-android",
     "tools": "apktool · dex2jar · smali · android tools"},
    {"icon": "📝", "title": "Reporting", "pkg": "kali-tools-reporting",
     "tools": "faraday · pipal · metagoofil · recordmydesktop"},
]

# Modern tools not always in the metapackages — install directly
EXTRAS = [
    {"icon": "⚡", "title": "SecLists (wordlists)", "cmd": "sudo apt install -y seclists",
     "tools": "The essential wordlist collection (fuzzing, passwords, discovery)."},
    {"icon": "🏛️", "title": "NetExec (nxc)", "cmd": "sudo apt install -y pipx && pipx install git+https://github.com/Pennyw0rth/NetExec",
     "tools": "Modern AD/network assessment (CrackMapExec successor)."},
    {"icon": "🎯", "title": "Nuclei (template scanner)", "cmd": "sudo apt install -y nuclei && nuclei -update-templates",
     "tools": "Fast template-based vulnerability scanner + latest templates."},
    {"icon": "🌐", "title": "httpx / katana / subfinder", "cmd": "sudo apt install -y httpx-toolkit katana subfinder",
     "tools": "ProjectDiscovery modern recon suite."},
    {"icon": "🩸", "title": "BloodHound + collectors", "cmd": "sudo apt install -y bloodhound && pipx install bloodhound-ce",
     "tools": "Active Directory attack-path mapping (also for blue-team audits)."},
]


_CSS = """<style>
.ki-wrap { max-width: 1100px; }
.ki-wrap h3 { margin: 16px 0 8px; font-size: 1.02rem; }
.ki-banner { background: rgba(255,153,51,.12); border: 1px solid rgba(255,153,51,.32);
  color: var(--body-text-color); border-radius: 12px; padding: 10px 14px; font-size: .86rem; }
.ki-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.ki-card { border: 1px solid var(--border-color-primary); border-radius: 14px; padding: 13px 14px;
  background: var(--block-background-fill); }
.ki-head { display: flex; align-items: center; gap: 8px; }
.ki-ico { font-size: 1.2rem; }
.ki-title { font-weight: 700; font-size: .96rem; flex: 1; }
.ki-size { font-size: .68rem; color: var(--body-text-color-subdued); border: 1px solid var(--border-color-primary);
  padding: 1px 7px; border-radius: 999px; }
.ki-tools { font-size: .78rem; color: var(--body-text-color-subdued); margin: 7px 0 9px; line-height: 1.5; }
.ki-cmd { background: #0d1117; color: #c9d1d9; border-radius: 9px; padding: 9px 11px !important; margin: 0;
  font-size: 12px; overflow-x: auto; border: 1px solid #30363d; }
.ki-cmd code { background: none !important; color: #8ef5b0 !important; padding: 0 !important; font-size: 12px; }
.ki-note { font-size: .76rem; color: var(--body-text-color-subdued); margin-top: 7px; }
.ki-foot { margin-top: 14px; font-size: .82rem; color: var(--body-text-color-subdued); }
</style>"""


# One curated command that installs the most powerful arsenal (metapackages + modern extras).
POWERFUL_CMD = (
    "sudo apt update && "
    "sudo apt install -y kali-linux-large seclists nuclei bloodhound && "
    "sudo apt install -y pipx && pipx ensurepath && "
    "pipx install git+https://github.com/Pennyw0rth/NetExec && "
    "nuclei -update-templates && "
    "echo '✅ Nanban: most powerful Kali arsenal installed.'"
)

POWERFUL_TOOLS = (
    "metasploit · nmap · sqlmap · burpsuite · wireshark · aircrack-ng · hashcat · john · hydra · "
    "nikto · nuclei · ffuf · gobuster · wpscan · zaproxy · netexec · bloodhound · impacket · "
    "responder · bettercap · recon-ng · seclists + ~600 more"
)


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _card(icon, title, cmd, tools, note="", size=""):
    size_badge = f'<span class="ki-size">{_esc(size)}</span>' if size else ""
    note_html = f'<div class="ki-note">💡 {_esc(note)}</div>' if note else ""
    return (
        '<div class="ki-card">'
        f'<div class="ki-head"><span class="ki-ico">{icon}</span>'
        f'<span class="ki-title">{_esc(title)}</span>{size_badge}</div>'
        f'<div class="ki-tools">🧰 {_esc(tools)}</div>'
        f'<pre class="ki-cmd"><code>{_esc(cmd)}</code></pre>'
        f'{note_html}</div>')


def installer_html() -> str:
    full = "".join(_card(b["icon"], b["title"], b["cmd"], b["tools"], b.get("note", ""), b.get("size", ""))
                   for b in BUNDLES)
    cats = "".join(_card(c["icon"], c["title"], f"sudo apt install -y {c['pkg']}", c["tools"])
                   for c in CATEGORIES)
    extras = "".join(_card(e["icon"], e["title"], e["cmd"], e["tools"]) for e in EXTRAS)
    return (
        _CSS +
        '<div class="ki-wrap">'
        '<div class="ki-banner">⚖️ Idhu ellame Kali-oda <b>official tool groups</b>. Un sontha Kali / WSL la '
        'run pannu. Practice = un lab / authorised / legal targets (Metasploitable, TryHackMe, HTB) mattum — '
        'veliya real system = illegal. Same tools, ethical use.</div>'
        '<h3>🚀 Full bundles — one command, lots of tools</h3>'
        f'<div class="ki-grid">{full}</div>'
        '<h3>🗂️ By category — install only what you need</h3>'
        f'<div class="ki-grid">{cats}</div>'
        '<h3>⚡ Modern extras — latest tools (direct install)</h3>'
        f'<div class="ki-grid">{extras}</div>'
        '<div class="ki-foot">Tip: Kali / WSL la <code>sudo apt update</code> mudhalla run pannu. '
        'Pernum download-ku time + disk venum. Install aana apuram Nanban Command Reference la entha '
        'tool-um search panni usage + Tanglish paaru.</div>'
        '</div>')
