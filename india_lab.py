"""
🇮🇳 India Lab — Nanban's futuristic security learning hub.

A red-team + blue-team LEARNING curriculum across today's and tomorrow's technologies.
For every domain you learn, in Tanglish:
  🎯 what the technology is,
  ⚔️ how attacks work (concept + which lab tool), at a lab/recognition level,
  🛡️ how to DEFEND it (hardening + detection) — the part that actually keeps you safe,
  🧪 a legal place to practise (your own lab, intentionally-vulnerable targets, or free legal platforms).

BOUNDARY (built-in, non-negotiable): practise only on targets you OWN, have WRITTEN permission for,
or that are MADE for practice (Metasploitable, DVWA, TryHackMe, Hack The Box, OWASP, PortSwigger).
Pointing these techniques at someone else's real system without permission is a crime — Nanban won't
help with that. India Lab teaches you to attack *practice* targets so you can *defend* the real ones.
"""

LEVELS = ["🟢 Beginner", "🟡 Intermediate", "🔴 Advanced", "🔮 Future-tech"]

# Legal practice platforms (no lab setup needed — browser is enough)
PLATFORMS = [
    ("TryHackMe", "tryhackme.com", "Guided rooms, beginner-friendly, step-by-step."),
    ("Hack The Box", "hackthebox.com", "Challenge machines + Academy courses."),
    ("PortSwigger Web Security Academy", "portswigger.net/web-security", "Best free web-pentest labs."),
    ("OWASP Juice Shop / DVWA / WebGoat", "owasp.org", "Install in your own lab, attack freely."),
    ("OverTheWire", "overthewire.org", "Linux + security wargames."),
    ("picoCTF", "picoctf.org", "Beginner CTF, learn by solving."),
    ("Metasploitable / VulnHub", "vulnhub.com", "Vulnerable VMs for your VirtualBox lab."),
]

# ---------------------------------------------------------------- curriculum

