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
