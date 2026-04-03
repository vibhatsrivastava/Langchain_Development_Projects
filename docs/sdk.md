# LangChain Development SDK (`langchain-dev-tools`)

> **Accelerate LangChain project development with automated scaffolding, composable integrations, and production-ready defaults.**

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Available Integrations](#available-integrations)
- [Command Reference](#command-reference)
- [Integration Guide](#integration-guide)
- [Roadmap](#roadmap)
- [FAQ](#faq)

---

## Introduction

The **LangChain Development SDK** (`langchain-dev-tools`) is a command-line tool that automates LangChain project scaffolding, eliminating manual boilerplate and reducing project setup time from **15 minutes to under 2 minutes**.

### Why Use It?

**Before SDK:**
- Manually create directory structure (`src/`, `tests/`)
- Copy-paste `sys.path` boilerplate from existing projects
- Configure `.env` files with 10+ environment variables
- Write pytest fixtures for mocking LLMs, vector stores, caches
- Add integration code (pgvector, Redis, Langfuse) from scratch
- Update root README with new project entry
- **Total time: ~15 minutes per project**

**With SDK:**
```powershell
langchain-dev new-project 05_sentiment_analysis --arch lcel --integrations langfuse
# ✅ Done in <2 minutes
```

The SDK generates:
- Complete project structure with tests (90% coverage template)
- Pre-configured `.env.example` with integration variables
- Integration-specific code (vector stores, caching, tracing)
- pytest fixtures for mocking all services
- README with setup instructions
- Automatic root README update

---

## Features

### 🏗️ **Project Scaffolding**
- **3 base architectures**: LCEL Chain, LangGraph Agent, Custom (minimal)
- **Composable integrations**: Mix-and-match vector stores, caching, observability
- **Project naming convention**: Enforces `NN_descriptive_name` pattern
- **Auto-generated tests**: pytest fixtures, conftest boilerplate

### 🔌 **Built-in Foundations** (Always Available)
Standard infrastructure shared across all projects:
- ✅ **Ollama LLM** — `get_llm()`, `get_chat_llm()`, `get_embeddings()`
- ✅ **HashiCorp Vault** — Secret management with `.env` fallback
- ✅ **Rate Limiting** — Token bucket algorithm for API rate limits
- ✅ **Retry Logic** — Exponential backoff for transient failures
- ✅ **Token Counting** — Track LLM usage and estimate costs
- ✅ **In-Memory Cache** — LRU cache for simple projects
- ✅ **Structured Logging** — `get_logger()` with `LOG_LEVEL` support

### 🎛️ **Optional Integrations** (v0.1.0)
Project-specific modules generated on demand:

| Category | Integration | Description |
|---|---|---|
| **Vector Stores** | Chroma | Local vector DB (ideal for development) |
| | pgvector | PostgreSQL + pgvector (production-ready) |
| | FAISS | Facebook AI Similarity Search (high-performance local) |
| **Caching** | Redis | In-memory caching for LLM responses |
| **Observability** | Langfuse | Open-source LLM tracing, cost tracking, evals |

### 🛠️ **Developer Tools**
- `langchain-dev validate` — Check project structure, .env vars
- `langchain-dev test` — Run pytest with coverage reporting
- `langchain-dev integrations list` — Discover available integrations
- `langchain-dev integrations info <name>` — Integration details, prerequisites

---

## Installation

### Prerequisites
- Python 3.10+ (matches repo test matrix)
- Git repository with shared `.venv` at root
- `.env` file configured (copy from `.env.example`)

### Install SDK (Editable Mode)

```powershell
# From repo root
pip install -e cli/
```

This installs the `langchain-dev` command globally in your `.venv`.

### Verify Installation

```powershell
langchain-dev --version
# Output: langchain-dev, version 0.1.0

langchain-dev --help
# Shows available commands
```

---

## Quick Start

###  Example 1: Basic LCEL Chain

```powershell
langchain-dev new-project 05_hello_lcel --arch lcel

cd projects/05_hello_lcel
cp .env.example .env
# Edit .env with your Ollama settings

python src/main.py
```

**Generated files:**
```
05_hello_lcel/
├── src/
│   └── main.py          # LCEL chain: prompt | llm | parser
├── tests/
│   ├── conftest.py      # pytest fixtures (mock_llm, mock_chat_llm)
│   └── test_main.py     # Unit tests with mocked LLM
├── requirements.txt     # Project dependencies
├── .env.example         # Environment variable template
└── README.md            # Setup instructions
```

### Example 2: RAG with pgvector + Langfuse

```powershell
langchain-dev new-project 06_rag_system \\
    --arch lcel \\
    --integrations pgvector,langfuse

cd projects/06_rag_system

# Setup PostgreSQL pgvector
psql -U postgres -c "CREATE DATABASE langchain_vectors;"
psql -U postgres -d langchain_vectors -c "CREATE EXTENSION vector;"
psql -U postgres -d langchain_vectors -f src/db/schema.sql

# Configure .env
cp .env.example .env
# Add POSTGRES_*, LANGFUSE_* variables

python src/main.py
```

**Generated files (in addition to base):**
```
06_rag_system/
├── src/
│   ├── main.py
│   ├── db/
│   │   ├── vector_store.py   # PgVectorStore class
│   │   └── schema.sql        # pgvector schema
│   └── monitoring/
│       └── tracing.py        # Langfuse tracing setup
├── tests/
│   └── conftest.py           # + pgvector/Langfuse mock fixtures
└── .env.example              # + POSTGRES_*, LANGFUSE_* vars
```

### Example 3: Interactive Mode

```powershell
langchain-dev new-project

# 🚀 LangChain Project Generator
# 
# Project name pattern: 05_my_project_name
# Enter project name: 07_chatbot
# 
# Available architectures:
#   lcel: LangChain Expression Language chain
#   langgraph: Stateful multi-agent system
#   custom: Minimal scaffold
# Select architecture [lcel]: langgraph
# 
# Available integrations:
#   VECTOR_STORE:
#     - chroma: Local vector database
#     - pgvector: PostgreSQL vector store
#     - faiss: High-performance local vectors
#   CACHE:
#     - redis: In-memory caching
#   OBSERVABILITY:
#     - langfuse: LLM tracing and observability
# 
# Select integrations (comma-separated, or 'none'): redis,langfuse
# 
# ✅ Project created successfully!
```

---

## Architecture

### Built-in vs Optional Integrations

The SDK uses a **two-tier integration model**:

#### **Built-in Integrations** (Always Available)
- **Location**: `common/` directory at repo root
- **Usage**: Imported by all projects (never duplicated)
- **Examples**: Ollama LLM, Vault, rate limiting, retry, caching
- **SDK behavior**: Generates import statements only

```python
# Generated in src/main.py
from common.llm_factory import get_llm
from common.utils import get_logger
from common.rate_limiter import get_ollama_rate_limiter
```

#### **Optional Integrations** (User-Selected)
- **Location**: Generated in project-specific `src/` directories
- **Usage**: Only included when explicitly requested via `--integrations`
- **Examples**: pgvector, Redis, Langfuse, Chroma, FAISS
- **SDK behavior**: Generates new Python files, adds dependencies, env vars

```python
# Generated in src/db/vector_store.py (when --integrations pgvector)
class PgVectorStore:
    def __init__(self):
        # PostgreSQL connection logic
        ...
```

### Template System

The SDK uses **Jinja2 templates** for code generation:

**Template Variables:**
- `{{ project_name }}` — Full project name (e.g., `05_sentiment_analysis`)
- `{{ project_number }}` — Project number (e.g., `05`)
- `{{ project_description }}` — Human-readable description
- `{{ architecture }}` — Selected architecture (`lcel`, `langgraph`, `custom`)
- `{{ integrations }}` — List of selected integrations
- `{{ has_vector_store }}`, `{{ has_cache }}`, `{{ has_observability }}` — Boolean flags

**Conditional Generation:**
```jinja2
{% if has_observability %}
from common.integrations.observability import init_tracing
{% endif %}
```

---

## Available Integrations

### Vector Stores

#### **Chroma** (`chroma`)
- **Description**: Local vector database (ideal for development)
- **Dependencies**: `chromadb>=0.4.22`, `langchain-chroma>=0.1.0`
- **Prerequisites**: None (local storage)
- **Use Case**: Prototyping, small datasets, local development
- **Generated Files**: `src/db/vector_store.py`

#### **pgvector** (`pgvector`)
- **Description**: PostgreSQL vector store (production-ready)
- **Dependencies**: `psycopg2-binary>=2.9.9`, `pgvector>=0.2.4`, `langchain-postgres>=0.0.6`
- **Prerequisites**: PostgreSQL 15+, `CREATE EXTENSION vector;`
- **Use Case**: Production RAG systems, enterprise deployments
- **Generated Files**: `src/db/vector_store.py`, `src/db/schema.sql`

#### **FAISS** (`faiss`)
- **Description**: Facebook AI Similarity Search (high-performance local)
- **Dependencies**: `faiss-cpu>=1.7.4`, `langchain-community>=0.0.20`
- **Prerequisites**: None (local index files)
- **Use Case**: Large local datasets, CPU-optimized search
- **Generated Files**: `src/db/vector_store.py`

### Caching

#### **Redis** (`redis`)
- **Description**: In-memory caching for LLM responses
- **Dependencies**: `redis>=5.0.0`, `langchain-redis>=0.1.0`
- **Prerequisites**: Redis server running at `REDIS_HOST:REDIS_PORT`
- **Use Case**: Cache expensive LLM calls, rate limiting, session storage
- **Generated Files**: `src/cache/redis_cache.py`

### Observability

#### **Langfuse** (`langfuse`)
- **Description**: Open-source LLM tracing and cost tracking
- **Dependencies**: `langfuse>=2.0.0`, `langchain-langfuse>=2.0.0`
- **Prerequisites**: Langfuse account (cloud.langfuse.com or self-hosted)
- **Use Case**: Production monitoring, cost tracking, user feedback
- **Generated Files**: `src/monitoring/tracing.py`

---

## Command Reference

### `langchain-dev new-project`

Create a new LangChain project from templates.

**Usage:**
```powershell
langchain-dev new-project [PROJECT_NAME] [OPTIONS]
```

**Options:**
| Flag | Description | Example |
|---|---|---|
| `--architecture`, `-a` | Base architecture | `--arch lcel` |
| `--integrations`, `-i` | Comma-separated integrations | `-i pgvector,langfuse` |
| `--projects-dir` | Projects directory | `--projects-dir custom_projects` |
| `--non-interactive` | Non-interactive mode | (flag only) |

**Examples:**
```powershell
# Interactive mode (recommended)
langchain-dev new-project

# Non-interactive
langchain-dev new-project 05_chatbot --arch langgraph -i redis,langfuse

# Minimal custom project
langchain-dev new-project 06_custom --arch custom --integrations none
```

---

### `langchain-dev integrations`

Discover and manage integration modules.

#### `integrations list`
List all available integrations.

**Usage:**
```powershell
langchain-dev integrations list [OPTIONS]
```

**Options:**
| Flag | Description |
|---|---|
| `--category`, `-c` | Filter by category (`vector_store`, `cache`, `observability`) |

**Examples:**
```powershell
# List all
langchain-dev integrations list

# List only vector stores
langchain-dev integrations list --category vector_store
```

#### `integrations info`
Show detailed integration information.

**Usage:**
```powershell
langchain-dev integrations info <INTEGRATION_NAME>
```

**Examples:**
```powershell
# pgvector details
langchain-dev integrations info pgvector

# Output:
# 📦 pgvector
# PostgreSQL vector store with pgvector extension (production-ready)
# 
# Category: vector_store
# 
# Dependencies:
#   - psycopg2-binary>=2.9.9
#   - pgvector>=0.2.4
#   - langchain-postgres>=0.0.6
# 
# Environment Variables:
#   POSTGRES_HOST=localhost
#   POSTGRES_PORT=5432
#   ...
# 
# Prerequisites:
#   - PostgreSQL 15+ installed and running
#   - pgvector extension: CREATE EXTENSION vector;
#   ...
```

---

### `langchain-dev validate`

Validate project structure and configuration.

**Usage:**
```powershell
langchain-dev validate [PROJECT_PATH]
```

**Checks:**
- ✅ Required directories (`src/`, `tests/`)
- ✅ Required files (`main.py`, `conftest.py`, `requirements.txt`, `.env.example`, `README.md`)
- ✅ `.env` file exists

**Examples:**
```powershell
# Validate current directory
langchain-dev validate

# Validate specific project
langchain-dev validate projects/05_my_project
```

---

### `langchain-dev test`

Run project tests with pytest.

**Usage:**
```powershell
langchain-dev test [PROJECT_PATH] [OPTIONS]
```

**Options:**
| Flag | Description |
|---|---|
| `--coverage` | Run with coverage report (enforces 90% minimum) |
| `--verbose`, `-v` | Verbose pytest output |

**Examples:**
```powershell
# Run tests in current directory
langchain-dev test

# Run with coverage
langchain-dev test --coverage

# Run specific project with verbose output
langchain-dev test projects/05_chatbot --coverage -v
```

---

## Integration Guide

### Adding a New Integration to a Project

**Scenario**: You have an existing project `05_basic_chain` and want to add Langfuse tracing.

**Options:**

#### Option 1: Manual Integration
1. **Add dependencies**: Edit `requirements.txt`
   ```
   langfuse>=2.0.0
   langchain-langfuse>=2.0.0
   ```

2. **Add environment variables**: Edit `.env.example`
   ```
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

3. **Copy integration code**: From `cli/langchain_dev/templates/integrations/langfuse/`
   ```powershell
   mkdir src/monitoring
   # Copy tracing.py template manually
   ```

4. **Add test fixtures**: Edit `tests/conftest.py`
   ```python
   @pytest.fixture
   def mock_langfuse_client(mocker):
       # ... copy fixture code from integration
   ```

#### Option 2: Regenerate Project (Future Feature)
```powershell
# Planned for v0.2.0
langchain-dev add-integration langfuse
```

---

### Creating Custom Integrations

**For v0.1.0**, integrations are built-in. **v0.3.0+** will support custom integration plugins.

**Plugin Structure (future):**
```python
# cli/langchain_dev/integrations/custom/my_integration.py
from ..base import IntegrationModule

class MyIntegration(IntegrationModule):
    @property
    def name(self) -> str:
        return "my_integration"
    
    # Implement get_dependencies(), get_env_vars(), etc.
```

---

## Roadmap

### **v0.1.0 (Current)** — Production-Ready Foundation

**Built-in Enhancements:**
- ✅ Rate limiting (token bucket algorithm)
- ✅ Retry logic (exponential backoff)
- ✅ Token counting and cost estimation
- ✅ Error handling (custom exceptions)
- ✅ In-memory LRU cache

**Optional Integrations:**
- ✅ Chroma, pgvector, FAISS (vector stores)
- ✅ Redis (caching)
- ✅ Langfuse (observability)

**CLI Commands:**
- ✅ `new-project` (interactive + non-interactive)
- ✅ `integrations list/info`
- ✅ `validate`
- ✅ `test`

**Target**: Cover 80% of production use cases with 20% of possible integrations

---

### **v0.2.0** — Expanded Ecosystem (Q2 2026)

**New Integrations:**
- Pinecone, Weaviate, Qdrant (cloud vector stores)
- LangSmith (LangChain official tracing)
- Supabase (PostgreSQL + Auth)
- MongoDB (agent state persistence)
- Celery (background tasks)
- LangServe (Fast API deployment)

**New Commands:**
- `add-integration` — Add integration to existing project
- `migrate` — Update existing projects to new SDK version
- `init` — Initialize SDK in existing repo

**Enhanced Features:**
- Custom template directory support (`--template-dir`)
- Project template export/import (share team templates)
- Pre-commit hooks for validation

---

### **v0.3.0** — Advanced and Specialized (Q3 2026)

**Specialized Integrations:**
- Neo4j (graph RAG)
- Elasticsearch (hybrid search)
- Kafka (event-driven agents)
- RabbitMQ (message queuing)

**Advanced Features:**
- **Custom integration plugins** — Developers create their own integration modules
- **Multi-project orchestration** — Manage suite of related projects
- **Code generation from docs** — Generate RAG projects from documentation URLs

**Enterprise Features:**
- Team templates (organization-specific best practices)
- Compliance validation (check for security patterns, PII handling)
- RBAC integration (role-based project templates)

---

### **v1.0.0** — Production Milestone (Q4 2026)

**Stability Guarantees:**
- Semantic versioning with backward compatibility
- 1-year LTS support for enterprise users

**Distribution:**
- PyPI package: `pip install langchain-dev-tools`
- Standalone binaries (Windows, macOS, Linux)

**External Adoption:**
- Support for non-monorepo usage (forks, external devs)
- Plugin marketplace (community integrations)

---

## FAQ

### **Q: Can I use this SDK outside this monorepo?**
**A (v0.1.0)**: Currently optimized for this monorepo structure. **v1.0.0** will support standalone usage.

### **Q: How do I add dependencies to generated projects?**
**A**: Edit `requirements.txt` in the project directory. Base dependencies are inherited from `requirements-base.txt` at repo root.

### **Q: Can I customize templates?**
**A (v0.1.0)**: Templates are built-in. **v0.2.0** will support `--template-dir` for custom templates.

### **Q: Does this replace manual project creation?**
**A**: For new projects, yes (recommended). Existing projects can stay manual or be migrated using `migrate` command (v0.2.0+).

### **Q: How does testing work with generated projects?**
**A**: Every project includes `tests/conftest.py` with mocked LLM/integration fixtures. Run `langchain-dev test --coverage` to enforce 90% coverage.

### **Q: What if I need an integration not in v0.1.0?**
**A**: Manually add it using the [Integration Guide](#integration-guide). Submit a feature request for inclusion in v0.2.0+.

### **Q: Can I use different LLM providers (OpenAI, Anthropic)?**
**A (v0.1.0)**: SDK generates Ollama-specific code. **v0.2.0** will support multiple LLM backends via `--llm-provider` flag.

---

## Support and Contributing

### **Bug Reports**
Submit issues to the repository with:
- SDK version (`langchain-dev --version`)
- Full command executed
- Error traceback

### **Feature Requests**
Propose new integrations or features via GitHub issues with:
- Use case description
- Integration category (`vector_store`, `cache`, etc.)
- Expected dependencies and prerequisites

### **Contributing**
See [docs/contributing.md](contributing.md) for development workflow.

---

**Built with ❤️ for the LangChain community**
