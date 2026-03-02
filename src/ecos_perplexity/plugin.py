"""Perplexity Plugin main class implementing ECOSPlugin.

Provides:
- MCP client initialization and configuration
- Health checks and lifecycle management
- Plugin manifest metadata
- Integration with ECOS-CLI plugin system

Authors: ECOS Development Team
Version: 0.1.0-alpha1
Created: 2026-03-02
"""

import logging
from typing import Dict, Any, Optional

try:
    from tools.core.plugin_interface import ECOSPlugin, PluginManifest, PluginStatus
except ImportError:
    # Fallback for standalone testing
    from enum import Enum
    
    class PluginStatus(Enum):
        UNINITIALIZED = "uninitialized"
        READY = "ready"
        ERROR = "error"
        SHUTDOWN = "shutdown"
    
    class PluginManifest:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    class ECOSPlugin:
        def __init__(self):
            self._status = PluginStatus.UNINITIALIZED
            self._logger = logging.getLogger(self.__class__.__name__)
        
        def initialize(self, config: Dict[str, Any]) -> None:
            raise NotImplementedError
        
        def health_check(self) -> bool:
            raise NotImplementedError
        
        def get_manifest(self) -> PluginManifest:
            raise NotImplementedError
        
        def shutdown(self) -> None:
            raise NotImplementedError


from ecos_perplexity.mcp.client import PerplexityMCPClient


class PerplexityPlugin(ECOSPlugin):
    """Perplexity SuperMemory Plugin for ECOS-CLI.
    
    Provides multi-session coordination capabilities:
    - Intent Hash tracking across Perplexity conversations
    - Conflict detection (duplicate intents)
    - MCP client for conversation history access
    - Future: Notion bidirectional sync, pattern extraction, MICS integration
    
    Configuration:
        mcp_server_url (str): MCP server URL (required)
        mcp_timeout (int): Request timeout in seconds (default: 10)
        enable_notion_sync (bool): Enable Notion integration (default: False)
        notion_token (str): Notion API token (required if enable_notion_sync=True)
    
    Example:
        >>> plugin = PerplexityPlugin()
        >>> plugin.initialize({
        ...     "mcp_server_url": "http://localhost:8080",
        ...     "mcp_timeout": 15
        ... })
        >>> plugin.health_check()
        True
    """
    
    def __init__(self):
        """Initialize plugin instance."""
        super().__init__()
        self.mcp_client: Optional[PerplexityMCPClient] = None
        self.config: Dict[str, Any] = {}
        self._logger = logging.getLogger("PerplexityPlugin")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary
        
        Raises:
            ValueError: If mcp_server_url missing or invalid
            ConnectionError: If MCP server unreachable
        """
        self._logger.info("Initializing PerplexityPlugin...")
        
        # Validate required config
        mcp_server_url = config.get("mcp_server_url")
        if not mcp_server_url:
            raise ValueError("mcp_server_url required in plugin configuration")
        
        # Extract optional config
        mcp_timeout = config.get("mcp_timeout", 10)
        
        # Initialize MCP client
        try:
            self.mcp_client = PerplexityMCPClient(
                server_url=mcp_server_url,
                timeout=mcp_timeout
            )
            self._logger.info(f"MCP client initialized: {mcp_server_url}")
        except Exception as e:
            self._status = PluginStatus.ERROR
            raise ConnectionError(f"Failed to initialize MCP client: {e}")
        
        # Store config
        self.config = config
        
        # Future: Initialize Notion client if enabled
        if config.get("enable_notion_sync", False):
            self._logger.warning("Notion sync not yet implemented (Phase 1)")
        
        # Mark ready
        self._status = PluginStatus.READY
        self._logger.info("PerplexityPlugin initialized successfully")
    
    def health_check(self) -> bool:
        """Verify plugin health status.
        
        Checks:
        - Plugin status is READY
        - MCP client initialized
        - MCP client state valid
        
        Returns:
            True if healthy, False otherwise
        """
        if self._status != PluginStatus.READY:
            self._logger.warning(f"Plugin not ready: {self._status}")
            return False
        
        if not self.mcp_client:
            self._logger.error("MCP client not initialized")
            return False
        
        # Future: Add actual MCP server ping
        return True
    
    def get_manifest(self) -> PluginManifest:
        """Return plugin metadata and configuration schema.
        
        Returns:
            PluginManifest with complete metadata
        """
        return PluginManifest(
            name="perplexity-supermemory",
            version="0.1.0-alpha1",
            entry_point="ecos_perplexity:PerplexityPlugin",
            config_schema={
                "type": "object",
                "properties": {
                    "mcp_server_url": {
                        "type": "string",
                        "description": "MCP server URL",
                        "examples": ["http://localhost:8080"]
                    },
                    "mcp_timeout": {
                        "type": "integer",
                        "description": "MCP request timeout in seconds",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 60
                    },
                    "enable_notion_sync": {
                        "type": "boolean",
                        "description": "Enable Notion bidirectional sync (Phase 1+)",
                        "default": False
                    },
                    "notion_token": {
                        "type": "string",
                        "description": "Notion API token (if enable_notion_sync=True)"
                    }
                },
                "required": ["mcp_server_url"]
            },
            dependencies=[
                "ecos-cli>=4.5.0",
                "mcp>=0.8.0",
                "notion-client>=2.0.0",
                "pydantic>=2.0.0",
                "aiohttp>=3.9.0"
            ],
            description="Perplexity SuperMemory coordination plugin with MCP integration, Intent Hash tracking, and conflict detection",
            author="ECOS Development Team",
            homepage="https://github.com/gerivdb/ecos-plugin-perplexity",
            tags=["perplexity", "memory", "coordination", "mcp", "intent-hash"]
        )
    
    def shutdown(self) -> None:
        """Cleanup plugin resources.
        
        Closes MCP client connections and releases resources.
        """
        self._logger.info("Shutting down PerplexityPlugin...")
        
        if self.mcp_client:
            # Future: Close MCP client connections
            self.mcp_client.reset()
            self._logger.info("MCP client cleaned up")
        
        self._status = PluginStatus.SHUTDOWN
        self._logger.info("PerplexityPlugin shutdown complete")
