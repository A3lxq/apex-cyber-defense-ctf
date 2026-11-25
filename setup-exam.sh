#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run this script as root: sudo bash setup-exam.sh"
  exit 1
fi

echo "====================================================================="
echo "   Setting up Apex Cyber Defense Pentesting Exam Target              "
echo "====================================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Install packages
echo "[*] Installing required packages..."
apt-get update -y || true
apt-get install -y nginx vsftpd openssh-server sudo curl net-tools --no-install-recommends

# 2. Deploy Web Files to /var/www/html (includes /backup/ and /backups/)
echo "[*] Deploying web files and hidden backup directories..."
rm -rf /var/www/html/*
cp -r "$SCRIPT_DIR/web/"* /var/www/html/
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

# 3. Create target user alicesmith
if ! id "alicesmith" &>/dev/null; then
    echo "[*] Creating user alicesmith..."
    useradd -m -s /bin/bash alicesmith
    echo "alicesmith:CyberVanguard" | chpasswd
fi

USER_HOME="/home/alicesmith"
mkdir -p "$USER_HOME/.ssh"
chmod 700 "$USER_HOME/.ssh"

# 4. Setup SSH Keys in .ssh
echo "[*] Setting up OpenSSH keypair for alicesmith..."
if [ -f "$SCRIPT_DIR/id_rsa" ]; then
    cp "$SCRIPT_DIR/id_rsa" "$USER_HOME/.ssh/id_rsa"
    cp "$SCRIPT_DIR/id_rsa.pub" "$USER_HOME/.ssh/authorized_keys"
else
    ssh-keygen -t rsa -b 2048 -f "$USER_HOME/.ssh/id_rsa" -N "" -C "alicesmith@apexdefense.local"
    cp "$USER_HOME/.ssh/id_rsa.pub" "$USER_HOME/.ssh/authorized_keys"
fi
chmod 600 "$USER_HOME/.ssh/authorized_keys"
chmod 600 "$USER_HOME/.ssh/id_rsa"

# In FTP: ONLY ssh_instructions.txt is hosted (No id_rsa, no backup folder)
rm -rf "$USER_HOME/id_rsa" "$USER_HOME/backups"
cp "$SCRIPT_DIR/ssh_instructions.txt" "$USER_HOME/ssh_instructions.txt"
chmod 644 "$USER_HOME/ssh_instructions.txt"

# Flag 2 (User Flag)
echo "FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}" > "$USER_HOME/user.txt"
chmod 600 "$USER_HOME/user.txt"

# Clue for next stage
cat << 'EOF' > "$USER_HOME/clue.txt"
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
EOF
chmod 644 "$USER_HOME/clue.txt"

chown -R alicesmith:alicesmith "$USER_HOME"

# Root Flag (Flag 3)
echo "FLAG{4p3x_d3f3ns3_pwn3d_5521}" > /root/root.txt
chmod 600 /root/root.txt

# 5. Sudoers GTFOBins Rule
echo "alicesmith ALL=(ALL) NOPASSWD: /usr/bin/find" > /etc/sudoers.d/alicesmith
chmod 440 /etc/sudoers.d/alicesmith

# 6. Configure FTP & SSH
cp "$SCRIPT_DIR/config/vsftpd.conf" /etc/vsftpd.conf
mkdir -p /var/run/vsftpd/empty
systemctl restart vsftpd || true

cp "$SCRIPT_DIR/config/sshd_config" /etc/ssh/sshd_config
echo "Apex Cyber Defense Appliance v3.11 (Restricted Access)" > /etc/issue.net
systemctl restart ssh || systemctl restart sshd || true

# 7. Restart Nginx
systemctl restart nginx || true

LOCAL_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "====================================================================="
echo "   TARGET ENVIRONMENT READY!                                        "
echo "====================================================================="
echo "Target IP: $LOCAL_IP"
echo "Open Ports: 80 (HTTP), 21 (FTP), 2222 (SSH)"
echo "Web Portal contains hidden directory: http://$LOCAL_IP/backup/"
echo "FTP Directory contains ONLY: ssh_instructions.txt"
echo "====================================================================="