# Each domain: id, icon, name, level, future(bool),
#   what_ta (what it is), attack_ta (how attacks work — concept + lab tool),
#   defend_ta (how to defend — hardening + detection), tools (lab tools), practice (legal target)
DOMAINS = [
    {
        "id": "web", "icon": "🌐", "name": "Web & API Security", "level": 0, "future": False,
        "what_ta": "Websites, web apps, REST/GraphQL APIs — internet-la ellame idhu mela than odudhu.",
        "attack_ta": "Common bugs: SQL injection (database-ah kaali pannradhu), XSS (user browser-la "
                     "script run), CSRF, SSRF, broken auth, IDOR (vera user data access), file upload. "
                     "Lab-la DVWA/Juice Shop mela tools vechi test panni epdi bug varudhu nu paapom.",
        "defend_ta": "Input validation + parameterised queries (SQLi stop), output encoding (XSS stop), "
                     "CSRF tokens, least-privilege DB user, WAF, security headers (CSP, HSTS), "
                     "rate-limiting, auth + session proper-ah. OWASP Top 10 padichu ovvonna fix pannu.",
        "tools": ["sqlmap", "nikto", "whatweb", "feroxbuster", "wfuzz", "burpsuite"],
        "practice": "DVWA, OWASP Juice Shop, PortSwigger Academy",
    },
    {
        "id": "network", "icon": "🖧", "name": "Network & Infrastructure", "level": 0, "future": False,
        "what_ta": "Computers, servers, routers onnoda epdi pesudhu — ports, services, protocols.",
        "attack_ta": "Recon-la start: open ports + services + versions kandupidi (nmap). Weak/old service "
                     "irundha adhu entry point. Lab-la Metasploitable scan panni enna run aagudhu nu paapom.",
        "defend_ta": "Theva illadha ports close pannu, firewall rules, service-ellam update, "
                     "network segmentation (VLAN), strong configs, monitoring (IDS). Attack surface-ah "
                     "chinnadhaka vai — evlo kammi service, avlo safe.",
        "tools": ["nmap", "netcat", "tshark", "metasploit"],
        "practice": "Metasploitable 2/3 in your VirtualBox lab",
    },
    {
        "id": "passwords", "icon": "🔑", "name": "Authentication & Passwords", "level": 0, "future": False,
        "what_ta": "Login systems, passwords, hashes — yaaru ulla varalaam nu decide pannradhu.",
        "attack_ta": "Weak passwords brute-force / dictionary attack-ku easy. Hash leak aana crack panna "
                     "try pannuvanga. Lab-la un sontha test hashes mela tools epdi work aagudhu nu kathuko.",
        "defend_ta": "Long passphrases + password manager, MFA/2FA (ellaidhaium mukkiyam), bcrypt/argon2 "
                     "hashing (salt), account lockout + rate-limit, passkeys/WebAuthn ku move. "
                     "Password reuse pannadhe.",
        "tools": ["hydra", "medusa", "ncrack", "ophcrack", "rainbowcrack"],
        "practice": "Your own test accounts / DVWA brute-force page only",
    },
    {
        "id": "wireless", "icon": "📡", "name": "Wireless & WiFi", "level": 1, "future": False,
        "what_ta": "WiFi networks, wireless signals — WPA2/WPA3 security.",
        "attack_ta": "Weak WiFi password / old WEP encryption vulnerable. Handshake capture panni "
                     "crack panna try pannuvanga. Idha *un sontha router* mela mattum test pannu.",
        "defend_ta": "WPA3 (illa minimum WPA2-AES), strong long WiFi password, WPS off, guest network "
                     "separate, router firmware update, default admin password maathu. Un router = un responsibility.",
        "tools": ["aircrack-ng", "airodump-ng", "aireplay-ng"],
        "practice": "Only your OWN home router / a dedicated test AP",
    },
    {
        "id": "osint", "icon": "🔎", "name": "OSINT & Recon", "level": 0, "future": False,
        "what_ta": "Publicly available information — emails, domains, metadata — vechi target-ah purinjikaradhu.",
        "attack_ta": "Public data (website, social, leaked docs) sekarichu attacker target map pannuvanga. "
                     "Photo metadata-la location kooda leak aagalaam. Awareness-ku idha therinjiko.",
        "defend_ta": "Un/company digital footprint kammi pannu, metadata strip pannu (exiftool), "
                     "oversharing thavir, privacy settings, employees-ku awareness training. "
                     "Attacker-ku enna theriyudho adha nee munnadiye paaru.",
        "tools": ["theharvester", "exiftool", "whatweb"],
        "practice": "Your own domain / your own files",
    },
    {
        "id": "exploit", "icon": "💥", "name": "Exploitation & Metasploit", "level": 1, "future": False,
        "what_ta": "Theriyira vulnerability-ah use panni access vaangradhu — pentest-oda core stage.",
        "attack_ta": "Known vulnerability (CVE) irukkura service-ku ready exploit irukkum. Metasploit "
                     "framework-la lab target mela epdi end-to-end flow nadakudhu nu safe-ah kathuko.",
        "defend_ta": "Patch management (CVE varudhu-dhan udane update), vulnerability scanning regular-ah, "
                     "EDR/antivirus, least privilege, network segmentation — exploit aanaalum spread aagaama "
                     "thadu. Unknown-ah irukkradhai vida patched-ah iru.",
        "tools": ["metasploit", "nmap"],
        "practice": "Metasploitable, HTB machines, TryHackMe",
    },
    {
        "id": "forensics", "icon": "🧬", "name": "Digital Forensics & Malware", "level": 1, "future": False,
        "what_ta": "Attack nadandha apuram evidence collect panni, malware-ah analyse pandradhu (blue team).",
        "attack_ta": "Attacker files hide panna, logs delete panna, malware pack panna try pannuvanga. "
                     "Defender-ah nee hidden data + malicious files kandupidikka kathukanum.",
        "defend_ta": "File analysis (binwalk, exiftool), packet analysis (tshark), malware pattern match "
                     "(yara rules), log analysis, incident response plan, backups. Attack-ah kandupidichu "
                     "evidence preserve pannradhu oru full skill.",
        "tools": ["binwalk", "exiftool", "tshark", "yara"],
        "practice": "Sample malware in an ISOLATED VM / forensics CTF challenges",
    },
    {
        "id": "cloud", "icon": "☁️", "name": "Cloud Security (AWS/Azure/GCP)", "level": 2, "future": False,
        "what_ta": "Modern apps cloud-la run aagudhu — S3 buckets, IAM, serverless, VMs.",
        "attack_ta": "Misconfigured storage (public S3 bucket), over-permissioned IAM roles, leaked keys "
                     "— idhuthaan cloud-la #1 problem. Lab-la un sontha free-tier account mela config test pannu.",
        "defend_ta": "Least-privilege IAM, storage public-access block, key rotation + secrets manager, "
                     "CloudTrail/logging, encryption at rest + transit, CSPM tools, MFA on root. "
                     "Config-ah correct-ah vechiye cloud-la 90% safe.",
        "tools": ["cloud provider CLI", "nmap", "custom scripts"],
        "practice": "Your own AWS/GCP free-tier, flaws.cloud, CloudGoat",
    },
    {
        "id": "containers", "icon": "📦", "name": "Containers & Kubernetes", "level": 2, "future": False,
        "what_ta": "Docker containers + Kubernetes — modern apps epdi package + deploy aagudho.",
        "attack_ta": "Insecure images (old packages), exposed Docker/K8s API, privileged containers, "
                     "secrets in images — container escape-ku vazhi. Lab-la local K8s (minikube) mela paapom.",
        "defend_ta": "Minimal + scanned images, non-root containers, no privileged mode, network policies, "
                     "RBAC, secrets management, API server lock-down, runtime security. "
                     "Image build pannumbodhe scan pannu.",
        "tools": ["trivy/scanners", "nmap", "kubectl"],
        "practice": "minikube + Kubernetes Goat in your lab",
    },
    {
        "id": "mobile", "icon": "📱", "name": "Mobile Security (Android/iOS)", "level": 2, "future": False,
        "what_ta": "Phone apps — APK/IPA, local storage, API calls, permissions.",
        "attack_ta": "Hardcoded secrets in app, insecure storage, weak API auth, no cert-pinning → traffic "
                     "intercept. Lab-la *un sontha test app* decompile panni epdi data store aagudhu nu paapom.",
        "defend_ta": "No secrets in app code, encrypted storage, certificate pinning, proper API auth + "
                     "server-side checks, obfuscation, MASVS standard follow pannu. Client-ah nambhadhe — "
                     "ella check-um server-la vai.",
        "tools": ["apktool/jadx", "mitmproxy", "frida"],
        "practice": "DIVA, InsecureBankv2, your own test APK",
    },
    {
        "id": "iot", "icon": "🔌", "name": "IoT & Hardware", "level": 2, "future": False,
        "what_ta": "Smart devices — cameras, sensors, routers, embedded firmware.",
        "attack_ta": "Default passwords, old firmware, open telnet/UART, firmware-la hardcoded keys — "
                     "IoT-la romba common. Lab-la firmware image binwalk vechi extract panni paapom.",
        "defend_ta": "Default creds maathu, firmware update, unused services off, network-la IoT-ah "
                     "separate VLAN-la pottu isolate pannu, encrypted comms, secure boot. "
                     "IoT device-ah romba trust pannadhe — isolate pannu.",
        "tools": ["binwalk", "nmap", "tshark"],
        "practice": "Your own old router firmware, IoTGoat",
    },
    {
        "id": "ai", "icon": "🤖", "name": "AI / LLM Security", "level": 3, "future": True,
        "what_ta": "AI models + LLM apps (Nanban maari!) — puthusa varradhu, future-oda biggest surface.",
        "attack_ta": "Prompt injection (AI-ah unexpected-ah nadakka vaikkradhu), jailbreaks, data/model "
                     "poisoning, sensitive data leak, insecure plugins. OWASP LLM Top 10 padichu purinjiko.",
        "defend_ta": "Input/output filtering, system-prompt isolation, least-privilege tool access, "
                     "output validation, rate-limit, PII redaction, guardrails, human-in-loop for risky "
                     "actions. Nanban-oda design-la idhellam already consider panniruken.",
        "tools": ["OWASP LLM guide", "garak (LLM scanner)"],
        "practice": "Gandalf (Lakera), your own local LLM setup",
    },
    {
        "id": "web3", "icon": "⛓️", "name": "Blockchain & Web3", "level": 3, "future": True,
        "what_ta": "Smart contracts, DeFi, crypto wallets — decentralised apps.",
        "attack_ta": "Smart-contract bugs (reentrancy, overflow, logic flaw) = direct money loss. "
                     "Phishing + wallet drain common. Lab-la testnet mela sample contract audit panni kathuko.",
        "defend_ta": "Contract audits, known-safe libraries (OpenZeppelin), testing + formal verification, "
                     "least-privilege keys, hardware wallet, user phishing awareness. Code = money, so "
                     "audit mukkiyam.",
        "tools": ["slither", "mythril", "foundry"],
        "practice": "Ethernaut, Damn Vulnerable DeFi (testnet)",
    },
    {
        "id": "ot", "icon": "🏭", "name": "OT / ICS / SCADA", "level": 3, "future": True,
        "what_ta": "Industrial systems — factories, power grid, water, manufacturing control.",
        "attack_ta": "Old protocols (no auth), legacy systems, IT-OT bridge weak → critical infra risk. "
                     "Idhu national-security level domain. Concept + defense level-la mattum kathuko, simulators-la.",
        "defend_ta": "IT-OT segmentation (air-gap / strict firewall), protocol monitoring, no internet on "
                     "OT, patch carefully, physical security, anomaly detection. India-oda critical infra-ku "
                     "idhu romba important.",
        "tools": ["simulators only", "tshark"],
        "practice": "Conpot honeypot, ICS simulators — never real plants",
    },
    {
        "id": "identity", "icon": "🪪", "name": "Identity & Zero-Trust", "level": 2, "future": True,
        "what_ta": "Future auth — passwordless, passkeys, SSO, zero-trust architecture.",
        "attack_ta": "Token theft, session hijack, SSO misconfig, phishing-based MFA bypass. "
                     "Identity-dhan puthu perimeter, so attack focus inga move aagudhu.",
        "defend_ta": "Passkeys/WebAuthn, phishing-resistant MFA, short-lived tokens, continuous "
                     "verification, device trust, 'never trust always verify' principle. "
                     "Password-ah fully ozhichu passkey-ku po.",
        "tools": ["concept + config review"],
        "practice": "Your own SSO/passkey test setup",
    },
    {
        "id": "quantum", "icon": "🔮", "name": "Post-Quantum Crypto", "level": 3, "future": True,
        "what_ta": "Future threat: quantum computers ippo irukkura encryption-ah break pannalaam.",
        "attack_ta": "'Harvest now, decrypt later' — ippo encrypted data store panni, future quantum-la "
                     "decrypt pannradhu. Direct attack illa, aana future-ku prepare aaganum.",
        "defend_ta": "Post-quantum algorithms (Kyber, Dilithium — NIST standards) ku migrate aaga start pannu, "
                     "crypto-agility (algorithm easy-ah maathakoodiya design), inventory your crypto. "
                     "Early-ah plan pannina future-la tension illa.",
        "tools": ["liboqs", "concept"],
        "practice": "Open Quantum Safe project demos",
    },
    {
        "id": "macos", "icon": "🍎", "name": "macOS Security (Mac)", "level": 2, "future": False,
        "what_ta": "Apple Mac laptop/desktop — macOS protection: SIP, Gatekeeper, XProtect, TCC, FileVault. "
                   "Default-ah strong, aana config + user habits mukkiyam.",
        "attack_ta": "Fake/unsigned apps via malware, phishing, TCC (privacy) bypass concepts, persistence "
                     "via LaunchAgents/LaunchDaemons. Idha *un sontha Mac* mela mattum audit panni kathuko.",
        "defend_ta": "macOS update pannu, Gatekeeper + SIP ON vai, App Store / signed apps mattum, FileVault "
                     "(disk encryption) ON, firewall ON, LaunchAgents review, least-privilege (admin illa daily). "
                     "Objective-See free tools (KnockKnock/BlockBlock) use pannu.",
        "tools": ["spctl", "csrutil", "Objective-See tools"],
        "practice": "Your own Mac + Objective-See tools",
    },
    {
        "id": "ios", "icon": "📱", "name": "iOS / iPadOS Security", "level": 3, "future": False,
        "what_ta": "iPhone/iPad — sandboxing, code signing, Secure Enclave, strong default security. "
                   "Attack panna romba kashtam (by design) — adhanaala defense + detection focus.",
        "attack_ta": "Phishing, malicious configuration profiles, mercenary spyware (high-value targets), "
                     "jailbreak concepts. Ordinary user-ku biggest risk = phishing + fake profiles, malware illa.",
        "defend_ta": "iOS update udane, high-risk-na Lockdown Mode ON, sketchy profiles/apps install pannadhe, "
                     "strong passcode + Face ID, app permissions review, un sontha device-ah MVT vechi compromise "
                     "check pannu. Apple-oda default security-ah break pannadhe.",
        "tools": ["MVT (own-device)", "Lockdown Mode", "iMazing"],
        "practice": "Your own iPhone/iPad backup, Lockdown Mode",
    },
    {
        "id": "legacy", "icon": "🕰️", "name": "Legacy Protocols & Classic Attacks", "level": 1,
        "future": False, "past": True,
        "what_ta": "Palaya tech innum pala idathula irukku — telnet, FTP, SMBv1, old Windows (XP/7), WEP, "
                   "default passwords. Hacking history-oda foundation — idha purinjaa modern-um clear aagum.",
        "attack_ta": "Encryption illadha protocols sniff pannalaam, SMBv1 (EternalBlue era) exploits, default "
                     "creds. Lab-la old Metasploitable mela classic attacks epdi work aagudhu nu paapom.",
        "defend_ta": "Legacy protocols disable pannu, old systems retire/upgrade, thavikka mudiyadhaadha legacy-ah "
                     "network-la isolate pannu, patch, default creds maathu. Old = risk; isolate illa kill.",
        "tools": ["nmap", "tshark", "metasploit (lab)"],
        "practice": "Metasploitable 2 in your VirtualBox lab",
    },
    {
        "id": "auto", "icon": "🚗", "name": "Automotive, Drones & Robotics", "level": 3, "future": True,
        "what_ta": "Cars, drones, robots — CAN bus, telematics, firmware. Future-oda emerging attack surface "
                   "(rolling computers).",
        "attack_ta": "CAN bus injection, key-fob relay, firmware tamper, GPS spoofing — concept level. Idhu "
                     "specialised + regulated field. Virtual simulators (ICSim) vechi safe-ah learn pannu.",
        "defend_ta": "Signed + secure firmware, CAN segmentation, encrypted telematics, secure OTA updates, "
                     "physical security, intrusion detection. Future vehicles = computers on wheels, so security "
                     "design-la irundhe venum.",
        "tools": ["ICSim simulator", "can-utils (vcan)"],
        "practice": "ICSim car-hacking simulator, virtual CAN",
    },
]

