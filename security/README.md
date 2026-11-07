# 🛡️ Nanban Security Lab — learn pentesting legally, from zero

A complete beginner's package to learn web/application security the right way: a **safe practice lab** you're allowed to attack, a **step-by-step curriculum**, **guided walkthroughs**, **quizzes**, and a **job-ready roadmap**. All free, all legal, all on your own computer.

> **The one rule:** only ever test your own lab, your own machines, or targets you have **explicit written permission** to test (including bug-bounty scope). Read `curriculum/00-ethics-and-the-law.md` first — it's the difference between a career and a crime.

## What's inside

```
nanban-security-lab/
├── README.md                  ← you are here
├── ROADMAP.md                 ← beginner → job-ready path + free resources
├── OSCP-PREP.md               ← OSCP/eJPT prep, methodology, report & note templates
├── KALI-SETUP.md              ← install Kali (WSL2 or VM), wired to Nanban + lab
├── lab/                       ← your legal practice range (Docker)
│   ├── docker-compose.yml     ← DVWA + Juice Shop + WebGoat, localhost-only
│   ├── start_lab.bat / .sh    ← start the targets
│   └── stop_lab.bat / .sh     ← stop them
├── curriculum/                ← read these in order (also great in Nanban Study mode)
│   ├── 00-ethics-and-the-law.md
│   ├── 01-how-the-web-works.md
│   ├── 02-recon-and-mapping.md
│   ├── 03-sql-injection.md
│   ├── 04-xss-and-common-web-bugs.md
│   ├── 05-tools-of-the-trade.md
│   ├── 06-password-attacks.md       (advanced)
│   ├── 07-privilege-escalation.md   (advanced)
│   ├── 08-active-directory.md       (advanced)
│   └── 09-network-and-binary.md     (advanced)
├── walkthroughs/              ← hands-on, on your own lab
│   ├── 01-sqli-dvwa.md
│   └── 02-xss-dvwa.md
└── quizzes/
    └── quiz-bank.md           ← test yourself (answers included)
```

## Start here (first week)

1. **Read** `curriculum/00-ethics-and-the-law.md`. Non-negotiable.
2. **Read** `curriculum/01-how-the-web-works.md`.
3. **Start the lab:** install [Docker Desktop](https://www.docker.com/products/docker-desktop/), open it once, then run `lab/start_lab.bat` (Windows) or `./lab/start_lab.sh` (Mac/Linux/WSL). First run downloads a few GB.
4. Open **Juice Shop** at `http://127.0.0.1:3000` and click around with DevTools (F12) open.
5. When you reach Module 3, do `walkthroughs/01-sqli-dvwa.md`.

## Your practice targets (after `start_lab`)

| Target | URL | What it's for |
|---|---|---|
| **DVWA** | http://127.0.0.1:8080 (admin/password) | Classic bugs with adjustable difficulty — best for the walkthroughs |
| **OWASP Juice Shop** | http://127.0.0.1:3000 | Modern app, gamified challenges |
| **OWASP WebGoat** | http://127.0.0.1:8081/WebGoat | Guided lessons with built-in theory |

All three are **intentionally vulnerable, made for learning**, and bound to `127.0.0.1` so they're never exposed beyond your computer.

## Getting the tools

**Full step-by-step install is in `KALI-SETUP.md`** (WSL2 and VM, both wired to Nanban). In short:

- **Kali Linux** (kali.org) or **Parrot OS** — free, ship with Burp, nmap, sqlmap, gobuster, Metasploit, Hydra, Wireshark, etc.
- Easiest on Windows: **WSL2** → `wsl --install -d kali-linux` (then `sudo apt update && sudo apt install -y kali-linux-headless`). Or run Kali in **VirtualBox/VMware** as a VM.
- Minimum to start web security: just **Burp Suite Community** (free) + your browser's DevTools.

### Drive the tools from Nanban
Your Nanban AI terminal already manages machines over SSH. Once Kali is running:
```
/server add kali  kali@<kali-ip>        (WSL: kali@127.0.0.1, or the VM's IP)
/server use kali
nmap -sV 127.0.0.1                      (scan your own lab)
```
Keep the tooling in Kali; use Nanban as the assistant that explains output and helps you learn.

## Use it with Nanban Study mode

1. Copy the `curriculum/`, `walkthroughs/`, `quizzes/` and `ROADMAP.md` files into Nanban's `documents/` folder.
2. In Nanban, switch to **📚 Study** mode.
3. Ask things like:
   - "Explain SQL injection like I'm a beginner."
   - "Quiz me on the OWASP Top 10."
   - "From my documents, what's the fix for XSS?"
   - (Coding mode) "Here's a DineFlow function — is it injectable? Show the safe version."

## The honest truth about this path

- It's a **real, legal, well-paid** career — application security, pentesting, bug bounty, blue team.
- The skill is understanding *why* things break so you can *prevent* them. Every attack you learn makes your own apps (like DineFlow) stronger.
- There are no shortcuts and no "all-in-one hacking OS that does it for you" — that mindset leads to trouble. Real skill is built one understood bug at a time, on targets you're allowed to touch.
- Stay on your lab and legal platforms. That boundary is what makes you a professional.

Start with Module 0. Then `start_lab`. Welcome to security. 🛡️
