"""Intent Hash Conflict Detector.

Detects duplicate and conflicting Intent Hashes across sessions.

Authors: ECOS Development Team
Created: 2026-03-02
"""

import logging
from typing import Dict, Set, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Ternary conflict types."""
    NONE = "none"  # No conflict
    SOFT = "soft"  # Similar but not identical
    HARD = "hard"  # Exact duplicate


@dataclass
class IntentRecord:
    """Record of tracked Intent Hash."""
    intent_hash: str
    first_seen: str
    last_seen: str
    occurrence_count: int = 1
    conversation_ids: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ConflictResult:
    """Result of conflict detection."""
    conflict_type: ConflictType
    existing_intent: Optional[IntentRecord] = None
    similarity_score: float = 0.0
    message: str = ""


class ConflictDetector:
    """Detect Intent Hash conflicts across sessions.
    
    Uses set-based tracking with similarity detection.
    Supports:
    - Exact duplicate detection (HARD conflict)
    - Similarity-based detection (SOFT conflict)
    - Active intent registry
    - Persistence export/import
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """Initialize conflict detector.
        
        Args:
            similarity_threshold: Threshold for SOFT conflicts (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
        self._active_intents: Dict[str, IntentRecord] = {}
        self._normalized_index: Dict[str, str] = {}  # normalized -> original
    
    def track_intent(
        self,
        intent_hash: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Track new Intent Hash.
        
        Args:
            intent_hash: Intent Hash to track
            conversation_id: Associated conversation ID
            metadata: Additional metadata
        """
        normalized = self._normalize_hash(intent_hash)
        timestamp = datetime.utcnow().isoformat()
        
        if intent_hash in self._active_intents:
            # Update existing record
            record = self._active_intents[intent_hash]
            record.last_seen = timestamp
            record.occurrence_count += 1
            if conversation_id and conversation_id not in record.conversation_ids:
                record.conversation_ids.append(conversation_id)
            if metadata:
                record.metadata.update(metadata)
        else:
            # Create new record
            record = IntentRecord(
                intent_hash=intent_hash,
                first_seen=timestamp,
                last_seen=timestamp,
                occurrence_count=1,
                conversation_ids=[conversation_id] if conversation_id else [],
                metadata=metadata or {}
            )
            self._active_intents[intent_hash] = record
            self._normalized_index[normalized] = intent_hash
        
        logger.debug(f"Tracked intent: {intent_hash} (count: {record.occurrence_count})")
    
    def check_conflict(
        self,
        intent_hash: str,
        check_similarity: bool = True
    ) -> ConflictResult:
        """Check if Intent Hash conflicts with existing.
        
        Args:
            intent_hash: Hash to check
            check_similarity: Enable similarity-based detection
        
        Returns:
            ConflictResult with ternary conflict type
        """
        # Check exact match (HARD conflict)
        if intent_hash in self._active_intents:
            existing = self._active_intents[intent_hash]
            return ConflictResult(
                conflict_type=ConflictType.HARD,
                existing_intent=existing,
                similarity_score=1.0,
                message=f"Exact duplicate found (seen {existing.occurrence_count} times)"
            )
        
        # Check normalized match
        normalized = self._normalize_hash(intent_hash)
        if normalized in self._normalized_index:
            original = self._normalized_index[normalized]
            existing = self._active_intents[original]
            return ConflictResult(
                conflict_type=ConflictType.HARD,
                existing_intent=existing,
                similarity_score=1.0,
                message=f"Normalized duplicate of '{original}'"
            )
        
        # Check similarity (SOFT conflict)
        if check_similarity:
            for existing_hash, record in self._active_intents.items():
                similarity = self._calculate_similarity(intent_hash, existing_hash)
                if similarity >= self.similarity_threshold:
                    return ConflictResult(
                        conflict_type=ConflictType.SOFT,
                        existing_intent=record,
                        similarity_score=similarity,
                        message=f"Similar to '{existing_hash}' (similarity: {similarity:.2f})"
                    )
        
        # No conflict
        return ConflictResult(
            conflict_type=ConflictType.NONE,
            message="No conflict detected"
        )
    
    def _normalize_hash(self, intent_hash: str) -> str:
        """Normalize Intent Hash for comparison.
        
        Args:
            intent_hash: Hash to normalize
        
        Returns:
            Normalized hash (lowercase, stripped)
        """
        return intent_hash.lower().strip().replace("-", "_")
    
    def _calculate_similarity(
        self,
        hash1: str,
        hash2: str
    ) -> float:
        """Calculate similarity between two Intent Hashes.
        
        Uses simple character-based similarity (Jaccard index).
        
        Args:
            hash1: First hash
            hash2: Second hash
        
        Returns:
            Similarity score [0.0-1.0]
        """
        # Normalize
        h1 = self._normalize_hash(hash1)
        h2 = self._normalize_hash(hash2)
        
        # Extract meaningful parts (split by _)
        parts1 = set(h1.split("_"))
        parts2 = set(h2.split("_"))
        
        # Jaccard similarity
        intersection = len(parts1 & parts2)
        union = len(parts1 | parts2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def get_active_intents(self) -> List[IntentRecord]:
        """Get list of all active Intent Hashes.
        
        Returns:
            List of IntentRecord objects, sorted by last_seen
        """
        records = list(self._active_intents.values())
        records.sort(key=lambda r: r.last_seen, reverse=True)
        return records
    
    def get_statistics(self) -> Dict:
        """Get detector statistics.
        
        Returns:
            Statistics dict
        """
        total_intents = len(self._active_intents)
        total_occurrences = sum(
            record.occurrence_count
            for record in self._active_intents.values()
        )
        duplicates = sum(
            1 for record in self._active_intents.values()
            if record.occurrence_count > 1
        )
        
        return {
            "total_unique_intents": total_intents,
            "total_occurrences": total_occurrences,
            "duplicate_count": duplicates,
            "average_occurrences": (
                total_occurrences / total_intents if total_intents > 0 else 0
            )
        }
    
    def clear(self) -> None:
        """Clear all tracked intents."""
        self._active_intents.clear()
        self._normalized_index.clear()
        logger.info("Conflict detector cleared")
    
    def remove_intent(self, intent_hash: str) -> bool:
        """Remove Intent Hash from tracking.
        
        Args:
            intent_hash: Hash to remove
        
        Returns:
            True if removed, False if not found
        """
        if intent_hash in self._active_intents:
            del self._active_intents[intent_hash]
            
            # Remove from normalized index
            normalized = self._normalize_hash(intent_hash)
            if normalized in self._normalized_index:
                del self._normalized_index[normalized]
            
            logger.info(f"Removed intent: {intent_hash}")
            return True
        return False
    
    def export_state(self) -> Dict:
        """Export detector state for persistence.
        
        Returns:
            State dict with all active intents
        """
        return {
            "similarity_threshold": self.similarity_threshold,
            "active_intents": {
                intent_hash: {
                    "intent_hash": record.intent_hash,
                    "first_seen": record.first_seen,
                    "last_seen": record.last_seen,
                    "occurrence_count": record.occurrence_count,
                    "conversation_ids": record.conversation_ids,
                    "metadata": record.metadata
                }
                for intent_hash, record in self._active_intents.items()
            }
        }
    
    def import_state(self, state: Dict) -> None:
        """Import detector state from persistence.
        
        Args:
            state: State dict from export_state()
        """
        self.clear()
        
        if "similarity_threshold" in state:
            self.similarity_threshold = state["similarity_threshold"]
        
        if "active_intents" in state:
            for intent_hash, record_data in state["active_intents"].items():
                record = IntentRecord(
                    intent_hash=record_data["intent_hash"],
                    first_seen=record_data["first_seen"],
                    last_seen=record_data["last_seen"],
                    occurrence_count=record_data["occurrence_count"],
                    conversation_ids=record_data["conversation_ids"],
                    metadata=record_data["metadata"]
                )
                self._active_intents[intent_hash] = record
                
                normalized = self._normalize_hash(intent_hash)
                self._normalized_index[normalized] = intent_hash
        
        logger.info(f"Imported {len(self._active_intents)} intents")
