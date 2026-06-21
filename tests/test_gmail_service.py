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

def test_sandbox_mode():
    service = GmailService(sandbox_mode=True)

    # Test list_labels in sandbox
    labels = service.list_labels()
    assert any(l['name'] == 'INBOX' for l in labels)

    # Test list_messages in sandbox
    messages = service.list_messages(max_results=5)
    assert len(messages) == 5
    assert messages[0]['id'] == 'sim_0'

    # Test get_message in sandbox
    message = service.get_message('sim_0')
    assert 'sim_0' in message['snippet']
    body = service.get_message_body(message)
    assert "Full body of simulated message sim_0." in body

@patch('src.gmail_service.build')
@patch('src.gmail_service.Credentials')
def test_manual_access_token(mock_creds_class, mock_build):
    token = "ya29.fake-token"
    service = GmailService(access_token=token)

    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds_class.return_value = mock_creds

    service.authenticate()

    mock_creds_class.assert_called_once_with(token)
    mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
