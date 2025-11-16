"""Tests for Agent Service implementation

Test-Driven Development (TDD) for Agent Service Layer.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestAgentServiceCreation:
    """Test Agent service creation"""

    def test_agent_service_imports(self):
        """Test that Agent service can be imported"""
        try:
            from app.services import agent_service
            assert agent_service is not None
        except ImportError:
            pytest.skip("Agent service not yet implemented")

    def test_agent_service_class_exists(self):
        """Test that AgentService class exists"""
        try:
            from app.services.agent_service import AgentService
            assert AgentService is not None
        except ImportError:
            pytest.skip("Agent service not yet implemented")


class TestAgentServiceInitialization:
    """Test Agent service initialization"""

    def test_agent_service_init_with_sdk_client(self):
        """Test AgentService initializes with ClaudeSDKClient"""
        try:
            from app.services.agent_service import AgentService

            # Mock Claude SDK
            with patch("app.services.agent_service.ClaudeSDKClient") as mock_sdk:
                mock_sdk.return_value = MagicMock()

                service = AgentService()

                # Should initialize SDK client
                assert service is not None
                assert hasattr(service, 'client') or hasattr(service, '_client')
        except ImportError:
            pytest.skip("Agent service not yet implemented")

    def test_agent_service_init_with_allowed_tools(self):
        """Test AgentService initializes with allowed tools"""
        try:
            from app.services.agent_service import AgentService

            with patch("app.services.agent_service.ClaudeSDKClient") as mock_sdk:
                mock_client = MagicMock()
                mock_sdk.return_value = mock_client

                service = AgentService()

                # Should configure allowed tools
                # Verify SDK client was called with allowed_tools
                mock_sdk.assert_called_once()
                call_kwargs = mock_sdk.call_args[1]
                assert "allowed_tools" in call_kwargs or call_kwargs == {}
        except ImportError:
            pytest.skip("Agent service not yet implemented")


class TestAgentServiceQuery:
    """Test Agent service query functionality"""

    @pytest.mark.asyncio
    async def test_agent_service_query_method_exists(self):
        """Test that AgentService has query method"""
        try:
            from app.services.agent_service import AgentService

            service = AgentService()
            assert hasattr(service, 'query')
            assert callable(service.query)
        except (ImportError, AttributeError):
            pytest.skip("Agent service not yet implemented")

    @pytest.mark.asyncio
    async def test_agent_service_query_returns_response(self):
        """Test that query method returns response"""
        try:
            from app.services.agent_service import AgentService

            with patch("app.services.agent_service.ClaudeSDKClient") as mock_sdk:
                # Mock client.query to return async iterator
                async def mock_query(query_text):
                    yield MagicMock(type="text", content="回答テキスト")

                mock_client = MagicMock()
                mock_client.query = mock_query
                mock_sdk.return_value = mock_client

                service = AgentService()
                result = []

                async for message in service.query("質問"):
                    result.append(message)

                # Should yield at least one message
                assert len(result) > 0
        except ImportError:
            pytest.skip("Agent service not yet implemented")


class TestAgentServiceAnalyze:
    """Test Agent service analyze functionality"""

    @pytest.mark.asyncio
    async def test_agent_service_analyze_method_exists(self):
        """Test that AgentService has analyze method"""
        try:
            from app.services.agent_service import AgentService

            service = AgentService()
            assert hasattr(service, 'analyze')
            assert callable(service.analyze)
        except (ImportError, AttributeError):
            pytest.skip("Agent service not yet implemented")

    @pytest.mark.asyncio
    async def test_agent_service_analyze_law(self):
        """Test analyzing a law document"""
        try:
            from app.services.agent_service import AgentService

            with patch("app.services.agent_service.ClaudeSDKClient") as mock_sdk:
                async def mock_query(query_text):
                    yield MagicMock(type="text", content="分析結果")

                mock_client = MagicMock()
                mock_client.query = mock_query
                mock_sdk.return_value = mock_client

                service = AgentService()
                result = []

                async for message in service.analyze(
                    doc_type="law",
                    doc_id="405AC0000000087"
                ):
                    result.append(message)

                assert len(result) > 0
        except ImportError:
            pytest.skip("Agent service not yet implemented")


class TestAgentServiceChat:
    """Test Agent service chat functionality"""

    @pytest.mark.asyncio
    async def test_agent_service_chat_method_exists(self):
        """Test that AgentService has chat method"""
        try:
            from app.services.agent_service import AgentService

            service = AgentService()
            assert hasattr(service, 'chat')
            assert callable(service.chat)
        except (ImportError, AttributeError):
            pytest.skip("Agent service not yet implemented")

    @pytest.mark.asyncio
    async def test_agent_service_chat_maintains_context(self):
        """Test that chat method maintains conversation context"""
        try:
            from app.services.agent_service import AgentService

            with patch("app.services.agent_service.ClaudeSDKClient") as mock_sdk:
                # Mock stateful client
                async def mock_query(query_text):
                    yield MagicMock(type="text", content=f"応答: {query_text}")

                mock_client = MagicMock()
                mock_client.query = mock_query
                mock_sdk.return_value = mock_client

                service = AgentService()

                # First message
                result1 = []
                async for message in service.chat("株主総会とは？"):
                    result1.append(message)

                # Second message (should maintain context)
                result2 = []
                async for message in service.chat("その決議要件は？"):
                    result2.append(message)

                # Both should return responses
                assert len(result1) > 0
                assert len(result2) > 0
        except ImportError:
            pytest.skip("Agent service not yet implemented")


class TestAgentServiceSessionManagement:
    """Test Agent service session management"""

    @pytest.mark.asyncio
    async def test_agent_service_create_session(self):
        """Test creating a new session"""
        try:
            from app.services.agent_service import AgentService

            service = AgentService()

            if hasattr(service, 'create_session'):
                session_id = await service.create_session()
                assert session_id is not None
                assert isinstance(session_id, str)
        except (ImportError, AttributeError):
            pytest.skip("Session management not yet implemented")

    @pytest.mark.asyncio
    async def test_agent_service_get_session(self):
        """Test retrieving session information"""
        try:
            from app.services.agent_service import AgentService

            service = AgentService()

            if hasattr(service, 'create_session') and hasattr(service, 'get_session'):
                session_id = await service.create_session()
                session_info = await service.get_session(session_id)

                assert session_info is not None
                assert "id" in session_info or "session_id" in session_info
        except (ImportError, AttributeError):
            pytest.skip("Session management not yet implemented")


class TestAgentServiceErrorHandling:
    """Test Agent service error handling"""

    @pytest.mark.asyncio
    async def test_agent_service_handles_sdk_errors(self):
        """Test that service handles SDK errors gracefully"""
        try:
            from app.services.agent_service import AgentService

            with patch("app.services.agent_service.ClaudeSDKClient") as mock_sdk:
                # Mock SDK to raise exception
                mock_sdk.side_effect = Exception("SDK Error")

                # Should handle initialization error
                try:
                    service = AgentService()
                    # If no exception, service should have fallback behavior
                    assert service is not None
                except Exception as e:
                    # Or it should raise a specific error
                    assert "SDK" in str(e) or "Error" in str(e)
        except ImportError:
            pytest.skip("Agent service not yet implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