# Single-run lab commands — copy-paste, runs on YOUR OWN lab target only.
# First line of each is a safety note. These are recon/audit/defense oriented, lab-scoped.
LAB_CMD = {
    "web": '# YOUR local DVWA only (set up in your lab)\nsqlmap -u "http://localhost/dvwa/vulnerabilities/sqli/?id=1&Submit=Submit" \\\n  --cookie="PHPSESSID=xxx; security=low" --batch --dbs',
    "network": 'TARGET=192.168.56.101   # your lab VM IP ONLY\nnmap -sV -sC -O $TARGET',
    "passwords": '# Crack YOUR OWN test hash — no real accounts\necho -n "password123" | md5sum | cut -d" " -f1 > myhash.txt\njohn --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt myhash.txt',
    "wireless": '# YOUR OWN router / test AP only\nsudo airmon-ng start wlan0\nsudo airodump-ng wlan0mon',
    "osint": '# YOUR OWN domain only\ntheHarvester -d yourdomain.com -b bing,duckduckgo',
    "exploit": '# Metasploitable lab target only\nmsfconsole -q -x "use auxiliary/scanner/portscan/tcp; set RHOSTS 192.168.56.101; run; exit"',
    "forensics": '# Analyse a file in an ISOLATED lab VM\nbinwalk suspicious.bin\nyara -r my_rules.yar ./sample_folder',
    "cloud": '# YOUR OWN cloud account only (read-only audit)\npip install scoutsuite\nscout aws   # or: prowler aws',
    "containers": '# Scan YOUR OWN image for known vulns\ntrivy image your-app:latest',
    "mobile": '# Decompile YOUR OWN test APK\napktool d your-test-app.apk -o out/\njadx-gui your-test-app.apk',
    "iot": '# Extract YOUR OWN device firmware (that you downloaded legally)\nbinwalk -e firmware.bin',
    "ai": '# Test YOUR OWN LLM app for prompt-injection / weaknesses\npip install garak\npython -m garak --model_type rest --generator_option_file your_llm.json',
    "web3": '# Audit YOUR OWN smart contract\npip install slither-analyzer\nslither YourContract.sol',
    "ot": '# Honeypot/simulator — never a real plant\nsudo conpot --template default',
    "identity": '# Review YOUR OWN auth config (example: check token expiry / MFA)\n# No attack tool — inspect your IdP settings + logs for weak policies.',
    "quantum": '# See which post-quantum algorithms your OpenSSL supports\nopenssl list -signature-algorithms | grep -i -E "dilithium|kyber|mldsa|mlkem"',
    "macos": '# Run on YOUR OWN Mac — defensive audit\ncsrutil status      # SIP on?\nspctl --status      # Gatekeeper on?\nfdesetup status     # FileVault (disk encryption) on?\n/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate',
    "ios": '# Check YOUR OWN iPhone encrypted backup for compromise (defensive)\npip install mvt\nmvt-ios check-backup --output ./results ./my_encrypted_backup',
    "legacy": 'TARGET=192.168.56.101   # your Metasploitable lab VM ONLY\nnmap -sV --script smb-protocols,ftp-anon,telnet-encryption,ssl-enum-ciphers $TARGET',
    "auto": '# Virtual CAN bus — no real car, 100% safe lab\nsudo modprobe vcan\nsudo ip link add dev vcan0 type vcan && sudo ip link set up vcan0\ncandump vcan0   # watch virtual CAN traffic (pair with ICSim)',
}


