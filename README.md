# ECOS Perplexity SuperMemory Plugin

**Version**: 0.1.0-alpha1  
**Status**: Phase 0 POC  
**ECOS-CLI**: ≥ 4.5.0  
**Python**: ≥ 3.10

Perplexity SuperMemory coordination plugin for ECOS-CLI. Provides multi-session coordination, Intent Hash tracking, conflict detection, and bidirectional Notion sync.

---

## 🎯 Features

### Phase 0 POC (Current)
- ✅ **Plugin Infrastructure**: ECOSPlugin interface implementation
- ✅ **MCP Client**: Fetch Perplexity conversations (10 conversations POC)
- ✅ **Intent Hash Extraction**: Regex-based pattern matching
- ✅ **Conflict Detection**: Simple duplicate tracking
- ✅ **Health Monitoring**: Health checks via PluginManager

### Phase 1 MVP (Coming)
- ⏳ Historique complet (≥500 conversations)
- ⏳ Zeta-DAG patterns + ML clustering
- ⏳ PostgreSQL storage + pgvector
- ⏳ Notion bidirectional sync
- ⏳ MICS coordination integration
- ⏳ Grafana dashboard + Prometheus metrics

### Phase 2 Automation (Planned)
- ⏳ Auto-prompt generation
- ⏳ Conversation threading (merge similaires)
- ⏳ Constitutional validation L0-L5
- ⏳ Intelligence proactive (anomaly detection)

---

## 🚀 Installation

### Prerequisites
```bash
# ECOS-CLI must be installed first
pip install ecos-cli>=4.5.0
```

### Install Plugin
```bash
# From PyPI (when published)
pip install ecos-plugin-perplexity

# Or from source
git clone https://github.com/gerivdb/ecos-plugin-perplexity.git
cd ecos-plugin-perplexity
pip install -e .
```

### Verify Installation
```python
from tools.core import PluginManager

manager = PluginManager()
await manager.discover_plugins()
print(manager.list_plugins())
# Output: [{'name': 'perplexity-supermemory', 'version': '0.1.0-alpha1', ...}]
```

---

## ⚡ Quick Start

### 1. Configuration

Create `config/plugins/perplexity-supermemory.yaml`:
```yaml
mcp:
  server_url: "https://perplexity.ai/api/mcp"
  api_key: "your-mcp-api-key"

notion:
  api_key: "your-notion-api-key"
  database_id: "your-perplexity-intent-registry-id"
```

### 2. Load Plugin

```python
import asyncio
from tools.core import PluginManager

async def main():
    manager = PluginManager()
    
    # Discover available plugins
    await manager.discover_plugins()
    
    # Load Perplexity plugin
    config = {
        "mcp": {
            "server_url": "https://perplexity.ai/api/mcp",
            "api_key": "your-key"
        }
    }
    await manager.load_plugin("perplexity-supermemory", config)
    
    # Get plugin instance
    plugin = manager.get_plugin("perplexity-supermemory")
    
    # TODO: Use plugin (Phase 0 POC implementation ongoing)
    # conversations = await plugin.mcp_client.fetch_conversations(limit=10)
    # for conv in conversations:
    #     intent = plugin.extractor.extract(conv)
    #     conflict = plugin.detector.check_conflict(intent)

asyncio.run(main())
```

### 3. Health Check

```python
# Check plugin health
healthy = await manager.health_check("perplexity-supermemory")
print(f"Plugin healthy: {healthy}")

# Check all plugins
status = await manager.health_check_all()
print(status)
```

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md) (Coming)
- [Configuration Reference](docs/CONFIGURATION.md) (Coming)
- [API Reference](docs/API_REFERENCE.md) (Coming)
- [Development Guide](docs/DEVELOPMENT.md) (Coming)

---

## 🏛️ Architecture

```
ecos-plugin-perplexity/
├── src/
│   └── ecos_perplexity/
│       ├── __init__.py          # Plugin exports
│       ├── plugin.py            # PerplexityPlugin (ECOSPlugin impl)
│       ├── mcp/
│       │   └── client.py        # MCP client for Perplexity
│       ├── patterns/
│       │   ├── extractor.py     # Intent Hash extraction
│       │   └── conflict_detector.py
│       └── storage/
│           ├── pg_manager.py    # PostgreSQL storage (Phase 1)
│           └── notion_sync.py   # Notion sync (Phase 1)
├── tests/
│   ├── unit/
│   └── integration/
├── config/
│   └── plugin_config.example.yaml
├── docs/
│   └── ...
└── pyproject.toml
```

### Entry Point

```toml
[project.entry-points."ecos.plugins"]
perplexity = "ecos_perplexity:PerplexityPlugin"
```

The plugin is automatically discovered by ECOS-CLI `PluginManager` via Python entry points.

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repo
git clone https://github.com/gerivdb/ecos-plugin-perplexity.git
cd ecos-plugin-perplexity

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_plugin.py -v

# Coverage report
pytest --cov=ecos_perplexity --cov-report=html
open htmlcov/index.html
```

### Code Quality

```bash
# Format with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type check with MyPy
mypy src/
```

---

## 📦 Dependencies

### Runtime
- `ecos-cli>=4.5.0` - Core ECOS-CLI framework
- `mcp>=0.8.0` - Perplexity MCP client
- `notion-client>=2.0.0` - Notion API client
- `pydantic>=2.0.0` - Data validation
- `aiohttp>=3.9.0` - Async HTTP client
- `jsonschema>=4.20.0` - Config validation

### Development
- `pytest>=7.4.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting
- `black>=23.0.0` - Code formatting
- `ruff>=0.1.0` - Linting
- `mypy>=1.7.0` - Type checking

---

## 📈 Roadmap

| Phase | Timeline | Status | φ-CPS |
|-------|----------|--------|--------|
| **Phase 0 POC** | 02-04/03/2026 | 🟡 In Progress | +0.020 |
| **Phase 1 MVP** | 05-18/03/2026 | ⏳ Planned | +0.050 |
| **Phase 2 Automation** | 19/03-01/04/2026 | ⏳ Planned | +0.075 |

**Total Impact**: +0.145 φ (EMM-5 gap: 12.54% → 9.87%)

---

## 👥 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **GitHub**: https://github.com/gerivdb/ecos-plugin-perplexity
- **ECOS-CLI**: https://github.com/gerivdb/ECOS-CLI
- **Issues**: https://github.com/gerivdb/ECOS-CLI/issues/204 (Phase 0 POC)
- **Parent Issue**: https://github.com/gerivdb/ECOS-CLI/issues/200 (Master)

---

**IntentHash¹¹**: `0xECOS_PERPLEXITY_SUPERMEMORY_MASTER_H1_20260302`  
**Author**: ECOS Development Team  
**Created**: 2026-03-02
