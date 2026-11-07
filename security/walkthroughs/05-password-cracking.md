# Walkthrough 5 — Password Cracking (on hashes you own)

Hands-on for Module 6. You'll crack password hashes with John the Ripper and Hashcat — using hashes **you generate yourself** — and run the one experiment that teaches password storage better than anything: watch a weak hash fall in seconds and a strong hash refuse to.

> Only ever crack hashes you own (your own lab's DB dump, or hashes you make here). Cracking someone else's hashes is the Module 0 line.

## Setup (all on your own Kali/Linux)
These tools ship with Kali. The famous wordlist `rockyou.txt` is at `/usr/share/wordlists/rockyou.txt` (gunzip it first if needed: `sudo gunzip /usr/share/wordlists/rockyou.txt.gz`).

## Step 1 — Make some hashes you own
Create hashes of a known password so you can see cracking work:
```bash
# A weak password, hashed two different ways
echo -n 'password123' | md5sum | awk '{print $1}' > weak_md5.txt
# bcrypt (slow hash) of the SAME password, using python
python3 -c "import bcrypt; print(bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode())" > strong_bcrypt.txt
cat weak_md5.txt strong_bcrypt.txt
```
Now you have the same password stored two ways — fast (MD5) and slow+salted (bcrypt).

## Step 2 — Crack the weak one (fast hash)
```bash
# John auto-detects many formats
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt weak_md5.txt
john --show --format=raw-md5 weak_md5.txt
```
It cracks almost instantly, because MD5 is fast — a GPU/CPU tries millions of guesses per second, and `password123` is in rockyou.

Same with Hashcat:
```bash
hashcat -m 0 -a 0 weak_md5.txt /usr/share/wordlists/rockyou.txt   # -m 0 = MD5
hashcat -m 0 --show weak_md5.txt
```

## Step 3 — Try the strong one (slow hash) — the lesson
```bash
john --format=bcrypt --wordlist=/usr/share/wordlists/rockyou.txt strong_bcrypt.txt
```
Watch the speed: bcrypt is **deliberately slow** (tens of ms per guess), so the same wordlist that cracked MD5 in a blink now crawls. For a weak password it may still eventually crack; for a long passphrase it becomes infeasible. That contrast — same password, wildly different crack time — **is** why bcrypt/argon2 exist. You just proved it yourself.

## Step 4 — Rules and masks (how real cracking gets smarter)
Attackers don't just use raw wordlists; they mutate them:
```bash
# Rule-based: applies mutations like password -> P@ssw0rd!, Password1, etc.
john --wordlist=/usr/share/wordlists/rockyou.txt --rules weak_md5.txt

# Mask/brute force: try all combos of a pattern (only feasible for short/weak)
hashcat -m 0 -a 3 weak_md5.txt '?l?l?l?l?l?d'   # 5 lowercase + 1 digit
```
This is why "add a number and a symbol" to a short password isn't enough — rules cover those mutations. **Length** is what actually helps.

## Step 5 — The defender's takeaways (the real goal)
You've now seen, firsthand:
- **Fast hashes (MD5/SHA1) are unsafe for passwords** — use **bcrypt, scrypt, or argon2id**.
- **Salting matters** — bcrypt salts automatically; identical passwords get different hashes, killing precomputed tables.
- **Length beats complexity** — a long passphrase resists both dictionary+rules and brute force.
- **Block breached passwords** (Have I Been Pwned) and **require MFA** so a cracked password alone isn't enough.

## Apply to DineFlow
Open where DineFlow hashes passwords. If it's MD5/SHA — or any fast hash, or unsalted — that's your highest-priority fix: switch to **argon2id** or **bcrypt** with a tuned work factor. You've now seen exactly what you're defending against.

## Clean up
```bash
rm -f weak_md5.txt strong_bcrypt.txt
```

## Key takeaways
- Cracking speed is governed by the **hash algorithm**, not luck — weak hash = instant, strong hash = infeasible.
- The MD5-vs-bcrypt experiment is the clearest password-storage lesson there is.
- Defenders win with slow salted hashing + length + breached-password blocking + MFA.

Back to **ROADMAP.md** / **OSCP-PREP.md** to keep going on legal platforms.
