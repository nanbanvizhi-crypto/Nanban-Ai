# 🐉 Kali Linux Setup — the most powerful security Linux, done simply

Kali is the industry-standard security distribution. Everything serious is already in it: **Burp Suite, Metasploit, sqlmap, nmap, Wireshark, Hydra, John, Nikto, gobuster, aircrack-ng**, and hundreds more. There is nothing "more powerful" to add — this *is* the powerful setup professionals use. You just point it at your own lab and legal targets (see `curriculum/00-ethics-and-the-law.md`).

Two ways to install. **WSL2 is easiest on Windows** (no VM, fast, shares your files). A **VM** gives you the full Kali desktop. Pick one; you can do both later.

---

## Option A — WSL2 (recommended, fastest)

Runs Kali *inside* Windows 10/11. No separate virtual machine.

### 1. Enable WSL2 (one time)
Open **PowerShell as Administrator** (Start → type "PowerShell" → right-click → Run as administrator) and run:
```powershell
wsl --install
```
Restart the laptop when it asks. This installs WSL2 itself.

### 2. Install Kali
In a normal PowerShell or Command Prompt:
```powershell
wsl --install -d kali-linux
```
It downloads Kali and opens it. Create a **username** and **password** when prompted (remember these — that password is your `sudo` password).

### 3. Update + install the full toolset
Inside the Kali window:
```bash
sudo apt update && sudo apt full-upgrade -y

# The big one: installs the standard pentesting tools (several GB, one time)
sudo apt install -y kali-linux-headless

# SSH server, so Nanban can connect to Kali
sudo apt install -y openssh-server
```
> `kali-linux-headless` = all the command-line tools without a desktop (perfect for WSL). Want the graphical tools too? use `kali-linux-default` instead.

### 4. Start SSH (so Nanban can drive it)
```bash
sudo service ssh start
# make it start automatically:
echo 'sudo service ssh start' >> ~/.bashrc
```
Find your Kali username and confirm SSH is up:
```bash
whoami
sudo service ssh status
```
WSL shares Windows' network, so from Nanban you connect to **`127.0.0.1`** (see "Connect to Nanban" below).

### 5. Verify the tools
```bash
nmap --version
sqlmap --version
msfconsole -v        # Metasploit (first run takes a minute)
which burpsuite gobuster hydra nikto wireshark
```

---

## Option B — Full Kali VM (full desktop)

Better if you want the graphical Kali experience or to keep it fully separate from Windows.

### 1. Install VirtualBox (free)
Download from virtualbox.org and install.

### 2. Download the Kali VM image
Go to **kali.org/get-kali/ → Virtual Machines → VirtualBox**. Download the pre-built image (it's large). This version already has tools installed.

### 3. Import and start
- In VirtualBox: **File → Import Appliance** → pick the downloaded file → Import.
- Give it at least **4 GB RAM** and 2 CPUs (Settings → System).
- Start the VM. Default login is usually `kali` / `kali` (change the password immediately: `passwd`).

### 4. Update + enable SSH
Inside the Kali desktop, open a terminal:
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
ip a                 # note the VM's IP address, e.g. 192.168.56.x
```

### 5. Networking so Nanban + lab are reachable
- In VirtualBox **Settings → Network**, use **Bridged Adapter** (VM gets its own IP on your network) or add a **Host-only Adapter**.
- From Nanban you'll connect to the VM's IP from step 4 (the `ip a` output).

---

## Connect Kali to Nanban

Once SSH is running in Kali:

```
# In the Nanban Terminal:
# WSL:  host is 127.0.0.1
/server add kali <your-kali-username>@127.0.0.1

# VM:   host is the VM's IP from `ip a`
/server add kali <your-kali-username>@192.168.56.101

/server test kali          # confirms it connects
/server use kali           # now the shell AND the AI work on Kali
```

Now you can run tools on Kali, driven from Nanban, against **your own lab**:
```bash
nmap -sV -p 3000,8080,8081 127.0.0.1          # scan your lab containers (WSL)
# or against the VM's view of the lab host
```
Or just ask Nanban in AI mode: *"kali-la en lab-oda DVWA-va nmap pannu, result-a explain pannu."*

---

## Connect Kali to your practice lab

Your lab (DVWA, Juice Shop, WebGoat) runs in Docker on Windows at `127.0.0.1`.

- **Kali in WSL2**: shares Windows networking → reach the lab at `127.0.0.1:8080`, `:3000`, `:8081` directly.
- **Kali VM**: `127.0.0.1` means the *VM itself*, not Windows. Reach the lab at your **Windows machine's LAN IP** (run `ipconfig` in Windows, use the IPv4 like `192.168.1.x:8080`). Or run the lab inside Kali itself (`docker compose up` from the `lab/` folder copied into Kali).

Quick check from Kali:
```bash
curl -I http://127.0.0.1:8080        # WSL
curl -I http://192.168.1.50:8080     # VM → Windows host IP
```

---

## First things to try (all on your own lab)

```bash
# 1. Recon your lab
nmap -sV -p 3000,8080,8081 127.0.0.1

# 2. Find paths on DVWA
gobuster dir -u http://127.0.0.1:8080 -w /usr/share/wordlists/dirb/common.txt

# 3. Launch Burp Suite (WSL with GUI, or in the VM desktop)
burpsuite &

# 4. See SQLi automation against your own lab (get the cookie from DevTools first)
sqlmap -u "http://127.0.0.1:8080/vulnerabilities/sqli/?id=1&Submit=Submit" \
       --cookie="PHPSESSID=XXXX; security=low" --batch
```

Pair each with the matching curriculum module and walkthrough so you understand *why*, not just *how*.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `wsl --install` not found | Update Windows; WSL needs Win10 2004+ or Win11 |
| Kali SSH refused from Nanban | In Kali: `sudo service ssh start` (WSL) / `sudo systemctl start ssh` (VM) |
| `/server test kali` times out (VM) | Use the VM's real IP from `ip a`, and set Bridged/Host-only networking |
| Can't reach lab from Kali VM | Use Windows' LAN IP (`ipconfig`), not `127.0.0.1` |
| Tools missing | `sudo apt install -y kali-linux-headless` (or `kali-linux-default` for GUI tools) |
| Burp won't open in WSL | Install a WSLg-capable Windows 11, or use the VM for GUI tools |

---

## The point, one more time

This **is** the powerful setup — the same one used by security professionals and in OSCP/pentest work. Power comes from *understanding* the tools and using them on systems you're allowed to touch, not from any "illegal" bundle (which would only be an attack box, and teaches you nothing extra). Keep Kali pointed at your lab and legal platforms (TryHackMe, HackTheBox, PortSwigger Academy, in-scope bug bounties), and you've got everything a serious learner needs.

Next: `ROADMAP.md` → Phase 1, and the walkthroughs in `walkthroughs/`.
