# Gmail API Integration for Anti-Scam AI

This project includes a Gmail API integration that allows you to fetch and analyze emails for potential scams.

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

## Troubleshooting Connection Issues (ERR_QUIC_PROTOCOL_ERROR)

If you encounter `ERR_QUIC_PROTOCOL_ERROR` or other network blocks during the OAuth login flow, you have two options:

### Option 1: Manual Access Token Override
1.  Go to the [Google OAuth Playground](https://developers.google.com/oauthplayground/).
2.  Select "Gmail API v1" and the required scopes (e.g., `https://www.googleapis.com/auth/gmail.readonly`).
3.  Click "Authorize APIs" and sign in.
4.  Click "Exchange authorization code for tokens".
5.  Copy the `access_token`.
6.  Either provide it to the `GmailService` constructor or set it in `config.yaml`:
    ```yaml
    gmail:
      access_token: "your_copied_access_token"
    ```

### Option 2: Sandbox Mode
If you want to develop without connecting to a real Gmail account:
1.  Enable `sandbox_mode` in `config.yaml`:
    ```yaml
    gmail:
      sandbox_mode: true
    ```
    Or pass `sandbox_mode=True` to the `GmailService` constructor.

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

# The service will automatically load settings from config.yaml
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
  access_token: null  # Manual override to bypass OAuth flow
  sandbox_mode: false  # Enable simulated data for development
```
