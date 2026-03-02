"""Perplexity MCP Client - POC basique fetch conversations.

Provides basic MCP integration for:
- Fetching conversation history from Perplexity
- Extracting Intent Hash v11 patterns
- Detecting simple conflicts (duplicate intents)

Authors: ECOS Development Team
Version: 0.1.0-alpha1
Created: 2026-03-02
"""

import re
import asyncio
from typing import List, Dict, Any, Optional
from collections import Counter
from enum import Enum


class Base3State(Enum):
    """Base-3 ternary state for validation."""
    PENDING = 0
    SUCCESS = 1
    FAILED = 2


class ConflictType(Enum):
    """Types of conflicts detected in conversations."""
    DUPLICATE_INTENT = "duplicate_intent"
    PATTERN_MISMATCH = "pattern_mismatch"
    NONE = "none"


class PerplexityMCPClient:
    """MCP Client for Perplexity conversation coordination.
    
    Provides basic POC functionality:
    - Fetch last N conversations
    - Extract Intent Hash v11 patterns (0xECOS_<COMPONENT>_<EVENT>_<TIMESTAMP>)
    - Detect duplicate intents (simple conflict detection)
    
    Args:
        server_url: MCP server URL (e.g., http://localhost:8080)
        timeout: Request timeout in seconds (default: 10)
    
    Example:
        >>> client = PerplexityMCPClient("http://localhost:8080")
        >>> conversations = await client.fetch_conversations(limit=10)
        >>> intents = client.extract_intent_hashes(conversations[0])
        >>> conflicts = client.detect_conflicts(intents)
    """
    
    # Intent Hash v11 pattern: 0xECOS_<COMPONENT>_<EVENT>_<TIMESTAMP>
    INTENT_HASH_PATTERN = r'0xECOS_[A-Z_]+_[0-9]{8,14}'
    
    def __init__(self, server_url: str, timeout: int = 10):
        """Initialize MCP client.
        
        Args:
            server_url: MCP server URL
            timeout: Request timeout in seconds
        """
        self.server_url = server_url
        self.timeout = timeout
        self._state = Base3State.PENDING
        
        # Note: Real MCP client would be initialized here
        # For POC, we use mock placeholder
        # self.client = mcp.Client(server_url, timeout=timeout)
        self.client = None
    
    async def fetch_conversations(
        self, 
        limit: int = 10, 
        order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Fetch last N conversations from Perplexity.
        
        Args:
            limit: Number of conversations to fetch (max 100)
            order: Sort order ('asc' or 'desc')
        
        Returns:
            List of conversation dictionaries with keys:
            - id: Conversation ID
            - title: Conversation title
            - created_at: Timestamp
            - messages: List of message objects
        
        Raises:
            ValueError: If limit out of range or invalid order
            ConnectionError: If MCP server unreachable
        """
        if not 1 <= limit <= 100:
            raise ValueError(f"Limit must be between 1 and 100, got {limit}")
        
        if order not in ["asc", "desc"]:
            raise ValueError(f"Order must be 'asc' or 'desc', got {order}")
        
        # POC: Mock implementation
        # Real implementation would use:
        # response = await self.client.call(
        #     "perplexity/list_conversations",
        #     {"limit": limit, "order": order}
        # )
        # return response.get("conversations", [])
        
        self._state = Base3State.SUCCESS
        return []
    
    async def get_conversation_detail(
        self, 
        conv_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get full conversation thread with all messages.
        
        Args:
            conv_id: Conversation ID
        
        Returns:
            Conversation dictionary with full message history,
            or None if conversation not found
        
        Raises:
            ValueError: If conv_id empty
            ConnectionError: If MCP server unreachable
        """
        if not conv_id:
            raise ValueError("conv_id cannot be empty")
        
        # POC: Mock implementation
        # Real implementation would use:
        # return await self.client.call(
        #     "perplexity/get_conversation",
        #     {"conversation_id": conv_id}
        # )
        
        self._state = Base3State.SUCCESS
        return None
    
    def extract_intent_hashes(self, conversation: Dict[str, Any]) -> List[str]:
        """Extract Intent Hash v11 patterns from conversation.
        
        Pattern: 0xECOS_<COMPONENT>_<EVENT>_<TIMESTAMP>
        
        Examples:
            - 0xECOS_PERPLEXITY_POC_MCP_20260302_230400
            - 0xECOS_AUTOMERGE_COORDINATOR_20260302
            - 0xECOS_DEPLOY_BUILD_20260301_153045
        
        Args:
            conversation: Conversation dictionary (recursive search in all values)
        
        Returns:
            List of unique Intent Hash strings found
        """
        if not conversation:
            return []
        
        # Convert entire conversation to string for pattern matching
        text = str(conversation)
        
        # Extract all matches and deduplicate
        matches = re.findall(self.INTENT_HASH_PATTERN, text)
        return list(set(matches))
    
    def detect_conflicts(
        self, 
        intents: List[str]
    ) -> List[Dict[str, Any]]:
        """Detect simple conflicts: duplicate intents.
        
        In POC phase, only duplicate Intent Hash detection.
        Future phases will add semantic conflict analysis.
        
        Args:
            intents: List of Intent Hash strings
        
        Returns:
            List of conflict dictionaries:
            - type: ConflictType enum
            - intent: Intent Hash string
            - count: Number of occurrences
            - severity: float [0.0, 1.0] (1.0 = critical)
        """
        if not intents:
            return []
        
        conflicts = []
        counts = Counter(intents)
        
        for intent, count in counts.items():
            if count > 1:
                # Duplicate intent detected
                conflicts.append({
                    "type": ConflictType.DUPLICATE_INTENT.value,
                    "intent": intent,
                    "count": count,
                    "severity": min(1.0, 0.5 + (count - 2) * 0.25),  # 0.5 base + escalation
                    "recommendation": "Review duplicate Intent Hash usage across sessions"
                })
        
        return conflicts
    
    def validate_intent_hash_format(self, intent: str) -> bool:
        """Validate Intent Hash v11 format.
        
        Args:
            intent: Intent Hash string to validate
        
        Returns:
            True if valid format, False otherwise
        """
        if not intent:
            return False
        
        return bool(re.fullmatch(self.INTENT_HASH_PATTERN, intent))
    
    @property
    def state(self) -> Base3State:
        """Get current client state."""
        return self._state
    
    def reset(self) -> None:
        """Reset client state to PENDING."""
        self._state = Base3State.PENDING
