import sys
import os

# Add the src directory to the path so we can import GmailService
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from gmail_service import GmailService

def main():
    """Example of using the GmailService class."""
    print("Initializing Gmail Service...")
    gmail = GmailService()

    try:
        print("Authenticating...")
        # Note: This will fail if credentials.json is not present
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
                print("-" * 20)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure you have followed the instructions in README.md to get your credentials.json file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
