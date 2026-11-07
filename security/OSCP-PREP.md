# 🎯 OSCP / eJPT Prep Track

A structured path to the two entry/mid certifications that actually get you hired, plus the methodology and note habits that matter more than any single tool. Everything is practiced on **legal platforms and your own lab** (Module 0 — doubly important for certs; the exams are legal, going off-scope is not).

## Which cert, and when

| Cert | Level | Format | Good for |
|---|---|---|---|
| **eJPT** (INE) | Entry | ~48h practical, guided | First cert; proves you can do a basic assessment |
| **OSCP** (OffSec) | Intermediate | 24h hands-on exam + report | The respected one; real hiring signal for pentest roles |
| **PNPT** (TCM) | Entry-mid | 5-day practical + AD + report | Great modern alternative, cheaper, includes AD |

Order for a beginner: **finish Modules 0–9** → **eJPT or PNPT** → **OSCP** when you can own medium HackTheBox boxes without hints.

## The methodology (this is the real skill)

Every box, every engagement follows the same loop. Internalize it and tools become details.

```
1. RECON        — scan everything. nmap -sC -sV -p-  (all ports, scripts, versions)
2. ENUMERATE    — for each service, dig deep. Web? dir-bust, read source, find inputs.
                  "Enumerate harder" is the #1 OSCP advice. You miss things by rushing.
3. EXPLOIT      — turn a finding into access. Known CVE? Weak creds? Injection? Upload?
4. FOOTHOLD     — get a shell as some user. Stabilize it.
5. PRIVESC      — enumerate the host (LinPEAS/WinPEAS), escalate to root/SYSTEM (Module 7).
6. LOOT & PIVOT — grab proof, find creds/paths to the next machine.
7. DOCUMENT     — screenshot and note EVERYTHING as you go (see template below).
```

The people who fail OSCP usually fail at **2 (enumeration)** and **7 (notes)**, not at exotic exploits.

## Study plan (3–6 months, part-time)

**Month 1–2: Foundations**
- Modules 0–5 of this course + PortSwigger Web Security Academy (free).
- TryHackMe: "Complete Beginner" + "Jr Penetration Tester" paths.

**Month 2–3: Breadth**
- Modules 6–9 (passwords, privesc, AD, network).
- TryHackMe: "Linux PrivEsc", "Windows PrivEsc", "Kerberoasting" rooms.
- Start easy HackTheBox machines (use write-ups when stuck — that's learning).

**Month 3–5: Depth & speed**
- HackTheBox: work through easy→medium boxes. Aim to reduce write-up reliance.
- Do the **TJnull OSCP-like list** (community list of HTB/VulnHub boxes that mirror OSCP style).
- Practice **writing a report** for every box (not just rooting it).

**Month 5–6: Exam prep**
- OffSec's PEN-200 course + lab (if doing OSCP) or eJPT's INE material.
- Timed practice: can you own a box in a few hours with full notes?
- Learn the **report template** cold — OSCP fails people for bad reports even when they rooted the boxes.

## Essential free resources

- **TryHackMe** — guided, beginner-friendly.
- **HackTheBox** + **TJnull's prep list** — the standard OSCP practice.
- **PortSwigger Academy** — web, free, best in class.
- **GTFOBins / LOLBAS** — privesc binary references.
- **HackTricks** (book.hacktricks.xyz) — the community methodology encyclopedia.
- **IppSec** (YouTube) — HTB box walkthroughs; watch how a pro enumerates.
- **pwn.college / picoCTF** — if you go toward binary exploitation.

## Note-taking — do this from day one

Good notes win exams and jobs. Use **CherryTree**, **Obsidian**, or **Notion**. One page per target. Screenshot every step (you need them for the report). Template:

```markdown
# Target: <name / IP>
Date: ____   OS: ____

## Recon
- nmap -sC -sV -p- <ip>  →  [paste open ports + services]
- Interesting: ____

## Enumeration
- Port 80: [tech stack, dirs found, inputs]
- Port 445: [shares, versions]
- ...

## Exploitation
- Vuln: ____  (CVE / misconfig / injection)
- Steps: [exact commands + screenshots]
- Foothold as: <user>  [screenshot of `id` / `whoami`]

## Privilege Escalation
- Enumeration finding: ____ (sudo -l / SUID / cron / kernel)
- Steps: [exact commands + screenshots]
- Root/SYSTEM proof: [screenshot of `id` / `whoami /priv` + proof file]

## Loot
- Creds found: ____
- Flags/proof: ____

## Remediation (write this — it's what clients pay for)
- Finding → how to fix it.
```

## The report (OSCP's hidden exam)

OSCP requires a professional report. Practice its structure now:
1. **Executive summary** — plain-English risk, for management.
2. **Methodology** — your approach.
3. **Findings** — each vuln: description, evidence (screenshots), impact, **remediation**.
4. **Appendix** — commands, raw output.

A rooted box with no report = fail. A clean report of a solid assessment = pass. Write one for every practice box.

## The rule, again

Exams and platforms are legal and in-scope. Your own lab is legal. Everything else — a company, a school, a random IP — is not, and it ends careers before they start. Stay in scope, always.
