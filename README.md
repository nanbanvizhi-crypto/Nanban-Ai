# 🤖 Nanban: Unga Local AI Agent

100% free. 100% unga laptop-la. Internet-ku unga chat pogaadhu, monthly fee illa, usage limit illa.

Browser-la open aagura chat app, 7 modes-oda:

| Mode | Enna pannum |
|---|---|
| 🤝 Personal Assistant | To-do list, calculations, quick questions, notes |
| 💻 Coding | Code ezhudhum, explain pannum, bugs fix pannum, files-a save pannum |
| ✍️ Writing | Letters, emails, posts, essays, Tamil ↔ English translation |
| 🔍 Research | Web-la search panni, pages-a padichu, source links-oda answer |
| 📚 Study | Unga PDF / notes-la irundhu answers, quiz, summary |
| 📈 Business | Ideas, cost/profit calculations, marketing, market research |
| 🛡️ Security Tutor | Pentesting / cybersecurity teacher — concepts, tools, lab guidance (unga sontha lab-ku mattum) |

Ella mode-layum: Tamil, English, Tanglish-la pesalaam. **Memory** irukku ("remember that..." nu sonna, adutha chat-layum nyabagam vechukkum).

Plus:
- **💻 Nanban Terminal**: AI agent + real terminal (bash/PowerShell/CMD) ore window-la, built-in code editor-oda.
- **🐉 Kali Linux section**: full-page Kali-OS styled workspace — terminal + AI ore idathula. Natural-a kelunga (Tanglish/English), AI command ezhudhum, neenga review panni Run pannunga. Built-in **Command Reference** — 59 tools (nmap, sqlmap, Metasploit full set, theHarvester, exiftool…) ovvoru command-aiyum English + Tanglish-la explain pannum. Unga sontha lab / authorised targets-ku mattum.
- **🖧 Servers**: unga VPS / Raspberry Pi / office machines-a SSH vazhiya neengalum AI-um manage panna.
- **🌐 Nanban Server**: always-on, multi-user web app + OpenAI-compatible API, phone-la irundhum access.
- **🧠 Smarter brains (free)**: Local Ollama defaults, aana **Admin → 🧠 AI model & settings**-la free cloud models (Groq, Google Gemini, Cerebras, **NVIDIA** build.nvidia.com) select pannalaam — free API key mattum. **🏆 Nanban Best** (best model per task) + **🏛️ Council** (several models combined) + auto-failover. Details: **MODELS.md**.
- **More built-in**: 🎤 **Voice** (speak + read-aloud), 📷 **Image understanding** (attach a photo, ask about it), 📱 **Telegram bot** (`telegram_bot.py`), 📲 **WhatsApp** (official Cloud API — `WHATSAPP-SETUP.md`), 🔔 **Scheduled tasks**, 🗄️ **Backup & restore**, 📊 **Usage dashboard**, 🌓 **light/dark toggle** — all in the app. 🍽️ DineFlow integration: `integrations/`.

---

## ✅ Setup (oru vaati mattum, ~20 nimisham)

Laptop: Windows 10/11, 16GB RAM, ~10GB free space.

1. **Python 3.13 install pannunga.** ⚠️ Python 3.15 vendaam: sila libraries-ku innum Windows support varala.
   - Python install manager irundha: Command Prompt-la `py install 3.13`
   - Illa-na python.org-la Python 3.13 installer download panni, **"Add python.exe to PATH"** tick pannunga.
   - "Python Launcher" (old version) installed-a irundha, Settings → Installed apps-la adha uninstall pannunga.
2. **Ollama install pannunga:** https://ollama.com/download → OllamaSetup.exe run pannunga.
3. Indha `local-ai-agent` folder-a unga laptop-la oru idathula vechukonga (e.g. `Documents\local-ai-agent`).
4. Folder-kulla **`setup.bat`**-a double-click pannunga. Libraries install aagi, model (~5GB) download aagum. Internet speed-a poruthu time edukkum.

## ▶️ Daily use — ONE click

Setup mudinja apram Desktop-la **Nanban** icon irukkum. **Adha double-click pannunga — avlo dhaan.**

Oru click-la ellame automatic-a varum:
- 🤖 Nanban app (chat, terminal, security, admin) browser-la open aagum
- 🌐 Server + API (phone/other devices access panna)
- 🧪 Security practice lab (Docker) — `AUTOSTART_LAB = True` vechaa
- 🐉 Kali — register panni irundha auto-connect

