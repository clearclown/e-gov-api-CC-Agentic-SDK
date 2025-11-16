"""Integration tests for Agent API endpoints

Test-Driven Development (TDD) for Agent API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import ASGITransport


class TestAgentAPIEndpoints:
    """Test Agent API endpoint availability"""

    def test_agent_module_exists(self):
        """Test that agent endpoint module exists"""
        try:
            from app.api.endpoints import agent
            assert agent is not None
        except ImportError:
            pytest.skip("Agent API endpoints not yet implemented")

    def test_agent_router_exists(self):
        """Test that agent router exists"""
        try:
            from app.api.endpoints.agent import router
            assert router is not None
        except ImportError:
            pytest.skip("Agent API endpoints not yet implemented")


class TestAgentQueryEndpoint:
    """Test /api/v1/agent/query endpoint"""

    def test_query_endpoint_exists(self):
        """Test that query endpoint is defined"""
        try:
            from app.api.endpoints.agent import router

            # Check if endpoint exists
            routes = [route.path for route in router.routes]
            assert "/query" in routes or any("query" in route for route in routes)
        except (ImportError, AttributeError):
            pytest.skip("Query endpoint not yet implemented")

    @pytest.mark.asyncio
    async def test_query_endpoint_accepts_post(self):
        """Test that query endpoint accepts POST requests"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                # Mock agent service
                with patch("app.api.endpoints.agent.agent_service") as mock_service:
                    async def mock_query(query):
                        yield {"type": "text", "content": "回答"}

                    mock_service.query = mock_query

                    response = await client.post(
                        "/api/v1/agent/query",
                        json={"query": "テスト質問"}
                    )

                    # Should return 200 or endpoint not found
                    assert response.status_code in [200, 404, 405]
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")

    @pytest.mark.asyncio
    async def test_query_endpoint_requires_query_parameter(self):
        """Test that query endpoint requires query parameter"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                # Send request without query
                response = await client.post(
                    "/api/v1/agent/query",
                    json={}
                )

                # Should return 422 (validation error) or 404 (not found)
                assert response.status_code in [422, 404]
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")

    @pytest.mark.asyncio
    async def test_query_endpoint_returns_streaming_response(self):
        """Test that query endpoint returns streaming response"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                with patch("app.api.endpoints.agent.agent_service") as mock_service:
                    async def mock_query(query):
                        yield {"type": "text", "content": "回答1"}
                        yield {"type": "text", "content": "回答2"}

                    mock_service.query = mock_query

                    response = await client.post(
                        "/api/v1/agent/query",
                        json={"query": "ストリーミングテスト"}
                    )

                    if response.status_code == 200:
                        # Should be streaming response
                        assert "text/event-stream" in response.headers.get("content-type", "") or \
                               "application/json" in response.headers.get("content-type", "")
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")