# ---------------------------------------------------------------- attack lifecycle
# The black-hat attack lifecycle (Cyber Kill Chain + MITRE ATT&CK, defensive education).
# For each stage: what the attacker is TRYING to do (concept), the warning signs a
# defender watches for, and how to DEFEND/DETECT. Lab tools are for learning on your
# OWN targets. No weaponised recipes — this is "know the enemy to defend".
KILL_CHAIN = [
    {
        "n": 1, "icon": "🔭", "stage": "Reconnaissance",
        "attacker_ta": "Target-ah pathi info sekarippanga — employees, emails, domains, open ports, "
                       "tech stack, leaked passwords. Attack planning-oda first step. Passive (public data) "
                       "+ active (scanning) nu rendu vidham.",
        "signs_ta": "Unexpected port scans, odd traffic from unknown IPs, repeated failed lookups, "
                    "un company info public-ah thedardhu.",
        "defend_ta": "Public footprint kammi pannu, unwanted services off, metadata strip, "
                     "scanning-ah IDS/firewall la detect+block, employees-ku OSINT awareness, "
                     "rate-limit. Attacker-ku kammi info kidaichaa, attack kashtam.",
        "tools": ["nmap", "theharvester", "whatweb", "exiftool"],
    },
    {
        "n": 2, "icon": "🧪", "stage": "Weaponization",
        "attacker_ta": "Recon la kandupidichadha vechi attack prepare pannuvanga — entha vulnerability, "
                       "entha payload, entha delivery method nu decide pannuvanga. Idhu attacker side-la "
                       "nadakudhu, so neenga direct-ah paakka mudiyadhu.",
        "signs_ta": "Direct sign illa (offline stage). Aana threat intel feeds-la new exploit/campaign "
                    "news varum — adha follow pannanum.",
        "defend_ta": "Patch fast (known CVE close pannu), threat intelligence follow, attack surface "
                     "chinnadhaka vai, email/web filtering ready vai. Vulnerability illaina weapon velai "
                     "pannadhu.",
        "tools": ["CVE/threat-intel feeds", "vuln scanners"],
    },
    {
        "n": 3, "icon": "📨", "stage": "Delivery",
        "attacker_ta": "Weapon-ah target-ku anuppuvanga — phishing email, malicious link/attachment, "
                       "fake website, USB drop, compromised software. #1 entry = phishing (human-ah emathuradhu).",
        "signs_ta": "Suspicious emails (urgency, wrong sender, odd links), unexpected attachments, "
                    "lookalike domains, employees reporting weird messages.",
        "defend_ta": "Email security (SPF/DKIM/DMARC, spam filter), link/attachment sandboxing, "
                     "security awareness training (phishing simulations), block macros, web filtering. "
                     "Human-ah train pannradhu than strongest defense inga.",
        "tools": ["email gateway", "awareness training", "DMARC"],
    },
    {
        "n": 4, "icon": "💥", "stage": "Exploitation",
        "attacker_ta": "Delivery success aana, vulnerability-ah trigger panni **initial access** vaanguvanga "
                       "— software bug, weak password, misconfig, illa user click. Inga than 'break-in' nadakudhu.",
        "signs_ta": "Crash logs, unexpected process start, new/unknown processes, exploit signatures, "
                    "abnormal app behaviour.",
        "defend_ta": "Patch management, EDR/antivirus, least privilege (user admin illa), application "
                     "allow-listing, MFA (stolen password-um pothadhu), input validation. Exploit aanaalum "
                     "privilege kammi-na damage kammi.",
        "tools": ["metasploit (lab)", "EDR", "patching"],
    },
    {
        "n": 5, "icon": "🪤", "stage": "Installation / Persistence",
        "attacker_ta": "Access-ah permanent-ah vechikka backdoor install pannuvanga — reboot aanaalum, "
                       "password maathinaalum access irukkanum. Scheduled tasks, services, registry, "
                       "hidden accounts use pannuvanga.",
        "signs_ta": "New unknown services/scheduled tasks, new admin accounts, odd autostart entries, "
                    "unexpected files in system folders, integrity changes.",
        "defend_ta": "File integrity monitoring, EDR behaviour detection, audit new accounts/services, "
                     "least privilege, application allow-listing, regular config review. Persistence-ah "
                     "early kandupidichaa attacker veliye.",
        "tools": ["EDR", "file integrity monitor", "yara"],
    },
    {
        "n": 6, "icon": "📡", "stage": "Command & Control (C2)",
        "attacker_ta": "Compromised machine-ah remote-ah control panna oru secret channel setup pannuvanga "
                       "(C2 server). Commands anuppa, data eduka idhu vazhi. Normal traffic-la hide panna "
                       "try pannuvanga (DNS, HTTPS).",
        "signs_ta": "Beaconing (regular small outbound calls), traffic to new/rare domains, odd DNS, "
                    "data to unknown IPs, connections at weird hours.",
        "defend_ta": "Network monitoring (NDR), DNS filtering, egress filtering (unwanted outbound block), "
                     "proxy inspection, threat-intel domain blocking, anomaly detection. C2 cut panna "
                     "attacker kai kattappadum.",
        "tools": ["tshark", "NDR/IDS", "DNS filtering"],
    },
    {
        "n": 7, "icon": "🎯", "stage": "Actions on Objectives",
        "attacker_ta": "Ippo goal reach pannuvanga — privilege escalation (admin aaganum), lateral movement "
                       "(vera machines-ku parava), data exfiltration (steal), illa ransomware/destruction. "
                       "Ithaan final 'impact' stage.",
        "signs_ta": "Large data transfers out, mass file encryption, new admin privilege, unusual access "
                    "to sensitive data, many internal logins (lateral movement).",
        "defend_ta": "Network segmentation (lateral movement thadu), least privilege + Zero Trust, DLP "
                     "(data loss prevention), encrypted + offline backups (ransomware recovery), monitoring, "
                     "incident response plan ready. Segment + backup = ransomware-ku best defense.",
        "tools": ["segmentation", "DLP", "backups", "SIEM"],
    },
]

