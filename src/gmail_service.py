import os.path
import base64
import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailService:
    """A service class to interact with the Gmail API."""

    def __init__(self, credentials_path=None, token_path=None, scopes=None, config_path='config.yaml'):
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
        self.service = None

    def authenticate(self):
        """Authenticates the user and returns the Gmail API service object."""
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}. "
                                            "Please refer to README.md for instructions on how to obtain it.")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            return self.service
        except HttpError as error:
            print(f"An error occurred during service creation: {error}")
            raise

    def list_messages(self, user_id='me', query='', max_results=10):
        """Lists messages in the user's mailbox matching the query."""
        if not self.service:
            self.authenticate()

        try:
            results = self.service.users().messages().list(userId=user_id, q=query, maxResults=max_results).execute()
            return results.get('messages', [])
        except HttpError as error:
            print(f"An error occurred while listing messages: {error}")
            return []

    def get_message(self, message_id, user_id='me', format='full'):
        """Gets a specific message by ID."""
        if not self.service:
            self.authenticate()

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
        if not self.service:
            self.authenticate()

        try:
            results = self.service.users().labels().list(userId=user_id).execute()
            return results.get('labels', [])
        except HttpError as error:
            print(f"An error occurred while listing labels: {error}")
            return []
