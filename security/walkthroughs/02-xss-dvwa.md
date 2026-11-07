# Walkthrough 2 — Reflected XSS on DVWA (guided, on your own lab)

Hands-on for Module 4, on **your own DVWA container**. Goal: watch input become code *in the browser*, then watch escaping neutralise it.

## Setup
1. Lab running, DVWA open at `http://127.0.0.1:8080`, logged in.
2. **DVWA Security** → **Low** → Submit.
3. Left menu → **XSS (Reflected)**.

## Step 1 — Normal behaviour
There's a "What's your name?" box. Enter `Dev`, submit. The page replies `Hello Dev`. Your input was placed straight into the page's HTML.

## Step 2 — Prove input becomes HTML
Enter: `<b>Dev</b>`
- The page shows **Dev** in bold. That's the discovery: the browser treated your input as an HTML tag, not text. The app put your input into the page without escaping it.

## Step 3 — From formatting to code
If `<b>` runs, so does `<script>`. A harmless proof that script executes:

Enter: `<script>alert(document.domain)</script>`
- A popup appears showing the site's domain. (`alert()` is the standard *harmless* proof-of-concept — it demonstrates script execution without doing anything damaging. Never go beyond a harmless proof, even on your lab, as a habit.)

What this means in the real world: instead of `alert()`, an attacker's script could read a non-HttpOnly session cookie, submit a form as you, or redirect you. Reflected XSS needs the victim to open a crafted link; **stored** XSS (try DVWA's **XSS (Stored)** page — e.g. a guestbook) runs for everyone automatically, which is worse. Try the stored one too and notice it persists across reloads.

## Step 4 — The important half: watch the fix work
1. **DVWA Security** → **Impossible** → Submit.
2. Back to **XSS (Reflected)**. Enter `<b>Dev</b>` and the `<script>` payload again.
3. Now the page literally prints `<b>Dev</b>` as text — your tags show as characters, nothing runs.

Why? The secure code **escapes output**: it converts `<` into `&lt;`, `>` into `&gt;`, so the browser renders them as the literal symbols instead of interpreting them as tags. Same input, rendered harmless — the fix from Module 4.

## What you just learned
- Detect XSS: put a harmless tag (`<b>`) in an input; if it renders, the field is injectable.
- Why it works: input was inserted into HTML without escaping.
- How it's fixed: output encoding/escaping (plus CSP and HttpOnly cookies as layers).

## Apply it to your own code (DineFlow)
- Are you using a template engine (React, Jinja2, Vue)? Then output is auto-escaped — **don't** bypass it with `dangerouslySetInnerHTML` / `|safe` / `v-html` unless you've sanitised with something like DOMPurify.
- Add a **Content-Security-Policy** header.
- Mark session cookies **HttpOnly**.

Now revisit Module 4's OWASP Top 10 tour — with two bugs under your belt, the pattern ("server trusted input" / "didn't check permissions" / "insecure default") will click.

Next: pick a track in **ROADMAP.md** and keep going on legal platforms.
