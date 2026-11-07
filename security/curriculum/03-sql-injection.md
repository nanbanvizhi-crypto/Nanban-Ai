# Module 3 — SQL Injection (SQLi)

The classic web vulnerability, and the best one to learn first because it teaches the core lesson: **mixing untrusted input with code is dangerous.** You'll understand how it happens, see it in your lab, and — most importantly — know exactly how to prevent it in your own apps.

## What a database query looks like

Apps store data in a database and fetch it with **SQL**. To log you in, the server might run:

```sql
SELECT * FROM users WHERE username = 'dev' AND password = 'secret';
```

The app builds that string by pasting your input into the middle. Here's the dangerous version (do **not** write code like this):

```python
# VULNERABLE — input pasted straight into the query string
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
```

## Why it breaks

The database can't tell the difference between *the code the developer wrote* and *the input the user typed* — it's all one string. So if the user types a username of:

```
' OR '1'='1
```

the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '...';
```

`'1'='1'` is always true, so the `WHERE` matches every row. The app thinks the login succeeded. The attacker is in — **without knowing any password.** That's SQL injection: input escaped out of its quotes and became part of the logic.

## What attackers can do with it (conceptually)

Depending on the app and database, SQLi can lead to:
- **Auth bypass** (the login trick above).
- **Reading data that isn't theirs** — dumping other users' records, using a `UNION` to append attacker-chosen columns to results.
- **"Blind" extraction** — when the app shows no data back, asking true/false questions ("is the first letter of the admin password > 'm'?") and reading the answer from timing or small behaviour changes. Slow, but automatable.
- In bad cases, reading files or running commands on the server.

You'll **see** these in a controlled way in the lab walkthrough (`walkthroughs/01-sqli-dvwa.md`), on DVWA, which exists for exactly this. The point isn't to collect payloads — it's to watch *why* each one works so the prevention makes sense.

## Seeing it in your lab (safe, legal)

1. Start the lab. Open DVWA `http://127.0.0.1:8080` (login `admin` / `password`), set security to **Low**.
2. Go to **SQL Injection**. There's an input that expects a user ID.
3. Enter a normal value → one user. Enter a classic test value like `1'` (a single quote) → an SQL **error** appears. That error is the tell: your quote broke the query, so input is reaching SQL unfiltered.
4. The walkthrough file takes it from there, step by step, and then has you **raise DVWA's security level** and watch the same inputs stop working — because the code now uses the fix below.

### About `sqlmap`

`sqlmap` is a tool that automates finding and exploiting SQLi. Against **your own lab** it's a great way to see how automated testing works:

```bash
# Only ever against your own lab / authorised targets
sqlmap -u "http://127.0.0.1:8080/vulnerabilities/sqli/?id=1&Submit=Submit" --cookie="PHPSESSID=...; security=low" --batch
```

Use it to understand what defenders are up against and why weak queries fall instantly. Pointing it at anything you don't own is the crime from Module 0.

## THE FIX — this is the real goal

SQL injection is **100% preventable**, and the fix is simple. Never build queries by pasting input into strings. Use **parameterised queries** (also called prepared statements), where the input is sent *separately* from the SQL, so the database always treats it as data, never as code.

```python
# SAFE — Python, parameterised. The '?' is a placeholder; username/password
# are passed separately and can never change the query's meaning.
cursor.execute(
    "SELECT * FROM users WHERE username = ? AND password = ?",
    (username, password),
)
```

```php
// SAFE — PHP PDO prepared statement
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->execute([$username, $password]);
```

```javascript
// SAFE — Node.js (mysql2), parameters passed as an array
conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", [username, password]);
```

Layered defences on top:
- **Use an ORM / query builder** (Django ORM, SQLAlchemy, Prisma, Sequelize) — they parameterise by default. Your DineFlow app should use one.
- **Least privilege**: the app's database account should only be able to do what it needs (no `DROP`, no admin).
- **Validate input types** (an ID should be an integer — reject anything else) as defence in depth, *not* as the main protection.
- **Never show raw database errors** to users; log them instead.
- Store passwords **hashed** (bcrypt/argon2), so even a dumped table doesn't reveal them.

If you only remember one thing from this whole course: **parameterise your queries.** That single habit kills the most common serious web bug.

## Key terms

- **SQL**: the language apps use to query databases.
- **Injection**: making input cross from "data" into "code".
- **Parameterised / prepared query**: input sent separately from SQL — the fix.
- **UNION-based / blind SQLi**: techniques for reading data; blind = inferred from behaviour when no data is shown.
- **ORM**: a library that builds safe queries for you.

Next: **Module 4 — Cross-Site Scripting (XSS).**
