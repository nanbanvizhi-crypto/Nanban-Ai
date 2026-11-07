# Module 9 — Network Attacks & Binary Exploitation (intro)

Two advanced areas, introduced so you know the landscape and where to go deeper. Both are practiced only on **your own lab/VMs/traffic** (Module 0).

---

## Part A — Network Attacks

Attacks that target the network itself rather than one app.

### Man-in-the-Middle (MITM)
Positioning yourself between two parties to read/alter traffic.
- **ARP spoofing** — on a local network, trick machines into sending traffic through you. Tools: `arpspoof`, `bettercap`, `ettercap`.
- What it reveals: any **unencrypted** traffic (HTTP, old protocols) is readable. This is *the* reason HTTPS exists.
- **Defender:** encrypt everything (HTTPS/TLS), use static ARP or dynamic ARP inspection on switches, segment networks, VPNs on untrusted networks.

### Packet analysis (Wireshark)
Capture and read network traffic on your own machine/lab. The single best way to *see* why unencrypted protocols are dangerous — you literally read the passwords. Also essential for defenders (detecting attacks, debugging).

### Network service attacks
- Scan for services (nmap), identify versions, look up known CVEs.
- Attack weak/default credentials on SSH, RDP, databases, SNMP (online attacks, Module 6).
- **Defender:** minimize exposed services, strong creds + MFA, patch, firewall, monitor.

### Wireless (your own network only)
- **WPA2 handshake capture + offline crack** (aircrack-ng) — teaches why long Wi-Fi passphrases matter. Only on your *own* router.
- **Defender:** WPA3 or WPA2 with a long passphrase, no WPS, separate guest network.

---

## Part B — Binary Exploitation (intro)

Finding and exploiting bugs in compiled programs (C/C++) — memory-corruption bugs. This is deep, low-level, and the hardest area; this is an orientation, not a full course.

### The core idea
C/C++ don't automatically check memory boundaries. If a program copies input into a fixed buffer without checking the length (**buffer overflow**), extra input spills into adjacent memory — which can overwrite control data and redirect the program.

```c
// VULNERABLE — no bounds check
char buf[64];
strcpy(buf, user_input);   // if user_input > 64 bytes, it overflows
```

### Concepts you'll meet
- **Stack buffer overflow** — overflow a local buffer to overwrite the saved return address, redirecting execution.
- **Modern mitigations** (why it's hard now): **ASLR** (randomized memory layout), **DEP/NX** (non-executable stack), **stack canaries** (detect overflow), **PIE**. Exploitation today is about defeating these.
- **ROP (Return-Oriented Programming)** — chaining existing code snippets to bypass NX.
- **Format string bugs, heap exploitation, use-after-free** — other classes.

### Tools
- **GDB** (+ GEF/pwndbg plugins) — debug and inspect memory.
- **pwntools** — Python library for writing exploits (for your own practice binaries).
- **Ghidra / radare2** — reverse engineering (reading compiled code).
- **checksec** — shows which mitigations a binary has.

### Where to learn it properly (legal)
- **picoCTF** — beginner binary-exploitation and reversing challenges, free.
- **pwn.college** — free, structured, university-grade.
- **ROP Emporium** — focused ROP practice binaries.
- **HackTheBox / exploit.education** — practice VMs.

All of these give you **binaries made for practice** — you attack those, not real software.

### The defender's view
- Use **memory-safe languages** (Rust, Go) for new systems code where possible.
- In C/C++: bounds-checked functions (`strncpy`, `snprintf`), compiler flags (`-fstack-protector`, `-D_FORTIFY_SOURCE=2`, PIE/ASLR, NX), static/dynamic analysis (ASan, fuzzing).
- Keep dependencies patched (many CVEs are memory bugs in libraries).

---

## How this fits your path

Most people specialize: **web** (Modules 1–5), **network/infrastructure + AD** (6–8, 9A), or **binary/reversing** (9B). For a developer, web + network + privesc is the highest-value combo. Binary exploitation is fascinating but a longer road — tackle it via picoCTF/pwn.college when curious.

## Key terms

- **MITM / ARP spoofing**: intercepting local network traffic.
- **Buffer overflow**: input overflowing a fixed buffer, corrupting memory.
- **ASLR / NX / stack canary / PIE**: modern exploit mitigations.
- **ROP**: chaining existing code to bypass NX.
- **pwntools / GDB / Ghidra**: exploitation and reversing tools.

Next: the **OSCP/eJPT prep track** (`../OSCP-PREP.md`) and keep practicing on legal platforms.
