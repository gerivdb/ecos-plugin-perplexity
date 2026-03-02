"""Intent Hash Pattern Extractor.

Extracts Intent Hash markers from Perplexity conversation text.

Authors: ECOS Development Team
Created: 2026-03-02
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Fuzzy ternary confidence levels."""
    LOW = 0.0
    MEDIUM = 0.5
    HIGH = 1.0


@dataclass
class ExtractedIntent:
    """Extracted Intent Hash with metadata."""
    intent_hash: str
    pattern_type: str
    confidence: float
    position: int
    context: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IntentHashExtractor:
    """Extract Intent Hash patterns from text.
    
    Supports multiple formats:
    - IntentHash¹¹: 0xH0_DESCRIPTION_YYYYMMDD
    - IntentHash¹⁰: 0xH1_DESCRIPTION_YYYYMMDD
    - IntentHash: 0xDESCRIPTION_HASH
    - Legacy: IntentHash: DESCRIPTION
    """
    
    # Regex patterns for different Intent Hash formats
    PATTERNS = {
        "h0_superscript": (
            r"IntentHash[\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079\u00b9\u00b9]+\s*:\s*"
            r"(0x[A-Za-z0-9_]+)"
        ),
        "h0_standard": r"IntentHash\s*:\s*(0x[A-Z][A-Z0-9_]+)",
        "h0_h1_prefix": r"IntentHash[\u00b9\u00b9]+\s*:\s*(0x(?:H0|H1)_[A-Z0-9_]+)",
        "legacy": r"IntentHash\s*:\s*([A-Z][A-Za-z0-9_\-]+)",
        "hex_only": r"\b(0x[A-F0-9]{8,})\b",  # Generic hex values
    }
    
    def __init__(self):
        """Initialize extractor with compiled patterns."""
        self.compiled_patterns = {
            name: re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            for name, pattern in self.PATTERNS.items()
        }
    
    def extract_intent_hash(
        self,
        text: str,
        min_confidence: float = 0.5
    ) -> List[ExtractedIntent]:
        """Extract all Intent Hashes from text.
        
        Args:
            text: Text to extract from
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of ExtractedIntent objects
        """
        extractions = []
        seen_hashes = set()  # Deduplicate
        
        for pattern_name, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                intent_hash = match.group(1)
                
                # Skip duplicates
                if intent_hash in seen_hashes:
                    continue
                seen_hashes.add(intent_hash)
                
                # Calculate confidence based on pattern type
                confidence = self._calculate_confidence(
                    pattern_name,
                    intent_hash,
                    text,
                    match.start()
                )
                
                if confidence < min_confidence:
                    continue
                
                # Extract surrounding context (50 chars before/after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                
                extractions.append(
                    ExtractedIntent(
                        intent_hash=intent_hash,
                        pattern_type=pattern_name,
                        confidence=confidence,
                        position=match.start(),
                        context=context,
                        metadata={
                            "length": len(intent_hash),
                            "has_prefix": intent_hash.startswith("0x"),
                            "match_group": match.group(0)
                        }
                    )
                )
        
        # Sort by position
        extractions.sort(key=lambda x: x.position)
        return extractions
    
    def _calculate_confidence(
        self,
        pattern_name: str,
        intent_hash: str,
        text: str,
        position: int
    ) -> float:
        """Calculate confidence score for extracted hash.
        
        Args:
            pattern_name: Name of matched pattern
            intent_hash: Extracted hash value
            text: Full text
            position: Match position
        
        Returns:
            Confidence score [0.0, 0.5, 1.0]
        """
        confidence = ConfidenceLevel.MEDIUM.value  # Default
        
        # High confidence for superscript patterns
        if pattern_name == "h0_superscript":
            confidence = ConfidenceLevel.HIGH.value
        
        # High confidence for H0/H1 prefix
        elif pattern_name == "h0_h1_prefix":
            confidence = ConfidenceLevel.HIGH.value
        
        # Medium confidence for standard format
        elif pattern_name == "h0_standard":
            confidence = ConfidenceLevel.MEDIUM.value
        
        # Low confidence for hex-only (could be false positive)
        elif pattern_name == "hex_only":
            confidence = ConfidenceLevel.LOW.value
        
        # Boost confidence if hash has date suffix (YYYYMMDD)
        if re.search(r"\d{8}$", intent_hash):
            confidence = min(1.0, confidence + 0.2)
        
        # Boost if preceded by "IntentHash" keyword
        context_before = text[max(0, position - 20):position]
        if "IntentHash" in context_before:
            confidence = min(1.0, confidence + 0.1)
        
        # Reduce if hash is too short (likely false positive)
        if len(intent_hash) < 10:
            confidence = max(0.0, confidence - 0.3)
        
        # Quantize to ternary fuzzy levels
        if confidence >= 0.75:
            return ConfidenceLevel.HIGH.value
        elif confidence >= 0.35:
            return ConfidenceLevel.MEDIUM.value
        else:
            return ConfidenceLevel.LOW.value
    
    def extract_from_conversation(
        self,
        conversation: Dict[str, Any],
        include_messages: bool = True
    ) -> List[ExtractedIntent]:
        """Extract Intent Hashes from full conversation.
        
        Args:
            conversation: Conversation dict with messages
            include_messages: Extract from message contents
        
        Returns:
            List of ExtractedIntent objects
        """
        all_extractions = []
        
        # Extract from title
        if "title" in conversation:
            title_extractions = self.extract_intent_hash(
                conversation["title"],
                min_confidence=0.5
            )
            for extraction in title_extractions:
                extraction.metadata["source"] = "title"
            all_extractions.extend(title_extractions)
        
        # Extract from messages
        if include_messages and "messages" in conversation:
            for idx, message in enumerate(conversation["messages"]):
                if "content" in message:
                    msg_extractions = self.extract_intent_hash(
                        message["content"],
                        min_confidence=0.5
                    )
                    for extraction in msg_extractions:
                        extraction.metadata["source"] = "message"
                        extraction.metadata["message_idx"] = idx
                        extraction.metadata["message_role"] = message.get("role")
                    all_extractions.extend(msg_extractions)
        
        return all_extractions
    
    def extract_metadata(
        self,
        text: str
    ) -> Dict[str, Any]:
        """Extract additional metadata from text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Metadata dict with tags, dates, etc.
        """
        metadata = {
            "tags": [],
            "dates": [],
            "phases": [],
            "repos": []
        }
        
        # Extract tags (#hashtag)
        tag_pattern = re.compile(r"#([A-Za-z0-9_\-]+)")
        metadata["tags"] = [m.group(1) for m in tag_pattern.finditer(text)]
        
        # Extract dates (YYYY-MM-DD or YYYYMMDD)
        date_pattern = re.compile(r"\b(\d{4}[-/]?\d{2}[-/]?\d{2})\b")
        metadata["dates"] = [m.group(1) for m in date_pattern.finditer(text)]
        
        # Extract phase markers (Phase 0, Phase 1, etc.)
        phase_pattern = re.compile(r"Phase\s+(\d+)", re.IGNORECASE)
        metadata["phases"] = [int(m.group(1)) for m in phase_pattern.finditer(text)]
        
        # Extract repo references (owner/repo)
        repo_pattern = re.compile(r"([a-z0-9_\-]+)/([a-z0-9_\-]+)", re.IGNORECASE)
        metadata["repos"] = [
            f"{m.group(1)}/{m.group(2)}"
            for m in repo_pattern.finditer(text)
            if "/" in m.group(0)  # Ensure it's a repo path
        ]
        
        return metadata
    
    def validate_intent_hash(
        self,
        intent_hash: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate Intent Hash format.
        
        Args:
            intent_hash: Hash to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Must start with 0x or be uppercase
        if not (intent_hash.startswith("0x") or intent_hash[0].isupper()):
            return False, "Intent Hash must start with '0x' or uppercase letter"
        
        # Length check
        if len(intent_hash) < 8:
            return False, "Intent Hash too short (minimum 8 characters)"
        
        if len(intent_hash) > 100:
            return False, "Intent Hash too long (maximum 100 characters)"
        
        # Character validation for 0x hashes
        if intent_hash.startswith("0x"):
            valid_chars = set("0123456789ABCDEFabcdef_")
            if not all(c in valid_chars for c in intent_hash[2:]):
                return False, "Invalid characters in hex Intent Hash"
        
        return True, None
