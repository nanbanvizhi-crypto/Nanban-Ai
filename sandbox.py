"""
🧪 Command Sandbox — practice security commands with SIMULATED output.

Nothing here runs for real. You type a command (nmap, sqlmap, whoami, ...) and Nanban
shows a realistic *fake* result against a built-in practice target (10.10.10.5 "metasploitable"),
plus a Tanglish explanation of what the command does and what the output means.

This lets you learn the tools with zero risk — no real target, no network, no danger. When you
move to a real lab (your own VirtualBox VM), the same commands work for real.
"""

TARGET = "10.10.10.5"
HOST = "metasploitable.lab"

# ---- canned realistic outputs (SIMULATED) -------------------------------

def _nmap(args: str) -> str:
    if "-p-" in args or "-sV" in args or "-sC" in args or not args.strip():
        return (f"Starting Nmap 7.94 ( https://nmap.org )\n"
                f"Nmap scan report for {HOST} ({TARGET})\n"
                f"Host is up (0.00042s latency).\n\n"
                "PORT     STATE SERVICE     VERSION\n"
                "21/tcp   open  ftp         vsftpd 2.3.4\n"
                "22/tcp   open  ssh         OpenSSH 4.7p1\n"
                "80/tcp   open  http        Apache httpd 2.2.8\n"
                "139/tcp  open  netbios-ssn Samba smbd 3.X\n"
                "445/tcp  open  microsoft-ds Samba smbd 3.X\n"
                "3306/tcp open  mysql       MySQL 5.0.51a\n"
                "Service detection performed. Nmap done: 1 IP address (1 host up) scanned in 6.21s")
    return (f"Nmap scan report for {HOST} ({TARGET})\nHost is up (0.00042s latency).\n"
            "PORT   STATE SERVICE\n22/tcp open  ssh\n80/tcp open  http\nNmap done: 1 host up.")


def _sqlmap(args: str) -> str:
    return ("        ___\n       __H__\n ___ ___[.]_____ ___ ___  {1.8}\n"
            "|_ -| . [']     | .'| . |\n|___|_  [']_|_|_|__,|  _|\n      |_|V...       |_|\n\n"
            "[*] starting @ 20:14:05\n[INFO] testing connection to the target URL\n"
            "[INFO] testing if the target URL content is stable\n"
            "[INFO] GET parameter 'id' appears to be injectable\n"
            "[INFO] the back-end DBMS is MySQL\n"
            "available databases [3]:\n[*] dvwa\n[*] information_schema\n[*] mysql\n"
            "[*] ending @ 20:14:11")


def _whoami(_): return "www-data"
def _id(_): return "uid=33(www-data) gid=33(www-data) groups=33(www-data)"
def _hostname(_): return HOST
def _ifconfig(_):
    return (f"eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n"
            f"        inet {TARGET}  netmask 255.255.255.0  broadcast 10.10.10.255\n"
            "        ether 08:00:27:a1:b2:c3  txqueuelen 1000  (Ethernet)")
def _ls(_): return "config.php  index.php  login.php  uploads  images  css  js"
def _ps(_):
    return ("  PID TTY          TIME CMD\n 1420 ?        00:00:01 apache2\n"
            " 1550 ?        00:00:00 mysqld\n 1888 pts/0    00:00:00 bash")
def _netstat(_):
    return ("Active connections\nProto Local Address      Foreign Address    State\n"
            f"tcp   {TARGET}:80        0.0.0.0:*          LISTEN\n"
            f"tcp   {TARGET}:3306      0.0.0.0:*          LISTEN\n"
            f"tcp   {TARGET}:22        0.0.0.0:*          LISTEN")


def _nikto(args):
    return (f"- Nikto v2.5.0\n+ Target IP:          {TARGET}\n+ Target Port:        80\n"
            "+ Server: Apache/2.2.8 (Ubuntu) PHP/5.2.4\n"
            "+ The anti-clickjacking X-Frame-Options header is not present.\n"
            "+ /config.php: PHP Config file may contain database IDs and passwords.\n"
            "+ /admin/: This might be interesting...\n+ 6 host(s) tested")


def _gobuster(args):
    return (f"===============================================================\n"
            f"Gobuster v3.6  Url: http://{TARGET}\n"
            "===============================================================\n"
            "/images               (Status: 301)\n/login.php            (Status: 200)\n"
            "/admin                (Status: 301)\n/uploads              (Status: 301)\n"
            "/config.php           (Status: 200)\nFinished")


def _hydra(args):
    return (f"Hydra v9.5 starting at 20:20:01\n[DATA] attacking ssh://{TARGET}:22\n"
            "[22][ssh] host: 10.10.10.5   login: msfadmin   password: msfadmin\n"
            "1 of 1 target successfully completed, 1 valid password found\n"
            "(practice box uses the well-known default msfadmin/msfadmin)")


