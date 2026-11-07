"""
Security learning hub for Nanban — one place for the pentesting course, the legal
practice lab, and the Kali connection. It consolidates what already exists
(Study docs, the Docker lab, the /server SSH feature); it does not add any new
offensive capability. Everything here points at the user's own lab / authorised
targets only (see security/curriculum/00-ethics-and-the-law.md).
"""

import shutil
import subprocess
from pathlib import Path

import config
import servers

SECURITY_DIR = config.BASE_DIR / "security"
LAB_DIR = SECURITY_DIR / "lab"

LESSONS = [
    ("📜 Ethics & the Law (read first)", "curriculum/00-ethics-and-the-law.md"),
    ("🌐 How the Web Works", "curriculum/01-how-the-web-works.md"),
    ("🔍 Recon & Mapping", "curriculum/02-recon-and-mapping.md"),
    ("💉 SQL Injection", "curriculum/03-sql-injection.md"),
    ("🪞 XSS & OWASP Top 10", "curriculum/04-xss-and-common-web-bugs.md"),
    ("🧰 Tools of the Trade", "curriculum/05-tools-of-the-trade.md"),
    ("🗂️ Kali Tools Reference (full catalog)", "TOOLS-REFERENCE.md"),
    ("🔑 Password Attacks", "curriculum/06-password-attacks.md"),
    ("⬆️ Privilege Escalation", "curriculum/07-privilege-escalation.md"),
    ("🏢 Active Directory Attacks", "curriculum/08-active-directory.md"),
    ("🌐 Network & Binary Exploitation", "curriculum/09-network-and-binary.md"),
    ("▶️ Walkthrough: SQLi on DVWA", "walkthroughs/01-sqli-dvwa.md"),
    ("▶️ Walkthrough: XSS on DVWA", "walkthroughs/02-xss-dvwa.md"),
    ("▶️ Walkthrough: Linux Privesc", "walkthroughs/03-privesc-linux.md"),
    ("▶️ Walkthrough: Windows Privesc", "walkthroughs/06-privesc-windows.md"),
    ("▶️ Walkthrough: Build an AD lab (GOAD)", "walkthroughs/04-build-ad-lab.md"),
    ("▶️ Walkthrough: Password Cracking", "walkthroughs/05-password-cracking.md"),
    ("🗺️ Roadmap (beginner → job-ready)", "ROADMAP.md"),
    ("🎯 OSCP / eJPT Prep Track", "OSCP-PREP.md"),
    ("🐉 Kali Linux Setup", "KALI-SETUP.md"),
    ("❓ Quiz Bank", "quizzes/quiz-bank.md"),
]

LAB_TARGETS = [
    ("DVWA", "http://127.0.0.1:8080", "admin / password"),
    ("OWASP Juice Shop", "http://127.0.0.1:3000", "—"),
    ("OWASP WebGoat", "http://127.0.0.1:8081/WebGoat", "—"),
    ("OWASP Mutillidae II", "http://127.0.0.1:8082", "—"),
    ("bWAPP", "http://127.0.0.1:8083/install.php", "bee / bug (after install)"),
    ("VAmPI (API)", "http://127.0.0.1:5001", "—"),
    ("DVGA (GraphQL)", "http://127.0.0.1:5013", "—"),
]


def available() -> bool:
    return SECURITY_DIR.is_dir()


def read_lesson(rel_path: str) -> str:
    try:
        return (SECURITY_DIR / rel_path).read_text(encoding="utf-8")
    except OSError as e:
        return f"_Could not open {rel_path}: {e}_"


# ---------------------------------------------------------------- lab control (Docker)

def _docker() -> str | None:
    return shutil.which("docker")


def _compose(*args: str, timeout: int = 600) -> tuple[int, str]:
    docker = _docker()
    if not docker:
        return 127, "Docker is not installed. Install Docker Desktop, open it once, then try again."
    try:
        result = subprocess.run([docker, "compose", *args], cwd=LAB_DIR,
                                capture_output=True, text=True, timeout=timeout)
        return result.returncode, (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, "Timed out. The first start downloads several GB — give it a few minutes and check again."
    except Exception as e:
        return 1, str(e)


def lab_status() -> str:
    docker = _docker()
    if not docker:
        return ("🔴 **Docker not found.** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/), "
                "open it once, then use **Start lab**.")
    code, out = _compose("ps", "--format", "{{.Name}} {{.State}}", timeout=20)
    if code != 0:
        return "🔴 Docker is installed but not running, or the lab isn't started. Open Docker Desktop, then **Start lab**."
    running = [line for line in out.splitlines() if "running" in line.lower()]
    if not running:
        return "⚪ Lab is **stopped**. Press **Start lab** to launch the practice targets."
    rows = ["🟢 **Lab is running** (localhost only):", "", "| Target | URL | Login |", "|---|---|---|"]
    rows += [f"| {name} | `{url}` | {login} |" for name, url, login in LAB_TARGETS]
    return "\n".join(rows)


def start_lab() -> str:
    code, out = _compose("up", "-d")
    if code == 0:
        return "✅ Starting the lab. First run downloads images (a few GB) — press **Refresh** in a moment.\n\n" + lab_status()
    return f"⚠️ {out}"


def stop_lab() -> str:
    code, out = _compose("down", timeout=120)
    return "🛑 Lab stopped." if code == 0 else f"⚠️ {out}"


# ---------------------------------------------------------------- Kali helper

def kali_status() -> str:
    names = servers.names()
    if "kali" in names:
        try:
            host = servers.connect("kali")
            return f"🟢 **Kali connected** — {host.os_name} ({host.user}@{host.host}). Use it from the 💻 Terminal tab: `/server use kali`."
        except Exception as e:
            return f"🟠 Kali is registered but not reachable: {e}. In Kali run `sudo service ssh start`."
    return ("⚪ **Kali not connected yet.** Follow **🐉 Kali Linux Setup** above, then in the 💻 Terminal tab:\n\n"
            "```\n/server add kali <your-username>@127.0.0.1\n/server test kali\n```")


def quick_commands() -> str:
    return ("Once Kali is connected (`/server use kali` in the Terminal tab), try these **against your own lab**:\n\n"
            "```bash\n"
            "nmap -sV -p 3000,8080,8081 127.0.0.1          # recon your lab\n"
            "gobuster dir -u http://127.0.0.1:8080 -w /usr/share/wordlists/dirb/common.txt\n"
            "burpsuite &                                    # open Burp Suite\n"
            "```\n"
            "**💬 Chat → 🛡️ Security Tutor mode** is your expert teacher: ask it to explain any concept, "
            "give you the exact command, interpret tool output, or quiz you. Paste output from the Terminal tab "
            "and it'll walk you through it.")
