# Gmail API Integration for Anti-Scam AI

This project now includes a Gmail API integration that allows you to fetch and analyze emails for potential scams.

## Prerequisites

To use the Gmail API integration, you need:

1.  **A Google Cloud Project**: If you don't have one, create it in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Enabled Gmail API**: Enable the Gmail API for your project in the Cloud Console.
3.  **OAuth 2.0 Credentials**:
    *   Go to the "APIs & Services" > "Credentials" page.
    *   Click "Create Credentials" > "OAuth client ID".
    *   Choose "Desktop app" as the application type.
    *   Download the JSON file and rename it to `credentials.json`.
    *   Place `credentials.json` in the root directory of this project.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

You can use the `GmailService` class to interact with the Gmail API.

### Basic Example

```python
from src.gmail_service import GmailService

gmail = GmailService()
gmail.authenticate()

# List latest messages
messages = gmail.list_messages(max_results=5)
for msg in messages:
    full_msg = gmail.get_message(msg['id'])
    print(f"Snippet: {full_msg['snippet']}")
```

See `examples/gmail_example.py` for a complete usage example.

## Configuration

Gmail settings can be configured in `config.yaml`:

```yaml
gmail:
  credentials_path: "credentials.json"
  token_path: "token.json"
  scopes: ["https://www.googleapis.com/auth/gmail.readonly"]
```
