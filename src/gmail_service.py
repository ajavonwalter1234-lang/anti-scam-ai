import os.path
import base64
import yaml
import requests
import json
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
try:
    from .persistence import LocalPersistence
except ImportError:
    from persistence import LocalPersistence

class GmailService:
    """A service class to interact with the Gmail API."""

    def __init__(self, credentials_path=None, token_path=None, scopes=None, config_path='config.yaml', access_token=None, sandbox_mode=False):
        # Try to load from config if not provided
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                try:
                    full_config = yaml.safe_load(f)
                    config = full_config.get('gmail', {})
                except yaml.YAMLError:
                    pass

        self.credentials_path = credentials_path or config.get('credentials_path', 'credentials.json')
        self.token_path = token_path or config.get('token_path', 'token.json')
        self.scopes = scopes or config.get('scopes', ['https://www.googleapis.com/auth/gmail.readonly'])
        self.access_token = access_token or config.get('access_token')
        self.sandbox_mode = sandbox_mode or config.get('sandbox_mode', False)
        self.persistence = LocalPersistence() if self.sandbox_mode else None
        self.service = None

    def authenticate(self, access_token_override=None, use_device_flow=False):
        """
        Authenticates the user and returns the Gmail API service object.
        Supports manual access token override and Google Device Flow to bypass network/iframe constraints.
        Automatically falls back to Sandbox Mode on network failure.
        """
        if self.sandbox_mode:
            print("Running in Sandbox Mode: Authentication skipped.")
            return None

        try:
            token = access_token_override or self.access_token
            creds = None

            if token:
                print("Using manual access token override.")
                creds = Credentials(token=token)
            elif os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

            if not creds or (not token and not creds.valid):
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif use_device_flow:
                    creds = self.authenticate_device_flow()
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}. "
                                                "Please refer to README.md for instructions on how to obtain it.")

                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                        # Use a short timeout for the local server to simulate network constraints
                        creds = flow.run_local_server(port=0, timeout_seconds=10)
                    except Exception as e:
                        print(f"Standard authentication failed or timed out: {e}")
                        print("Attempting Google Device Flow fallback...")
                        creds = self.authenticate_device_flow()

                if creds and not token:
                    with open(self.token_path, 'w') as token_file:
                        token_file.write(creds.to_json())

            if creds:
                self.service = build('gmail', 'v1', credentials=creds)
                return self.service
            else:
                raise Exception("Failed to obtain credentials.")

        except Exception as error:
            print(f"Authentication failed: {error}")
            print("Encountered network or protocol issue. Falling back to Local Sandbox Mode.")
            self.enable_sandbox_mode()
            return None

    def authenticate_device_flow(self):
        """
        Implements Google OAuth 2.0 Device Flow.
        This bypasses port-forwarding, QUIC protocol issues, and iframe constraints.
        """
        print("\n--- Google Device Flow Authentication ---")

        if not os.path.exists(self.credentials_path):
             raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}.")

        with open(self.credentials_path, 'r') as f:
            client_config = json.load(f)
            client_id = client_config.get('installed', {}).get('client_id')
            client_secret = client_config.get('installed', {}).get('client_secret')

        if not client_id or not client_secret:
            raise ValueError("Invalid credentials.json: Missing client_id or client_secret.")

        # 1. Request Device and User Codes
        device_code_url = "https://oauth2.googleapis.com/device/code"
        scope_str = " ".join(self.scopes)
        response = requests.post(device_code_url, data={
            'client_id': client_id,
            'scope': scope_str
        })

        if response.status_code != 200:
            raise Exception(f"Failed to initiate device flow: {response.text}")

        data = response.json()
        device_code = data['device_code']
        user_code = data['user_code']
        verification_url = data['verification_url']
        interval = data['interval']
        expires_in = data['expires_in']

        print(f"\n1. Go to: {verification_url}")
        print(f"2. Enter code: {user_code}")
        print(f"\nWaiting for authorization (expires in {expires_in} seconds)...")

        # 2. Poll for Token
        token_url = "https://oauth2.googleapis.com/token"
        start_time = time.time()
        while time.time() - start_time < expires_in:
            time.sleep(interval)
            response = requests.post(token_url, data={
                'client_id': client_id,
                'client_secret': client_secret,
                'device_code': device_code,
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
            })

            token_data = response.json()
            if response.status_code == 200:
                print("Successfully authenticated via Device Flow.")
                return Credentials(
                    token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_url,
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=self.scopes
                )
            elif token_data.get('error') != 'authorization_pending':
                raise Exception(f"Device flow polling failed: {token_data.get('error_description', token_data.get('error'))}")

        raise Exception("Device flow timed out.")

    def enable_sandbox_mode(self):
        """Enables sandbox mode dynamically."""
        self.sandbox_mode = True
        if not self.persistence:
            self.persistence = LocalPersistence()
        print("Local Sandbox Mode initialized.")

    def sign_in_as_guest(self, launch_terminal=False):
        """Simulates 'Sign in as Guest' by instantly booting into sandbox mode."""
        print("Guest Sign-In detected. Bypassing Firebase/Google handshake.")
        self.enable_sandbox_mode()
        if launch_terminal:
            try:
                from .terminal_app import TerminalApp
            except ImportError:
                from terminal_app import TerminalApp
            app = TerminalApp(sandbox_mode=True)
            app.run()

    def list_messages(self, user_id='me', query='', max_results=10):
        """Lists messages in the user's mailbox matching the query."""
        if not self.service and not self.sandbox_mode:
            self.authenticate()

        if self.sandbox_mode:
            print("Running in Sandbox Mode: Returning simulated messages.")
            return self.persistence.get('messages', [
                {'id': 'msg_1', 'threadId': 'thread_1'},
                {'id': 'msg_2', 'threadId': 'thread_2'}
            ])

        try:
            results = self.service.users().messages().list(userId=user_id, q=query, maxResults=max_results).execute()
            return results.get('messages', [])
        except HttpError as error:
            print(f"An error occurred while listing messages: {error}")
            return []

    def get_message(self, message_id, user_id='me', format='full'):
        """Gets a specific message by ID."""
        if not self.service and not self.sandbox_mode:
            self.authenticate()

        if self.sandbox_mode:
            print(f"Running in Sandbox Mode: Returning simulated message {message_id}.")
            simulated_messages = self.persistence.get('messages_content', {
                'msg_1': {'id': 'msg_1', 'snippet': 'Urgent: Financial transfer required', 'payload': {'mimeType': 'text/plain', 'body': {'data': 'YmFzZTY0IGVuY29kZWQgc2NhbSBjb250ZW50'}}},
                'msg_2': {'id': 'msg_2', 'snippet': 'Hello from your bank', 'payload': {'mimeType': 'text/plain', 'body': {'data': 'SGVsbG8sIHRoaXMgaXMgbm90IGEgc2NhbS4='}}}
            })
            return simulated_messages.get(message_id)

        try:
            return self.service.users().messages().get(userId=user_id, id=message_id, format=format).execute()
        except HttpError as error:
            print(f"An error occurred while fetching message {message_id}: {error}")
            return None

    def get_message_body(self, message):
        """Extracts the body from a Gmail message, handling nested structures."""
        payload = message.get('payload')
        if not payload:
            return ""

        return self._extract_body_from_payload(payload)

    def _extract_body_from_payload(self, payload):
        """Helper to recursively extract body from payload parts."""
        mime_type = payload.get('mimeType')
        body_data = payload.get('body', {}).get('data')

        if mime_type == 'text/plain' and body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8')

        parts = payload.get('parts', [])
        body = ""
        for part in parts:
            part_body = self._extract_body_from_payload(part)
            if part_body:
                body += part_body
                # If we found plain text in a multipart/alternative, we might prefer it and stop
                if payload.get('mimeType') == 'multipart/alternative':
                    return part_body

        return body

    def list_labels(self, user_id='me'):
        """Lists labels in the user's mailbox."""
        if not self.service and not self.sandbox_mode:
            self.authenticate()

        if self.sandbox_mode:
            print("Running in Sandbox Mode: Returning simulated labels.")
            return self.persistence.get('labels', [
                {'name': 'INBOX'}, {'name': 'SPAM'}, {'name': 'TRASH'}
            ])

        try:
            results = self.service.users().labels().list(userId=user_id).execute()
            return results.get('labels', [])
        except HttpError as error:
            print(f"An error occurred while listing labels: {error}")
            return []
