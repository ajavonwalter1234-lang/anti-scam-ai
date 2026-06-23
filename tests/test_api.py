import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Generation API is running" in response.json()["message"]

@patch("main.generate_media.delay")
def test_generate_endpoint_success(mock_delay):
    # Mocking Celery task delay method
    mock_task = MagicMock()
    mock_task.id = "test-task-id"
    mock_delay.return_value = mock_task

    payload = {
        "prompt": "A futuristic city at sunset",
        "generation_type": "image",
        "aspect_ratio": "16:9"
    }

    response = client.post("/api/v1/generate", json=payload)

    assert response.status_code == 202
    assert response.json()["task_id"] == "test-task-id"
    assert response.json()["status"] == "PENDING"
    mock_delay.assert_called_once_with(
        prompt="A futuristic city at sunset",
        gen_type="image",
        aspect_ratio="16:9"
    )

def test_generate_endpoint_invalid_payload():
    payload = {
        "prompt": "ab", # Too short (min_length=3)
        "generation_type": "invalid_type",
        "aspect_ratio": "invalid"
    }
    response = client.post("/api/v1/generate", json=payload)
    assert response.status_code == 422

@patch("main.AsyncResult")
def test_status_endpoint_pending(mock_async_result):
    mock_result = MagicMock()
    mock_result.state = "PENDING"
    mock_async_result.return_value = mock_result

    response = client.get("/api/v1/status/test-task-id")

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"
    assert response.json()["task_id"] == "test-task-id"

@patch("main.AsyncResult")
def test_status_endpoint_processing(mock_async_result):
    mock_result = MagicMock()
    mock_result.state = "PROCESSING"
    mock_result.info = {"progress": 40}
    mock_async_result.return_value = mock_result

    response = client.get("/api/v1/status/test-task-id")

    assert response.status_code == 200
    assert response.json()["status"] == "PROCESSING"
    assert response.json()["progress"] == 40

@patch("main.AsyncResult")
def test_status_endpoint_success(mock_async_result):
    mock_result = MagicMock()
    mock_result.state = "SUCCESS"
    mock_result.result = {"url": "http://cdn.com/output.png"}
    mock_async_result.return_value = mock_result

    response = client.get("/api/v1/status/test-task-id")

    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
    assert response.json()["result"]["url"] == "http://cdn.com/output.png"
