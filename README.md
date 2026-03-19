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

# 2. Set up environment
cp .env.example .env
# Edit .env with your OLLAMA_BASE_URL and OLLAMA_API_KEY

# 3. Install base dependencies
pip install -r requirements-base.txt

# 4. Run a project
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
- [Models](docs/models.md) — Default model, alternatives, how to swap
- [Prerequisites](docs/prerequisites.md) — System requirements
- [Contributing](docs/contributing.md) — How to add a new project

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
