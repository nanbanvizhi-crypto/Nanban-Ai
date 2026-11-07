# Module 0 — Ethics and the Law (read this first, seriously)

Security testing is a real, respected, well-paid skill. The **only** thing that separates a security professional from a criminal is **permission**. Same commands, same tools — one has written authorisation, the other goes to jail. Learn this module before any other.

## The one rule

**Only test systems you own, or systems you have explicit written permission to test.**

That's it. Everything else follows from this.

- Your own lab (DVWA, Juice Shop, WebGoat in the `lab/` folder) → yes, attack freely. They are built for it.
- A VM or server you rent and own → yes.
- A legal practice platform (TryHackMe, HackTheBox, PortSwigger Academy) → yes, within their rules.
- A friend's website, your college portal, a company you don't work for, "just testing" a random site → **no.** Even if you find a bug and mean well. Even if you don't change anything.

## Why it matters (India + global)

- In India, unauthorised access is an offence under the **Information Technology Act, 2000** (Sections 43 and 66). Penalties include fines and imprisonment.
- Most countries have an equivalent (USA: CFAA, UK: Computer Misuse Act).
- "I was only learning" is not a legal defence. Intent to help does not make access authorised.
- Scanning or probing a system you don't own can itself be the offence — you don't have to "break in".

## Responsible disclosure (the right way to report a real bug)

If you ever find a vulnerability in something that isn't yours (e.g. you notice it by accident):
1. **Stop.** Don't dig deeper, don't download data, don't test further.
2. Check if they have a **bug bounty** or **security.txt** / responsible-disclosure policy. Many companies pay for bugs reported properly (HackerOne, Bugcrowd).
3. Report it privately to them. Give them time to fix it before telling anyone.
4. Never demand money or threaten — that's extortion, a separate crime.

## Your mindset as a learner

- You are learning to **defend**. Every attack technique you understand is a thing you now know how to prevent in your own apps (like DineFlow).
- The best pentesters are the best defenders. Understanding the attack is how you write code that resists it.
- Curiosity is good. Keep it pointed at your own lab and legal platforms.

## Quick self-check

- Can I scan my neighbour's Wi-Fi "just to see"? → **No.**
- Can I run sqlmap against `http://127.0.0.1:8080` (my DVWA)? → **Yes.**
- I found a SQL bug on my college site. What do I do? → **Don't test further; report it privately; don't access data.**
- A site has a bug bounty listed. Can I test it? → **Yes, within the scope and rules they publish.**

Next: **Module 1 — How the Web Actually Works.**
