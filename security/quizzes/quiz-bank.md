# Security Quiz Bank

Self-test questions for each module. Answers are at the bottom — try before peeking.
You can also drop this into Nanban's `documents/` and say "quiz me on this" in Study mode.

## Module 0 — Ethics & Law
1. What single thing makes security testing legal rather than criminal?
2. You find a SQL bug on your college's website by accident. What are the correct next steps?
3. True/False: scanning a system you don't own is fine as long as you don't change anything.
4. What is a bug bounty program?

## Module 1 — How the Web Works
5. Which HTTP method is typically used to submit a login form?
6. Why is validation done only in the browser (frontend) not real security?
7. In `GET /search?q=shoes`, which part is user input an attacker can change?
8. A server returns status 500 after you send odd input. Why might that interest a tester?

## Module 2 — Recon
9. What does `nmap` tell you about a target?
10. What is "attack surface"?
11. What's the difference between passive and active recon?
12. What tool would you use to find an unlinked `/admin` page, and how does it work?

## Module 3 — SQL Injection
13. In one sentence, what is the root cause of SQL injection?
14. Why does the input `' OR '1'='1` often bypass a login?
15. What is the single most effective fix, and how does it work?
16. Give two defence-in-depth measures beyond that main fix.

## Module 4 — XSS & OWASP Top 10
17. How is XSS similar to SQLi, and how is it different?
18. Which XSS type is most dangerous and why: stored, reflected, or DOM-based?
19. What is the primary fix for XSS?
20. What is IDOR / Broken Access Control? Give an example.
21. Name the three recurring "shapes" most web bugs reduce to.

## Module 5 — Tools
22. Which tool sits between your browser and the target to inspect/modify requests?
23. What's the difference between an online and an offline password attack?
24. Why is Kali Linux recommended for beginners gathering tools?
25. For a developer focused on web security, which small set of tools covers most needs?

---

## Answers

1. **Explicit permission** (you own it, or have written authorisation).
2. Stop immediately, don't access data or test further, find their disclosure/bug-bounty policy, report privately, never threaten.
3. **False.** Scanning/probing without permission can itself be the offence.
4. A program where an organisation invites testers to find bugs *within a defined scope*, often paying for valid reports (HackerOne, Bugcrowd).
5. **POST** (data goes in the body).
6. The browser is controlled by the attacker; they can bypass any client-side limit. The **server** must re-validate.
7. The `q=shoes` query parameter (and really the whole URL/headers/cookies).
8. A 500 often means the server **crashed on your input** — a sign the input reached code unsafely (possible injection).
9. Open **ports** and the **services/versions** running on them.
10. The full set of inputs/endpoints an attacker can reach.
11. Passive = gather info without touching the target; active = send requests to it (only when authorised).
12. `gobuster`/`ffuf`/`dirb` — they request many common paths from a **wordlist** and report which exist.
13. Untrusted input is mixed into a query as **code** instead of being kept as **data**.
14. It makes the `WHERE` clause always true (`'1'='1'`), so every row matches and the app thinks login succeeded.
15. **Parameterised / prepared queries** — input is sent to the database separately from the SQL, so it can never change the query's meaning.
16. Any two: ORM/query builder, least-privilege DB account, input type validation, hide raw DB errors, hash passwords.
17. Both are injection (input becomes code). SQLi → code runs in the **database**; XSS → script runs in the **victim's browser**.
18. **Stored** — it's saved and runs automatically for every viewer, no crafted link needed.
19. **Output encoding/escaping** by context (plus CSP and HttpOnly cookies as layers).
20. The app doesn't check *what you're allowed to access*; e.g. changing `/order?id=1001` to `1002` shows another user's order.
21. (a) Server trusted input it shouldn't; (b) server didn't check permissions; (c) insecure default/misconfiguration.
22. An intercepting **proxy** — Burp Suite (or OWASP ZAP).
23. Online = guessing against a live login (slow, noisy, rate-limited); offline = cracking stolen **hashes** (fast — why strong, salted hashing matters).
24. It ships with the standard tools **pre-installed and configured**, so you don't assemble them one by one.
25. **Burp Suite + browser DevTools + sqlmap + solid understanding of the OWASP bugs.**
