# Nanban Security Learning Roadmap (beginner → job-ready)

A realistic path from zero to employable in defensive/offensive security, using **free** resources and legal practice. Go in order; don't rush. Consistency beats speed.

## Phase 0 — Foundations (2–4 weeks)
**Goal:** understand computers and networks before "hacking" anything.
- Read curriculum Modules 0 and 1 (ethics, how the web works).
- Learn basic **Linux command line** (navigating, files, permissions). Free: "Linux Journey" (linuxjourney.com), OverTheWire **Bandit** (a fun legal game that teaches Linux + SSH).
- Learn **networking basics**: IP, ports, DNS, HTTP. Free: "Computer Networking" crash courses on YouTube; Professor Messer's Network+ videos.
- Know at least one scripting language a little — **Python** is ideal (you already code, so lean on that).

## Phase 1 — Web Security Core (4–8 weeks)
**Goal:** understand and find the most common web bugs. This is the highest-value area for a developer.
- Curriculum Modules 2–5 + both lab walkthroughs.
- **PortSwigger Web Security Academy** (portswigger.net/web-security) — *free*, made by the Burp Suite team, the best web-security training that exists. Do the **SQL injection** and **XSS** learning paths, then Access Control, Authentication, SSRF.
- Install **Burp Suite Community** and use it on every exercise.
- Practise on your **own lab** (DVWA, Juice Shop, WebGoat) alongside the Academy.

## Phase 2 — Guided Practice Platforms (ongoing, 2–3 months)
**Goal:** apply skills on realistic machines with hints.
- **TryHackMe** (tryhackme.com) — beginner-friendly, guided rooms. Do the "Complete Beginner" and "Web Fundamentals" paths. Small subscription, lots free.
- **HackTheBox Academy** + **Starting Point** machines — a step up, more realistic.
- **PentesterLab** — focused web exercises.
- Keep notes for every box: what you found, how, and the fix.

## Phase 2.5 — Advanced modules (do these after web core)
Curriculum Modules **6–9** take you past web apps into full-system pentesting:
- **06 Password Attacks**, **07 Privilege Escalation**, **08 Active Directory**, **09 Network & Binary**.
- Then follow **`OSCP-PREP.md`** for the certification path, methodology, and report/note templates.

## Phase 3 — Specialise (3–6 months)
Pick a direction based on what you enjoyed:
- **Application Security / Secure Development** (great fit for you — ties to DineFlow): secure coding, code review, DevSecOps, threat modeling. Certs: none required to start; a strong GitHub + bug-bounty findings speak loudly.
- **Penetration Testing**: full-scope offensive testing. Entry cert: **eJPT** (affordable, practical). Later: **OSCP** (hard, respected, hands-on exam).
- **Blue Team / SOC / Defence**: detection, monitoring, incident response. Certs: **Security+**, **BTL1**.
- **Bug Bounty**: hunt real bugs legally for pay on **HackerOne** / **Bugcrowd**, strictly within each program's scope and rules.

## Phase 4 — Prove it
- **Bug bounties** (legal, in-scope) — real findings, sometimes real money.
- **Write-ups / blog** of what you learn — shows skill and communication.
- **GitHub** of your tools, notes, secure-code examples.
- **CTFs** (Capture The Flag competitions, e.g. picoCTF for beginners) — fun, legal, resume-worthy.

## The free resources, in one list
- **portswigger.net/web-security** — web security, free, best in class.
- **owasp.org** — Top 10, cheat sheets, testing guide (the reference defenders use).
- **tryhackme.com** — guided practice.
- **overthewire.org** — Linux/wargames (Bandit first).
- **picoctf.org** — beginner CTF.
- **Kali Linux** / **Parrot OS** — tool distros.
- **Your lab** (`lab/`) — DVWA, Juice Shop, WebGoat.

## How to use Nanban alongside this
- **Study mode**: copy the `curriculum/`, `walkthroughs/` and this file into Nanban's `documents/` folder. Then ask Nanban to explain anything, summarise a module, or **quiz you** ("quiz me on SQL injection").
- **Terminal / Servers**: install Kali in WSL2 or a VM, then `/server add kali kali@…` and run tools there, driven from Nanban, against your lab.
- **Coding mode**: paste a function from DineFlow and ask "is this injectable? show the parameterised version." That loop — learn the attack, fix your own code — is the whole point.

## The rule that never changes
Only ever test your own lab, your own machines, or targets you have **explicit written permission** (incl. bug-bounty scope) to test. Re-read Module 0 whenever you're unsure. This is what keeps it a career instead of a crime.
