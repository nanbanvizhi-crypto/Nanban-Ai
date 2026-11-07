# Module 8 — Active Directory Attacks

Active Directory (AD) runs the networks of almost every company — it's how Windows machines, users, and permissions are centrally managed. Most real-world corporate pentests are AD pentests. This module explains how AD is attacked so you understand how to defend it. Practice only in **your own AD lab** (how to build one is below) or legal platforms.

## What AD is (the ground you're standing on)

- A **Domain Controller (DC)** holds the central database of users, computers, and groups.
- Users log in once; AD (via **Kerberos**) issues tickets that grant access across the network.
- Admins manage everything through groups and policies (GPOs).
- The attacker's goal is usually **Domain Admin** — control of the whole domain.

Because everything trusts the DC, a single weak point can cascade into total compromise. That's why AD security is its own discipline.

## The attack chain (concepts, defender-focused)

AD attacks follow a recognizable flow. Understanding each step tells you what to monitor and harden.

1. **Recon / enumeration** — map users, groups, computers, trusts. Tools: **BloodHound** (graphs attack paths), `ldapsearch`, PowerView. *Defender:* BloodHound run by *you* shows your own risky paths — fix them.
2. **Initial access** — phishing, a weak service, password spray. *Defender:* MFA, user training, strong passwords, lockouts.
3. **Credential theft:**
   - **Kerberoasting** — request service tickets and crack them offline to get service-account passwords. Works because some service accounts have weak passwords. *Defender:* long (25+ char) managed service-account passwords, monitor ticket requests.
   - **AS-REP Roasting** — targets accounts with "no pre-auth" set. *Defender:* require Kerberos pre-auth.
   - **LLMNR/NBT-NS poisoning** (Responder) — capture hashes from chatty network name resolution. *Defender:* disable LLMNR/NBT-NS.
4. **Lateral movement** — reuse credentials/hashes to hop between machines (**Pass-the-Hash**, **Pass-the-Ticket**). *Defender:* limit local admin reuse (LAPS), tiered admin, network segmentation.
5. **Privilege escalation to Domain Admin** — abuse misconfigured ACLs, GPOs, or delegation that BloodHound reveals. *Defender:* audit and fix those ACLs/delegations.
6. **Persistence / domination** — **DCSync** (impersonate a DC to pull all password hashes), **Golden Ticket** (forge Kerberos tickets). *Defender:* protect the KRBTGT account, monitor replication, tier-0 isolation.

## The key insight

AD compromise is rarely one magic exploit — it's a **chain of small misconfigurations**: a weak service password here, excessive permissions there, an old protocol enabled somewhere. Defenders win by closing the chain: BloodHound your own domain, fix the paths, enable MFA, disable legacy protocols, tier your admins.

## Build your own AD lab (legal, free)

To practice legally, build a lab you own:
- **GOAD (Game of Active Directory)** — a free, deliberately-vulnerable AD lab you deploy on your own hardware (github.com/Orange-Cyberdefense/GOAD). Built for exactly this.
- **Microsoft's eval VMs** — free time-limited Windows Server/client VMs to build a small domain in VirtualBox/VMware.
- **TryHackMe / HackTheBox** — guided AD rooms and the "Pro Labs" AD networks (legal, in-scope).

Never practice AD attacks against a domain you don't own — including a workplace or school domain. That's the Module 0 line, and AD attacks are especially serious legally.

## Defender's checklist (the real takeaway)

- Run **BloodHound** against your own domain; fix the shortest paths to Domain Admin.
- **MFA** on all accounts, especially admins.
- **Disable legacy protocols**: LLMNR, NBT-NS, NTLMv1.
- **Strong service-account passwords** (managed/gMSA, 25+ chars) — kills Kerberoasting.
- **Tier your admins** (tier-0 DCs isolated), use **LAPS** for local admin passwords.
- Protect **KRBTGT** (rotate it), monitor for DCSync/replication from non-DCs.
- Patch DCs promptly.

## Key terms

- **Domain Controller (DC)**: the server running AD.
- **Kerberos**: AD's ticket-based authentication.
- **BloodHound**: graphs attack paths in AD (offensive recon *and* defensive audit).
- **Kerberoasting / AS-REP Roasting**: stealing and cracking service/user tickets.
- **Pass-the-Hash / Pass-the-Ticket**: reusing credentials without the plaintext password.
- **DCSync / Golden Ticket**: domain-domination techniques.
- **GOAD**: a free vulnerable AD lab you run yourself.

Next: **Module 9 — Network Attacks & Binary Exploitation (intro).**
