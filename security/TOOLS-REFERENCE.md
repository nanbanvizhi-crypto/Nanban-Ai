# 🧰 Kali Tools Reference — what's installed and how to use it

A categorized catalog of the main security tools that ship with Kali Linux: what each does, and a usage example. **Every example targets your own lab** (`127.0.0.1` / your VMs) or authorised platforms — that boundary is what keeps this legal (see `curriculum/00-ethics-and-the-law.md`).

Most of these come preinstalled with `kali-linux-headless` / `kali-linux-default`. If one is missing: `sudo apt install <name>`. You can also add anything else (`git clone`, `pip install`, build from source) — nothing stops you.

> Format: **tool** — what it does. `example against your own lab`

---

## 1. Reconnaissance & scanning

- **nmap** — the port/service scanner. `nmap -sC -sV -p- 127.0.0.1`
- **masscan** — very fast port scanner for large ranges. `masscan 127.0.0.1 -p1-65535 --rate 1000`
- **rustscan** — fast port discovery that pipes into nmap. `rustscan -a 127.0.0.1 -- -sV`
- **netdiscover / arp-scan** — find live hosts on your local network. `sudo arp-scan --localnet`
- **dnsenum / dnsrecon / fierce** — DNS enumeration for a domain you own.
- **theHarvester** — gather emails/subdomains from public sources (recon).
- **whatweb / wafw00f** — fingerprint web tech and detect WAFs. `whatweb http://127.0.0.1:8080`
- **enum4linux-ng** — enumerate SMB/Windows shares and users. `enum4linux-ng <your-vm-ip>`

## 2. Web application testing

- **Burp Suite** — the intercepting proxy; see/modify/replay every request. The core web tool. `burpsuite &`
- **OWASP ZAP** — free full web scanner + proxy. `zaproxy &`
- **sqlmap** — automated SQL injection detection/exploitation. `sqlmap -u "http://127.0.0.1:8080/vulnerabilities/sqli/?id=1&Submit=Submit" --cookie="PHPSESSID=..;security=low" --batch`
- **gobuster / ffuf / feroxbuster** — directory & file brute-forcing. `ffuf -u http://127.0.0.1:8080/FUZZ -w /usr/share/wordlists/dirb/common.txt`
- **nikto** — quick web-server misconfig scanner. `nikto -h http://127.0.0.1:8080`
- **wpscan** — WordPress vulnerability scanner (for your own WP install). `wpscan --url http://127.0.0.1:8080`
- **commix** — automated command-injection testing. (on your own lab)
- **wfuzz** — flexible web fuzzer for parameters/headers.

## 3. Password attacks

- **hydra** — online brute force against login services (SSH, HTTP, RDP…). `hydra -l admin -P rockyou.txt 127.0.0.1 http-post-form "/login.php:user=^USER^&pass=^PASS^:Failed"`
- **john (John the Ripper)** — offline hash cracking, auto-detects formats. `john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt`
- **hashcat** — GPU-accelerated hash cracking. `hashcat -m 0 -a 0 hashes.txt rockyou.txt`
- **medusa / ncrack** — alternative online brute-forcers.
- **crunch / cewl** — wordlist generators (cewl scrapes a site to build a custom list).
- **hash-identifier / hashid** — identify what type a hash is. `hashid <hash>`

## 4. Exploitation frameworks

- **Metasploit** (`msfconsole`) — the big exploitation framework: exploits, payloads, post-modules. Use against Metasploitable/your own VMs. `msfconsole`
- **searchsploit** — offline copy of Exploit-DB; find public exploits by software/version. `searchsploit apache 2.4`
- **msfvenom** — generate payloads (for your own lab targets). `msfvenom -p linux/x64/shell_reverse_tcp LHOST=.. LPORT=.. -f elf`
- **beef-xss** — browser exploitation framework (hook a browser in your lab).

## 5. Network attacks & sniffing

