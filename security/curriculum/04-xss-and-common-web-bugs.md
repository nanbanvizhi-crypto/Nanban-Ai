# Module 4 — XSS and Other Common Web Bugs

SQLi was input crossing into *database code*. **Cross-Site Scripting (XSS)** is input crossing into *the page's JavaScript*. Same root cause — untrusted input treated as code — different place. This module covers XSS plus a tour of the other bugs in the OWASP Top 10 so you know the landscape.

## Cross-Site Scripting (XSS)

### What it is
A site takes user input and puts it into a page **without sanitising it**. If an attacker's input contains HTML/JavaScript, the victim's browser runs it — as if the site wrote it. The attacker's script now runs with the victim's session.

Example: a comment box that shows comments back. Attacker posts:

```html
<script>/* steal the victim's session cookie, or act as them */</script>
```

Now everyone who views that comment runs the attacker's script in their own logged-in session.

### The three types
- **Stored XSS**: the payload is saved (a comment, a profile name) and runs for every viewer. Most dangerous.
- **Reflected XSS**: the payload is in a URL/parameter and reflected straight back in the response; the attacker has to get the victim to click a crafted link.
- **DOM-based XSS**: the unsafe handling happens in the browser's own JavaScript, not the server.

### What it leads to
Session theft (acting as the victim), defacing pages, keylogging a form, redirecting to phishing, performing actions as the victim. It targets *users* of the site, not the server directly.

### See it in your lab
DVWA and Juice Shop both have XSS exercises. On DVWA (security **Low**) → **XSS (Reflected)**, enter your name, see it appear. Then enter a harmless proof like `<b>test</b>` and watch it render as **bold** — meaning the browser interpreted your input as HTML. That's the whole bug: if `<b>` becomes bold, `<script>` becomes code. The walkthrough `walkthroughs/02-xss-dvwa.md` goes step by step and then has you raise the security level to watch the fix work.

### THE FIX
- **Escape output by context.** When putting user data into HTML, convert `<` `>` `&` `"` into `&lt;` `&gt;` etc. so the browser shows them as text, never tags. Every modern template engine does this automatically (React, Jinja2, Vue) — don't disable it (`dangerouslySetInnerHTML`, `|safe`, `v-html` are the escape hatches to avoid unless you're certain).
- **Content Security Policy (CSP)**: a response header that tells the browser "only run scripts from these sources", blocking injected inline scripts even if one slips through.
- **Use frameworks' built-in protections**; sanitise rich HTML with a vetted library (DOMPurify) if you must allow some formatting.
- **HttpOnly cookies**: mark session cookies `HttpOnly` so JavaScript can't read them — limits what stolen-session XSS can grab.

## A tour of the rest (OWASP Top 10, in plain words)

The **OWASP Top 10** is the industry's list of the most common web risks. You've met two; here's the landscape so recon and testing make sense.

1. **Broken Access Control** — the app doesn't properly check *what you're allowed to do*. E.g. changing `/order?id=1001` to `1002` and seeing someone else's order (called **IDOR**). Hugely common. Fix: check ownership/permissions on the server for every request.
2. **Cryptographic Failures** — sensitive data sent/stored without proper encryption (plaintext passwords, HTTP instead of HTTPS). Fix: HTTPS everywhere, hash passwords (bcrypt/argon2), encrypt sensitive data at rest.
3. **Injection** — SQLi, and also command injection (input reaching a shell), LDAP, etc. Fix: parameterise, never pass input to a shell.
4. **Insecure Design** — the flaw is in how the feature was designed, not a coding slip. Fix: threat-model features before building.
5. **Security Misconfiguration** — default passwords, debug mode on in production, verbose errors, open cloud buckets. Fix: harden configs, disable defaults, least privilege.
6. **Vulnerable & Outdated Components** — using a library with a known CVE. Fix: keep dependencies updated, scan them (`npm audit`, Dependabot).
7. **Identification & Authentication Failures** — weak login: no rate limiting, weak passwords allowed, broken session handling. Fix: strong password policy, MFA, rate limits, secure sessions.
8. **Software & Data Integrity Failures** — trusting updates/data without verifying them (e.g. an unsigned auto-update). Fix: verify signatures, lock dependencies.
9. **Security Logging & Monitoring Failures** — you can't detect or investigate an attack because nothing was logged. Fix: log security events, alert on anomalies.
10. **Server-Side Request Forgery (SSRF)** — tricking the server into making requests to places it shouldn't (internal services, cloud metadata). Fix: validate/allow-list outbound URLs.

## The pattern across all of them

Almost every item reduces to one of:
- *The server trusted input it shouldn't have* (injection, XSS).
- *The server didn't check what the user is allowed to do* (access control).
- *Something was left in an insecure default/configuration* (misconfig, outdated components).

Learn to see those three shapes and the whole list becomes intuitive.

## Key terms

- **XSS**: injecting script that runs in a victim's browser.
- **Output encoding / escaping**: turning input into harmless text for its context — the XSS fix.
- **CSP**: a header restricting what scripts a page may run.
- **IDOR / Broken Access Control**: accessing resources you shouldn't by changing an identifier.
- **OWASP Top 10**: the standard list of common web risks.

Next: **Module 5 — Tools of the Trade.**
