# LangChain Development Projects

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![LangChain](https://img.shields.io/badge/LangChain-latest-green?logo=chainlink)
![Ollama](https://img.shields.io/badge/Ollama-local%20%7C%20hosted-orange)
![License](https://img.shields.io/github/license/vibhatsrivastava/Langchain_Development_Projects)

A curated **monorepo** of Agentic AI applications built with [LangChain](https://docs.langchain.com/) and [Ollama](https://ollama.com/). Each project is self-contained and demonstrates a specific use case, integration, or agentic pattern.

---

## Stack

| Component | Technology |
|-----------|-----------|
| LLM Framework | [LangChain](https://docs.langchain.com/) + [LangGraph](https://langchain-ai.github.io/langgraph/) |
| LLM Runtime | [Ollama](https://ollama.com/) (remote hosted or local) |
| Default Model | `gpt-oss:20b` (20B parameter OSS model) |
| Embeddings | `nomic-embed-text` via Ollama |

---

## Projects

| # | Project | Description |
|---|---------|-------------|
| 01 | [Hello LangChain](projects/01_hello_langchain/) | Minimal working example — chain setup, LLM call, prompt template |

> More projects will be added to this table as they are developed.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/vibhatsrivastava/Langchain_Development_Projects.git
cd Langchain_Development_Projects

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your OLLAMA_BASE_URL and OLLAMA_API_KEY

# 3. Create a virtual environment (prevents dependency conflicts between projects)
python -m venv venv

# 4. Activate the virtual environment
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (Command Prompt):
# venv\Scripts\activate.bat
# macOS / Linux:
# source venv/bin/activate

# 5. Install base dependencies
pip install -r requirements-base.txt

# 6. Run a project
cd projects/01_hello_langchain
pip install -r requirements.txt
python src/main.py
```

See [docs/getting_started.md](docs/getting_started.md) for full setup instructions.

---

## Repository Structure

```
Langchain_Development_Projects/
├── projects/                  # Individual AI projects (self-contained)
│   └── 01_hello_langchain/
├── common/                    # Shared utilities used across projects
│   ├── llm_factory.py         # Reusable LLM & embeddings builders
│   ├── utils.py               # Logging, env helpers
│   └── prompts/               # Shared prompt templates
├── docs/                      # Documentation
│   ├── getting_started.md
│   ├── models.md              # Model reference + how to swap models
│   ├── prerequisites.md
│   └── contributing.md
├── .env.example               # Environment variable template
├── requirements-base.txt      # Shared base dependencies
└── README.md
```

---

## Documentation

- [Getting Started](docs/getting_started.md) — Setup for hosted or local Ollama
- [Models](docs/models.md) — Default model, alternatives, how to swap, and LLM class reference
- [Prerequisites](docs/prerequisites.md) — System requirements
- [Contributing](docs/contributing.md) — How to add a new project

---

## Common LLM Factory

All projects share a central `common/llm_factory.py` that provides three builder functions. Import the one that fits your use case — no boilerplate, no repeated configuration.

| Builder | Returns | Use When |
|---|---|---|
| `get_llm()` | `OllamaLLM` | Simple string chains, single-turn prompts |
| `get_chat_llm()` | `ChatOllama` | Agents, memory, tool-calling, JSON mode |
| `get_embeddings()` | `OllamaEmbeddings` | RAG, vector stores, similarity search |

All three read `OLLAMA_BASE_URL`, `OLLAMA_API_KEY`, and `OLLAMA_MODEL` from your `.env`. The `model` argument overrides the env default for that call only.

---

### `get_llm()` — Raw String Completion

Best for simple prompt → string output chains with no message history.

```python
from common.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate

llm = get_llm()  # uses OLLAMA_MODEL from .env; add model= or temperature= to override

prompt = PromptTemplate.from_template("Summarise the following in one sentence:\n{text}")
chain = prompt | llm

result = chain.invoke({"text": "LangChain is a framework for building LLM-powered applications."})
print(result)
# → "LangChain is a framework that simplifies building applications powered by large language models."
```

---

### `get_chat_llm()` — Conversational & Agentic

Required for multi-turn conversations, LangGraph agents, tool calling, and structured JSON output.
Uses OpenAI-compatible message roles (`system` / `human` / `ai`).

```python
from common.llm_factory import get_chat_llm
from langchain_core.prompts import ChatPromptTemplate

chat = get_chat_llm()  # uses OLLAMA_MODEL from .env; supports format="json" and num_ctx=

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that answers concisely."),
    ("human", "{question}"),
])
chain = prompt | chat

response = chain.invoke({"question": "What is the difference between RAG and fine-tuning?"})
print(response.content)
# → "RAG retrieves external context at inference time; fine-tuning bakes knowledge into model weights."
```

---

### `get_embeddings()` — Semantic Search & RAG

Returns dense vector representations of text for use with any LangChain vector store.

```python
from common.llm_factory import get_embeddings
from langchain_core.vectorstores import InMemoryVectorStore

embeddings = get_embeddings()  # uses OLLAMA_EMBEDDING_MODEL from .env; add model= to override

docs = [
    "LangChain simplifies building LLM applications.",
    "Ollama lets you run large language models locally.",
    "RAG combines retrieval with language model generation.",
]
vector_store = InMemoryVectorStore.from_texts(docs, embedding=embeddings)

results = vector_store.similarity_search("How do I run LLMs on my machine?", k=1)
print(results[0].page_content)
# → "Ollama lets you run large language models locally."
```

> For full parameter reference and advanced examples (JSON mode, extended context window, multi-turn memory), see [docs/models.md](docs/models.md#llm-classes--choosing-the-right-builder).

---

## Adding a New Project

Each project under `projects/` should follow the standard scaffold:

```
projects/NN_project_name/
├── src/
│   └── main.py
├── requirements.txt      # Project-specific deps (in addition to base)
├── .env.example          # Any project-specific env vars
└── README.md             # Project description, usage, sample output
```

See [docs/contributing.md](docs/contributing.md) for the full conventions.

---

## License

[MIT](LICENSE)
