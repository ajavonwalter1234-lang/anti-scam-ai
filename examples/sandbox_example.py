import sys
import os

# Add the src directory to the path so we can import GmailService
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from gmail_service import GmailService

def main():
    """Example of using the GmailService in Sandbox Mode."""
    print("=== Anti-Scam AI: Guest Sign-In (Sandbox Mode) ===")

    # Initialize service in sandbox mode (simulating Guest Sign-In)
    gmail = GmailService(sandbox_mode=True)
    gmail.sign_in_as_guest()

    print("\nFetching latest messages from Sandbox...")
    messages = gmail.list_messages()

    for msg in messages:
        full_msg = gmail.get_message(msg['id'])
        snippet = full_msg.get('snippet', 'No snippet available')
        print(f"Message ID: {msg['id']}")
        print(f"Snippet: {snippet}")

        # In a real app, we would run analysis here
        if "Urgent" in snippet or "Financial" in snippet:
            print("Status: [!] POTENTIAL SCAM DETECTED")
        else:
            print("Status: [OK] Clean")
        print("-" * 30)

    print("\nSandbox operations completed. All data persisted locally.")

if __name__ == "__main__":
    main()