Thaniya thaniya click vेṇḍaam. Andha black window-a open-laye vechirunga (adhu server). Close panna ellame stop aagum.

Extra ways (venum-na mattum): `start_terminal.bat` (terminal mattum), endha folder-la-yum `nanban` command, `build_app.bat` → real `Nanban.exe`.

## 💻 Nanban Terminal (AI + terminal)

Windows Terminal-la open panna best-a irukkum (colours, emojis). Rendu modes, **Ctrl+T** press panni maathalaam:

| Mode | Enna |
|---|---|
| **✦ AI** | Normal-a pesunga: "indha folder-la enna irukku?", "calc.py-la bug fix pannu", "Flask app create pannu". AI commands run pannum, files read/edit pannum. Periya task-ku step plan pottu, ovvoru step-um tick pannum (`/plan`). |
| **$ SHELL** | Real terminal: `git`, `python`, `pip`, `vim`, `nano`, `htop`, `apt`, `ssh`, ellam work aagum. |

**Moonu shells, ore window-la:** Linux bash (WSL) · PowerShell · Command Prompt (CMD). `/linux`, `/powershell`, `/cmd` nu switch pannalaam. AI command generate pannum podhu endha shell-nu adhuve decide pannum (Linux command-na bash, Windows admin-na PowerShell, `dir`/`ipconfig` maadhiri old commands-na CMD).

**Auto-explain:** neenga type panna command fail aana, AI automatic-a 2-3 lines-la "ean fail aachu, correct command idhu" nu sollum. Venaam-na `config.py`-la `AUTO_EXPLAIN_ERRORS = False`.

**Safety:** AI ovvoru command-um file change-um run panradhukku munnaadi kaattum (files-ku colour diff). `y` = OK, `n` = vendaam (apram AI-ku enna pannanum-nu sollalaam), `a` = ellathukkum auto-approve. `rm -rf` maadhiri risky commands auto-approve-la kooda kekkum.

**Shortcuts:**
- `!git status`: AI mode-la irundhe oru shell command run pannalaam
- `?idhu en fail aachu`: shell mode-la irundhe AI kitta kekkalaam (last command-um adhoda output-um AI-ku theriyum)
- `cmd: ipconfig`, `ps: Get-Process`, `sh: ls -la`: endha mode-la irundhaalum oru specific shell-la oru command
- **Tab**: file names / commands complete · **↑ ↓**: history · **Ctrl+C**: stop · **Ctrl+D** / `/exit`: quit

**Commands:**

| Command | Enna |
|---|---|
| `/edit app.py` | Built-in code editor (syntax colours, line numbers). Ctrl+S save, Ctrl+Q quit, Ctrl+F find, Ctrl+G go to line |
| `/view app.py` | File-a colour-oda kaattum |
| `/tree` | Folder tree |
| `/linux` / `/powershell` / `/cmd` | Default shell maathalaam |
| `/plan` | AI-oda current step plan |
| `/vpn` · `/vpn on` · `/vpn off` · `/vpn ip` | VPN status, connect/disconnect (Windows VPN profile), public IP check |
| `/auto` | Auto-approve on/off |
| `/model qwen2.5-coder:7b` | AI model maathalaam (coding-ku idhu best) |
| `/new` | Pudhu conversation |
| `/help` | Ella commands |

### 🐧 Full Linux venum-na (WSL, oru vaati)

1. Start menu → PowerShell → right-click → **Run as administrator**
2. `wsl --install` type pannunga
3. Laptop restart pannunga. Ubuntu window open aagum, username + password create pannunga.
4. Nanban Terminal open pannunga. Automatic-a Linux bash use pannum (illa `/linux` type pannunga).

Ippo `apt install`, `sudo`, bash scripts ellam work aagum. `sudo` maadhiri password kekkura commands-a neengale `!` pottu run pannunga (e.g. `!sudo apt update`).

## 📱 Phone-la use panradhu (Android + iPhone)

Model laptop-la dhaan odum; phone browser-la adha open panreenga. Laptop on-la, Nanban running-la irukkanum.

