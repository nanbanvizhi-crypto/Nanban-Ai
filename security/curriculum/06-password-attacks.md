# Module 6 — Password Attacks (and why they work)

Passwords are the softest part of most systems. Understanding how they're attacked is how you learn to store and protect them properly. All practice here is on **your own lab / hashes you own** (Module 0).

## Two completely different situations

1. **Online attack** — guessing against a live login (web form, SSH, RDP). Slow, noisy, and stoppable by the defender (rate limits, lockouts, MFA).
2. **Offline attack** — you already have the password *hashes* (e.g. you dumped a DB on your own lab, or cracked a captured file) and you crack them on your own hardware. Fast, silent, limited only by the hash algorithm's strength.

The defender's job is different for each: stop online guessing with rate-limiting/MFA; make offline cracking infeasible with strong, slow, salted hashing.

## How password hashing works (the thing you're protecting)

Servers never store your actual password — they store a **hash** (a one-way fingerprint). At login they hash what you typed and compare.

- **Bad:** fast hashes (MD5, SHA1, unsalted SHA256). A GPU tries billions/sec → cracked in seconds.
- **Good:** slow, salted, memory-hard hashes — **bcrypt, scrypt, argon2**. Deliberately slow (tens of ms each), with a random **salt** per password so identical passwords hash differently and precomputed tables ("rainbow tables") are useless.

This is why "store passwords hashed" isn't enough — *which* hash matters enormously.

## Online attacks (concept + lab)

Tools like **Hydra** throw a username + password list at a login. On your own lab:

```bash
# Against YOUR DVWA login (lab only). Teaches why rate-limiting matters.
hydra -l admin -P /usr/share/wordlists/rockyou.txt 127.0.0.1 http-post-form \
  "/login.php:username=^USER^&password=^PASS^:Login failed"
```

What you learn: with no lockout and a weak password, this succeeds. With a lockout after 5 tries, or MFA, it doesn't. That's the lesson — you're seeing *why* the defenses exist.

**Defender fixes:** rate-limit logins, lock/slow after failures, require MFA, ban common passwords, log and alert on bursts of failures, use CAPTCHA on repeated failures.

## Offline attacks (concept + lab)

If you have hashes (from your own lab's DB), tools like **John the Ripper** and **Hashcat** crack them.

```bash
# John: crack a hash file you obtained from YOUR lab
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
john --show hashes.txt

# Hashcat (GPU): -m is the hash type (0=MD5, 1800=sha512crypt, 3200=bcrypt)
hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt
```

What you learn directly: an **MD5** hash of a weak password falls in seconds; a **bcrypt** hash of the *same* password may take years. Run both on your lab and watch the speed difference — that single experiment teaches hashing better than any lecture.

**Attack methods to understand:**
- **Dictionary** — try words from a list (rockyou.txt is the famous one, from a real breach).
- **Rule-based** — mutate words (`password` → `P@ssw0rd!`) with rules.
- **Brute force / mask** — try all combinations up to a length (only feasible for short/weak passwords).
- **Credential stuffing** — reuse passwords leaked from other breaches (why password reuse is dangerous).

## Defender's playbook (the real goal)

- Hash with **argon2id** or **bcrypt** (work factor tuned to ~250ms), always **salted**.
- Enforce length over complexity (a long passphrase beats `P@ss1`).
- Block known-breached passwords (Have I Been Pwned's API/list).
- **MFA** everywhere it matters — it defeats stolen/guessed passwords.
- Rate-limit and lock online logins; monitor for credential stuffing.
- Never log passwords; never email them; rotate on breach.

## Apply to DineFlow

Check how DineFlow stores user passwords. If it's anything but bcrypt/argon2 with per-user salt, that's the highest-priority fix. Add login rate-limiting and offer MFA.

## Key terms

- **Hash**: one-way fingerprint of a password.
- **Salt**: random per-password value that defeats precomputed tables.
- **Slow/memory-hard hash**: bcrypt/scrypt/argon2 — makes offline cracking infeasible.
- **Online vs offline**: guessing a live login vs cracking stolen hashes.
- **Credential stuffing**: reusing breached passwords across sites.

Next: **Module 7 — Privilege Escalation.**
