"""
🎓 Guided Labs — step-by-step interactive security practice (safe sandbox).

Each lab is a sequence of steps. For every step you see: what to do (Tanglish), the command to
run, and a hint. You run it in the sandbox (simulated output), then move to the next step.
No real target, no risk. Finishing a lab earns XP in the Progress tracker.
"""

import sandbox

# Each step: instruct_ta, cmd (suggested command), hint_ta, teaches_ta
LABS = [
    {
        "id": "recon101",
        "title": "Recon Basics — find what's running",
        "level": "🟢 Beginner",
        "goal_ta": "Oru target-la enna services odudhu nu kandupidikka kathukradhu (recon). Attack-oda "
                   "mudhal stage — enna irukku nu theriyama onnum panna mudiyadhu.",
        "xp": 30,
        "steps": [
            {"instruct_ta": "Mudhalla target reachable-aanu check pannu.",
             "cmd": "ping 10.10.10.5",
             "hint_ta": "ping = host up-aanu paakka.",
             "teaches_ta": "Host alive-nu confirm aanadhu. Ippo scan pannalaam."},
            {"instruct_ta": "Open ports + services scan pannu (version detection-oda).",
             "cmd": "nmap -sV 10.10.10.5",
             "hint_ta": "-sV = service version kaattum.",
             "teaches_ta": "Pala port open — FTP(21), SSH(22), HTTP(80), MySQL(3306). "
                           "vsftpd 2.3.4 old version = interesting."},
            {"instruct_ta": "Web server (port 80) la enna irukku nu scan pannu.",
             "cmd": "nikto 10.10.10.5",
             "hint_ta": "nikto = web vulnerability scanner.",
             "teaches_ta": "Missing security headers + exposed config.php theridhu. Web side weak."},
            {"instruct_ta": "Oru old service-ku ready exploit irukkaanu thedu.",
             "cmd": "searchsploit vsftpd 2.3.4",
             "hint_ta": "searchsploit = Exploit-DB offline search.",
             "teaches_ta": "vsftpd 2.3.4-ku backdoor exploit irukku. Recon → known-vuln match = classic path. "
                           "Defense: service-ah update pannu, old versions retire pannu."},
        ],
    },
    {
        "id": "webapp101",
        "title": "Web App Testing — DVWA SQL injection",
        "level": "🟡 Intermediate",
        "goal_ta": "Oru vulnerable web app-la SQL injection epdi kandupidikradhu + epdi defend pandradhu.",
        "xp": 45,
        "steps": [
            {"instruct_ta": "Web server-la hidden directories thedu.",
             "cmd": "gobuster dir -u http://10.10.10.5",
             "hint_ta": "gobuster = directory brute-force.",
             "teaches_ta": "/login.php, /config.php, /admin theridhu. Attack surface map aachu."},
            {"instruct_ta": "Login/input parameter-ah SQL injection-ku test pannu.",
             "cmd": "sqlmap -u http://10.10.10.5/vuln?id=1 --dbs",
             "hint_ta": "--dbs = databases list panna try pannum.",
             "teaches_ta": "'id' parameter injectable. Databases (dvwa, mysql) leak aachu. "
                           "Idhu happen aagudhu = input validation illa."},
            {"instruct_ta": "Oru config file content paaru (leaked creds example).",
             "cmd": "cat config.php",
             "hint_ta": "config files-la DB creds irukkalaam.",
             "teaches_ta": "Empty DB password theridhu — weak config. Defense: strong creds + "
                           "parameterised queries + least-privilege DB user. SQLi fully stoppable."},
        ],
    },
    {
        "id": "privesc101",
        "title": "Post-Exploit — who am I, what next",
        "level": "🔴 Advanced",
        "goal_ta": "Access kidaicha apuram enna paakanum — privilege + system info (post-exploitation concept).",
        "xp": 40,
        "steps": [
            {"instruct_ta": "Ippo entha user-nu paaru.",
             "cmd": "whoami",
             "hint_ta": "whoami = current user.",
             "teaches_ta": "www-data = limited web user. Admin illa, so next goal = privilege escalation."},
            {"instruct_ta": "User-oda full privilege details paaru.",
             "cmd": "id",
             "hint_ta": "id = uid/gid/groups.",
             "teaches_ta": "Groups paathu enna access irukku nu theriyum."},
            {"instruct_ta": "Running processes paaru (enna services root-ah odudhu).",
             "cmd": "ps aux",
             "hint_ta": "ps = processes.",
             "teaches_ta": "root-ah odura service-la bug irundha privilege escalation. Defense: least privilege, "
                           "patch, monitoring. Attacker spread aagaama segment pannu."},
        ],
    },
]


def lab_by_id(lid: str) -> dict | None:
    return next((l for l in LABS if l["id"] == lid), None)


def labs_list() -> list[dict]:
    return LABS


def step_markdown(lid: str, step_idx: int) -> str:
    lab = lab_by_id(lid)
    if not lab:
        return "Oru lab thernedu."
    n = len(lab["steps"])
    if step_idx >= n:
        return (f"## ✅ Lab complete — {lab['title']}\n\nNalla velai! +{lab['xp']} XP earn pannine. "
                "Progress tab-la paaru. Vera lab try pannu.")
    s = lab["steps"][step_idx]
    return (f"## {lab['title']}\n**Step {step_idx+1} / {n}**  ·  {lab['level']}\n\n"
            f"🎯 {s['instruct_ta']}\n\n"
            f"**Run this:**\n```bash\n{s['cmd']}\n```\n\n"
            f"💡 _Hint: {s['hint_ta']}_\n\n"
            "Keela **Run step** click pannu → output + enna kathukkiye nu paaru → **Next step**.")


def run_step(lid: str, step_idx: int) -> tuple[str, str]:
    """Return (sandbox_output, teaches_ta) for the step's command."""
    lab = lab_by_id(lid)
    if not lab or step_idx >= len(lab["steps"]):
        return "", ""
    s = lab["steps"][step_idx]
    out, _expl = sandbox.run(s["cmd"])
    return out, s["teaches_ta"]
