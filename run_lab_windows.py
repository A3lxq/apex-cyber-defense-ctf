import os
import sys
import threading
import socket
from http.server import SimpleHTTPRequestHandler, HTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")

# ---------------------------------------------------------------------------
# 1. HTTP SERVER (Port 80 / 8080) - Serves Website & Hidden /backup/ Directory
# ---------------------------------------------------------------------------
class CustomHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def log_message(self, format, *args):
        print(f"[HTTP 80] {self.address_string()} - {format % args}")

def run_http_server(port=80):
    try:
        server = HTTPServer(("0.0.0.0", port), CustomHTTPHandler)
        print(f"[+] [PORT {port}] HTTP Web Server running at http://localhost:{port}/")
        print(f"    [Web Structure] Hidden Directory available: http://localhost:{port}/backup/")
        server.serve_forever()
    except PermissionError:
        print(f"[!] Port {port} requires Administrator privileges. Retrying on port 8080...")
        run_http_server(8080)
    except Exception as e:
        print(f"[-] HTTP Server error on port {port}: {e}")

# ---------------------------------------------------------------------------
# 2. FTP SERVER (Port 21 / 2121) - Serves ONLY ssh_instructions.txt
# ---------------------------------------------------------------------------
def run_ftp_server(port=21):
    instructions_file = os.path.join(BASE_DIR, "ssh_instructions.txt")
    with open(instructions_file, "r", encoding="utf-8") as f:
        instructions_content = f.read().replace("\n", "\r\n").encode("utf-8")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
        print(f"[+] [PORT {port}] FTP Gateway running (User: alicesmith | Pass: CyberVanguard)")
        print(f"    [FTP Content] ONLY ssh_instructions.txt is hosted (Points to web /backup/)")
    except PermissionError:
        print(f"[!] Port {port} requires Admin. Retrying FTP on port 2121...")
        run_ftp_server(2121)
        return
    except Exception as e:
        print(f"[-] FTP Server error on port {port}: {e}")
        return

    while True:
        try:
            client, addr = sock.accept()
            threading.Thread(target=handle_ftp_client, args=(client, addr, instructions_content), daemon=True).start()
        except Exception:
            break

def handle_ftp_client(conn, addr, instructions_content):
    conn.sendall(b"220 Apex Cyber Defense Secure FTP Gateway v2.4 Ready.\r\n")
    user = ""
    authenticated = False
    pasv_listener = None

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            cmd_line = data.decode("utf-8", errors="ignore").strip()
            parts = cmd_line.split(" ", 1)
            cmd = parts[0].upper()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if cmd == "USER":
                user = arg
                conn.sendall(b"331 Please specify the password.\r\n")
            elif cmd == "PASS":
                print(f"[FTP] Login attempt: user='{user}' pass='{arg}' from {addr[0]}")
                if user.lower() == "alicesmith" and arg.lower() == "cybervanguard":
                    authenticated = True
                    conn.sendall(b"230 Login successful.\r\n")
                    print(f"[FTP] [+] Successful authentication for alicesmith from {addr[0]}")
                else:
                    conn.sendall(b"530 Login incorrect.\r\n")
            elif cmd == "SYST":
                conn.sendall(b"215 UNIX Type: L8\r\n")
            elif cmd == "PWD":
                conn.sendall(b'257 "/home/alicesmith" is current directory.\r\n')
            elif cmd == "TYPE":
                conn.sendall(b"200 Switching to Binary mode.\r\n")
            elif cmd == "PASV":
                if pasv_listener:
                    try:
                        pasv_listener.close()
                    except Exception:
                        pass
                pasv_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                pasv_listener.bind(("0.0.0.0", 0))
                pasv_listener.listen(1)
                pasv_port = pasv_listener.getsockname()[1]
                p1 = pasv_port // 256
                p2 = pasv_port % 256
                conn.sendall(f"227 Entering Passive Mode (127,0,0,1,{p1},{p2}).\r\n".encode())
            elif cmd in ("CWD", "XCWD", "CDUP", "XCUP"):
                conn.sendall(b"250 Directory successfully changed to /.\r\n")
            elif cmd in ("LIST", "NLST"):
                conn.sendall(b"150 Here comes the directory listing.\r\n")
                if pasv_listener:
                    dconn, _ = pasv_listener.accept()
                    listing = f"-rw-r--r-- 1 alicesmith alicesmith {len(instructions_content)} Nov 24 12:00 ssh_instructions.txt\r\n"
                    dconn.sendall(listing.encode())
                    dconn.close()
                    pasv_listener.close()
                    pasv_listener = None
                conn.sendall(b"226 Directory send OK.\r\n")
            elif cmd == "RETR":
                target_file = arg.strip("/")
                if target_file in ("ssh_instructions.txt", "/ssh_instructions.txt"):
                    conn.sendall(f"150 Opening ASCII mode data connection for {target_file}.\r\n".encode())
                    if pasv_listener:
                        dconn, _ = pasv_listener.accept()
                        dconn.sendall(instructions_content)
                        dconn.close()
                        pasv_listener.close()
                        pasv_listener = None
                    conn.sendall(b"226 Transfer complete.\r\n")
                    print(f"[FTP] {addr[0]} retrieved {target_file}")
                else:
                    conn.sendall(b"550 File not found. Notice: Keys are stored in the web /backup/ directory! Check ssh_instructions.txt.\r\n")
            elif cmd == "QUIT":
                conn.sendall(b"221 Goodbye.\r\n")
                break
            else:
                conn.sendall(b"502 Command not implemented.\r\n")
        except Exception:
            break
    conn.close()

