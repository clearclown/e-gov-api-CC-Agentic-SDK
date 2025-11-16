"""DeepSeek AI Client Adapter

DeepSeek AI uses OpenAI-compatible API, so we use the OpenAI SDK.
"""

import logging
from typing import AsyncIterator, Dict, Any, Optional

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

from app.services.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class DeepSeekClient(BaseLLMClient):
    """DeepSeek AI LLM client

    Uses OpenAI-compatible API via the OpenAI SDK.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        system_prompt: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        **kwargs
    ):
        """Initialize DeepSeek client

        Args:
            api_key: DeepSeek API key
            model: DeepSeek model identifier (e.g., 'deepseek-chat', 'deepseek-coder')
            system_prompt: Optional system prompt
            base_url: DeepSeek API base URL
            **kwargs: Additional parameters
        """
        super().__init__(api_key, model, system_prompt, **kwargs)

        if not OPENAI_AVAILABLE:
            logger.error("OpenAI SDK not available (required for DeepSeek)")
            self._client = None
            return

        try:
            # Initialize OpenAI client with DeepSeek endpoint
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            self._messages = []
            self._last_response = None
            logger.info(f"DeepSeek client initialized with model: {model}")

        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {e}")
            self._client = None

    async def connect(self) -> None:
        """Connect to DeepSeek API (no explicit connection needed)"""
        logger.info("DeepSeek client ready")

    async def query(
        self,
        message: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send query to DeepSeek

        Args:
            message: User message
            session_id: Optional session ID (for message history)
            **kwargs: Additional parameters
        """
        if not self._client:
            raise RuntimeError("DeepSeek client not initialized")

        # Add system prompt if this is the first message
        if not self._messages and self.system_prompt:
            self._messages.append({
                "role": "system",
                "content": self.system_prompt
            })

        # Add user message
        self._messages.append({
            "role": "user",
            "content": message
        })

        # Send request to DeepSeek
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=self._messages,
                stream=True,
                **kwargs
            )
            self._last_response = response

        except Exception as e:
            logger.error(f"DeepSeek query error: {e}")
            raise

    async def receive_response(self) -> AsyncIterator[Dict[str, Any]]:
        """Receive streaming response from DeepSeek

        Yields:
            Response messages in standardized format
        """
        if not self._client or not self._last_response:
            yield {
                "type": "error",
                "content": "DeepSeek client not initialized or no response available"
            }
            return

        try:
            full_content = ""

            async for chunk in self._last_response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    content = delta.content if delta.content else ""

                    if content:
                        full_content += content
                        yield {
                            "type": "text",
                            "content": content,
                            "metadata": {
                                "model": self.model,
                                "provider": "deepseek",
                                "finish_reason": chunk.choices[0].finish_reason
                            }
                        }

            # Add assistant response to message history
            if full_content:
                self._messages.append({
                    "role": "assistant",
                    "content": full_content
                })

        except Exception as e:
            logger.error(f"DeepSeek response error: {e}")
            yield {
                "type": "error",
                "content": f"DeepSeek error: {str(e)}"
            }

    async def disconnect(self) -> None:
        """Disconnect from DeepSeek API"""
        if self._client:
            await self._client.close()
        logger.info("Disconnected from DeepSeek API")

    @property
    def provider_name(self) -> str:
        """Return provider name"""
        return "deepseek"
