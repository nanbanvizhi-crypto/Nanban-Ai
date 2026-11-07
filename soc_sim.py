"""
🛡️ SOC Simulator — blue-team log analysis practice.

You're a SOC analyst. Nanban shows you a set of logs with an attack hidden inside. You answer
multiple-choice questions: what's the attack, which IP, what to do. Instant feedback teaches you
to *detect* attacks — the defender's core skill. Solving a scenario earns XP.
"""

SCENARIOS = [
    {
        "id": "bruteforce",
        "title": "SSH brute-force?",
        "level": "🟢 Beginner",
        "xp": 25,
        "logs": (
            "Nov 07 02:11:03 sshd[2011]: Failed password for root from 185.220.14.9 port 51002\n"
            "Nov 07 02:11:04 sshd[2012]: Failed password for root from 185.220.14.9 port 51010\n"
            "Nov 07 02:11:05 sshd[2013]: Failed password for admin from 185.220.14.9 port 51022\n"
            "Nov 07 02:11:06 sshd[2014]: Failed password for admin from 185.220.14.9 port 51031\n"
            "Nov 07 02:11:08 sshd[2015]: Failed password for test from 185.220.14.9 port 51040\n"
            "... (480 more failed attempts in 90 seconds) ...\n"
            "Nov 07 02:12:39 sshd[2498]: Accepted password for admin from 185.220.14.9 port 51560"
        ),
        "questions": [
            {"q_ta": "Indha logs-la enna attack theriyudhu?",
             "options": ["Normal login activity", "SSH brute-force attack",
                         "Port scan", "SQL injection"],
             "answer": 1,
             "explain_ta": "90 seconds-la 480+ failed passwords, pala usernames — classic brute-force. "
                           "Kadaisila 'Accepted' = attack SUCCESS aachu (admin account compromised)."},
            {"q_ta": "Entha IP suspicious?",
             "options": ["127.0.0.1", "185.220.14.9", "192.168.1.1", "10.0.0.5"],
             "answer": 1,
             "explain_ta": "185.220.14.9 — ellaa failed + success attempts idhil irundhu than. Block pannanum."},
            {"q_ta": "First response action enna?",
             "options": ["Ignore pannu", "Andha IP block + admin password reset + sessions kill",
                         "Server-ah off pannu", "Wait and watch"],
             "answer": 1,
             "explain_ta": "Account compromised, so: IP block, admin password reset, active sessions kill, "
                           "MFA enable. Defense munnadiye: rate-limit + fail2ban + key-only SSH."},
        ],
    },
    {
        "id": "portscan",
        "title": "Reconnaissance scan?",
        "level": "🟢 Beginner",
        "xp": 25,
        "logs": (
            "14:02:11 firewall: DROP TCP 203.0.113.44 -> 10.0.0.5:21\n"
            "14:02:11 firewall: DROP TCP 203.0.113.44 -> 10.0.0.5:22\n"
            "14:02:11 firewall: DROP TCP 203.0.113.44 -> 10.0.0.5:23\n"
            "14:02:11 firewall: DROP TCP 203.0.113.44 -> 10.0.0.5:25\n"
            "14:02:12 firewall: DROP TCP 203.0.113.44 -> 10.0.0.5:80\n"
            "14:02:12 firewall: DROP TCP 203.0.113.44 -> 10.0.0.5:443\n"
            "14:02:12 firewall: DROP TCP 203.0.113.44 -> 10.0.0.5:3306\n"
            "(one source IP hitting 1000 ports in 3 seconds)"
        ),
        "questions": [
            {"q_ta": "Idhu enna activity?",
             "options": ["Data exfiltration", "Port scan (reconnaissance)",
                         "Brute-force", "DDoS"],
             "answer": 1,
             "explain_ta": "Oru IP, short time-la niraya different ports sequential-ah — port scan. "
                           "Attack lifecycle Stage 1 (Recon). Attacker enna open nu paakuraan."},
            {"q_ta": "Idhu kill-chain la entha stage?",
             "options": ["Actions on Objectives", "Reconnaissance",
                         "Installation", "Command & Control"],
             "answer": 1,
             "explain_ta": "Recon stage — info gathering. Innum break-in aagala, aana warning sign. "
                           "Monitor + block + un attack surface kuraikka."},
        ],
    },
    {
        "id": "exfil",
        "title": "Data exfiltration / C2?",
        "level": "🟡 Intermediate",
        "xp": 35,
        "logs": (
            "03:00:01 proxy: 10.0.0.23 -> evil-cdn[.]top  GET /beacon  (512 B)\n"
            "03:05:01 proxy: 10.0.0.23 -> evil-cdn[.]top  GET /beacon  (512 B)\n"
            "03:10:01 proxy: 10.0.0.23 -> evil-cdn[.]top  GET /beacon  (512 B)\n"
            "03:15:02 proxy: 10.0.0.23 -> evil-cdn[.]top  POST /upload (240 MB)\n"
            "(regular 512B calls every 5 min, then one huge upload at 3 AM)"
        ),
        "questions": [
            {"q_ta": "Indha pattern enna kaattudhu?",
             "options": ["Normal web browsing", "C2 beaconing + data exfiltration",
                         "Software update", "Backup job"],
             "answer": 1,
             "explain_ta": "Every 5 min exact 512B calls = C2 beaconing (malware phone-home). "
                           "Appuram 240MB upload 3AM-ku = data exfiltration. Rendum red flags."},
            {"q_ta": "Entha clue most suspicious?",
             "options": ["3 AM timing", "Regular beacon interval + rare domain + huge upload",
                         "GET request", "Port 443"],
             "answer": 1,
             "explain_ta": "Regular exact-interval beacon + unknown domain (evil-cdn.top) + large off-hours "
                           "upload — combination. Defense: egress filtering, DNS/domain blocking, NDR, DLP."},
        ],
    },
]


def scenario_by_id(sid: str) -> dict | None:
    return next((s for s in SCENARIOS if s["id"] == sid), None)


def scenarios_list() -> list[dict]:
    return SCENARIOS


def intro_markdown(sid: str) -> str:
    s = scenario_by_id(sid)
    if not s:
        return "Oru scenario thernedu."
    return (f"## 🛡️ {s['title']}  ·  {s['level']}\n\n"
            "Nee oru SOC analyst. Keezha logs paaru, appuram kelvikku bathil sollu.\n\n"
            f"**📋 Logs:**\n```\n{s['logs']}\n```")


def question_markdown(sid: str, qidx: int) -> tuple[str, list]:
    s = scenario_by_id(sid)
    if not s or qidx >= len(s["questions"]):
        return f"## ✅ Solved — {s['title'] if s else ''}\n\n+{s['xp'] if s else 0} XP! Vera scenario try pannu.", []
    q = s["questions"][qidx]
    return (f"**Question {qidx+1} / {len(s['questions'])}:** {q['q_ta']}", q["options"])


def check_answer(sid: str, qidx: int, choice: str) -> tuple[bool, str]:
    s = scenario_by_id(sid)
    if not s or qidx >= len(s["questions"]):
        return False, ""
    q = s["questions"][qidx]
    try:
        picked = q["options"].index(choice)
    except ValueError:
        return False, "Oru option thernedu."
    ok = picked == q["answer"]
    mark = "✅ Correct!" if ok else f"❌ Illa. Sari bathil: **{q['options'][q['answer']]}**"
    return ok, f"{mark}\n\n{q['explain_ta']}"
