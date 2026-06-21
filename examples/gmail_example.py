import sys
import os

# Add the src directory to the path so we can import GmailService
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from gmail_service import GmailService

def run_demo(sandbox=False):
    mode_name = "SANDBOX" if sandbox else "REAL"
    print(f"\n--- Starting Gmail Service Demo ({mode_name} MODE) ---")

    gmail = GmailService(sandbox_mode=sandbox)

    try:
        print("Authenticating...")
        gmail.authenticate()

        print("\nFetching Labels:")
        labels = gmail.list_labels()
        for label in labels:
            print(f"- {label['name']}")

        print("\nFetching latest 5 messages:")
        messages = gmail.list_messages(max_results=5)

        if not messages:
            print("No messages found.")
        else:
            for msg in messages:
                full_msg = gmail.get_message(msg['id'])
                snippet = full_msg.get('snippet', 'No snippet available')
                print(f"Message ID: {msg['id']}")
                print(f"Snippet: {snippet}")
                body = gmail.get_message_body(full_msg)
                print(f"Body length: {len(body)} characters")
                print("-" * 20)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure you have followed the instructions in README.md to get your credentials.json file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Example of using the GmailService class."""
    # Run sandbox demo by default to ensure it works without real credentials
    run_demo(sandbox=True)

    # In a real environment, you'd run:
    # run_demo(sandbox=False)

if __name__ == "__main__":
    main()
