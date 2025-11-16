"""Base LLM Client Interface

Defines the abstract interface that all LLM providers must implement.
This allows for easy switching between different LLM providers (Anthropic, DeepSeek, Gemini).
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients

    All LLM provider implementations must inherit from this class
    and implement the required methods.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Initialize LLM client

        Args:
            api_key: API key for the LLM provider
            model: Model identifier
            system_prompt: Optional system prompt/instruction
            **kwargs: Additional provider-specific parameters
        """
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.kwargs = kwargs

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the LLM service (if required)

        Some providers may need an explicit connection step,
        others may not. Implement as needed.
        """
        pass

    @abstractmethod
    async def query(
        self,
        message: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send a query to the LLM

        Args:
            message: User message/query
            session_id: Optional session ID for stateful conversations
            **kwargs: Additional provider-specific parameters
        """
        pass

    @abstractmethod
    async def receive_response(self) -> AsyncIterator[Dict[str, Any]]:
        """Receive streaming response from the LLM

        Yields:
            Response messages with standardized format:
            {
                "type": "text" | "error" | "tool_use" | etc,
                "content": str,
                "metadata": Optional[Dict]
            }
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the LLM service (if required)"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'anthropic', 'deepseek', 'gemini')"""
        pass
