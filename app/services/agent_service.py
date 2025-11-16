"""Agent Service for legal AI interactions with Multi-LLM support

This service provides high-level AI agent functionality for legal queries,
document analysis, and natural language conversations.

Supports multiple LLM providers:
- Anthropic Claude (via Claude Agent SDK)
- DeepSeek AI
- Google Gemini

Features:
- query: General legal queries with streaming responses
- analyze: Document analysis (laws and cases)
- chat: Stateful conversation with context
- Session management for conversation history
"""

import logging
import uuid
from typing import AsyncIterator, Dict, Any, Optional
from datetime import datetime, UTC

from app.core.config import settings
from app.services.llm import create_llm_client, BaseLLMClient

logger = logging.getLogger(__name__)


class AgentService:
    """Multi-LLM Agent service for legal AI interactions

    Provides streaming AI responses for legal queries, document analysis,
    and conversational interactions with context management.

    Supports multiple LLM providers via unified interface.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize Agent service with specified LLM provider

        Args:
            provider: LLM provider ('anthropic', 'deepseek', 'gemini')
                     Defaults to settings.default_llm_provider
            api_key: API key for the provider (defaults to settings)
            model: Model identifier (defaults to provider-specific model)
        """
        # Determine provider
        if provider is None:
            provider = getattr(settings, 'default_llm_provider', 'anthropic')

        self.provider = provider.lower()

        # Get API key from settings if not provided
        if api_key is None:
            if self.provider == 'anthropic':
                api_key = getattr(settings, 'anthropic_api_key', None)
            elif self.provider == 'deepseek':
                api_key = getattr(settings, 'deepseek_api_key', None)
            elif self.provider == 'gemini':
                api_key = getattr(settings, 'google_api_key', None)

        if not api_key:
            logger.warning(f"No API key found for provider: {self.provider}")
            self._client = None
            self.sessions = {}
            return

        # System prompt for legal AI agent
        system_prompt = """あなたは日本の法律の専門家です。

以下の能力を持っています：
- 法令検索と分析
- 判例検索と分析
- 法令と判例の関連性分析
- 法的質問への回答

正確で有用な法的情報を提供してください。
回答は日本語で、明確かつ専門的に行ってください。"""

        # Create LLM client using factory
        try:
            self._client: BaseLLMClient = create_llm_client(
                provider=self.provider,
                api_key=api_key,
                model=model,
                system_prompt=system_prompt
            )
            logger.info(f"Agent service initialized with provider: {self.provider}")

        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self._client = None

        # Session storage (in-memory for now)
        self.sessions: Dict[str, Dict[str, Any]] = {}

    @property
    def client(self) -> Optional[BaseLLMClient]:
        """Access to underlying LLM client"""
        return self._client

    async def query(
        self,
        query_text: str,
        provider: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Execute a general legal query with streaming response

        Args:
            query_text: User's legal question or query
            provider: Optional provider override for this query

        Yields:
            Streaming response messages with type and content
        """
        # Use override provider if specified
        if provider and provider.lower() != self.provider:
            temp_service = AgentService(provider=provider)
            async for message in temp_service.query(query_text):
                yield message
            return

        if not self._client:
            yield {
                "type": "error",
                "content": "Agent service not properly initialized",
                "provider": self.provider
            }
            return

        try:
            logger.info(f"Executing query with {self.provider}: {query_text}")

            # Connect to LLM
            await self._client.connect()

            # Send query
            await self._client.query(query_text)

            # Stream response
            async for message in self._client.receive_response():
                # Add provider information
                message["provider"] = self.provider
                yield message

        except Exception as e:
            logger.error(f"Query error with {self.provider}: {e}", exc_info=True)
            yield {
                "type": "error",
                "content": f"Query failed: {str(e)}",
                "provider": self.provider
            }

    async def analyze(
        self,
        doc_type: str,
        doc_id: str,
        provider: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Analyze a legal document (law or case)

        Args:
            doc_type: Type of document ('law' or 'case')
            doc_id: Document identifier
            provider: Optional provider override for this analysis

        Yields:
            Streaming analysis results
        """
        # Use override provider if specified
        if provider and provider.lower() != self.provider:
            temp_service = AgentService(provider=provider)
            async for message in temp_service.analyze(doc_type, doc_id):
                yield message
            return

        if not self._client:
            yield {
                "type": "error",
                "content": "Agent service not properly initialized",
                "provider": self.provider
            }
            return

        try:
            logger.info(f"Analyzing {doc_type}: {doc_id} with {self.provider}")

            # Construct analysis query
            if doc_type == "law":
                query = f"法令ID「{doc_id}」の内容を詳しく分析してください。"
            elif doc_type == "case":
                query = f"判例ID「{doc_id}」の内容を詳しく分析してください。"
            else:
                yield {
                    "type": "error",
                    "content": f"Invalid doc_type: {doc_type}",
                    "provider": self.provider
                }
                return

            # Connect and send query
            await self._client.connect()
            await self._client.query(query)

            async for message in self._client.receive_response():
                message["provider"] = self.provider
                yield message

        except Exception as e:
            logger.error(f"Analysis error with {self.provider}: {e}", exc_info=True)
            yield {
                "type": "error",
                "content": f"Analysis failed: {str(e)}",
                "provider": self.provider
            }

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        provider: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Conduct stateful conversation with context

        Args:
            message: User message
            session_id: Optional session ID for context continuity
            provider: Optional provider override for this chat

        Yields:
            Streaming chat responses with session information
        """
        # Use override provider if specified
        if provider and provider.lower() != self.provider:
            temp_service = AgentService(provider=provider)
            async for msg in temp_service.chat(message, session_id):
                yield msg
            return

        if not self._client:
            yield {
                "type": "error",
                "content": "Agent service not properly initialized",
                "provider": self.provider
            }
            return

        try:
            # Create or get session
            if session_id is None:
                session_id = await self.create_session()

            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "id": session_id,
                    "created_at": datetime.now(UTC).isoformat(),
                    "messages": [],
                    "provider": self.provider
                }

            logger.info(f"Chat in session {session_id} with {self.provider}: {message}")

            # Add user message to history
            self.sessions[session_id]["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now(UTC).isoformat()
            })

            # Connect and send query
            await self._client.connect()
            await self._client.query(message, session_id=session_id)

            full_response = ""
            async for msg in self._client.receive_response():
                if "content" in msg:
                    content = msg["content"]
                    full_response += content

                    yield {
                        **msg,
                        "session_id": session_id,
                        "provider": self.provider
                    }

            # Add assistant response to history
            self.sessions[session_id]["messages"].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now(UTC).isoformat()
            })

        except Exception as e:
            logger.error(f"Chat error with {self.provider}: {e}", exc_info=True)
            yield {
                "type": "error",
                "content": f"Chat failed: {str(e)}",
                "session_id": session_id,
                "provider": self.provider
            }

    async def create_session(self, provider: Optional[str] = None) -> str:
        """Create a new conversation session

        Args:
            provider: Optional provider for this session

        Returns:
            New session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now(UTC).isoformat(),
            "messages": [],
            "provider": provider or self.provider
        }
        logger.info(f"Created session: {session_id} with provider: {provider or self.provider}")
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information

        Args:
            session_id: Session identifier

        Returns:
            Session data with messages, or None if not found
        """
        return self.sessions.get(session_id)


# Global service instances (one per provider)
_agent_services: Dict[str, AgentService] = {}


def get_agent_service(provider: Optional[str] = None) -> AgentService:
    """Get or create agent service instance for specified provider

    Args:
        provider: LLM provider name (defaults to settings.default_llm_provider)

    Returns:
        AgentService instance for the specified provider
    """
    if provider is None:
        provider = getattr(settings, 'default_llm_provider', 'anthropic')

    provider = provider.lower()

    if provider not in _agent_services:
        _agent_services[provider] = AgentService(provider=provider)

    return _agent_services[provider]
