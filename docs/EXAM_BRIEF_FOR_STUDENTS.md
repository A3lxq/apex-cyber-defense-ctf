# Practical Network Penetration Testing Examination
**Subject:** Offensive Security & Host Compromise Assessment  
**Duration:** 3 Hours  
**Target:** Provided Candidate IP Address (`<TARGET_IP>`)

---

## 1. Exam Overview & Rules of Engagement
You have been tasked with performing a black-box penetration test against a corporate perimeter server belonging to **Apex Cyber Defense Systems**. Your goal is to conduct full reconnaissance, exploit perimeter services, establish initial foothold, escalate privileges to `root`, and retrieve all proof flags.

### Rules of Engagement:
1. **Target Scope:** Only the provided IP address is in scope. Do not scan or attack any adjacent hosts on the network.
2. **Denial of Service (DoS):** Aggressive stress testing, flooding (SYN flood, DoS), or destructive actions are strictly forbidden.
3. **Proof Artifacts:** You must recover **3 flags** across the target:
   - **Flag 1 (Web Reconnaissance Flag)**
   - **Flag 2 (User Footprint Flag - SSH)**
   - **Flag 3 (Root Compromise Flag)**
4. **Format of Flags:** All flags follow the exact pattern: `FLAG{...}`.

---

## 2. Examination Objectives & Milestones

| Stage | Objective | Deliverables | Points |
|---|---|---|---|
| **Phase 1: Port Scanning & Recon** | Identify all open TCP ports and examine the web portal. | Nmap report, discovered services, Target username, Flag 1 | 25 pts |
| **Phase 2: Wordlist & FTP Access** | Harvest web copy using `cewl`, crack FTP credentials, and retrieve secure assets. | Generated wordlist, FTP credentials, SSH private key | 25 pts |
| **Phase 3: SSH Key Access** | Determine the SSH service port, set file permissions, and login as the user. | Connection syntax, active user shell, Flag 2 | 25 pts |
| **Phase 4: Privilege Escalation** | Exploit internal misconfiguration via GTFOBins, catch reverse shell, and achieve root. | PrivEsc method, root proof, Flag 3 | 25 pts |
| **Total** | | | **100 pts** |

---

## 3. Important Hints & Constraints
- **Target Surface:** Exactly **3 TCP ports** are accessible from the outside. Any default assumption about standard service ports may fail.
- **Web Authentication:** The corporate website displays a staff login portal; however, policy prevents direct web authentication. Pay close attention to corporate notices and developer comments.
- **Wordlists:** Standard generic wordlists (like `rockyou.txt`) are not required. The password is derived directly from the target company's web assets.
- **Key Permissions:** UNIX SSH clients enforce strict security policies regarding private key permissions.
- **Privilege Escalation:** Investigate permissions granted to your user account and consult standard Unix privilege escalation repositories ([GTFOBins](https://gtfobins.github.io/)).

Good luck!