1. `config.py`-la: `LAN_ACCESS = True`, `WEB_PASSWORD = "unga-password"` (idhu illaama phone access on aagaadhu).
2. Nanban restart pannunga. Tray icon → **Phone: show QR code** (illa sidebar-la QR irukku).
3. Phone-um laptop-um **same Wi-Fi**-la irukkanum. QR scan pannunga, login: user `nanban`, password neenga vechadhu.
4. Phone browser menu → **"Add to Home Screen"** (Android Chrome: ⋮ → Add to Home screen; iPhone Safari: Share → Add to Home Screen). Ippo app icon maadhiri full-screen-la open aagum.

Phone-la ellam irukku: chat, 6 modes + **🖥️ Computer** mode (laptop-la commands run panna, files edit panna), **💻 Terminal tab** (laptop-la commands type panni run pannalaam, output live-a varum, "Ask AI about this result" button).

**Safety phone-la:** Computer mode-la AI act panna sidebar-la **"⚡ Allow actions"** tick pannanum. `rm -rf` maadhiri risky commands phone-la irundhu run aagave aagaadhu.

**Veettukku veliya irundhu** (mobile data-la) use panna: free **Tailscale** app-a laptop-layum phone-layum install panni same account-la login pannunga. Apram laptop-oda Tailscale IP (e.g. `http://100.x.y.z:7860`) phone-la open pannunga. Port forwarding, public IP edhuvum thevai illa, traffic encrypted.

## 🖧 Servers: unga servers-a Nanban-ala manage pannunga (SSH)

VPS, Raspberry Pi, office PC, cloud VM: SSH irukkura endha Linux machine-ayum Nanban Terminal-la irundhu control pannalaam. Neengalum command type pannalaam, AI-um pannum.

**Server add panradhu (oru vaati):**
```
/server add vps root@203.0.113.10                 # password kekkum (session-ku mattum nyabagam)
/server add pi pi@192.168.1.50 --key C:\Users\me\.ssh\id_ed25519 --notes home raspberry pi
/server add office dev@10.0.0.5:2222 --password xxx --save-password   # file-la save aagum (plain text), key dhaan safe
```

**Use panradhu:**

| Command | Enna |
|---|---|
| `/server list` | Ella servers |
| `/server status` | Ellathoda health table: uptime, load, memory, disk, top processes |
| `/server use vps` | Ippo shell mode commands-um AI-um **vps**-la work aagum. Prompt-la ⇅ vps nu theriyum |
| `/server local` | Thirumba laptop-ku |
| `/server ssh vps` | Full interactive SSH (vim, htop, sudo password ellam) |
| `/server push app.py /var/www/` · `/server pull /var/log/nginx/error.log .` | Files upload / download |
| `/server test vps` · `/server remove vps` | Connection check / delete |

**AI-oda servers-la:** `/server use` panna thevai illa. AI mode-la direct-a sollunga:
- "vps-la nginx status check panni, error log last 50 lines paaru"
- "pi-la disk evlo free irukku? 80%-ku mela irundha old logs clean pannu"
- "office server-la /opt/app-la git pull panni service restart pannu"

AI endha server-nu peru vechu purinjukkum, ovvoru command-um file change-um munnaadi kaattum (`y` sonna dhaan run aagum). Server-la risky commands (`rm -rf`, `reboot`...) red-la warn pannum.

Server-la interactive program (`htop`, `vim`) type panna, Nanban automatic-a real SSH session open pannum. Windows-la `ssh` command illa-na: Settings → Apps → Optional features → **OpenSSH Client**.

## 🌐 Nanban Server: always-on + multi-user + API

Ore laptop-a veettu/office "AI server"-a vekka. Ore port-la web app + API.

**Setup:**
1. `config.py`-la users add pannunga:
   ```python
   USERS = {"dev": "strong-pass", "amma": "another"}
   ADMIN_USERS = ["dev"]
   API_KEYS = ["nanban-sk-" + "edhaavadhu-long-random-text"]
   ```
2. `start_server.bat` double-click (illa `python server.py`). Web app: `http://<laptop-ip>:8000`, API docs: `http://<laptop-ip>:8000/docs`.
3. Windows login aanadhum automatic-a start aaga: Command Prompt-la folder-kulla `.venv\Scripts\python server.py --install-autostart`. (Remove: `--remove-autostart`.)

