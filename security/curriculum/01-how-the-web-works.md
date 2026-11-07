# Module 1 — How the Web Actually Works

You can't test what you don't understand. Before any security, you need a clear picture of what happens when you open a web page. This module has no attacks — it's the foundation everything else stands on.

## Client and server

- **Client** = your browser (Chrome, Safari). It *requests* things.
- **Server** = a computer somewhere running the website's code. It *responds*.
- They talk over **HTTP** (or **HTTPS**, which is HTTP inside encryption).

When you type `example.com`:
1. Your browser finds the server's address (DNS turns the name into an IP like `93.184.216.34`).
2. It opens a connection and sends an **HTTP request**.
3. The server runs some code and sends back an **HTTP response** (usually HTML).
4. Your browser draws the page.

## An HTTP request, piece by piece

```
GET /products?id=42 HTTP/1.1      <- method, path, query string
Host: example.com                  <- which site
Cookie: session=abc123             <- who you are (your login token)
User-Agent: Mozilla/5.0 ...        <- what browser you claim to be
```

- **Method**: `GET` (fetch something), `POST` (send data, e.g. a login form), also `PUT`, `DELETE`.
- **Path**: which page/resource (`/products`).
- **Query string**: `?id=42` — parameters. **This is user input.** Remember that.
- **Headers**: extra info (host, cookies, content type).
- **Body** (for POST): the actual data, e.g. `username=dev&password=secret`.

## An HTTP response

```
HTTP/1.1 200 OK                    <- status code
Content-Type: text/html            <- what kind of data
Set-Cookie: session=abc123         <- server giving you a token

<html>...the page...</html>        <- the body
```

Status codes you'll see constantly:
- **200** OK · **301/302** redirect · **403** forbidden · **404** not found · **500** server error (often interesting — the server crashed on your input).

## The key security insight

**Everything the client sends can be changed by the attacker.** The URL, the query string, the form fields, the cookies, the headers — all of it. Your browser sends them politely, but nothing *forces* a client to be polite.

A server that trusts incoming data because "the form only allows 10 characters" or "the dropdown only has 3 options" is wrong — those limits live in the browser, which the attacker controls. **The server must re-check everything.** Almost every web vulnerability is a version of *the server trusted input it shouldn't have.*

## Where the vulnerable parts live

- **Frontend** (HTML/CSS/JS in the browser): what you see. Validation here is for convenience, never security.
- **Backend** (server code: Python, PHP, Node…): makes the real decisions. Must validate everything.
- **Database** (MySQL, PostgreSQL…): stores data. The backend talks to it with **SQL queries** — the subject of Module 3.

## See it yourself (on your own lab)

1. Start the lab, open Juice Shop at `http://127.0.0.1:3000`.
2. Press **F12** to open browser DevTools → **Network** tab.
3. Click around. Watch each request appear: method, URL, status.
4. Click one request → see its headers, and the response.

That Network tab, plus a tool called **Burp Suite** (Module 6), is 80% of web testing: *look at the requests, change them, resend them.*

## Key terms

- **Parameter**: a named input (`id=42`, `username=dev`).
- **Endpoint**: a path the server responds to (`/login`, `/api/users`).
- **Payload**: the specific input you send to test something.
- **Session / cookie**: how the server remembers you're logged in.

Next: **Module 2 — Recon: Mapping a Target.**
