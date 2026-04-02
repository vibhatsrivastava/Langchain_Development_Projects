# GitHub Copilot Workspace Instructions

> Applies to all files in this repository.

---

## Repo Overview

This is a **Python monorepo** of Agentic AI projects built with [LangChain](https://docs.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/), running LLMs via [Ollama](https://ollama.com/) (local or remote hosted).

**Current branch:** `dev` | **Default branch:** `main`

---

## Repository Structure

```
Langchain_Development_Projects/
├── common/                    # Shared utilities — import from any project
│   ├── llm_factory.py         # LLM builders: get_llm(), get_chat_llm(), get_embeddings()
│   ├── utils.py               # get_logger(), require_env()
│   └── prompts/
│       └── base_prompts.py    # QA_PROMPT, RAG_PROMPT, REACT_SYSTEM_PROMPT
├── projects/                  # Self-contained AI projects
│   └── 01_hello_langchain/    # Minimal LCEL chain example
├── Playground/                # Practice use case documents (.md) and scripts
├── Quick-Reference/           # Concept guides for learning and interview prep
├── docs/                      # Setup and contribution documentation
├── .env.example               # Required environment variable template
└── requirements-base.txt      # Shared base dependencies for all projects
```

---

## Environment Setup

**All projects share a single `.venv` at the repo root.**

```powershell
# Windows — activate the shared virtual environment
.venv\Scripts\Activate.ps1

# Install base dependencies (once, after cloning)
pip install -r requirements-base.txt
```

**Required `.env` variables** (copy from `.env.example`):

| Variable | Purpose | Example |
|---|---|---|
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` or remote URL |
| `OLLAMA_API_KEY` | Bearer token for remote servers; blank for local | `your_token` |
| `OLLAMA_MODEL` | Default LLM model | `gpt-oss:20b` |
| `OLLAMA_EMBEDDING_MODEL` | Default embedding model | `nomic-embed-text` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

**Optional: HashiCorp Vault Integration**

For teams with multiple developers, use **HashiCorp Vault** for centralized secret management:

| Variable | Purpose | Example |
|---|---|---|
| `VAULT_ENABLED` | Enable Vault (default: `false`) | `true` |
| `VAULT_ADDR` | Vault server URL | `http://vault.example.com:8200` |
| `VAULT_TOKEN` | Vault authentication token | `hvs.your_vault_token` |
| `VAULT_SECRET_PATH` | Secret path (default: `ollama`) | `ollama` |
| `VAULT_MOUNT_POINT` | KV mount point (default: `secret`) | `secret` |

When `VAULT_ENABLED=true`, `OLLAMA_API_KEY` is retrieved from Vault with automatic fallback to `.env` if unreachable. See [docs/vault.md](../docs/vault.md) for setup instructions.

**Credential Retrieval Strategy:**
- `common/llm_factory.py` uses `common/vault.py::get_secret()` for API key retrieval
- **Vault-first**: Tries Vault if enabled; logs success/failure
- **Automatic fallback**: Uses `.env` if Vault unreachable or key not found
- **Zero code changes**: Projects use `get_llm()` as before — credential source is transparent
- **Backward compatible**: Vault disabled by default; existing workflows unchanged

---

## The `common/` Package — Always Use It

Every project **must** use the shared `common/` package instead of directly instantiating LangChain classes. Add the sys.path insert pattern at the top of every project script:

```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
```

### LLM Factory — Which Builder to Use

| Builder | Returns | Use When |
|---|---|---|
| `get_llm()` | `OllamaLLM` | Simple string chains, single-turn prompts, no message history |
| `get_chat_llm()` | `ChatOllama` | Agents, memory, tool-calling, JSON mode, LangGraph nodes |
| `get_embeddings()` | `OllamaEmbeddings` | RAG, vector stores, similarity search |

```python
from common.llm_factory import get_llm, get_chat_llm, get_embeddings

llm        = get_llm()                                     # OllamaLLM, default model
chat       = get_chat_llm()                                # ChatOllama, default model
chat_json  = get_chat_llm(format="json")                   # structured output
chat_large = get_chat_llm(model="llama3.1:8b", num_ctx=8192)
embeddings = get_embeddings()                              # nomic-embed-text
```

All builders read `OLLAMA_BASE_URL`, `OLLAMA_API_KEY`, and `OLLAMA_MODEL` from `.env`. The `model=` argument overrides the env default for that call only.

### Shared Utilities

```python
from common.utils import get_logger, require_env

logger   = get_logger(__name__)          # structured logger; reads LOG_LEVEL from .env
base_url = require_env("OLLAMA_BASE_URL") # raises EnvironmentError if key is missing
```

### Shared Prompts

```python
from common.prompts.base_prompts import QA_PROMPT, RAG_PROMPT, REACT_SYSTEM_PROMPT
```

---

## Coding Conventions

### Chain Composition — Always Use LCEL

Use the `|` pipe operator (LangChain Expression Language) to compose chains:

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | get_llm() | StrOutputParser()
result = chain.invoke({"question": "..."})
```

### Agents — Prefer LangGraph

For new agents, use `langgraph.prebuilt.create_react_agent` over `AgentExecutor`:

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def my_tool(input: str) -> str:
    """Tool description the LLM uses to decide when to call it."""
    return ...

agent = create_react_agent(model=get_chat_llm(), tools=[my_tool])
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
answer = result["messages"][-1].content
```

### Tool Definitions

- Decorate with `@tool` from `langchain_core.tools`
- Write a clear, specific docstring — the LLM reads it to decide when to call the tool
- Use typed parameters; avoid `**kwargs`
- Return a `str` for simple tools; use Pydantic schemas for complex inputs

### Project Structure for New Projects

```
projects/NN_project_name/
├── src/
│   └── main.py            # Entry point; uses common/ imports
├── requirements.txt       # Project-specific deps only (base deps in root)
└── README.md              # Description, usage, sample output
```

**Important**: Do NOT create project-level `.env` or `.env.example` files. All environment variables must be defined in the root-level `.env.example` and documented in the project's README if they're project-specific.

---

## Documentation Conventions

### Quick-Reference

Files in `Quick-Reference/` follow indexed naming (`01_`, `02_`, ...) and cover concepts with definitions, diagrams, examples, and interview Q&A. See existing files for format reference.

### Playground

Files in `Playground/` are practice use cases. Each `.md` file documents one scenario with sections: Use Case Description, Objective, Step-by-Step Thought Process, Pseudo Code, High Level Workflow Diagram, Low Level Workflow Diagram, Implementation Steps, Code Snippets, Test Cases, Expected Outcomes.

A corresponding `.py` file contains the runnable implementation.

---

## Testing Conventions

**All code must maintain >= 90% test coverage.** This repository uses pytest with comprehensive testing standards.

### Testing Framework

- **Framework**: pytest >=8.0.0 with pytest-cov, pytest-mock, pytest-asyncio
- **Coverage threshold**: 90% minimum (enforced via `pytest.ini`)
- **Mock strategy**: All LLM/Ollama calls must be mocked (no real API calls in tests)

### Running Tests

```powershell
# Run all tests with coverage report
pytest --cov --cov-report=term-missing

# Run tests for specific module
pytest common/tests/test_llm_factory.py -v

# Verify >= 90% coverage (fails if below threshold)
pytest --cov --cov-fail-under=90

# Run only unit tests (fast)
pytest -m unit
```

### Test Structure

Each project/module has a `tests/` directory parallel to the code:

```
common/
├── llm_factory.py
└── tests/
    ├── conftest.py             # Shared fixtures (mock_llm, mock_chat_llm)
    ├── test_llm_factory.py     # Tests for llm_factory.py
    └── test_utils.py           # Tests for utils.py

projects/01_hello_langchain/
├── src/
│   └── main.py
└── tests/
    ├── conftest.py             # Project-specific fixtures
    └── test_main.py            # Tests for main.py
```

### Critical Rules

1. **Mock all LLMs**: Never make real Ollama/LLM API calls in tests. Use `mock_llm`, `mock_chat_llm`, and `mock_embeddings` fixtures from `common/tests/conftest.py`
2. **90% coverage minimum**: Every new module must achieve >= 90% coverage
3. **Test before commit**: Always run `pytest --cov --cov-fail-under=90` before pushing code
4. **Test types required**: Unit tests (isolated functions), Integration tests (chains/agents), Mocked LLM interactions

### Using the Test Agent

To automatically generate comprehensive tests with >= 90% coverage:

```
@test-agent generate tests for common/llm_factory.py
```

The test agent analyzes code, generates test files, and verifies coverage. See [.github/test-agent.agent.md](.github/test-agent.agent.md) for details.

### Example Test Pattern

```python
import pytest
from unittest.mock import Mock

def test_chain_with_mocked_llm(mock_llm):
    """Test LCEL chain with mocked LLM (no real API calls)."""
    mock_llm.invoke.return_value = "Mocked response"
    
    chain = prompt | get_llm() | StrOutputParser()
    result = chain.invoke({"question": "test"})
    
    assert result == "Mocked response"
    mock_llm.invoke.assert_called_once()
```

### Documentation

- **Detailed testing guide**: [docs/testing.md](docs/testing.md) — Comprehensive patterns and examples
- **Configuration**: `pytest.ini` — Coverage thresholds and test discovery
- **Test agent**: [.github/test-agent.agent.md](.github/test-agent.agent.md) — Automated test generation

**Remember**: No code is complete without tests. Coverage is non-negotiable.

---

## Running Projects

```powershell
# From repo root, with .venv active
python projects/01_hello_langchain/src/main.py

# Or from the project directory
cd projects/01_hello_langchain
python src/main.py
```

---

## Key Documentation

- [docs/getting_started.md](docs/getting_started.md) — Full environment setup
- [docs/models.md](docs/models.md) — Model reference, LLM class guide, how to swap models
- [docs/contributing.md](docs/contributing.md) — How to add a new project
- [docs/prerequisites.md](docs/prerequisites.md) — System requirements
- [Quick-Reference/01_What_Is_Agentic_AI.md](Quick-Reference/01_What_Is_Agentic_AI.md) — Concepts overview
- [Quick-Reference/02_ReAct_Pattern_Deep_Dive.md](Quick-Reference/02_ReAct_Pattern_Deep_Dive.md) — ReAct pattern
- [Quick-Reference/03_RAG_Retrieval_Augmented_Generation.md](Quick-Reference/03_RAG_Retrieval_Augmented_Generation.md) — RAG pipeline
- [Quick-Reference/04_Ollama.md](Quick-Reference/04_Ollama.md) — Ollama setup and API

---

## Common Pitfalls

- **Import errors from `common/`** — Always add the `sys.path.insert` at the top of project scripts before importing from `common/`
- **`.env` not found** — `llm_factory.py` calls `load_dotenv()` which searches upward; ensure `.env` exists at repo root
- **Project-level `.env` files** — NEVER create `.env` or `.env.example` files inside project directories; all environment configuration belongs in the root `.env` file. `load_dotenv()` searches upward from `common/` and will find the root `.env` automatically.
- **Wrong LLM class** — Use `get_chat_llm()` (not `get_llm()`) for agents and LangGraph nodes; `OllamaLLM` does not support tool calling
- **Model not available** — Run `ollama list` to see downloaded models; run `ollama pull <model>` if missing
- **`OLLAMA_API_KEY` left blank for remote** — Remote Ollama servers require the Bearer token; check `.env`
- **`venv/` vs `.venv/`** — The repo uses `.venv/` at the root; some projects have their own `venv/` but the shared `.venv` is preferred
