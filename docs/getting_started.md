# Getting Started

This guide walks you through setting up your environment to run any project in this monorepo.

---

## Prerequisites

Before you begin, complete the steps in [prerequisites.md](prerequisites.md).

---

## Option A — Remote / Company-Hosted Ollama (Default)

This is the standard setup when using the shared `gpt-oss:20b` model on a hosted server.

### 1. Clone the Repository

```bash
git clone https://github.com/vibhatsrivastava/Langchain_Development_Projects.git
cd Langchain_Development_Projects
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```dotenv
OLLAMA_BASE_URL=https://your-ollama-server.example.com   # Provided by your admin
OLLAMA_API_KEY=your_api_key_here                         # Provided by your admin
OLLAMA_MODEL=gpt-oss:20b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

> **Note:** Never commit your `.env` file. It is listed in `.gitignore`.

### 3. Install Base Dependencies

```bash
pip install -r requirements-base.txt
```

### 4. Run a Project

```bash
cd projects/01_hello_langchain
pip install -r requirements.txt      # project-specific deps, if any
python src/main.py
```

### 5. Verify Connectivity (Optional)

```bash
curl -H "Authorization: Bearer your_api_key_here" https://your-ollama-server.example.com/api/tags
```

You should see a JSON list of available models on the server.

---

## Option B — Local Ollama (Self-Hosted)

Use this if you want to run models entirely on your own machine without any server access.

### 1. Install Ollama

Download and install from [https://ollama.com/download](https://ollama.com/download).

On Windows, the installer adds Ollama as a background service. On macOS/Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve   # start the server (runs on http://localhost:11434)
```

### 2. Pull a Model

```bash
ollama pull gpt-oss:20b              # default model (if available locally)
# OR any alternative model:
ollama pull llama3.1:8b
ollama pull mistral:7b
```

See [models.md](models.md) for a full list of recommended models and pull commands.

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Update `.env` for local use:

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=                        # Leave blank — no auth for local Ollama
OLLAMA_MODEL=llama3.1:8b               # Or whichever model you pulled
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### 4. Pull Embedding Model

```bash
ollama pull nomic-embed-text           # required for RAG/embedding projects
```

### 5. Install & Run

```bash
pip install -r requirements-base.txt
cd projects/01_hello_langchain
python src/main.py
```

---

## Shared `common/` Library

All projects can import from the `common/` package:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.llm_factory import get_llm, get_embeddings
from common.utils import get_logger

logger = get_logger(__name__)
llm = get_llm()                          # uses OLLAMA_MODEL from .env
llm = get_llm(model="llama3.1:8b")      # override per-call
```

---

## Per-Project Environment Overrides

Each project may have its own `.env.example` for project-specific variables. When present, merge it with the root `.env`:

```bash
# From inside a project directory
cat ../../.env.example > .env
cat .env.example >> .env
# Then edit .env with your values
```
