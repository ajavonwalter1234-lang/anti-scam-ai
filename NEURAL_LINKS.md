# Neural Links: Troubleshooting & Security Overrides

This guide provides instructions for resolving network and protocol issues encountered while using Anti-Scam AI.

## 1. Gmail Authentication & Sync Issue (ERR_QUIC_PROTOCOL_ERROR)

### The Root Cause
Modern browsers (primarily Google Chrome) standardly negotiate connection protocols using the experimental QUIC (HTTP/3) protocol. In certain secure firewalls or development sandbox environments, QUIC packets (UDP traffic) may be blocked, triggering the `ERR_QUIC_PROTOCOL_ERROR`.

### Solutions

#### Option A: Disable QUIC in Chrome
1. Open a new tab in Chrome.
2. Paste `chrome://flags/#enable-quic` into the address bar.
3. Change the **Experimental QUIC protocol** setting to **Disabled**.
4. Restart your browser.

#### Option B: Manual Access Token Override
You can bypass the OAuth handshake entirely by providing a manual access token.
1. Go to the [Google OAuth Playground](https://developers.google.com/oauthplayground/).
2. Select the **Gmail API v1** and choose the `https://www.googleapis.com/auth/gmail.readonly` scope.
3. Click **Authorize APIs** and sign in.
4. Click **Exchange authorization code for tokens**.
5. Copy the **Access Token**.
6. Apply the token in your configuration or via the API:

```yaml
# config.yaml
gmail:
  access_token: "YOUR_ACCESS_TOKEN_HERE"
```

In code:
```python
gmail_service.authenticate(access_token_override="YOUR_ACCESS_TOKEN_HERE")
```

## 2. Guest Sign-In Failure

### The Root Cause
Network constraints blocking Google QUIC connections may also impede standard Firebase handshake requests, causing Guest Sign-In (Anonymous Authentication) to fail.

### Self-Healing Fallback: Local Sandbox Mode
Anti-Scam AI now features an automatic fallback protocol. If the application is unable to connect to authentication servers (e.g., encountering `ERR_CONNECTION_TIMED_OUT` on `firebaseapp.com`), it will gracefully initialize **Local Sandbox Mode**.

- **Instant Boot**: Clicking "Sign in as Guest" (or running `python start_sandbox.py`) now instantly boots up an operational local terminal environment.
- **Simulated Vectors**: Features fully simulated scan vectors and responsive scanner loops.
- **Local Persistence**: Threat reports, keyword edits, and purged mail sectors are saved seamlessly to local storage (simulated via `data/local_storage.json`).

All operations in Sandbox Mode are kept private to your local session.