**Users:** ovvoruthtarukkum thani memory, thani to-do list. Admin users-ku mattum **Terminal tab**, **Computer mode**, **Admin tab** (machine stats, yaar online, API usage, servers health, logs, AI model settings, **💾 Storage breakdown** — Ollama models, Kali/WSL, Docker lab, app folders ovvonnum size-oda separate card-la).

**Veliya irundhu access:**
- **Tailscale (recommended, free):** laptop + phone/other laptop-la install panni same account login. Apram `http://100.x.y.z:8000`. Encrypted, port forwarding vendaam.
- **Cloudflare Tunnel (temporary public link):** `cloudflared tunnel --url http://localhost:8000` → oru `https://xxx.trycloudflare.com` URL varum. Public-a irukkum, so USERS password-um API keys-um strong-a vechukonga.

**API use panradhu (B):** OpenAI-compatible. ChatGPT API-ku ezhudhina code-la base URL mattum maathina podhum.

```python
# pip install openai
from openai import OpenAI
client = OpenAI(base_url="http://192.168.1.10:8000/v1", api_key="nanban-sk-...")
reply = client.chat.completions.create(
    model="nanban:coding",          # nanban = assistant mode, nanban:research = web search-oda, illa raw "llama3.1:8b"
    messages=[{"role": "user", "content": "Python-la fibonacci function ezhudhu"}],
)
print(reply.choices[0].message.content)
```

```python
# Plain requests, conversation-oda (session_id reuse pannunga)
import requests
r = requests.post("http://192.168.1.10:8000/api/agent", headers={"Authorization": "Bearer nanban-sk-..."},
                  json={"message": "Naalaiku meeting add pannu", "mode": "assistant", "session_id": "dineflow-user-42"})
print(r.json()["reply"])
```

```bash
# Servers via API (DevOps automation, cron jobs, monitoring)
curl -H "Authorization: Bearer nanban-sk-..." http://192.168.1.10:8000/api/servers/status
curl -H "Authorization: Bearer nanban-sk-..." -X POST http://192.168.1.10:8000/api/servers/vps/run -d '{"command":"df -h"}' -H "Content-Type: application/json"
```

Endpoints: `GET /v1/models`, `POST /v1/chat/completions` (stream OK), `POST /api/agent`, `GET /api/servers`, `GET /api/servers/status`, `POST /api/servers/{name}/run`, `GET /api/health`, `GET /docs`. Rate limit: `API_RATE_LIMIT` per minute per key. Usage log: `data/api_usage.jsonl`.

**Honest limits:** 16GB laptop + 8B model = ore samayathula 2-3 per comfortable-a; adhukku mela queue aagi slow aagum. Laptop 24/7 on-la irukkanum, sleep off pannunga (Settings → Power → Sleep: Never, plugged in).

## 🛡️ VPN

Nanban unga laptop-la dhaan odudhu. So unga Windows-la endha VPN on pannaalum (ProtonVPN free, WireGuard, NordVPN, edhuvum), Nanban-oda web search, downloads, terminal commands ellam **already adhu vazhiya dhaan pogum**. Thaniya onnum set panna vendaam.

Nanban enna pannum:
- Terminal status bar-layum, chat sidebar-layum **🛡️ VPN ON/off** kaattum.
- `/vpn ip`: internet unga-la eppadi paakudhu (IP + country). VPN work aaguthaa-nu check panna.
- `/vpn on` / `/vpn off`: Windows Settings-la add panna VPN profile-a connect/disconnect. (ProtonVPN maadhiri apps-ku avanga app-laye on pannunga.)
- **Kill switch:** `config.py`-la `REQUIRE_VPN = True` vechaa, VPN off-a irukkum podhu AI-oda internet tools (web search, page fetch) block aagum.

Honest-a: VPN speed-a Nanban maatha mudiyaadhu; adhu VPN server-um unga internet-um dhaan.

## 📂 Folders

| Folder | Enna |
|---|---|
| `documents/` | Study mode-ku PDF, Word, .txt, .md files inga podunga (illa app-la upload pannunga) |
| `workspace/` | Agent save panra files (code, essays, notes) inga varum |
| `data/` | Memory, to-do list, document index. Delete panna ellam reset aagidum |

## ⚙️ Customize (`config.py` open panni maathunga)

