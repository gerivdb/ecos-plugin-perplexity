"""Perplexity Plugin Main Entry Point.

Implements ECOSPlugin interface for ECOS-CLI integration.
"""

from typing import Dict, Any, Optional, List
import logging

from tools.core.plugin_interface import (
    ECOSPlugin,
    PluginManifest,
    PluginStatus,
    PluginInitializationError
)

from ecos_perplexity.mcp.client import (
    PerplexityMCPClient,
    MCPResponseState
)
from ecos_perplexity.patterns.extractor import (
    IntentHashExtractor,
    ExtractedIntent
)
from ecos_perplexity.patterns.conflict_detector import (
    ConflictDetector,
    ConflictType
)


logger = logging.getLogger(__name__)


class PerplexityPlugin(ECOSPlugin):
    """Perplexity SuperMemory coordination plugin.
    
    Provides:
    - MCP client for Perplexity conversation history
    - Intent Hash extraction and tracking
    - Conflict detection across sessions
    - Notion sync for Meta-Roadmap (Phase 1)
    
    Phase 0 POC Features:
    - Fetch 10 conversations from MCP
    - Extract Intent Hashes with confidence scoring
    - Detect HARD/SOFT conflicts
    - Health monitoring
    """
    
    def __init__(self):
        super().__init__()
        self.mcp_client: Optional[PerplexityMCPClient] = None
        self.extractor: Optional[IntentHashExtractor] = None
        self.detector: Optional[ConflictDetector] = None
        self.notion_sync: Optional[Any] = None  # Phase 1
        
        # Component initialization tracking
        self._components_initialized = {
            "mcp_client": False,
            "extractor": False,
            "detector": False
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration.
        
        Args:
            config: Plugin configuration with MCP and Notion settings
        
        Raises:
            PluginInitializationError: If required config missing or init fails
        """
        try:
            self._status = PluginStatus.INITIALIZING
            self._logger.info("Initializing PerplexityPlugin...")
            
            # Validate required config
            if "mcp" not in config:
                raise ValueError("MCP configuration required")
            
            mcp_config = config["mcp"]
            if "server_url" not in mcp_config or "api_key" not in mcp_config:
                raise ValueError("MCP server_url and api_key required")
            
            # Initialize MCP client
            self._logger.info("Initializing MCP client...")
            self.mcp_client = PerplexityMCPClient(
                server_url=mcp_config["server_url"],
                api_key=mcp_config["api_key"],
                timeout=mcp_config.get("timeout", 30),
                max_retries=mcp_config.get("max_retries", 3)
            )
            self._components_initialized["mcp_client"] = True
            
            # Initialize Intent Hash extractor
            self._logger.info("Initializing Intent Hash extractor...")
            self.extractor = IntentHashExtractor()
            self._components_initialized["extractor"] = True
            
            # Initialize conflict detector
            self._logger.info("Initializing conflict detector...")
            similarity_threshold = config.get(
                "conflict_detection", {}
            ).get("similarity_threshold", 0.85)
            self.detector = ConflictDetector(
                similarity_threshold=similarity_threshold
            )
            self._components_initialized["detector"] = True
            
            # TODO Phase 1: Initialize Notion sync
            # if "notion" in config:
            #     self.notion_sync = NotionSyncManager(config["notion"])
            
            self._status = PluginStatus.READY
            self._logger.info(
                "PerplexityPlugin initialized successfully "
                f"(components: {self._components_initialized})"
            )
        
        except ValueError as e:
            self._status = PluginStatus.ERROR
            self._logger.error(f"Configuration error: {e}")
            raise PluginInitializationError(f"Invalid configuration: {e}")
        
        except Exception as e:
            self._status = PluginStatus.ERROR
            self._logger.error(f"Initialization failed: {e}")
            raise PluginInitializationError(
                f"Failed to initialize PerplexityPlugin: {e}"
            )
    
    def health_check(self) -> bool:
        """Check plugin health status.
        
        Returns:
            True if all components operational
        """
        if self._status != PluginStatus.READY:
            self._logger.warning(f"Plugin not ready (status: {self._status})")
            return False
        
        # Check all components initialized
        if not all(self._components_initialized.values()):
            self._logger.error(
                f"Components not initialized: {self._components_initialized}"
            )
            return False
        
        # Check MCP client connectivity (async, so can't ping here)
        # In real usage, would do: asyncio.run(self.mcp_client.ping())
        if self.mcp_client is None or self.mcp_client._closed:
            self._logger.error("MCP client not available")
            return False
        
        # Check other components exist
        if self.detector is None or self.extractor is None:
            self._logger.error("Core components missing")
            return False
        
        self._logger.debug("Health check passed")
        return True
    
    async def fetch_and_analyze_conversations(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Fetch conversations and analyze Intent Hashes.
        
        Phase 0 POC workflow:
        1. Fetch conversations from MCP
        2. Extract Intent Hashes
        3. Check for conflicts
        4. Return analysis results
        
        Args:
            limit: Number of conversations to fetch
        
        Returns:
            Analysis results dict
        """
        if self._status != PluginStatus.READY:
            raise RuntimeError("Plugin not initialized")
        
        results = {
            "conversations_fetched": 0,
            "intents_extracted": [],
            "conflicts_detected": [],
            "statistics": {}
        }
        
        try:
            # Fetch conversations
            self._logger.info(f"Fetching {limit} conversations...")
            response = await self.mcp_client.fetch_conversations(limit=limit)
            
            if response.state != MCPResponseState.SUCCESS:
                self._logger.error(f"MCP fetch failed: {response.error}")
                return results
            
            conversations = response.data
            results["conversations_fetched"] = len(conversations)
            self._logger.info(f"Fetched {len(conversations)} conversations")
            
            # Process each conversation
            for conv in conversations:
                # Fetch full conversation detail
                detail_response = await self.mcp_client.get_conversation_detail(
                    conversation_id=conv.id,
                    include_messages=True
                )
                
                if detail_response.state != MCPResponseState.SUCCESS:
                    self._logger.warning(
                        f"Failed to fetch detail for {conv.id}: "
                        f"{detail_response.error}"
                    )
                    continue
                
                conv_detail = detail_response.data
                
                # Extract Intent Hashes
                extractions = self.extractor.extract_from_conversation(
                    {
                        "title": conv.title,
                        "messages": [
                            {
                                "content": msg.content,
                                "role": msg.role
                            }
                            for msg in conv_detail["messages"]
                        ]
                    },
                    include_messages=True
                )
                
                # Check for conflicts and track
                for extraction in extractions:
                    intent_hash = extraction.intent_hash
                    
                    # Check conflict before tracking
                    conflict = self.detector.check_conflict(
                        intent_hash,
                        check_similarity=True
                    )
                    
                    if conflict.conflict_type != ConflictType.NONE:
                        results["conflicts_detected"].append({
                            "intent_hash": intent_hash,
                            "conflict_type": conflict.conflict_type.value,
                            "similarity_score": conflict.similarity_score,
                            "message": conflict.message,
                            "conversation_id": conv.id
                        })
                        self._logger.warning(
                            f"Conflict detected: {conflict.message}"
                        )
                    
                    # Track intent
                    self.detector.track_intent(
                        intent_hash=intent_hash,
                        conversation_id=conv.id,
                        metadata={
                            "confidence": extraction.confidence,
                            "pattern_type": extraction.pattern_type,
                            "source": extraction.metadata.get("source")
                        }
                    )
                    
                    results["intents_extracted"].append({
                        "intent_hash": intent_hash,
                        "confidence": extraction.confidence,
                        "pattern_type": extraction.pattern_type,
                        "conversation_id": conv.id
                    })
            
            # Get detector statistics
            results["statistics"] = self.detector.get_statistics()
            
            self._logger.info(
                f"Analysis complete: {results['conversations_fetched']} convs, "
                f"{len(results['intents_extracted'])} intents, "
                f"{len(results['conflicts_detected'])} conflicts"
            )
        
        except Exception as e:
            self._logger.error(f"Analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def get_manifest(self) -> PluginManifest:
        """Return plugin manifest.
        
        Returns:
            PluginManifest with metadata and config schema
        """
        return PluginManifest(
            name="perplexity-supermemory",
            version="0.1.0-alpha1",
            entry_point="ecos_perplexity:PerplexityPlugin",
            config_schema={
                "type": "object",
                "properties": {
                    "mcp": {
                        "type": "object",
                        "properties": {
                            "server_url": {"type": "string"},
                            "api_key": {"type": "string"},
                            "timeout": {"type": "integer", "default": 30},
                            "max_retries": {"type": "integer", "default": 3}
                        },
                        "required": ["server_url", "api_key"]
                    },
                    "notion": {
                        "type": "object",
                        "properties": {
                            "api_key": {"type": "string"},
                            "database_id": {"type": "string"},
                        },
                        "required": ["api_key", "database_id"]
                    },
                    "conflict_detection": {
                        "type": "object",
                        "properties": {
                            "similarity_threshold": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "default": 0.85
                            }
                        }
                    }
                },
                "required": ["mcp"]
            },
            dependencies=[
                "mcp>=0.8.0",
                "notion-client>=2.0.0",
                "aiohttp>=3.9.0",
                "pydantic>=2.0.0"
            ],
            description="Perplexity SuperMemory coordination plugin for ECOS-CLI",
            author="ECOS Development Team",
            homepage="https://github.com/gerivdb/ecos-plugin-perplexity",
            tags=["perplexity", "memory", "coordination", "mcp", "notion"]
        )
    
    def shutdown(self) -> None:
        """Cleanup plugin resources."""
        try:
            self._logger.info("Shutting down PerplexityPlugin...")
            
            # Close MCP client
            if self.mcp_client and not self.mcp_client._closed:
                # Note: In async context would do: await self.mcp_client.close()
                # For now just mark as closed
                self.mcp_client._closed = True
            
            # Clear detector state (optional)
            # if self.detector:
            #     self.detector.clear()
            
            self._status = PluginStatus.SHUTDOWN
            self._logger.info("PerplexityPlugin shutdown complete")
        
        except Exception as e:
            self._logger.error(f"Shutdown error: {e}")
