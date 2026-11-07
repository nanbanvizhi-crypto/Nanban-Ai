# Module 2 — Recon: Mapping a Target

Before testing anything, you build a picture of it: what's running, what pages exist, what inputs it takes. This is **reconnaissance**. On a real engagement it's the first phase; in your lab it's how you learn to see an app the way a tester does.

> Everything here is run against **your own lab** (`127.0.0.1`) or legal platforms. Scanning something you don't own is covered in Module 0 — don't.

## Two kinds of recon

- **Passive**: information you gather without touching the target (public records, search engines). Low risk, used in real engagements before scope is active.
- **Active**: you send requests to the target and see how it answers (port scans, directory discovery). You only do this on systems you're authorised to test.

## Step 1 — What's running? (ports and services)

A server is reachable on numbered **ports**. A web app is usually on 80 (HTTP) or 443 (HTTPS). A quick map of open ports tells you what a machine offers.

**`nmap`** is the standard tool. On your lab:

```bash
# What's open on your own machine's lab containers
nmap -p 3000,8080,8081 127.0.0.1

# Service/version detection (what software, what version)
nmap -sV -p 3000,8080,8081 127.0.0.1
```

What you learn: which ports answer, what software and version sits behind them. Old versions → known, already-published vulnerabilities (you'd look them up in CVE databases). Reading a version banner is passive-ish and harmless on your own box.

## Step 2 — Map the application (pages and inputs)

Now you explore the web app itself.

- **By hand**: click every link, every form. Note each endpoint and every input (query params, form fields, headers, cookies). Keep a list — this is your "attack surface".
- **Browser DevTools** (F12 → Network): watch requests, find API calls the UI makes (`/api/...`) that aren't obvious links.
- **Directory discovery**: tools like `gobuster` or `ffuf` ask the server for common paths (`/admin`, `/backup`, `/.git`) using a wordlist, to find pages not linked anywhere.

```bash
# Example against YOUR lab's DVWA — find paths using a wordlist
gobuster dir -u http://127.0.0.1:8080 -w /usr/share/wordlists/dirb/common.txt
```

What you learn: hidden admin panels, forgotten backup files, API endpoints. Each one is a new thing to understand.

## Step 3 — Fingerprint the tech

Figure out what the app is built with — it tells you what bugs to expect.

- Response headers (`Server:`, `X-Powered-By:`) often name the software.
- Error pages, cookie names (`PHPSESSID` → PHP, `JSESSIONID` → Java), file extensions (`.php`, `.aspx`).
- Browser extension **Wappalyzer** names frameworks/libraries for you.

## Building your notes

For each target, keep a simple map:

```
Target: DVWA (127.0.0.1:8080)
Tech: PHP + MySQL, Apache
Endpoints:
  /login.php        inputs: username, password
  /vulnerabilities/sqli/   inputs: id (GET)
  /vulnerabilities/xss_r/  inputs: name (GET)
Interesting: /config/ exposed? /setup.php?
```

This map is what you actually test in the next modules. Good recon makes everything after it faster.

## Defender's view (how this maps back to protecting DineFlow)

- Don't leak versions in headers (`Server`, `X-Powered-By`) — turn them off.
- Don't leave backup files, `.git` folders, or `/admin` with no auth reachable.
- Rate-limit and log unusual request patterns (lots of 404s = someone running a directory scan).

## Key terms

- **Attack surface**: the full set of inputs/endpoints an attacker can reach.
- **Port scan**: checking which network ports answer.
- **Fingerprinting**: identifying the software/versions in use.
- **Wordlist**: a file of common names used to guess paths, usernames, passwords.
- **CVE**: a public ID for a known vulnerability (e.g. CVE-2021-44228).

Next: **Module 3 — SQL Injection.**
