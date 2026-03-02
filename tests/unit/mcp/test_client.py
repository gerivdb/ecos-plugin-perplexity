"""Unit tests for PerplexityMCPClient.

Test coverage:
- Intent Hash extraction (pattern matching)
- Conflict detection (duplicates)
- Input validation
- Base-3 state transitions
- Async operations (mocked)

Authors: ECOS Development Team
Version: 0.1.0-alpha1
Created: 2026-03-02
"""

import pytest
from ecos_perplexity.mcp.client import (
    PerplexityMCPClient,
    Base3State,
    ConflictType,
)


@pytest.fixture
def mock_client():
    """Fixture providing PerplexityMCPClient instance."""
    return PerplexityMCPClient("http://localhost:8080")


class TestIntentHashExtraction:
    """Test Intent Hash v11 pattern extraction."""
    
    def test_extract_single_intent(self, mock_client):
        """Test extraction of single Intent Hash."""
        conversation = {
            "id": "test-1",
            "text": "Processing 0xECOS_TEST_ACTION_20260302_230400 now"
        }
        intents = mock_client.extract_intent_hashes(conversation)
        
        assert len(intents) == 1
        assert "0xECOS_TEST_ACTION_20260302_230400" in intents
    
    def test_extract_multiple_intents(self, mock_client):
        """Test extraction of multiple Intent Hashes."""
        conversation = {
            "text": "Intent 0xECOS_TEST_ACTION_20260302 and 0xECOS_DEPLOY_BUILD_20260301"
        }
        intents = mock_client.extract_intent_hashes(conversation)
        
        assert len(intents) == 2
        assert "0xECOS_TEST_ACTION_20260302" in intents
        assert "0xECOS_DEPLOY_BUILD_20260301" in intents
    
    def test_extract_deduplicates(self, mock_client):
        """Test that duplicate intents are deduplicated."""
        conversation = {
            "messages": [
                {"text": "Using 0xECOS_SAME_INTENT_20260302"},
                {"text": "Also 0xECOS_SAME_INTENT_20260302"}
            ]
        }
        intents = mock_client.extract_intent_hashes(conversation)
        
        assert len(intents) == 1
        assert "0xECOS_SAME_INTENT_20260302" in intents
    
    def test_extract_empty_conversation(self, mock_client):
        """Test extraction from empty conversation."""
        intents = mock_client.extract_intent_hashes({})
        assert intents == []
    
    def test_extract_no_matches(self, mock_client):
        """Test extraction when no Intent Hashes present."""
        conversation = {"text": "Just regular text without hashes"}
        intents = mock_client.extract_intent_hashes(conversation)
        assert intents == []


class TestConflictDetection:
    """Test conflict detection logic."""
    
    def test_no_conflicts_empty(self, mock_client):
        """Test no conflicts with empty list."""
        conflicts = mock_client.detect_conflicts([])
        assert len(conflicts) == 0
    
    def test_no_conflicts_unique(self, mock_client):
        """Test no conflicts with unique intents."""
        intents = [
            "0xECOS_A_20260301",
            "0xECOS_B_20260302",
            "0xECOS_C_20260303"
        ]
        conflicts = mock_client.detect_conflicts(intents)
        assert len(conflicts) == 0
    
    def test_conflict_duplicate(self, mock_client):
        """Test conflict detection for duplicates."""
        intents = [
            "0xECOS_A_20260301",
            "0xECOS_A_20260301",  # Duplicate
            "0xECOS_B_20260302"
        ]
        conflicts = mock_client.detect_conflicts(intents)
        
        assert len(conflicts) == 1
        assert conflicts[0]["type"] == ConflictType.DUPLICATE_INTENT.value
        assert conflicts[0]["intent"] == "0xECOS_A_20260301"
        assert conflicts[0]["count"] == 2
        assert 0.5 <= conflicts[0]["severity"] <= 1.0
    
    def test_conflict_multiple_duplicates(self, mock_client):
        """Test multiple conflicts detected."""
        intents = [
            "0xECOS_A_20260301",
            "0xECOS_A_20260301",
            "0xECOS_B_20260302",
            "0xECOS_B_20260302",
            "0xECOS_B_20260302",  # 3x
        ]
        conflicts = mock_client.detect_conflicts(intents)
        
        assert len(conflicts) == 2
        
        # Find conflict for A
        conflict_a = next(c for c in conflicts if c["intent"] == "0xECOS_A_20260301")
        assert conflict_a["count"] == 2
        
        # Find conflict for B (should have higher severity)
        conflict_b = next(c for c in conflicts if c["intent"] == "0xECOS_B_20260302")
        assert conflict_b["count"] == 3
        assert conflict_b["severity"] > conflict_a["severity"]


class TestValidation:
    """Test input validation."""
    
    def test_validate_correct_format(self, mock_client):
        """Test validation of correct Intent Hash format."""
        valid_intents = [
            "0xECOS_TEST_20260302",
            "0xECOS_DEPLOY_BUILD_20260301_153045",
            "0xECOS_AUTOMERGE_COORDINATOR_202603021804"
        ]
        
        for intent in valid_intents:
            assert mock_client.validate_intent_hash_format(intent) is True
    
    def test_validate_incorrect_format(self, mock_client):
        """Test validation rejects incorrect formats."""
        invalid_intents = [
            "ECOS_TEST_20260302",  # Missing 0x
            "0xECOS_test_20260302",  # Lowercase
            "0xECOS_20260302",  # Missing component
            "0xECOS_TEST_2026",  # Timestamp too short
            "",  # Empty
        ]
        
        for intent in invalid_intents:
            assert mock_client.validate_intent_hash_format(intent) is False
    
    @pytest.mark.asyncio
    async def test_fetch_conversations_invalid_limit(self, mock_client):
        """Test fetch_conversations rejects invalid limits."""
        with pytest.raises(ValueError, match="Limit must be between"):
            await mock_client.fetch_conversations(limit=0)
        
        with pytest.raises(ValueError, match="Limit must be between"):
            await mock_client.fetch_conversations(limit=101)
    
    @pytest.mark.asyncio
    async def test_fetch_conversations_invalid_order(self, mock_client):
        """Test fetch_conversations rejects invalid order."""
        with pytest.raises(ValueError, match="Order must be"):
            await mock_client.fetch_conversations(order="invalid")
    
    @pytest.mark.asyncio
    async def test_get_conversation_empty_id(self, mock_client):
        """Test get_conversation_detail rejects empty ID."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await mock_client.get_conversation_detail("")


class TestBase3State:
    """Test Base-3 state management."""
    
    def test_initial_state_pending(self, mock_client):
        """Test initial state is PENDING."""
        assert mock_client.state == Base3State.PENDING
    
    @pytest.mark.asyncio
    async def test_state_success_after_fetch(self, mock_client):
        """Test state transitions to SUCCESS after successful fetch."""
        await mock_client.fetch_conversations(limit=5)
        assert mock_client.state == Base3State.SUCCESS
    
    def test_reset_state(self, mock_client):
        """Test state reset to PENDING."""
        mock_client._state = Base3State.SUCCESS
        mock_client.reset()
        assert mock_client.state == Base3State.PENDING
