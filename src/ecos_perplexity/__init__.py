"""ECOS Perplexity SuperMemory Plugin.

Multi-session coordination plugin for Perplexity with:
- Intent Hash tracking and conflict detection
- Notion bidirectional sync
- MCP client for conversation history
- MICS integration for session orchestration

Authors: ECOS Development Team
Version: 0.1.0-alpha1
Created: 2026-03-02
"""

from ecos_perplexity.plugin import PerplexityPlugin

__version__ = "0.1.0-alpha1"
__all__ = ["PerplexityPlugin"]
