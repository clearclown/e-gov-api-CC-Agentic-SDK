"""API endpoint tests for Agent endpoints

Tests the FastAPI agent endpoints with multi-LLM provider support.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.services.agent_service import AgentService


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_agent_service():
    """Create a mock agent service"""
    service = MagicMock(spec=AgentService)
    service.provider = "anthropic"
    service.sessions = {}

    # Mock async methods
    service.create_session = AsyncMock(return_value="test-session-id")
    service.get_session = AsyncMock(return_value={
        "id": "test-session-id",
        "created_at": "2025-11-16T00:00:00",
        "messages": [],
        "provider": "anthropic"
    })

    # Mock streaming methods
    async def mock_query(query, provider=None):
        yield {"type": "text", "content": "Test response"}

    async def mock_analyze(doc_type, doc_id, provider=None):
        yield {"type": "text", "content": "Test analysis"}

    async def mock_chat(message, session_id=None, provider=None):
        yield {"type": "text", "content": "Test chat response"}
        yield {"type": "session_id", "content": session_id or "new-session-id"}

    service.query = mock_query
    service.analyze = mock_analyze
    service.chat = mock_chat

    return service


class TestQueryEndpoint:
    """Test /api/v1/agent/query endpoint"""

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_query_with_default_provider(self, mock_get_service, client, mock_agent_service):
        """Test query with default provider"""
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/query",
            json={"query": "What is labor law?"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json; charset=utf-8"

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_query_with_anthropic_provider(self, mock_get_service, client, mock_agent_service):
        """Test query with Anthropic provider"""
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/query",
            json={
                "query": "What is labor law?",
                "provider": "anthropic"
            }
        )

        assert response.status_code == 200
        mock_get_service.assert_called_once_with("anthropic")

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_query_with_deepseek_provider(self, mock_get_service, client, mock_agent_service):
        """Test query with DeepSeek provider"""
        mock_agent_service.provider = "deepseek"
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/query",
            json={
                "query": "What is labor law?",
                "provider": "deepseek"
            }
        )

        assert response.status_code == 200
        mock_get_service.assert_called_once_with("deepseek")

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_query_with_gemini_provider(self, mock_get_service, client, mock_agent_service):
        """Test query with Gemini provider"""
        mock_agent_service.provider = "gemini"
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/query",
            json={
                "query": "What is labor law?",
                "provider": "gemini"
            }
        )

        assert response.status_code == 200
        mock_get_service.assert_called_once_with("gemini")

    def test_query_empty_string(self, client):
        """Test query with empty string"""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": ""}
        )

        assert response.status_code == 422  # Validation error

    def test_query_whitespace_only(self, client):
        """Test query with whitespace only"""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "   "}
        )

        assert response.status_code == 422  # Validation error

    def test_query_invalid_provider(self, client):
        """Test query with invalid provider"""
        response = client.post(
            "/api/v1/agent/query",
            json={
                "query": "What is labor law?",
                "provider": "invalid-provider"
            }
        )

        assert response.status_code == 422  # Validation error


class TestAnalyzeEndpoint:
    """Test /api/v1/agent/analyze endpoint"""

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_analyze_law_document(self, mock_get_service, client, mock_agent_service):
        """Test analyzing a law document"""
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/analyze",
            json={
                "doc_type": "law",
                "doc_id": "123456"
            }
        )

        assert response.status_code == 200

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_analyze_case_document(self, mock_get_service, client, mock_agent_service):
        """Test analyzing a case document"""
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/analyze",
            json={
                "doc_type": "case",
                "doc_id": "ABC789"
            }
        )

        assert response.status_code == 200

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_analyze_with_provider(self, mock_get_service, client, mock_agent_service):
        """Test analyze with specific provider"""
        mock_agent_service.provider = "deepseek"
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/analyze",
            json={
                "doc_type": "law",
                "doc_id": "123456",
                "provider": "deepseek"
            }
        )

        assert response.status_code == 200
        mock_get_service.assert_called_once_with("deepseek")

    def test_analyze_invalid_doc_type(self, client):
        """Test analyze with invalid document type"""
        response = client.post(
            "/api/v1/agent/analyze",
            json={
                "doc_type": "invalid",
                "doc_id": "123456"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_analyze_missing_doc_id(self, client):
        """Test analyze without document ID"""
        response = client.post(
            "/api/v1/agent/analyze",
            json={"doc_type": "law"}
        )

        assert response.status_code == 422  # Validation error


class TestChatEndpoint:
    """Test /api/v1/agent/chat endpoint"""

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_chat_without_session(self, mock_get_service, client, mock_agent_service):
        """Test chat without existing session"""
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/chat",
            json={"message": "Hello, I need legal advice"}
        )

        assert response.status_code == 200

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_chat_with_session(self, mock_get_service, client, mock_agent_service):
        """Test chat with existing session"""
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/chat",
            json={
                "message": "Tell me more",
                "session_id": "test-session-id"
            }
        )

        assert response.status_code == 200

    @patch('app.api.endpoints.agent.get_agent_service')
    def test_chat_with_provider(self, mock_get_service, client, mock_agent_service):
        """Test chat with specific provider"""
        mock_agent_service.provider = "gemini"
        mock_get_service.return_value = mock_agent_service

        response = client.post(
            "/api/v1/agent/chat",
            json={
                "message": "Hello",
                "provider": "gemini"
            }
        )

        assert response.status_code == 200
        mock_get_service.assert_called_once_with("gemini")

    def test_chat_empty_message(self, client):
        """Test chat with empty message"""
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": ""}
        )

        assert response.status_code == 422  # Validation error

    def test_chat_whitespace_message(self, client):
        """Test chat with whitespace-only message"""
        response = client.post(
            "/api/v1/agent/chat",
            json={"message": "   "}
        )

        assert response.status_code == 422  # Validation error


class TestSessionEndpoints:
    """Test session management endpoints"""

    @patch('app.api.endpoints.agent.get_agent_service')
    @pytest.mark.asyncio
    async def test_create_session_default_provider(self, mock_get_service, client, mock_agent_service):
        """Test creating session with default provider"""
        mock_get_service.return_value = mock_agent_service

        response = client.post("/api/v1/agent/session")

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"] == "test-session-id"

    @patch('app.api.endpoints.agent.get_agent_service')
    @pytest.mark.asyncio
    async def test_create_session_with_provider(self, mock_get_service, client, mock_agent_service):
        """Test creating session with specific provider"""
        mock_agent_service.provider = "deepseek"
        mock_get_service.return_value = mock_agent_service

        response = client.post("/api/v1/agent/session?provider=deepseek")

        assert response.status_code == 200
        mock_get_service.assert_called_with("deepseek")

    @patch('app.api.endpoints.agent.get_agent_service')
    @pytest.mark.asyncio
    async def test_get_session_exists(self, mock_get_service, client, mock_agent_service):
        """Test retrieving existing session"""
        mock_get_service.return_value = mock_agent_service

        response = client.get("/api/v1/agent/session/test-session-id")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-session-id"
        assert "created_at" in data
        assert "messages" in data
        assert data["provider"] == "anthropic"

    @patch('app.api.endpoints.agent.get_agent_service')
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, mock_get_service, client, mock_agent_service):
        """Test retrieving non-existent session"""
        mock_agent_service.get_session = AsyncMock(return_value=None)
        mock_get_service.return_value = mock_agent_service

        response = client.get("/api/v1/agent/session/nonexistent-id")

        assert response.status_code == 404


class TestProviderValidation:
    """Test provider parameter validation across all endpoints"""

    @pytest.mark.parametrize("endpoint,method,payload", [
        ("/api/v1/agent/query", "POST", {"query": "test"}),
        ("/api/v1/agent/analyze", "POST", {"doc_type": "law", "doc_id": "123"}),
        ("/api/v1/agent/chat", "POST", {"message": "test"}),
    ])
    def test_invalid_provider_rejected(self, client, endpoint, method, payload):
        """Test that invalid providers are rejected"""
        payload["provider"] = "invalid-llm"

        if method == "POST":
            response = client.post(endpoint, json=payload)

        assert response.status_code == 422

    @pytest.mark.parametrize("endpoint,method,payload,provider", [
        ("/api/v1/agent/query", "POST", {"query": "test"}, "anthropic"),
        ("/api/v1/agent/query", "POST", {"query": "test"}, "deepseek"),
        ("/api/v1/agent/query", "POST", {"query": "test"}, "gemini"),
        ("/api/v1/agent/analyze", "POST", {"doc_type": "law", "doc_id": "123"}, "anthropic"),
        ("/api/v1/agent/chat", "POST", {"message": "test"}, "anthropic"),
    ])
    @patch('app.api.endpoints.agent.get_agent_service')
    def test_valid_providers_accepted(self, mock_get_service, client, endpoint, method, payload, provider, mock_agent_service):
        """Test that all valid providers are accepted"""
        mock_agent_service.provider = provider
        mock_get_service.return_value = mock_agent_service

        payload["provider"] = provider

        if method == "POST":
            response = client.post(endpoint, json=payload)

        assert response.status_code == 200
        mock_get_service.assert_called_with(provider)
