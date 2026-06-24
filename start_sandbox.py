import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gmail_service import GmailService

import socket

def check_connectivity(host="8.8.8.8", port=53, timeout=3):
    """Checks if external network is accessible."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def main():
    """Main entry point to start the Anti-Scam AI Sandbox."""
    print("Initializing Anti-Scam AI Self-Healing Protocol...")

    print("Checking network connectivity...")
    if not check_connectivity():
        print("[!] Warning: External network unreachable (ERR_CONNECTION_TIMED_OUT).")
        print("[!] Bypassing standard Firebase/Google authentication handshakes.")
    else:
        print("[+] Network accessible. Proceeding with Self-Healing Local Sandbox for secure isolation.")

    # Force sandbox mode for this entry point
    gmail = GmailService(sandbox_mode=True)

    # Launch Guest Sign-In with Terminal UI
    gmail.sign_in_as_guest(launch_terminal=True)

if __name__ == "__main__":
    main()
