import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gmail_service import GmailService

def main():
    """Main entry point to start the Anti-Scam AI Sandbox."""
    print("Initializing Anti-Scam AI Self-Healing Protocol...")

    # Force sandbox mode for this entry point
    gmail = GmailService(sandbox_mode=True)

    # Launch Guest Sign-In with Terminal UI
    gmail.sign_in_as_guest(launch_terminal=True)

if __name__ == "__main__":
    main()
