import pytest
import base64
from unittest.mock import MagicMock, patch
from src.gmail_service import GmailService

@pytest.fixture
def gmail_service():
    return GmailService(credentials_path='mock_creds.json', token_path='mock_token.json')

def test_get_message_body_plain_text(gmail_service):
    message = {
        'payload': {
            'mimeType': 'text/plain',
            'body': {
                'data': base64.urlsafe_b64encode(b"Hello World").decode('utf-8')
            }
        }
    }
    body = gmail_service.get_message_body(message)
    assert body == "Hello World"

def test_get_message_body_multipart(gmail_service):
    message = {
        'payload': {
            'mimeType': 'multipart/mixed',
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {
                        'data': base64.urlsafe_b64encode(b"Hello Multipart").decode('utf-8')
                    }
                },
                {
                    'mimeType': 'text/html',
                    'body': {
                        'data': base64.urlsafe_b64encode(b"<html></html>").decode('utf-8')
                    }
                }
            ]
        }
    }
    body = gmail_service.get_message_body(message)
    assert body == "Hello Multipart"

def test_get_message_body_nested(gmail_service):
    message = {
        'payload': {
            'mimeType': 'multipart/mixed',
            'parts': [
                {
                    'mimeType': 'multipart/alternative',
                    'parts': [
                        {
                            'mimeType': 'text/plain',
                            'body': {
                                'data': base64.urlsafe_b64encode(b"Nested Body").decode('utf-8')
                            }
                        }
                    ]
                }
            ]
        }
    }
    body = gmail_service.get_message_body(message)
    assert body == "Nested Body"

@patch('src.gmail_service.build')
@patch('src.gmail_service.Credentials')
@patch('os.path.exists')
def test_authenticate_existing_token(mock_exists, mock_creds_class, mock_build, gmail_service):
    mock_exists.return_value = True
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds_class.from_authorized_user_file.return_value = mock_creds

    gmail_service.authenticate()

    mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)

@patch('src.gmail_service.build')
def test_list_messages(mock_build, gmail_service):
    mock_service = MagicMock()
    gmail_service.service = mock_service

    mock_messages = [{'id': '123'}, {'id': '456'}]
    # Set up the chain: service.users().messages().list().execute()
    mock_list_call = mock_service.users().messages().list
    mock_list_call.return_value.execute.return_value = {'messages': mock_messages}

    messages = gmail_service.list_messages()

    assert messages == mock_messages
    mock_list_call.assert_called_once_with(userId='me', q='', maxResults=10)

@patch('src.gmail_service.build')
def test_authenticate_with_access_token_override(mock_build, gmail_service):
    # Test with access_token_override in authenticate()
    mock_token = "test_override_token"
    gmail_service.authenticate(access_token_override=mock_token)

    args, kwargs = mock_build.call_args
    assert kwargs['credentials'].token == mock_token

@patch('src.gmail_service.requests.post')
@patch('src.gmail_service.time.sleep', return_value=None)
@patch('src.gmail_service.build')
def test_authenticate_device_flow_success(mock_build, mock_sleep, mock_requests_post, gmail_service):
    # Mock credentials.json
    mock_creds_json = '{"installed": {"client_id": "id", "client_secret": "secret"}}'

    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = mock_creds_json
        with patch('os.path.exists', return_value=True):

            # Response for device code request
            mock_resp_code = MagicMock()
            mock_resp_code.status_code = 200
            mock_resp_code.json.return_value = {
                'device_code': 'dev_123',
                'user_code': 'ABC-DEF',
                'verification_url': 'https://google.com/device',
                'interval': 1,
                'expires_in': 100
            }

            # Response for token polling (success)
            mock_resp_token = MagicMock()
            mock_resp_token.status_code = 200
            mock_resp_token.json.return_value = {
                'access_token': 'access_123',
                'refresh_token': 'refresh_123'
            }

            mock_requests_post.side_effect = [mock_resp_code, mock_resp_token]

            creds = gmail_service.authenticate_device_flow()

            assert creds.token == 'access_123'
            assert creds.refresh_token == 'refresh_123'
            assert mock_requests_post.call_count == 2

@patch('src.gmail_service.InstalledAppFlow.from_client_secrets_file')
@patch('src.gmail_service.build')
def test_authenticate_fallback_to_device_flow(mock_build, mock_flow_class, gmail_service):
    # Standard flow raises exception
    mock_flow = MagicMock()
    mock_flow.run_local_server.side_effect = Exception("Port blocked")
    mock_flow_class.return_value = mock_flow

    # Need to mock os.path.exists for BOTH credentials and token checks
    # authenticate() checks token_path first, then credentials_path
    with patch('os.path.exists') as mock_exists:
        # 1st call: self.token_path (os.path.exists(self.token_path)) -> False
        # 2nd call: self.credentials_path (in authenticate_device_flow) -> True
        mock_exists.side_effect = lambda path: path == 'mock_creds.json'

        with patch.object(GmailService, 'authenticate_device_flow') as mock_device_auth:
            mock_creds = MagicMock()
            mock_creds.to_json.return_value = '{"token": "fake"}'
            mock_device_auth.return_value = mock_creds

            with patch('builtins.open', create=True):
                gmail_service.authenticate()

            mock_device_auth.assert_called_once()
            mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)

def test_list_messages_sandbox_mode():
    service = GmailService(sandbox_mode=True)
    messages = service.list_messages()
    assert len(messages) == 2
    assert messages[0]['id'] == 'msg_1'

def test_get_message_sandbox_mode():
    service = GmailService(sandbox_mode=True)
    message = service.get_message('msg_1')
    assert message['id'] == 'msg_1'
    assert 'Urgent' in message['snippet']

def test_authenticate_fallback_to_sandbox(gmail_service):
    # Mocking build to raise an exception to trigger fallback
    with patch('src.gmail_service.build', side_effect=Exception("Network Error")):
        with patch('os.path.exists', return_value=True):
            with patch('src.gmail_service.Credentials.from_authorized_user_file') as mock_creds:
                mock_creds.return_value.valid = True
                service = gmail_service.authenticate()
                assert service is None
                assert gmail_service.sandbox_mode is True

def test_sign_in_as_guest():
    service = GmailService()
    assert service.sandbox_mode is False
    service.sign_in_as_guest()
    assert service.sandbox_mode is True

@patch('src.gmail_service.build')
def test_authenticate_with_constructor_access_token(mock_build):
    # Test with access_token in constructor
    mock_token = "constructor_token"
    service = GmailService(access_token=mock_token)
    service.authenticate()

    args, kwargs = mock_build.call_args
    assert kwargs['credentials'].token == mock_token
