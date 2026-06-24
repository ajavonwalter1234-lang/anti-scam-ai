import os.path
import base64
import yaml
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

    def authenticate(self, access_token_override=None):
        """
        Authenticates the user and returns the Gmail API service object.
        Supports manual access token override to bypass QUIC protocol issues.
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
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}. "
                                                "Please refer to README.md for instructions on how to obtain it.")
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                    # Use a short timeout for the local server to simulate network constraints
                    creds = flow.run_local_server(port=0, timeout_seconds=10)

                if not token:
                    with open(self.token_path, 'w') as token_file:
                        token_file.write(creds.to_json())

            self.service = build('gmail', 'v1', credentials=creds)
            return self.service
        except Exception as error:
            print(f"Authentication failed: {error}")
            print("Encountered network or protocol issue. Falling back to Local Sandbox Mode.")
            self.enable_sandbox_mode()
            return None

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
