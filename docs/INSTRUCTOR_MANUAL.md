# Instructor & Examiner Manual
**Lab Name:** Apex Cyber Defense - Network Pentesting Exam  
**Target Environment:** Docker or Linux VM (Debian / Ubuntu)

---

## 1. Master Flag & Credential Reference

| Phase | Item | Value / Location | Points |
|---|---|---|---|
| **Web Recon** | Username | `alicesmith` (Found on `/index.html` and `/about.html`) | 10 pts |
| **Web Recon** | Flag 1 | `FLAG{w3b_r3c0n_us3rn4m3_f0und_9482}` (In `/about.html` HTML source) | 15 pts |
| **CeWL / FTP** | FTP Password | `CyberVanguard` (Scraped by CeWL from homepage text) | 15 pts |
| **FTP Loot** | SSH Private Key | `id_rsa` in Alice's FTP home directory | 10 pts |
| **SSH Access** | SSH Port | `2222` (Port 22 is disabled) | 10 pts |
| **SSH Shell** | Flag 2 | `FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}` (In `/home/alicesmith/user.txt`) | 15 pts |
| **PrivEsc** | Sudo Rule | `alicesmith ALL=(ALL) NOPASSWD: /usr/bin/find` | 10 pts |
| **Root Shell** | Flag 3 | `FLAG{r00t_gtf0b1n5_pr1v3sc_succ3ss_8821}` (In `/root/root.txt`) | 15 pts |
| **Total** | | | **100 pts** |

---

## 2. Deployment Instructions

### Option A: Turnkey Docker Deployment (Recommended)
From the lab root directory:
```bash
# Build and launch the container in the background
docker compose up -d --build

# Verify container status and exposed ports
docker compose ps
```
The container will listen on:
- Port `80` (HTTP)
- Port `21` (FTP)
- Port `2222` (SSH)

To stop and reset the container:
```bash
docker compose down -v
docker compose up -d --build
```

### Option B: Bare-Metal / Virtual Machine (Ubuntu / Debian)
Copy the `pentest-exam-lab` folder to a clean Ubuntu 20.04/22.04 or Debian 11/12 virtual machine and run:
```bash
sudo bash setup-exam.sh
```
The script will install all dependencies, configure services, generate the keypairs, set permissions, and output the target IP.

---

## 3. Network Architecture & Firewall Verification
To verify that **only the 3 designated ports** are responding to network scans:
```bash
# From an instructor machine or attacker host:
nmap -p- -sV <TARGET_IP>
```
Expected output:
```text
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.x
80/tcp   open  http    nginx
2222/tcp open  ssh     OpenSSH 9.x
```
*(Port 22 will show as CLOSED or FILTERED).*

---

## 4. Grading Rubric
- **Partial Credit:**
  - Discovered username `alicesmith` but missed Flag 1: award 10/25.
  - Successfully logged into FTP but failed to find non-standard SSH port: award 50/100.
  - Reached SSH user shell (Flag 1 + Flag 2 captured) but could not escalate to root: award 75/100.
  - Full root compromise (All 3 flags + report): award 100/100.