# Overall defensive posture (blue team)
DEFENSE_STACK = [
    ("🧅 Defense-in-Depth", "Oru layer illa — pala layers. Perimeter, network, host, app, data, "
     "human — ovvonnilum protection. Oru layer fail aanaalum adutha layer thaduthu nikkum."),
    ("🚫 Zero Trust", "'Never trust, always verify.' Ulla irundhaalum verify pannu. Least privilege, "
     "MFA, device trust, micro-segmentation. Modern network-oda base idhu."),
    ("👁️ Detect & Respond (SOC/SIEM)", "Logs ellam oru idathula sekari (SIEM), anomaly-ah alert pannu, "
     "24/7 monitor. Attack-ah live-ah kandupidichu stop pannradhu."),
    ("🚑 Incident Response (IR)", "Attack nadandha: Prepare → Identify → Contain → Eradicate → Recover → "
     "Lessons. Plan munnadiye ready vai — panic illa, process."),
    ("💾 Backup & Recovery", "Encrypted, offline, tested backups. Ransomware/disaster aanaalum "
     "recover panna mudiyum. '3-2-1 rule': 3 copies, 2 media, 1 offsite."),
    ("🧑‍🏫 Human Layer", "Phishing simulation, awareness training, strong passwords + password manager, "
     "MFA everywhere. Weakest link = human, so strongest training inge."),
]


