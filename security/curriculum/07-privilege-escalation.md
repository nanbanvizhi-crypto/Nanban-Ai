# Module 7 — Privilege Escalation

You've gained a foothold on a machine as a low-privilege user (in your lab). **Privilege escalation (privesc)** is going from that limited access to full control (root on Linux, Administrator/SYSTEM on Windows). It's a core OSCP skill and — crucially — understanding it teaches you to *harden* your own systems. Practice only on your own lab/VMs (Module 0).

## Why privesc exists

Systems have many moving parts: services running as root, scheduled jobs, file permissions, installed software. A misconfiguration in any of them can let a normal user do something they shouldn't. Privesc is systematically finding that one weak link. Defenders prevent it by closing those same gaps.

## The method: enumerate, don't guess

Privesc is 90% **enumeration** — gathering information about the system until something stands out. Automated scripts help, but understanding *what* they look for is the skill.

### Linux enumeration (on your own VM)

```bash
id; whoami; sudo -l                      # who am I, what can I sudo
uname -a; cat /etc/os-release            # kernel/OS version (old = known exploits)
find / -perm -4000 -type f 2>/dev/null   # SUID binaries (run as owner, often root)
cat /etc/crontab; ls -la /etc/cron.*     # scheduled jobs you might hijack
ps aux                                   # services running as root
ls -la /home/*; find / -writable -type d 2>/dev/null   # writable places
env; cat ~/.bash_history                 # leaked secrets
```

Automated: **LinPEAS** (`linpeas.sh`) runs all of this and highlights findings. Run it on your lab VM and *read why* each flagged item matters.

### Common Linux privesc paths (concepts)
- **Misconfigured sudo** — `sudo -l` shows a command you can run as root that can be abused (e.g. a text editor that can spawn a shell). The site **GTFOBins** catalogs which binaries can be abused and how — it's a defender's checklist too.
- **SUID binaries** — a program that runs as its owner (root). If it's a known-abusable binary or a custom one with a flaw, it's a path up.
- **Writable cron jobs / scripts run by root** — if root runs a script you can edit, you control root.
- **Kernel exploits** — an old kernel with a public CVE (last resort; can crash the box).
- **Credentials in files** — passwords in configs, history, backups.

### Windows enumeration (on your own VM)
```
whoami /priv                    # your privileges (SeImpersonate etc. are gold)
systeminfo                      # OS version/patches (missing patches = exploits)
```
- **WinPEAS** is the Windows equivalent of LinPEAS.
- Common paths: unquoted service paths, weak service permissions, `SeImpersonatePrivilege` (Potato attacks), stored credentials, AlwaysInstallElevated, scheduled tasks.

## The defender's view (this is why you're learning it)

Every privesc path is a hardening checklist item:
- **Audit sudo rules** — least privilege, no shell-spawning binaries, no wildcards.
- **Minimize SUID binaries** — `find / -perm -4000` on your own servers and remove what isn't needed.
- **Protect cron/scripts run as root** — not writable by normal users.
- **Patch** — old kernels/OS = known exploits. Keep current.
- **No secrets in files/history** — use proper secret storage.
- **Windows:** quote service paths, tighten service perms, remove AlwaysInstallElevated, limit privileges.

Run LinPEAS/WinPEAS against your *own* servers (DineFlow's host) and fix what it flags — that's exactly what an attacker would exploit.

## Practice

- **TryHackMe**: "Linux PrivEsc" and "Windows PrivEsc" rooms — guided, legal, excellent.
- **HackTheBox**: retired machines with privesc write-ups.
- Your own VMs: install an old Ubuntu, run LinPEAS, try the SUID/sudo paths, then harden it and watch them close.

## Key terms

- **Foothold**: initial low-priv access.
- **Enumeration**: systematically gathering system info to find weaknesses.
- **SUID**: a binary that runs with its owner's privileges.
- **GTFOBins / LOLBAS**: catalogs of abusable built-in binaries (Linux / Windows) — also hardening references.
- **LinPEAS / WinPEAS**: enumeration scripts that highlight privesc paths.

Next: **Module 8 — Active Directory Attacks.**
