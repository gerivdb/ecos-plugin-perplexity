"""Unit tests for PerplexityPlugin.

Test coverage:
- Plugin initialization
- Configuration validation
- Health checks
- Manifest metadata
- Lifecycle management

Authors: ECOS Development Team
Version: 0.1.0-alpha1
Created: 2026-03-02
"""

import pytest
from ecos_perplexity.plugin import PerplexityPlugin, PluginStatus


class TestPluginInitialization:
    """Test plugin initialization and configuration."""
    
    def test_init_creates_instance(self):
        """Test plugin instance creation."""
        plugin = PerplexityPlugin()
        assert plugin is not None
        assert plugin.mcp_client is None
        assert plugin.config == {}
    
    def test_initialize_with_valid_config(self):
        """Test initialization with valid configuration."""
        plugin = PerplexityPlugin()
        config = {
            "mcp_server_url": "http://localhost:8080",
            "mcp_timeout": 15
        }
        
        plugin.initialize(config)
        
        assert plugin.mcp_client is not None
        assert plugin.config == config
        assert plugin._status == PluginStatus.READY
    
    def test_initialize_missing_mcp_url(self):
        """Test initialization fails without mcp_server_url."""
        plugin = PerplexityPlugin()
        
        with pytest.raises(ValueError, match="mcp_server_url required"):
            plugin.initialize({})
    
    def test_initialize_default_timeout(self):
        """Test initialization uses default timeout."""
        plugin = PerplexityPlugin()
        config = {"mcp_server_url": "http://localhost:8080"}
        
        plugin.initialize(config)
        
        assert plugin.mcp_client.timeout == 10  # Default


class TestHealthCheck:
    """Test plugin health check."""
    
    def test_health_check_not_initialized(self):
        """Test health check fails if not initialized."""
        plugin = PerplexityPlugin()
        assert plugin.health_check() is False
    
    def test_health_check_after_init(self):
        """Test health check succeeds after initialization."""
        plugin = PerplexityPlugin()
        plugin.initialize({"mcp_server_url": "http://localhost:8080"})
        
        assert plugin.health_check() is True
    
    def test_health_check_after_shutdown(self):
        """Test health check fails after shutdown."""
        plugin = PerplexityPlugin()
        plugin.initialize({"mcp_server_url": "http://localhost:8080"})
        plugin.shutdown()
        
        assert plugin.health_check() is False


class TestManifest:
    """Test plugin manifest."""
    
    def test_get_manifest(self):
        """Test manifest contains required fields."""
        plugin = PerplexityPlugin()
        manifest = plugin.get_manifest()
        
        assert manifest.name == "perplexity-supermemory"
        assert manifest.version == "0.1.0-alpha1"
        assert manifest.entry_point == "ecos_perplexity:PerplexityPlugin"
        assert "mcp_server_url" in manifest.config_schema["properties"]
        assert manifest.author == "ECOS Development Team"
    
    def test_manifest_config_schema(self):
        """Test manifest config schema structure."""
        plugin = PerplexityPlugin()
        manifest = plugin.get_manifest()
        schema = manifest.config_schema
        
        assert schema["type"] == "object"
        assert "mcp_server_url" in schema["required"]
        assert schema["properties"]["mcp_timeout"]["default"] == 10


class TestLifecycle:
    """Test plugin lifecycle management."""
    
    def test_shutdown_cleans_resources(self):
        """Test shutdown properly cleans resources."""
        plugin = PerplexityPlugin()
        plugin.initialize({"mcp_server_url": "http://localhost:8080"})
        
        plugin.shutdown()
        
        assert plugin._status == PluginStatus.SHUTDOWN
    
    def test_shutdown_idempotent(self):
        """Test shutdown can be called multiple times safely."""
        plugin = PerplexityPlugin()
        plugin.initialize({"mcp_server_url": "http://localhost:8080"})
        
        plugin.shutdown()
        plugin.shutdown()  # Should not raise
        
        assert plugin._status == PluginStatus.SHUTDOWN
