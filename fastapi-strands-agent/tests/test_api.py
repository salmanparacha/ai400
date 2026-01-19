"""
Tests for the FastAPI Strands Agent API.

These tests mock the AgentPool to avoid actual model calls.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_agent_pool():
    """Mock the agent pool to return a mock agent."""
    with patch("app.main.agent_pool") as mock_pool:
        # Mock the agent
        agent_mock = MagicMock()
        agent_mock.invoke_async = AsyncMock()
        agent_mock.invoke_async.return_value.message = {
            "content": [{"text": "Hello from Mock Agent"}]
        }

        # Mock pool methods
        mock_pool.get = AsyncMock(return_value=agent_mock)
        mock_pool.start = AsyncMock()
        mock_pool.stop = AsyncMock()
        mock_pool.remove = AsyncMock()
        mock_pool.active_sessions = 1
        mock_pool.session_ids = ["test_session"]

        yield mock_pool, agent_mock


@pytest.fixture
def client(mock_agent_pool):
    """Create test client with mocked agent pool."""
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """Test health check returns pool status."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_sessions" in data
    assert "sessions" in data


def test_chat_endpoint(client, mock_agent_pool):
    """Test chat endpoint calls agent and returns response."""
    mock_pool, agent_mock = mock_agent_pool

    payload = {
        "message": "Hello",
        "session_id": "test_session",
        "model_provider": "nova-lite",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello from Mock Agent"
    assert data["session_id"] == "test_session"

    # Verify pool.get was called with correct params
    mock_pool.get.assert_called_once_with("test_session", "nova-lite")

    # Verify agent.invoke_async was called
    agent_mock.invoke_async.assert_called_once_with("Hello")


def test_chat_with_anthropic_model(client, mock_agent_pool):
    """Test chat endpoint with different model provider."""
    mock_pool, _ = mock_agent_pool

    payload = {
        "message": "Think hard",
        "session_id": "test_session_2",
        "model_provider": "anthropic",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    mock_pool.get.assert_called_with("test_session_2", "anthropic")


def test_chat_strips_thinking_tags(client, mock_agent_pool):
    """Test that thinking tags are removed from response."""
    _, agent_mock = mock_agent_pool

    # Return response with thinking tags
    agent_mock.invoke_async.return_value.message = {
        "content": [{"text": "<thinking>internal thoughts</thinking>Clean response"}]
    }

    payload = {"message": "Test", "session_id": "test_session"}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "thinking" not in data["response"]
    assert data["response"] == "Clean response"


def test_delete_session(client, mock_agent_pool):
    """Test session deletion endpoint."""
    mock_pool, _ = mock_agent_pool

    response = client.delete("/session/my-session?provider=nova-lite")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "removed"
    assert data["session_id"] == "my-session"

    mock_pool.remove.assert_called_once_with("my-session", "nova-lite")


def test_chat_with_string_content(client, mock_agent_pool):
    """Test handling of string content in response."""
    _, agent_mock = mock_agent_pool

    # Return response with string content
    agent_mock.invoke_async.return_value.message = {"content": "Direct string response"}

    payload = {"message": "Test", "session_id": "test_session"}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Direct string response"


def test_chat_with_text_attribute(client, mock_agent_pool):
    """Test handling of content blocks with text attribute."""
    _, agent_mock = mock_agent_pool

    # Create mock block with text attribute
    mock_block = MagicMock()
    mock_block.text = "Response from text attribute"

    agent_mock.invoke_async.return_value.message = {"content": [mock_block]}

    payload = {"message": "Test", "session_id": "test_session"}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Response from text attribute"
