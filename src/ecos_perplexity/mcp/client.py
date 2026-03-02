"""Perplexity MCP Client.

HTTP client for accessing Perplexity conversation history via MCP protocol.

Authors: ECOS Development Team
Created: 2026-03-02
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError


logger = logging.getLogger(__name__)


class MCPResponseState(Enum):
    """Ternary state for MCP responses."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class MCPConversation:
    """Perplexity conversation metadata."""
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    intent_hash: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class MCPMessage:
    """Single message in conversation."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MCPResponse:
    """Ternary response wrapper."""
    state: MCPResponseState
    data: Any = None
    error: Optional[str] = None
    retry_after: Optional[int] = None


class PerplexityMCPClient:
    """Async HTTP client for Perplexity MCP API.
    
    Provides:
    - Conversation listing with pagination
    - Conversation detail fetching
    - Retry logic with exponential backoff
    - Rate limiting detection
    - Ternary response states
    """
    
    def __init__(
        self,
        server_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize MCP client.
        
        Args:
            server_url: MCP server base URL
            api_key: API authentication key
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session: Optional[ClientSession] = None
        self._closed = False
    
    async def _get_session(self) -> ClientSession:
        """Get or create aiohttp session.
        
        Returns:
            Active ClientSession
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "ECOS-Plugin-Perplexity/0.1.0"
                }
            )
        return self._session
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> MCPResponse:
        """Execute HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
        
        Returns:
            MCPResponse with ternary state
        """
        url = f"{self.server_url}/{endpoint.lstrip('/')}"
        session = await self._get_session()
        
        for attempt in range(self.max_retries):
            try:
                async with session.request(method, url, **kwargs) as response:
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(f"Rate limited, retry after {retry_after}s")
                        return MCPResponse(
                            state=MCPResponseState.PENDING,
                            retry_after=retry_after
                        )
                    
                    # Handle success
                    if 200 <= response.status < 300:
                        data = await response.json()
                        return MCPResponse(
                            state=MCPResponseState.SUCCESS,
                            data=data
                        )
                    
                    # Handle errors
                    error_text = await response.text()
                    logger.error(
                        f"Request failed: {response.status} - {error_text}"
                    )
                    
                    # Don't retry client errors (4xx)
                    if 400 <= response.status < 500:
                        return MCPResponse(
                            state=MCPResponseState.FAILED,
                            error=f"Client error {response.status}: {error_text}"
                        )
            
            except ClientError as e:
                logger.error(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return MCPResponse(
                    state=MCPResponseState.FAILED,
                    error=f"Connection error: {str(e)}"
                )
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return MCPResponse(
                    state=MCPResponseState.FAILED,
                    error=f"Unexpected error: {str(e)}"
                )
        
        return MCPResponse(
            state=MCPResponseState.FAILED,
            error=f"Max retries ({self.max_retries}) exceeded"
        )
    
    async def fetch_conversations(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "updated_at",
        order_dir: str = "desc"
    ) -> MCPResponse:
        """Fetch list of Perplexity conversations.
        
        Args:
            limit: Maximum number of conversations to fetch
            offset: Pagination offset
            order_by: Sort field (created_at, updated_at)
            order_dir: Sort direction (asc, desc)
        
        Returns:
            MCPResponse with List[MCPConversation] on success
        """
        params = {
            "limit": min(limit, 100),  # Cap at 100
            "offset": offset,
            "order_by": order_by,
            "order_dir": order_dir
        }
        
        response = await self._request("GET", "/conversations", params=params)
        
        if response.state == MCPResponseState.SUCCESS:
            # Parse conversations
            conversations = [
                MCPConversation(
                    id=conv["id"],
                    title=conv.get("title", "Untitled"),
                    created_at=conv["created_at"],
                    updated_at=conv["updated_at"],
                    message_count=conv.get("message_count", 0),
                    intent_hash=conv.get("intent_hash"),
                    tags=conv.get("tags", [])
                )
                for conv in response.data.get("conversations", [])
            ]
            response.data = conversations
        
        return response
    
    async def get_conversation_detail(
        self,
        conversation_id: str,
        include_messages: bool = True
    ) -> MCPResponse:
        """Fetch detailed conversation with messages.
        
        Args:
            conversation_id: Conversation UUID
            include_messages: Include full message history
        
        Returns:
            MCPResponse with conversation detail and messages
        """
        params = {"include_messages": "true" if include_messages else "false"}
        
        response = await self._request(
            "GET",
            f"/conversations/{conversation_id}",
            params=params
        )
        
        if response.state == MCPResponseState.SUCCESS:
            conv_data = response.data
            
            # Parse messages if included
            messages = []
            if include_messages and "messages" in conv_data:
                messages = [
                    MCPMessage(
                        id=msg["id"],
                        role=msg["role"],
                        content=msg["content"],
                        timestamp=msg["timestamp"],
                        metadata=msg.get("metadata", {})
                    )
                    for msg in conv_data["messages"]
                ]
            
            response.data = {
                "conversation": MCPConversation(
                    id=conv_data["id"],
                    title=conv_data.get("title", "Untitled"),
                    created_at=conv_data["created_at"],
                    updated_at=conv_data["updated_at"],
                    message_count=conv_data.get("message_count", 0),
                    intent_hash=conv_data.get("intent_hash"),
                    tags=conv_data.get("tags", [])
                ),
                "messages": messages
            }
        
        return response
    
    async def ping(self) -> bool:
        """Health check ping.
        
        Returns:
            True if server reachable
        """
        try:
            response = await self._request("GET", "/health")
            return response.state == MCPResponseState.SUCCESS
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._closed = True
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