def levels_available() -> list[str]:
    return LEVELS


def kill_chain_markdown() -> str:
    out = ["## 🎯 Black-hat Attack Lifecycle — stage by stage",
           "_Real attackers (black hats) epdi end-to-end velai pannuranga nu purinjikaradhu — "
           "appo than ovvoru stage-ayum **detect + defend** panna mudiyum. Idhu 'know your enemy' "
           "defensive framework (Cyber Kill Chain + MITRE ATT&CK)._", ""]
    for s in KILL_CHAIN:
        out.append(f"### {s['icon']} Stage {s['n']} — {s['stage']}")
        out.append(f"**🎭 Attacker enna pannuvanga:** {s['attacker_ta']}")
        out.append(f"**🚩 Warning signs (detect):** {s['signs_ta']}")
        out.append(f"**🛡️ Defend epdi:** {s['defend_ta']}")
        out.append(f"**🧰 Related tools:** {' · '.join('`'+t+'`' for t in s['tools'])}")
        out.append("")
    out.append("> ⚖️ **Boundary:** idhu defense-ku. Ovvoru technique-ayum un sontha lab / authorised "
               "target / legal platform-la mattum practice pannu. Veliya real system mel = crime.")
    return "\n".join(out)


def defense_stack_markdown() -> str:
    out = ["## 🛡️ Defense playbook — epdi idha ellame thaduppadhu", ""]
    for title, desc in DEFENSE_STACK:
        out.append(f"**{title}** — {desc}\n")
    return "\n".join(out)


