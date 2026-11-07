# Walkthrough 1 — SQL Injection on DVWA (guided, on your own lab)

A first hands-on exercise. Everything here happens on **your own DVWA container** at `127.0.0.1` — a target built to be practised on. Read Module 3 first.

Goal: *watch* why a weak query breaks, then watch the fix make the same input harmless. Understanding beats collecting payloads.

## Setup
1. Start the lab: `lab/start_lab.bat` (or `./start_lab.sh`). Wait for images to download the first time.
2. Open `http://127.0.0.1:8080`. Log in: `admin` / `password`.
3. First visit only: click **Create / Reset Database** on the setup page.
4. Left menu → **DVWA Security** → set to **Low** → Submit. (We'll raise this later.)
5. Left menu → **SQL Injection**.

## Step 1 — Normal behaviour
There's a **User ID** box. Enter `1`, submit. You get one user's first/last name. The app is running something like `SELECT first_name, last_name FROM users WHERE user_id = '1'`.

## Step 2 — Prove input reaches SQL
Enter a single quote: `'`
- You get a **database error**. That error is the whole discovery: your quote broke out of the string and reached the SQL engine. If input were handled safely, you'd get "user not found", not an SQL error.

## Step 3 — See the logic bend
Enter: `1' OR '1'='1`
- Now you get **every** user, not one. Why: the query became `... WHERE user_id = '1' OR '1'='1'`, and `'1'='1'` is always true, so every row matches. You've made the app's logic do something the developer never intended — using only the input box.

Sit with that. You didn't "hack" anything mysterious; you typed characters the server trusted. That trust is the bug.

## Step 4 — (Optional) see how data gets extracted
Module 3 described UNION-based extraction. DVWA's own help and the PortSwigger Academy SQLi labs walk this specific technique step by step on legal targets. Do it there when you're ready — the mechanism is "append my own SELECT to the results". The *lesson* is identical: the query trusted input.

## Step 5 — The important half: watch the fix work
1. Go back to **DVWA Security** → set to **Impossible** → Submit.
2. Return to **SQL Injection**. Try `'` and `1' OR '1'='1` again.
3. They do **nothing** now — just "user not found" or no error. 

Why? At the **Impossible** level, DVWA's code uses a **parameterised query** (and checks the input is an integer). The input is sent to the database separately from the SQL, so your quotes and `OR` are treated as a literal (nonsensical) user ID, never as code. Same input, neutralised — exactly the fix from Module 3.

If you open DVWA's source for the two levels (it's on disk in the container, and on the DVWA GitHub), you can read the difference: string-concatenation at Low, prepared statement at Impossible. Reading that diff is the single most useful thing in this walkthrough.

## What you just learned
- How to *detect* SQLi (break the query with a quote, watch for errors/behaviour change).
- *Why* it works (input became code).
- *How it's fixed* (parameterised queries + type checks) — and you saw the fix defeat the attack.

## Apply it to your own code (DineFlow)
Open any place DineFlow builds a SQL query. If it pastes variables into a query string, rewrite it as a parameterised query / ORM call today. You now know firsthand what you're preventing.

Next: **Walkthrough 2 — XSS on DVWA.**
