# Module 5 — Tools of the Trade

A tour of the standard security tools: what each one is, when you'd use it, and how it fits the workflow you've learned (recon → map → test → understand → fix). You run all of these against **your own lab or authorised targets only** (Module 0).

The best way to get these isn't to collect them one by one — it's to use **Kali Linux** or **Parrot OS**, free security distributions that ship with all of them pre-installed. Run Kali in WSL2 (Windows) or a VM, and drive it from Nanban with `/server add kali …`. See `../README.md` → "Getting the tools".

## The core toolkit

### Burp Suite (web proxy) — the one you'll use most
Sits between your browser and the target and lets you **see, pause, change, and resend** every request. This is the heart of web testing.
- **Proxy**: intercept a request, edit any field, forward it. This is how you test "what if I change `id=1` to `id=2`?" (access control) or inject a payload into a parameter.
- **Repeater**: resend one request over and over with tweaks — perfect for understanding a bug.
- **Intruder**: automate sending many payloads into a parameter (the free edition is rate-limited).
- Free **Community Edition** is plenty to learn with. OWASP **ZAP** is a fully-free alternative.

### nmap (network scanner)
Finds open ports and identifies services/versions on a host. Your first recon step for a machine. (Module 2.)

### Directory/content discovery — gobuster, ffuf, dirb
Use a wordlist to find pages and files not linked anywhere (`/admin`, `/backup`). (Module 2.)

### sqlmap (SQLi automation)
Detects and exploits SQL injection automatically. Great for seeing, on your own lab, how fast a weak query falls — and therefore why parameterised queries matter. (Module 3.)

### Nikto / web scanners
Quick checks for common misconfigurations and known-vulnerable files on a web server. Noisy, but a fast first look on your lab.

### Hydra / John the Ripper / Hashcat (password tools)
- **Hydra**: tests login forms against a password list (teaches you why rate-limiting and lockouts matter).
- **John / Hashcat**: crack *password hashes you already have* (e.g. from your own lab) — teaches why slow hashes (bcrypt/argon2) and salts matter for defenders.

### Wireshark (packet analysis)
Watches raw network traffic. Shows you, concretely, why HTTP (unencrypted) is unsafe — you can read it — and why HTTPS matters. Great learning tool on your own traffic.

### Metasploit (exploitation framework)
A large framework of known exploits and payloads, used against systems with known vulnerabilities. Advanced; practise only against purpose-built vulnerable VMs (e.g. Metasploitable) that you run yourself.

### Browser DevTools + Wappalyzer
Built into your browser. DevTools (F12) shows requests, storage, and the DOM. Wappalyzer fingerprints the tech stack. Free, always available, underrated.

## How they fit the workflow

```
Recon        nmap, Wappalyzer, DevTools
Mapping      gobuster/ffuf, Burp (browse through proxy)
Testing      Burp Repeater/Intruder, sqlmap, Nikto
Passwords    Hydra (online), John/Hashcat (offline, your own hashes)
Analysis     Wireshark
Advanced     Metasploit (own vulnerable VMs)
```

You do **not** need to master all of these. For web app security — the most useful area for a developer — **Burp Suite + DevTools + sqlmap + understanding the bugs** covers the vast majority. Start there.

## A healthy way to practise

- Spin up the lab (`lab/`), pick one tool, one target, one bug. Understand it fully before moving on.
- After every exercise, write the **fix** in your own words. That's the skill that pays.
- Keep notes. Future-you (and job interviews) will thank you.

## Key terms

- **Proxy (intercepting)**: a tool that sits between browser and server so you can inspect/modify traffic (Burp, ZAP).
- **Kali / Parrot**: Linux distros preloaded with security tools.
- **Framework (Metasploit)**: a collection of exploits/payloads with a common interface.
- **Online vs offline password attack**: online = against a live login (slow, noisy, rate-limited); offline = against stolen hashes (fast, why strong hashing matters).

Next: **Module 6 — Your Learning Roadmap** (see `../ROADMAP.md`).