ERA_PAST = "⏳ Classic (past)"


def domains_for(level_label: str = "All", query: str = "") -> list[dict]:
    q = (query or "").strip().lower()
    out = []
    for d in DOMAINS:
        if level_label != "All":
            if level_label == "🔮 Future-tech":
                if not d.get("future"):
                    continue
            elif level_label == ERA_PAST:
                if not d.get("past"):
                    continue
            elif LEVELS[d["level"]] != level_label:
                continue
        if q and q not in (d["name"] + d["what_ta"] + d["attack_ta"] + d["defend_ta"]).lower():
            continue
        out.append(d)
    return out


def domain_by_id(did: str) -> dict | None:
    return next((d for d in DOMAINS if d["id"] == did), None)


# ---------------------------------------------------------------- rendering

def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cards_html(level_label: str = "All", query: str = "") -> str:
    ds = domains_for(level_label, query)
    if not ds:
        return '<div class="il-empty">Edhuvum match aagala. Vera word try pannu.</div>'
    cells = []
    for d in ds:
        badge = LEVELS[d["level"]]
        if d.get("future"):
            era = '<span class="il-fut">🔮 Future</span>'
        elif d.get("past"):
            era = '<span class="il-past">⏳ Classic</span>'
        else:
            era = ''
        run = '<span class="il-run">⚡ 1-run</span>' if LAB_CMD.get(d["id"]) else ''
        tools = " · ".join(_esc(t) for t in d["tools"][:4])
        cells.append(
            f'<div class="il-card" data-id="{d["id"]}">'
            f'<div class="il-card-top"><span class="il-ico">{d["icon"]}</span><span>{era}{run}</span></div>'
            f'<div class="il-name">{_esc(d["name"])}</div>'
            f'<div class="il-lvl">{badge}</div>'
            f'<div class="il-what">{_esc(d["what_ta"])}</div>'
            f'<div class="il-tools">🧰 {tools}</div>'
            f'<div class="il-row2"><span class="il-tag il-atk">⚔️ Attack</span>'
            f'<span class="il-tag il-def">🛡️ Defend</span></div>'
            '</div>')
    return f'<div class="il-grid">{"".join(cells)}</div>'


