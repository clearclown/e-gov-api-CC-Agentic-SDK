"""Google Gemini Client Adapter

Uses the Google Generative AI SDK for Gemini models.
"""

import logging
from typing import AsyncIterator, Dict, Any, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from app.services.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class GeminiClient(BaseLLMClient):
    """Google Gemini LLM client

    Uses the Google Generative AI SDK.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Initialize Gemini client

        Args:
            api_key: Google API key
            model: Gemini model identifier (e.g., 'gemini-2.0-flash-exp', 'gemini-1.5-pro')
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
        """
        super().__init__(api_key, model, system_prompt, **kwargs)

        if not GENAI_AVAILABLE:
            logger.error("Google Generative AI SDK not available")
            self._client = None
            return

        try:
            # Configure Gemini API
            genai.configure(api_key=api_key)

            # Create generation config
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_output_tokens", 8192),
            }

            # Initialize Gemini model
            self._model = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                system_instruction=system_prompt
            )

            # Initialize chat session (will be created on first query)
            self._chat = None
            self._last_response = None

            logger.info(f"Gemini client initialized with model: {model}")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._client = None
            self._model = None

    async def connect(self) -> None:
        """Connect to Gemini API (no explicit connection needed)"""
        logger.info("Gemini client ready")

    async def query(
        self,
        message: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send query to Gemini

        Args:
            message: User message
            session_id: Optional session ID (for chat continuity)
            **kwargs: Additional parameters
        """
        if not self._model:
            raise RuntimeError("Gemini client not initialized")

        try:
            # Initialize chat if not exists
            if self._chat is None:
                self._chat = self._model.start_chat(history=[])

            # Send message and get response (streaming)
            response = await self._chat.send_message_async(
                message,
                stream=True
            )
            self._last_response = response

        except Exception as e:
            logger.error(f"Gemini query error: {e}")
            raise

    async def receive_response(self) -> AsyncIterator[Dict[str, Any]]:
        """Receive streaming response from Gemini

        Yields:
            Response messages in standardized format
        """
        if not self._model or not self._last_response:
            yield {
                "type": "error",
                "content": "Gemini client not initialized or no response available"
            }
            return

        try:
            async for chunk in self._last_response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield {
                        "type": "text",
                        "content": chunk.text,
                        "metadata": {
                            "model": self.model,
                            "provider": "gemini",
                            "candidates": len(chunk.candidates) if hasattr(chunk, 'candidates') else 0
                        }
                    }

        except Exception as e:
            logger.error(f"Gemini response error: {e}")
            yield {
                "type": "error",
                "content": f"Gemini error: {str(e)}"
            }

    async def disconnect(self) -> None:
        """Disconnect from Gemini API"""
        self._chat = None
        logger.info("Disconnected from Gemini API")

    @property
    def provider_name(self) -> str:
        """Return provider name"""
        return "gemini"
