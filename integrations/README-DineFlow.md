# 🍽️ Connect Nanban AI into DineFlow

Nanban exposes an **OpenAI-compatible API**, so DineFlow can use it as its AI brain.

## 1. Turn on the Nanban API (one time)
In `config.py`:
```python
USERS = {"dev": "a-strong-password"}          # the server needs at least one user
API_KEYS = ["nanban-sk-" + "make-this-long-random"]
```
Run **`start_server.bat`**. Your API is now at `http://<host>:8000/v1` and `http://<host>:8000/api/agent`.

## 2a. Drop-in widget (plain JS — any site)
Open **`dineflow-widget.html`**, set `NANBAN_URL` and `NANBAN_KEY` at the top, and either
open it, or copy its `<style> + <div id="nb-ai"> + <script>` into any DineFlow page. You get a
floating "💬 AI" button with a chat box, wired to Nanban with per-user memory.

## 2b. React component (for a React DineFlow)
```jsx
import { useState } from "react";

const NANBAN_URL = "http://127.0.0.1:8000";
const NANBAN_KEY = "nanban-sk-...";

export function DineFlowAI() {
  const [log, setLog] = useState([]);
  const [q, setQ] = useState("");

  async function send() {
    if (!q.trim()) return;
    const mine = q; setQ(""); setLog(l => [...l, { role: "user", text: mine }, { role: "ai", text: "…" }]);
    const r = await fetch(`${NANBAN_URL}/api/agent`, {
      method: "POST",
      headers: { Authorization: `Bearer ${NANBAN_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ message: mine, mode: "assistant", session_id: "dineflow-react" }),
    });
    const data = await r.json();
    setLog(l => [...l.slice(0, -1), { role: "ai", text: data.reply || "(no reply)" }]);
  }

  return (
    <div style={{ maxWidth: 380 }}>
      <div style={{ height: 300, overflowY: "auto", border: "1px solid #eadfd3", borderRadius: 12, padding: 10 }}>
        {log.map((m, i) => (
          <div key={i} style={{ textAlign: m.role === "user" ? "right" : "left", margin: "6px 0" }}>
            <span style={{ background: m.role === "user" ? "#f0e4d7" : "#fff", padding: "8px 12px", borderRadius: 14, display: "inline-block" }}>{m.text}</span>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
        <input value={q} onChange={e => setQ(e.target.value)} onKeyDown={e => e.key === "Enter" && send()}
               placeholder="Ask DineFlow AI…" style={{ flex: 1, padding: 9, borderRadius: 10, border: "1px solid #e7dccf" }} />
        <button onClick={send} style={{ background: "#c56a44", color: "#fff", border: 0, borderRadius: 10, padding: "0 16px" }}>Send</button>
      </div>
    </div>
  );
}
```

## 3. Or the raw API
```javascript
// OpenAI-compatible — point any OpenAI client at Nanban
fetch(`${NANBAN_URL}/v1/chat/completions`, {
  method: "POST",
  headers: { Authorization: `Bearer ${NANBAN_KEY}`, "Content-Type": "application/json" },
  body: JSON.stringify({ model: "nanban:assistant", messages: [{ role: "user", content: "..." }] })
});
```

**Reachability:** if DineFlow runs on the same machine → `127.0.0.1`. If it's hosted/live → deploy
Nanban to the cloud (`cloud/CLOUD-DEPLOY.md`) and use that URL. The model behind it (local, Groq,
NVIDIA, 🏆 Best, 🏛️ Council) is whatever you pick in Nanban's Admin — with auto-failover.
