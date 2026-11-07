# Walkthrough 3 — Linux Privilege Escalation (on your own VM)

Hands-on for Module 7. You'll go from a normal user to root on a **vulnerable VM you own**, by enumerating and finding the weak link — then you'll harden it and watch the paths close. That last step is the point: every escalation you do is a hardening lesson for your own servers.

> **Target:** your own VM. Best options: **Metasploitable 2** (download from SourceForge, run in VirtualBox — a whole box built to be practised on), a TryHackMe "Linux PrivEsc" room, or any Ubuntu VM you set up yourself. Never a machine you don't own (Module 0).

## Setup
1. In VirtualBox/VMware, run Metasploitable 2 (or your Ubuntu VM). Note its IP (`ip a` inside it).
2. From Kali (connected to Nanban via `/server use kali`), confirm you can reach it: `ping <vm-ip>`.
3. Get a normal-user shell on it (on Metasploitable, SSH in as `msfadmin`/`msfadmin`, or via any foothold you practised in earlier modules). You're now a low-priv user — the starting point.

## Step 1 — Who am I, and what can I already do?
```bash
id                 # your user and groups
whoami
sudo -l            # commands you can run as root (may ask your password)
hostname; uname -a # OS and kernel version
```
Write down everything. `sudo -l` is the first jackpot to check — if it lists a command you can run as root, that's often a direct path up.

## Step 2 — Enumerate the system (the real work)
```bash
# SUID binaries — programs that run as their owner (often root)
find / -perm -4000 -type f 2>/dev/null

# Scheduled jobs — something root runs on a timer you might control
cat /etc/crontab; ls -la /etc/cron.*

# Services running as root
ps aux | grep root

# Writable files/dirs you shouldn't be able to edit
find / -writable -type f 2>/dev/null | grep -vE '^/proc|^/sys' | head
find / -perm -2 -type f 2>/dev/null | grep -vE '^/proc|^/sys' | head

# Secrets lying around
cat ~/.bash_history; env; ls -la /home/*
```

**Automate it:** copy **LinPEAS** to the VM and run it — it does all the above and colour-codes what matters:
```bash
# from Kali: serve linpeas, then on the VM: curl it and run
# (download linpeas.sh from the PEASS-ng GitHub onto YOUR vm)
./linpeas.sh | tee linpeas-out.txt
```
Read the red/yellow highlights and, for each, ask "why is this a risk?" — that understanding is the skill, not the script.

## Step 3 — Pick a path and escalate

Common findings on a box like Metasploitable and what they mean:

- **`sudo -l` shows an abusable command.** Look it up on **GTFOBins** — it tells you if that binary can spawn a root shell (many can: editors, interpreters, `find`, etc.). Example pattern: if you can `sudo` a program that can run shell commands, you run it and ask it for a shell.
- **A world-writable script run by root cron.** Edit it to do what you want; when root's cron runs it, your code runs as root.
- **An unusual SUID binary.** Check GTFOBins for it; a known-abusable SUID binary gives a root shell.
- **Old kernel with a public CVE.** Last resort (can crash the box); match `uname -r` to a known local-privesc CVE.
- **Reused/leaked credentials** in config or history → `su` to a higher-privilege user.

Do **one** path fully. Get your root shell, confirm:
```bash
id        # should now show uid=0(root)
```
Grab the proof file (on CTF boxes, the root flag) — and screenshot every step for your notes (Module OSCP-PREP).

## Step 4 — The important half: harden it, watch it close
Now fix what you exploited, as the defender:
- Abusable `sudo` rule → remove it or restrict to a non-shell-spawning command, no wildcards.
- Writable root cron script → `chmod` it so only root can edit; put it outside user-writable paths.
- Unneeded SUID binary → `chmod -s` it or remove the package.
- Old kernel → `apt update && apt full-upgrade`.
- Leaked creds → remove them, use proper secret storage.

Re-run LinPEAS. The path you used should no longer be flagged. You just did exactly what a defender does: find the weak link an attacker would use, and close it.

## Apply to your own servers (DineFlow's host)
Run `sudo -l`, `find / -perm -4000`, and LinPEAS on your *own* server. Fix what they flag **before** an attacker finds it. This is unglamorous and it's most of real-world security.

## Key takeaways
- Privesc = **enumerate relentlessly**, then exploit one weak link.
- The same checks are a hardening checklist for your servers.
- Notes + screenshots at every step (you'll need them for reports and OSCP).

Next: **Walkthrough 4 — Build your own Active Directory lab**, or **Walkthrough 5 — Password cracking**.