def detail_markdown(did: str) -> str:
    d = domain_by_id(did)
    if not d:
        return "Oru domain select pannu (card click pannu, illa dropdown-la thernedu)."
    fut = "  ·  🔮 Future-tech" if d.get("future") else ""
    return (
        f"## {d['icon']} {d['name']}\n"
        f"**Level:** {LEVELS[d['level']]}{fut}\n\n"
        f"### 🎯 Enna idhu\n{d['what_ta']}\n\n"
        f"### ⚔️ Attack epdi nadakudhu (concept — lab target mela mattum)\n{d['attack_ta']}\n\n"
        f"### 🛡️ Defend epdi pandradhu (idhu than mukkiyam)\n{d['defend_ta']}\n\n"
        f"### 🧰 Lab tools\n{' · '.join('`'+t+'`' for t in d['tools'])}\n\n"
        + (f"### ⚡ Single-run lab command (un lab target mattum)\n```bash\n{LAB_CMD[did]}\n```\n\n"
           if LAB_CMD.get(did) else "")
        + f"### 🧪 Enga practice pannu (legal)\n{d['practice']}\n\n"
        "> ⚖️ **Reminder:** un sontha lab / permission irukkura / practice-ku-made target mattum. "
        "Veliya real system = illegal."
    )


def platforms_markdown() -> str:
    rows = "\n".join(f"- **{n}** ({u}) — {desc}" for n, u, desc in PLATFORMS)
    return "### 🌍 Free + legal practice platforms\n" + rows


def tutor_prompt(question: str, did: str = "") -> list[dict]:
    """Build a Tanglish, defense-first lab-tutor prompt for the AI."""
    ctx = ""
    d = domain_by_id(did) if did else None
    if d:
        ctx = (f"\nCurrent topic: {d['name']} — {d['what_ta']} "
               f"Attack idea: {d['attack_ta']} Defense: {d['defend_ta']}")
    sys = (
        "You are Nanban India Lab — a friendly cybersecurity tutor for a learner practising in their "
        "OWN isolated lab and on legal platforms (TryHackMe, HTB, OWASP, PortSwigger). "
        "Reply in Tanglish (Tamil in English letters) + English, NEVER Tamil script. "
        "Teach both sides: how an attack works (concept + which lab tool, at a learning level) AND "
        "how to defend/detect it — always lead with understanding and defense. "
        "Scope everything to practice targets the learner owns or is authorised for; if asked to attack "
        "a real third-party system without permission, refuse warmly and explain it's illegal, then "
        "redirect to a lab target. Be clear, encouraging, and practical." + ctx)
    return [{"role": "system", "content": sys},
            {"role": "user", "content": question}]