- **Peru maathanum:** `AGENT_NAME = "Nanban"`
- **Vera model:** `MODEL = "qwen2.5:7b"` (Tamil-ku konjam better). Maathina apram Command Prompt-la `ollama pull qwen2.5:7b` run pannunga.
  - Coding-ku best: `qwen2.5-coder:7b`
  - Romba fast, light: `llama3.2:3b`
- **Creative answers:** `TEMPERATURE = 0.9` (consistent-a venum-na `0.3`)
- **Code run panna allow panna:** `ALLOW_CODE_RUN = True`. Agent ezhudhura Python code unga laptop-la run aagum, so purinjukittu on pannunga.
- **Mode prompts / tools:** `MODES` section-la ovvoru mode-oda instructions-um tools-um maathalaam.

## 🔧 Pudhu tool add panradhu (example)

`tools.py`-la oru function ezhudhunga:

```python
def word_count(text: str) -> str:
    """Count the words in a piece of text.

    Args:
        text: The text to count
    """
    return f"{len(text.split())} words"
```

Apram `ALL_TOOLS` list-la `word_count` add pannunga, `config.py`-la oru mode-oda `"tools"` list-la `"word_count"` add pannunga. Avlo dhaan, agent adha use pannum.

## ❓ Problems

| Problem | Fix |
|---|---|
| "Python 3.13 is needed" | Command Prompt-la `py install 3.13`, apram setup.bat again |
| `py install` work aagala | Installed apps-la old "Python Launcher" uninstall pannunga, pudhu Command Prompt open pannunga |
| "Can't reach Ollama" | Start menu-la Ollama app open pannunga (system tray-la llama icon varum) |
| "model not found" | Command Prompt-la `ollama pull llama3.1:8b` |
| Answers romba slow | `MODEL = "llama3.2:3b"` try pannunga, illa vera apps close pannunga |
| `nanban` command work aagala | setup.bat-la Y press panneengala? Pudhu terminal window open pannunga |
| Terminal-la `/linux` → "WSL not installed" | Mela "Full Linux venum-na" steps |
| Terminal-la boxes/emojis odanju theriyudhu | Windows Terminal app use pannunga (Microsoft Store-la free) |
| Phone-la open aagala | Same Wi-Fi-aa? `LAN_ACCESS = True` + `WEB_PASSWORD` set pannitu Nanban restart panneengala? Windows Firewall popup vandha "Allow" pannunga |
| Tray icon varala | `start.bat` use pannunga; illa `.venv\Scripts\pythonw.exe launcher.py` run pannunga |
| `/server add` → "login failed" | Username/password/key check; server-la `ssh user@host` manual-a work aaguthaa paarunga |
| Server-la AI command "took longer than 120s" | `config.py` → `COMMAND_TIMEOUT` increase; illa long jobs-ku `nohup cmd &` |
| `python server.py` → "only served on 127.0.0.1" | `config.py`-la `USERS` add pannunga (login illaama network-ku open aagaadhu) |
| API 401 | `Authorization: Bearer <key>` header, key `API_KEYS`-la irukkanum |
| `build_app.bat` fail | Antivirus PyInstaller-a block pannalaam; `start.bat` / Desktop shortcuts already work aagum, exe optional dhaan |
| Web search work aagala | Internet connection check pannunga (search mattum dhaan internet use pannum) |
| Document search error | `ollama pull nomic-embed-text` |

## 📝 Honest-a sollanum-na

8B local model romba nalla work pannum, aana ChatGPT/Claude level-ku periya cloud models maadhiri illa. Romba complex reasoning-la thappu pannalaam, so important vishayangalai (money, health, legal) double-check pannunga.

## 🚀 Live / online

Want a public URL or to put this on GitHub? See **`DEPLOY.md`** — Cloudflare Tunnel (your own Nanban, public, free, all features), GitHub, and a chat-only cloud demo (`deploy/`). Vercel/Netlify can't host the full app (no persistent server or model) — DEPLOY.md explains why and what to use instead.

**📱 Phone works even when the laptop is OFF?** Yes — host Nanban on a cheap always-on server (no GPU; the AI brain is a free Groq/NVIDIA model). Full step-by-step for Railway / Render / a Docker VPS is in **`cloud/CLOUD-DEPLOY.md`**. Everything is set by environment variables (key, password) — no code editing.

**🌍 Just want your phone to reach the laptop from anywhere?** Easiest of all: **Admin → 🌍 Remote access → Start** gives you a QR code to scan. (Laptop stays on.)
