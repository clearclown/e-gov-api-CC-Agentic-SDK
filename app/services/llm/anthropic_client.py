"""Anthropic Claude Client Adapter

Wraps the Claude Agent SDK to conform to the BaseLLMClient interface.
"""

import logging
from typing import AsyncIterator, Dict, Any, Optional

try:
    from claude_agent_sdk import ClaudeSDKClient, types as sdk_types
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    ClaudeSDKClient = None
    sdk_types = None

from app.services.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude LLM client

    Wraps the Claude Agent SDK to provide a unified interface.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[list[str]] = None,
        **kwargs
    ):
        """Initialize Anthropic Claude client

        Args:
            api_key: Anthropic API key
            model: Claude model identifier
            system_prompt: Optional system prompt
            allowed_tools: List of allowed MCP tool names
            **kwargs: Additional parameters
        """
        super().__init__(api_key, model, system_prompt, **kwargs)

        if not SDK_AVAILABLE:
            logger.error("Claude Agent SDK not available")
            self._client = None
            return

        # Set API key in environment
        import os
        os.environ['ANTHROPIC_API_KEY'] = api_key

        # Default allowed tools
        if allowed_tools is None:
            allowed_tools = [
                "search_law",
                "search_case",
                "analyze_law_case_relationship",
                "get_law_detail",
                "get_case_detail",
                "ask_legal_question",
            ]

        # Create Claude SDK options
        try:
            options = sdk_types.ClaudeAgentOptions(
                model=model,
                system_prompt=system_prompt or "あなたは日本の法律の専門家です。",
                allowed_tools=allowed_tools,
            )

            # Initialize Claude SDK client
            self._client = ClaudeSDKClient(options=options)
            logger.info(f"Anthropic client initialized with model: {model}")

        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self._client = None

    async def connect(self) -> None:
        """Connect to Claude SDK"""
        if self._client:
            await self._client.connect()
            logger.info("Connected to Anthropic Claude SDK")

    async def query(
        self,
        message: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send query to Claude

        Args:
            message: User message
            session_id: Optional session ID
            **kwargs: Additional parameters
        """
        if not self._client:
            raise RuntimeError("Anthropic client not initialized")

        await self._client.query(message, session_id=session_id)

    async def receive_response(self) -> AsyncIterator[Dict[str, Any]]:
        """Receive streaming response from Claude

        Yields:
            Response messages in standardized format
        """
        if not self._client:
            yield {
                "type": "error",
                "content": "Anthropic client not initialized"
            }
            return

        try:
            async for message in self._client.receive_response():
                if hasattr(message, 'content'):
                    content = message.content
                    msg_type = getattr(message, 'type', 'text')

                    yield {
                        "type": msg_type,
                        "content": content if isinstance(content, str) else str(content),
                        "metadata": {
                            "model": self.model,
                            "provider": "anthropic"
                        }
                    }

        except Exception as e:
            logger.error(f"Anthropic response error: {e}")
            yield {
                "type": "error",
                "content": f"Anthropic error: {str(e)}"
            }

    async def disconnect(self) -> None:
        """Disconnect from Claude SDK"""
        # Claude SDK handles cleanup automatically
        logger.info("Disconnected from Anthropic Claude SDK")

    @property
    def provider_name(self) -> str:
        """Return provider name"""
        return "anthropic"
