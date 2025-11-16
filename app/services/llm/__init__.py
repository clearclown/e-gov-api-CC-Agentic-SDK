"""LLM Client Factory

Provides factory functions for creating LLM clients based on provider name.
"""

from typing import Optional, Dict, Any
from app.services.llm.base import BaseLLMClient
from app.services.llm.anthropic_client import AnthropicClient
from app.services.llm.deepseek_client import DeepSeekClient
from app.services.llm.gemini_client import GeminiClient


def create_llm_client(
    provider: str,
    api_key: str,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs
) -> BaseLLMClient:
    """Factory function to create LLM client based on provider

    Args:
        provider: Provider name ('anthropic', 'deepseek', 'gemini')
        api_key: API key for the provider
        model: Optional model name (uses default if not specified)
        system_prompt: Optional system prompt
        **kwargs: Additional provider-specific parameters

    Returns:
        Initialized LLM client

    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.lower()

    if provider == "anthropic":
        return AnthropicClient(
            api_key=api_key,
            model=model or "claude-3-5-sonnet-20241022",
            system_prompt=system_prompt,
            **kwargs
        )

    elif provider == "deepseek":
        return DeepSeekClient(
            api_key=api_key,
            model=model or "deepseek-chat",
            system_prompt=system_prompt,
            **kwargs
        )

    elif provider == "gemini":
        return GeminiClient(
            api_key=api_key,
            model=model or "gemini-2.0-flash-exp",
            system_prompt=system_prompt,
            **kwargs
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


__all__ = [
    "BaseLLMClient",
    "AnthropicClient",
    "DeepSeekClient",
    "GeminiClient",
    "create_llm_client"
]