def _msf(args):
    return ("       =[ metasploit v6.4.0                          ]\n"
            "+ -- --=[ 2400 exploits - 1200 auxiliary - 410 post  ]\n\n"
            "msf6 > (type 'use <module>' then 'set RHOSTS 10.10.10.5' then 'run')\n"
            "[*] This is a simulated console for learning the workflow.")


def _searchsploit(args):
    q = args.strip() or "vsftpd"
    return (f"------------------------------------- ---------------------------------\n"
            f" Exploit Title                       |  Path\n"
            "------------------------------------- ---------------------------------\n"
            f" {q} 2.3.4 - Backdoor Command Exec   | unix/remote/17491.rb\n"
            "------------------------------------- ---------------------------------")


def _ping(args):
    return (f"PING {TARGET} 56(84) bytes of data.\n"
            f"64 bytes from {TARGET}: icmp_seq=1 ttl=64 time=0.42 ms\n"
            f"64 bytes from {TARGET}: icmp_seq=2 ttl=64 time=0.38 ms\n"
            "--- ping statistics ---\n2 packets transmitted, 2 received, 0% packet loss")


# command prefix -> (handler, Tanglish explanation)
SIM = {
    "nmap": (_nmap, "nmap = port scanner. Open ports + services + versions kaattum. Recon-oda first step. "
                    "Old versions (vsftpd 2.3.4) theridhaa, adhu possible entry point."),
    "sqlmap": (_sqlmap, "sqlmap = SQL injection automate pannum. 'id' parameter injectable-nu kaattudhu, "
                        "appuram databases list panniduchu. Defense: parameterised queries."),
    "nikto": (_nikto, "nikto = web server vulnerability scanner. Missing headers, exposed config files, "
                      "interesting folders kaattum. Defense: headers + hide sensitive files."),
    "gobuster": (_gobuster, "gobuster = hidden directories/files brute-force (wordlist vechi). /admin, "
                            "/config.php maari hidden paths kandupidikkum."),
    "dirb": (_gobuster, "dirb = gobuster maari directory brute-force."),
    "hydra": (_hydra, "hydra = login brute-force (SIMULATED). Practice box default creds (msfadmin) kaattum. "
                      "Defense: strong password + MFA + account lockout. *Un lab mattum.*"),
    "msfconsole": (_msf, "Metasploit = exploit framework. Workflow: use module -> set RHOSTS -> run. "
                         "Idhu simulated console, workflow kathukradhukku."),
    "msf": (_msf, "Metasploit console (simulated)."),
    "searchsploit": (_searchsploit, "searchsploit = known exploits-ah offline-ah thedum (Exploit-DB). "
                                    "Oru service version-ku exploit irukkaanu check panna."),
    "whoami": (_whoami, "whoami = ippo entha user-ah irukkom nu kaattum. 'www-data' = web server user "
                        "(limited privilege). Next goal usually privilege escalation."),
    "id": (_id, "id = user-oda uid/gid/groups. Privilege level purinjikka."),
    "hostname": (_hostname, "hostname = machine peyar."),
    "ifconfig": (_ifconfig, "ifconfig/ip a = network interfaces + IP address kaattum."),
    "ip": (_ifconfig, "ip a = IP + interface details."),
    "ls": (_ls, "ls = folder-la files list. config.php maari files interesting."),
    "ps": (_ps, "ps = running processes. apache2, mysqld maari services theriyum."),
    "netstat": (_netstat, "netstat = open/listening ports + connections."),
    "ping": (_ping, "ping = host reachable-aanu check (ICMP)."),
    "cat": (lambda a: "<?php\n$db_user='root';\n$db_pass='';  // weak: empty DB password\n?>",
            "cat = file content padikka. config files-la creds leak aagalaam (idhu lab example)."),
}

HELP = sorted(set(SIM.keys()))


def run(command: str) -> tuple[str, str]:
    """Return (simulated_output, tanglish_explanation). Never executes anything."""
    command = (command or "").strip()
    if not command:
        return "", "Oru command type pannu — e.g. `nmap -sV 10.10.10.5`"
    tool = command.split()[0].lower().lstrip("./")
    args = command[len(command.split()[0]):]
    if tool in SIM:
        handler, expl = SIM[tool]
        try:
            out = handler(args)
        except Exception:
            out = "(simulated)"
        banner = f"$ {command}\n"
        return banner + out, expl
    return (f"$ {command}\n[sandbox] '{tool}' is not simulated yet.\n"
            f"Try one of: {', '.join(HELP)}",
            "Indha command sandbox-la illa. Mela list la irundhu try pannu. "
            "Ella output-um simulated — safe practice.")