# ---------------------------------------------------------------------------
# 3. INTERACTIVE SIMULATED SSH SERVER (Port 2222)
# ---------------------------------------------------------------------------
def run_ssh_sim_server(port=2222):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
        print(f"[+] [PORT {port}] OpenSSH Service (Port 2222) Ready for candidate connections.")
    except Exception as e:
        print(f"[-] SSH Sim error on port {port}: {e}")
        return

    while True:
        try:
            client, addr = sock.accept()
            threading.Thread(target=handle_ssh_session, args=(client, addr), daemon=True).start()
        except Exception:
            break

def handle_ssh_session(conn, addr):
    banner = (
        "\r\n============================================================\r\n"
        " Apex Cyber Defense Appliance v3.11 (Restricted Port 2222)\r\n"
        " Authorized authentication: alicesmith (Key-based active)\r\n"
        "============================================================\r\n"
        "Last login: Mon Nov 24 10:15:22 2026 from internal-vpn\r\n\r\n"
    )
    conn.sendall(banner.encode())
    prompt = b"alicesmith@apex-defense-target:~$ "
    conn.sendall(prompt)

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            cmd = data.decode("utf-8", errors="ignore").strip()
            if not cmd:
                conn.sendall(prompt)
                continue

            if cmd == "exit":
                conn.sendall(b"logout\r\nConnection to target closed.\r\n")
                break
            elif cmd in ("id", "whoami"):
                conn.sendall(b"uid=1001(alicesmith) gid=1001(alicesmith) groups=1001(alicesmith)\r\n")
            elif cmd in ("ls", "ls -la"):
                conn.sendall(b"total 20\r\ndrwxr-xr-x 4 alicesmith alicesmith 4096 Nov 24 12:00 .\r\ndrwxr-xr-x 3 root       root       4096 Nov 24 11:50 ..\r\n-rw-r--r-- 1 alicesmith alicesmith  810 Nov 24 12:00 clue.txt\r\n-rw------- 1 alicesmith alicesmith   45 Nov 24 12:00 user.txt\r\n")
            elif "user.txt" in cmd and "cat" in cmd:
                conn.sendall(b"FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}\r\n")
            elif "clue.txt" in cmd and "cat" in cmd:
                clue_text = (
                    "========================================================================\r\n"
                    "STAGE 3 COMPLETE - PRIVILEGE ESCALATION NOTICE\r\n"
                    "========================================================================\r\n"
                    "Flag 2: FLAG{ssh_k3y_auth_p0rt_2222_pwn3d_1834}\r\n\r\n"
                    "CLUE FOR NEXT STAGE:\r\n"
                    "The target system has a misconfigured administrative utility.\r\n"
                    "1. Check what commands your user is permitted to run as root: sudo -l\r\n"
                    "2. Check GTFOBins (https://gtfobins.github.io/) to exploit this binary.\r\n"
                    "3. Catch a root reverse shell (nc -lvnp 4444) or spawn root.\r\n"
                    "4. Capture the final root flag located at /root/root.txt\r\n"
                    "========================================================================\r\n"
                )
                conn.sendall(clue_text.encode())
            elif cmd == "sudo -l":
                sudo_out = (
                    "Matching Defaults entries for alicesmith on apex-defense-target:\r\n"
                    "    env_reset, mail_badpass, secure_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin\r\n\r\n"
                    "User alicesmith may run the following commands on apex-defense-target:\r\n"
                    "    (ALL) NOPASSWD: /usr/bin/find\r\n"
                )
                conn.sendall(sudo_out.encode())
            elif "find" in cmd and "sudo" in cmd:
                root_shell_msg = (
                    "\r\n[+] GTFOBins Exploit Executed! Elevated to root context!\r\n"
                    "root@apex-defense-target:/home/alicesmith# id\r\n"
                    "uid=0(root) gid=0(root) groups=0(root)\r\n"
                    "root@apex-defense-target:/home/alicesmith# cat /root/root.txt\r\n"
                    "FLAG{4p3x_d3f3ns3_pwn3d_5521}\r\n"
                    "root@apex-defense-target:/home/alicesmith# \r\n"
                )
                conn.sendall(root_shell_msg.encode())
            elif "/root/root.txt" in cmd and "cat" in cmd:
                conn.sendall(b"FLAG{4p3x_d3f3ns3_pwn3d_5521}\r\n")
            elif cmd == "help":
                conn.sendall(b"Supported exam commands: ls, cat, id, whoami, sudo -l, sudo find, exit\r\n")
            else:
                conn.sendall(f"bash: {cmd}: command executed\r\n".encode())

            conn.sendall(prompt)
        except Exception:
            break
    conn.close()

# ---------------------------------------------------------------------------
# MAIN LAUNCHER
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 65)
    print("   APEX CYBER DEFENSE - EXAM SERVER SIMULATOR (REVISED)   ")
    print("=" * 65)
    print("Starting all 3 challenge services concurrently on localhost...")
    print("Press Ctrl+C at any time to stop the server.\n")

    t_http = threading.Thread(target=run_http_server, daemon=True)
    t_ftp = threading.Thread(target=run_ftp_server, daemon=True)
    t_ssh = threading.Thread(target=run_ssh_sim_server, daemon=True)

    t_http.start()
    t_ftp.start()
    t_ssh.start()

    print("\n[+] Target is ACTIVE and waiting for candidate attacks!")
    print("    - Web:  http://localhost/ (or http://localhost:8080/)")
    print("    - FTP:  localhost:21      (or localhost:2121)")
    print("    - SSH:  localhost:2222\n")

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\n[*] Stopping all exam services. Goodbye!")
        sys.exit(0)
