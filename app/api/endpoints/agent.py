"""Agent API endpoints for legal AI interactions

FastAPI endpoints for Claude Agent SDK-based legal AI functionality:
- /query: General legal queries
- /analyze: Document analysis
- /chat: Conversational interactions
- /session: Session management
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
import json

from app.services.agent_service import get_agent_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


# ============================================================================
# Request/Response Models
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for general legal queries"""
    query: str = Field(..., min_length=1, description="Legal query or question")
    provider: Optional[str] = Field(None, description="LLM provider: 'anthropic', 'deepseek', or 'gemini'")

    @field_validator('query')
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ['anthropic', 'deepseek', 'gemini']:
            raise ValueError('provider must be "anthropic", "deepseek", or "gemini"')
        return v.lower() if v else None


class AnalyzeRequest(BaseModel):
    """Request model for document analysis"""
    doc_type: str = Field(..., description="Document type: 'law' or 'case'")
    doc_id: str = Field(..., min_length=1, description="Document identifier")
    provider: Optional[str] = Field(None, description="LLM provider: 'anthropic', 'deepseek', or 'gemini'")

    @field_validator('doc_type')
    @classmethod
    def validate_doc_type(cls, v: str) -> str:
        if v not in ['law', 'case']:
            raise ValueError('doc_type must be "law" or "case"')
        return v

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ['anthropic', 'deepseek', 'gemini']:
            raise ValueError('provider must be "anthropic", "deepseek", or "gemini"')
        return v.lower() if v else None


class ChatRequest(BaseModel):
    """Request model for chat interactions"""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    provider: Optional[str] = Field(None, description="LLM provider: 'anthropic', 'deepseek', or 'gemini'")

    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ['anthropic', 'deepseek', 'gemini']:
            raise ValueError('provider must be "anthropic", "deepseek", or "gemini"')
        return v.lower() if v else None


class SessionResponse(BaseModel):
    """Response model for session creation"""
    session_id: str = Field(..., description="Unique session identifier")


# ============================================================================
# Streaming Helper
# ============================================================================

async def stream_json_lines(async_iterator):
    """Convert async iterator to JSON lines stream

    Args:
        async_iterator: Async iterator of dictionaries

    Yields:
        JSON-encoded lines for streaming response
    """
    try:
        async for item in async_iterator:
            yield json.dumps(item, ensure_ascii=False) + "\n"
    except Exception as e:
        logger.error(f"Streaming error: {e}", exc_info=True)
        yield json.dumps({
            "type": "error",
            "content": f"Stream error: {str(e)}"
        }, ensure_ascii=False) + "\n"


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/query")
async def query_endpoint(request: QueryRequest):
    """Execute a general legal query

    Streams AI responses for legal questions and queries.
    Supports multiple LLM providers (anthropic, deepseek, gemini).

    Args:
        request: Query request with legal question and optional provider

    Returns:
        Streaming JSON lines with AI responses
    """
    try:
        logger.info(f"Query endpoint: provider={request.provider}, query={request.query}")

        # Get agent service for the specified provider
        service = get_agent_service(request.provider)

        # Stream query response
        return StreamingResponse(
            stream_json_lines(service.query(request.query, request.provider)),
            media_type="application/json"
        )

    except Exception as e:
        logger.error(f"Query endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_endpoint(request: AnalyzeRequest):
    """Analyze a legal document (law or court case)

    Provides detailed AI analysis of specified legal documents.
    Supports multiple LLM providers (anthropic, deepseek, gemini).

    Args:
        request: Analysis request with doc_type, doc_id, and optional provider

    Returns:
        Streaming JSON lines with analysis results
    """
    try:
        logger.info(f"Analyze endpoint: provider={request.provider}, {request.doc_type} {request.doc_id}")

        # Get agent service for the specified provider
        service = get_agent_service(request.provider)

        # Stream analysis response
        return StreamingResponse(
            stream_json_lines(
                service.analyze(request.doc_type, request.doc_id, request.provider)
            ),
            media_type="application/json"
        )

    except Exception as e:
        logger.error(f"Analyze endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Conduct conversational interaction with context

    Maintains conversation history within sessions for contextual responses.
    Supports multiple LLM providers (anthropic, deepseek, gemini).

    Args:
        request: Chat request with message, optional session_id, and optional provider

    Returns:
        Streaming JSON lines with chat responses including session_id
    """
    try:
        logger.info(f"Chat endpoint: provider={request.provider}, session={request.session_id}, message={request.message}")

        # Get agent service for the specified provider
        service = get_agent_service(request.provider)

        # Stream chat response
        return StreamingResponse(
            stream_json_lines(
                service.chat(request.message, request.session_id, request.provider)
            ),
            media_type="application/json"
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session", response_model=SessionResponse)
async def create_session_endpoint(provider: Optional[str] = None):
    """Create a new conversation session

    Args:
        provider: Optional LLM provider for this session

    Returns:
        SessionResponse with new session_id
    """
    try:
        logger.info(f"Creating new session with provider: {provider}")

        # Get agent service for the specified provider
        service = get_agent_service(provider)
        session_id = await service.create_session(provider)

        return SessionResponse(session_id=session_id)

    except Exception as e:
        logger.error(f"Create session error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_endpoint(session_id: str, provider: Optional[str] = None):
    """Retrieve session information and message history

    Args:
        session_id: Session identifier
        provider: Optional provider for this session

    Returns:
        Session data with messages and metadata
    """
    try:
        logger.info(f"Get session: {session_id}")

        # Get agent service for the specified provider
        service = get_agent_service(provider)
        session_data = await service.get_session(session_id)

        if session_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found: {session_id}"
            )

        return session_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