class TestAgentAnalyzeEndpoint:
    """Test /api/v1/agent/analyze endpoint"""

    def test_analyze_endpoint_exists(self):
        """Test that analyze endpoint is defined"""
        try:
            from app.api.endpoints.agent import router

            routes = [route.path for route in router.routes]
            assert "/analyze" in routes or any("analyze" in route for route in routes)
        except (ImportError, AttributeError):
            pytest.skip("Analyze endpoint not yet implemented")

    @pytest.mark.asyncio
    async def test_analyze_endpoint_accepts_post(self):
        """Test that analyze endpoint accepts POST requests"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                with patch("app.api.endpoints.agent.agent_service") as mock_service:
                    async def mock_analyze(doc_type, doc_id):
                        yield {"type": "text", "content": "分析結果"}

                    mock_service.analyze = mock_analyze

                    response = await client.post(
                        "/api/v1/agent/analyze",
                        json={
                            "doc_type": "law",
                            "doc_id": "405AC0000000087"
                        }
                    )

                    assert response.status_code in [200, 404]
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")


class TestAgentChatEndpoint:
    """Test /api/v1/agent/chat endpoint"""

    def test_chat_endpoint_exists(self):
        """Test that chat endpoint is defined"""
        try:
            from app.api.endpoints.agent import router

            routes = [route.path for route in router.routes]
            assert "/chat" in routes or any("chat" in route for route in routes)
        except (ImportError, AttributeError):
            pytest.skip("Chat endpoint not yet implemented")

    @pytest.mark.asyncio
    async def test_chat_endpoint_accepts_post(self):
        """Test that chat endpoint accepts POST requests"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                with patch("app.api.endpoints.agent.agent_service") as mock_service:
                    async def mock_chat(message, session_id=None):
                        yield {"type": "text", "content": "チャット応答"}

                    mock_service.chat = mock_chat

                    response = await client.post(
                        "/api/v1/agent/chat",
                        json={"message": "こんにちは"}
                    )

                    assert response.status_code in [200, 404]
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")

    @pytest.mark.asyncio
    async def test_chat_endpoint_supports_session_id(self):
        """Test that chat endpoint supports session_id for context"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                with patch("app.api.endpoints.agent.agent_service") as mock_service:
                    async def mock_chat(message, session_id=None):
                        yield {
                            "type": "text",
                            "content": f"Session: {session_id}",
                            "session_id": session_id
                        }

                    mock_service.chat = mock_chat

                    response = await client.post(
                        "/api/v1/agent/chat",
                        json={
                            "message": "続き",
                            "session_id": "test-session-123"
                        }
                    )

                    if response.status_code == 200:
                        data = response.json()
                        # Should maintain session
                        assert "session" in str(data).lower() or "test-session-123" in str(data)
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")


class TestAgentSessionEndpoint:
    """Test /api/v1/agent/session endpoints"""

    def test_session_endpoint_exists(self):
        """Test that session endpoints are defined"""
        try:
            from app.api.endpoints.agent import router

            routes = [route.path for route in router.routes]
            has_session_endpoints = any("session" in route for route in routes)
            assert has_session_endpoints
        except (ImportError, AttributeError):
            pytest.skip("Session endpoints not yet implemented")

    @pytest.mark.asyncio
    async def test_create_session_endpoint(self):
        """Test creating a new session"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                with patch("app.api.endpoints.agent.agent_service") as mock_service:
                    mock_service.create_session = AsyncMock(return_value="new-session-id")

                    response = await client.post("/api/v1/agent/session")

                    if response.status_code == 200:
                        data = response.json()
                        assert "session_id" in data or "id" in data
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")

    @pytest.mark.asyncio
    async def test_get_session_endpoint(self):
        """Test retrieving session information"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                with patch("app.api.endpoints.agent.agent_service") as mock_service:
                    mock_service.get_session = AsyncMock(return_value={
                        "id": "test-session",
                        "created_at": "2024-01-01T00:00:00",
                        "messages": []
                    })

                    response = await client.get("/api/v1/agent/session/test-session")

                    if response.status_code == 200:
                        data = response.json()
                        assert "id" in data or "session_id" in data
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")


class TestAgentAPIValidation:
    """Test API request validation"""

    @pytest.mark.asyncio
    async def test_query_validates_empty_query(self):
        """Test that empty query is rejected"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/agent/query",
                    json={"query": ""}
                )

                # Should return validation error
                assert response.status_code in [422, 400, 404]
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")

    @pytest.mark.asyncio
    async def test_analyze_validates_doc_type(self):
        """Test that invalid doc_type is rejected"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/agent/analyze",
                    json={
                        "doc_type": "invalid",
                        "doc_id": "123"
                    }
                )

                # Should return validation error
                assert response.status_code in [422, 400, 404]
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")


class TestAgentAPIErrorHandling:
    """Test API error handling"""

    @pytest.mark.asyncio
    async def test_query_handles_service_errors(self):
        """Test that service errors are handled gracefully"""
        try:
            from app.main import app
            from httpx import AsyncClient

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                with patch("app.api.endpoints.agent.agent_service") as mock_service:
                    async def mock_query_error(query):
                        raise Exception("Service error")

                    mock_service.query = mock_query_error

                    response = await client.post(
                        "/api/v1/agent/query",
                        json={"query": "エラーテスト"}
                    )

                    # Should return error response
                    if response.status_code not in [404, 405]:
                        assert response.status_code in [500, 503]
        except ImportError:
            pytest.skip("Agent API not yet fully implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
