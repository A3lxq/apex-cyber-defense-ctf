#!/bin/bash
set -e

echo "[*] Initializing Apex Cyber Defense Exam Environment..."

if ! id "alicesmith" &>/dev/null; then
    useradd -m -s /bin/bash alicesmith
    echo "alicesmith:CyberVanguard" | chpasswd
fi

USER_HOME="/home/alicesmith"
mkdir -p "$USER_HOME/.ssh"
chmod 700 "$USER_HOME/.ssh"

if [ -f "/scripts/id_rsa" ]; then
    cp "/scripts/id_rsa" "$USER_HOME/.ssh/id_rsa"
    cp "/scripts/id_rsa.pub" "$USER_HOME/.ssh/authorized_keys"
else
    ssh-keygen -t rsa -b 2048 -f "$USER_HOME/.ssh/id_rsa" -N "" -C "alicesmith@apexdefense.local"
    cp "$USER_HOME/.ssh/id_rsa.pub" "$USER_HOME/.ssh/authorized_keys"
fi
chmod 600 "$USER_HOME/.ssh/authorized_keys"
chmod 600 "$USER_HOME/.ssh/id_rsa"

# FTP has ONLY ssh_instructions.txt (No key in FTP!)
rm -rf "$USER_HOME/id_rsa" "$USER_HOME/backups"
cp /scripts/ssh_instructions.txt "$USER_HOME/ssh_instructions.txt"
chmod 644 "$USER_HOME/ssh_instructions.txt"

# Flag 2 & Clue
echo "FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}" > "$USER_HOME/user.txt"
chmod 600 "$USER_HOME/user.txt"

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

# Root Flag
mkdir -p /root
echo "FLAG{4p3x_d3f3ns3_pwn3d_5521}" > /root/root.txt
chmod 600 /root/root.txt

# Sudoers
cp /etc/sudoers_exam /etc/sudoers.d/alicesmith 2>/dev/null || true
chmod 440 /etc/sudoers.d/alicesmith

mkdir -p /run/sshd
ssh-keygen -A
mkdir -p /var/run/vsftpd/empty

service nginx start

# Not `service vsftpd start`: that wrapper's `start-stop-daemon
# --background -m` pidfile tracking is unreliable in at least one real
# container/pod environment observed during testing -- it wrote its
# OWN pid (and itself never exited, spinning at 100% CPU) instead of
# vsftpd's actual forked pid, so the init script's own post-start
# `ps -C vsftpd | grep "$_PID"` check always failed even though vsftpd
# was genuinely running fine. Launching it directly sidesteps that
# daemonization dance entirely -- nothing else here needs the pidfile.
/usr/sbin/vsftpd /etc/vsftpd.conf &

exec /usr/sbin/sshd -D -e -f /etc/ssh/sshd_config