- **Wireshark** — capture and analyze packets (read your own traffic to see why HTTP is unsafe). `wireshark &`
- **tcpdump** — command-line packet capture. `sudo tcpdump -i eth0 -w cap.pcap`
- **bettercap** — all-in-one network attack framework (MITM, sniffing) — your own network only. `sudo bettercap -iface eth0`
- **ettercap / arpspoof** — ARP spoofing / MITM on a network you own.
- **responder** — LLMNR/NBT-NS poisoning to capture hashes (AD lab). `sudo responder -I eth0`
- **mitmproxy** — interactive HTTPS proxy for inspecting traffic you control.

## 6. Active Directory

- **BloodHound** + **SharpHound/bloodhound-python** — graph AD attack paths. `bloodhound-python -u u -p p -d dom.local -ns <dc> -c All`
- **impacket** (GetUserSPNs, secretsdump, psexec, wmiexec…) — the AD/Windows protocol swiss-army knife. `GetUserSPNs.py dom.local/user:pass -dc-ip <dc> -request`
- **crackmapexec / netexec** — spray creds & check access across a domain. `crackmapexec smb <subnet>/24 -u user -p pass`
- **evil-winrm** — WinRM shell to a Windows host you have creds for. `evil-winrm -i <ip> -u user -p pass`
- **certipy / Rubeus** — AD Certificate Services and Kerberos attacks (on your GOAD lab).
- **ldapsearch / windapsearch** — query LDAP/AD directory.

## 7. Wireless (your own network only)

- **aircrack-ng suite** — capture WPA handshakes and crack them offline — only your own router. `aircrack-ng -w rockyou.txt capture.cap`
- **wifite** — automates the aircrack workflow.
- **kismet** — wireless network detector/sniffer.
- **hcxdumptool / hcxtools** — modern handshake capture for hashcat.

## 8. Reverse engineering & binary exploitation

- **Ghidra** — NSA's free reverse-engineering suite (decompiler). `ghidra`
- **radare2 / rizin** — command-line RE framework.
- **gdb** (+ **gef**/**pwndbg**) — debugger for binary exploitation. `gdb ./vuln`
- **pwntools** — Python library for writing exploits (practice binaries). `pip install pwntools`
- **checksec** — show a binary's mitigations (ASLR/NX/canary/PIE). `checksec --file=./vuln`
- **binwalk** — analyze/extract firmware and embedded files.

## 9. Post-exploitation & privesc

- **LinPEAS / WinPEAS** — enumerate a host for privesc paths (from the PEASS-ng project). `./linpeas.sh`
- **linux-exploit-suggester / windows-exploit-suggester** — match OS/kernel to known local exploits.
- **pspy** — watch processes/cron as an unprivileged user (Linux).
- **chisel / ligolo-ng** — tunneling/pivoting through a compromised host (your lab network).
- **socat / nc (netcat)** — the networking swiss-army knife: shells, transfers, port relays.

## 10. OSINT & misc

- **recon-ng** — modular OSINT framework.
- **spiderfoot** — automated OSINT collection.
- **exiftool** — read metadata from files/images.
- **cyberchef** (web) — the "cyber swiss-army knife" for encoding/decoding/crypto.
- **seclists** — the essential collection of wordlists (`/usr/share/seclists`). `sudo apt install seclists`

---

## How to use this reference

1. Figure out **what phase you're in** (recon → web/network → exploit → post-exploit) and pick the matching category.
2. Read the tool's own help: `<tool> -h` or `man <tool>`.
3. Run it **against your lab** (`127.0.0.1`, your VMs) and compare the output to the relevant curriculum module.
4. Ask Nanban in Chat: *"explain this nmap output"* or *"what does this sqlmap flag do?"* — paste the output and learn as you go.

## Installing more

Kali is a normal Linux — add anything:
```bash
sudo apt update && sudo apt install <tool>        # from Kali's repos
pipx install <python-tool>                         # python CLI tools
git clone https://github.com/<author>/<tool>       # from source
sudo apt install kali-linux-large                  # a much bigger default toolset
```

## The one rule (again, because it's the whole game)

Every tool here is neutral — a professional's instrument. What makes using it legal is **permission**: your own lab, your own VMs, or a target you're explicitly authorised to test. Point any of these at something you don't own and it's the crime from Module 0, no matter the tool. Keep it on your lab and legal platforms, and you're training exactly like the pros.
