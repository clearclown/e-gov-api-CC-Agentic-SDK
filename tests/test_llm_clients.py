"""Unit tests for LLM client adapters

Tests for the base LLM client interface and all provider-specific adapters.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.llm import create_llm_client, BaseLLMClient
from app.services.llm.anthropic_client import AnthropicClient
from app.services.llm.deepseek_client import DeepSeekClient
from app.services.llm.gemini_client import GeminiClient


class TestLLMClientFactory:
    """Test the LLM client factory function"""

    def test_create_anthropic_client(self):
        """Test creating an Anthropic client"""
        client = create_llm_client(
            provider="anthropic",
            api_key="test-key",
            model="claude-3-5-sonnet-20241022"
        )
        assert isinstance(client, AnthropicClient)
        assert client.provider_name == "anthropic"
        assert client.model == "claude-3-5-sonnet-20241022"

    def test_create_deepseek_client(self):
        """Test creating a DeepSeek client"""
        client = create_llm_client(
            provider="deepseek",
            api_key="test-key",
            model="deepseek-chat"
        )
        assert isinstance(client, DeepSeekClient)
        assert client.provider_name == "deepseek"
        assert client.model == "deepseek-chat"

    def test_create_gemini_client(self):
        """Test creating a Gemini client"""
        client = create_llm_client(
            provider="gemini",
            api_key="test-key",
            model="gemini-2.0-flash-exp"
        )
        assert isinstance(client, GeminiClient)
        assert client.provider_name == "gemini"
        assert client.model == "gemini-2.0-flash-exp"

    def test_invalid_provider(self):
        """Test that invalid provider raises ValueError"""
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_llm_client(
                provider="invalid-provider",
                api_key="test-key"
            )

    def test_default_models(self):
        """Test that default models are used when not specified"""
        # Test Anthropic default
        anthropic_client = create_llm_client(provider="anthropic", api_key="test-key")
        assert anthropic_client.model == "claude-3-5-sonnet-20241022"

        # Test DeepSeek default
        deepseek_client = create_llm_client(provider="deepseek", api_key="test-key")
        assert deepseek_client.model == "deepseek-chat"

        # Test Gemini default
        gemini_client = create_llm_client(provider="gemini", api_key="test-key")
        assert gemini_client.model == "gemini-2.0-flash-exp"


class TestAnthropicClient:
    """Test Anthropic Claude client"""

    @pytest.fixture
    def client(self):
        """Create a test Anthropic client"""
        return AnthropicClient(
            api_key="test-key",
            model="claude-3-5-sonnet-20241022",
            system_prompt="Test prompt"
        )

    def test_initialization(self, client):
        """Test client initialization"""
        assert client.api_key == "test-key"
        assert client.model == "claude-3-5-sonnet-20241022"
        assert client.system_prompt == "Test prompt"
        assert client.provider_name == "anthropic"

    @pytest.mark.asyncio
    async def test_connect(self, client):
        """Test connection (should not raise error)"""
        if client._client:
            await client.connect()
            # If SDK available, should connect without error
            assert True
        else:
            # If SDK not available, should still not raise error
            await client.connect()
            assert True


class TestDeepSeekClient:
    """Test DeepSeek AI client"""

    @pytest.fixture
    def client(self):
        """Create a test DeepSeek client"""
        return DeepSeekClient(
            api_key="test-key",
            model="deepseek-chat",
            system_prompt="Test prompt"
        )

    def test_initialization(self, client):
        """Test client initialization"""
        assert client.api_key == "test-key"
        assert client.model == "deepseek-chat"
        assert client.system_prompt == "Test prompt"
        assert client.provider_name == "deepseek"

    @pytest.mark.asyncio
    async def test_connect(self, client):
        """Test connection (should not raise error)"""
        await client.connect()
        assert True


class TestGeminiClient:
    """Test Google Gemini client"""

    @pytest.fixture
    def client(self):
        """Create a test Gemini client"""
        return GeminiClient(
            api_key="test-key",
            model="gemini-2.0-flash-exp",
            system_prompt="Test prompt"
        )

    def test_initialization(self, client):
        """Test client initialization"""
        assert client.api_key == "test-key"
        assert client.model == "gemini-2.0-flash-exp"
        assert client.system_prompt == "Test prompt"
        assert client.provider_name == "gemini"

    @pytest.mark.asyncio
    async def test_connect(self, client):
        """Test connection (should not raise error)"""
        await client.connect()
        assert True


class TestBaseLLMClientInterface:
    """Test that all clients implement the base interface correctly"""

    @pytest.mark.parametrize("provider,client_class", [
        ("anthropic", AnthropicClient),
        ("deepseek", DeepSeekClient),
        ("gemini", GeminiClient),
    ])
    def test_client_implements_interface(self, provider, client_class):
        """Test that each client implements BaseLLMClient interface"""
        client = create_llm_client(provider=provider, api_key="test-key")
        assert isinstance(client, BaseLLMClient)
        assert isinstance(client, client_class)

        # Check required methods exist
        assert hasattr(client, 'connect')
        assert hasattr(client, 'query')
        assert hasattr(client, 'receive_response')
        assert hasattr(client, 'disconnect')
        assert hasattr(client, 'provider_name')

        # Check provider_name is correctly set
        assert client.provider_name == provider
