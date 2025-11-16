"""Integration tests for Agent Service

Tests the AgentService with multi-LLM provider support.
"""

import pytest
from app.services.agent_service import AgentService, get_agent_service


class TestAgentServiceInitialization:
    """Test Agent Service initialization with different providers"""

    def test_create_anthropic_service(self):
        """Test creating service with Anthropic provider"""
        service = AgentService(provider="anthropic", api_key="test-key")
        assert service.provider == "anthropic"
        assert service.sessions == {}

    def test_create_deepseek_service(self):
        """Test creating service with DeepSeek provider"""
        service = AgentService(provider="deepseek", api_key="test-key")
        assert service.provider == "deepseek"
        assert service.sessions == {}

    def test_create_gemini_service(self):
        """Test creating service with Gemini provider"""
        service = AgentService(provider="gemini", api_key="test-key")
        assert service.provider == "gemini"
        assert service.sessions == {}

    def test_default_provider(self):
        """Test default provider when not specified"""
        service = AgentService(api_key="test-key")
        assert service.provider in ["anthropic", "deepseek", "gemini"]

    def test_missing_api_key(self):
        """Test service creation without API key"""
        service = AgentService(provider="anthropic")
        # Should create service but with mock client
        assert service.provider == "anthropic"
        assert service._client is None


class TestAgentServiceSessionManagement:
    """Test session management functionality"""

    @pytest.fixture
    def service(self):
        """Create a test service"""
        return AgentService(provider="anthropic", api_key="test-key")

    @pytest.mark.asyncio
    async def test_create_session(self, service):
        """Test creating a new session"""
        session_id = await service.create_session()

        assert isinstance(session_id, str)
        assert len(session_id) > 0
        assert session_id in service.sessions

        session_data = service.sessions[session_id]
        assert session_data["id"] == session_id
        assert "created_at" in session_data
        assert session_data["messages"] == []
        assert session_data["provider"] == "anthropic"

    @pytest.mark.asyncio
    async def test_create_session_with_provider(self, service):
        """Test creating session with explicit provider"""
        session_id = await service.create_session(provider="deepseek")

        session_data = service.sessions[session_id]
        assert session_data["provider"] == "deepseek"

    @pytest.mark.asyncio
    async def test_get_session(self, service):
        """Test retrieving session data"""
        # Create a session
        session_id = await service.create_session()

        # Retrieve it
        session_data = await service.get_session(session_id)

        assert session_data is not None
        assert session_data["id"] == session_id
        assert "created_at" in session_data
        assert "messages" in session_data

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, service):
        """Test retrieving non-existent session"""
        session_data = await service.get_session("nonexistent-id")
        assert session_data is None


class TestGetAgentServiceFactory:
    """Test the get_agent_service factory function"""

    def test_get_default_service(self):
        """Test getting service with default provider"""
        service = get_agent_service()
        assert isinstance(service, AgentService)

    def test_get_anthropic_service(self):
        """Test getting Anthropic service"""
        service = get_agent_service("anthropic")
        assert isinstance(service, AgentService)
        assert service.provider == "anthropic"

    def test_get_deepseek_service(self):
        """Test getting DeepSeek service"""
        service = get_agent_service("deepseek")
        assert isinstance(service, AgentService)
        assert service.provider == "deepseek"

    def test_get_gemini_service(self):
        """Test getting Gemini service"""
        service = get_agent_service("gemini")
        assert isinstance(service, AgentService)
        assert service.provider == "gemini"

    def test_service_caching(self):
        """Test that services are cached per provider"""
        service1 = get_agent_service("anthropic")
        service2 = get_agent_service("anthropic")

        # Should return the same instance
        assert service1 is service2

    def test_different_providers_different_instances(self):
        """Test that different providers get different instances"""
        service1 = get_agent_service("anthropic")
        service2 = get_agent_service("deepseek")

        assert service1 is not service2
        assert service1.provider == "anthropic"
        assert service2.provider == "deepseek"
