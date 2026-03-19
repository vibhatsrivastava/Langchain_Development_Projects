# Models Reference

This page documents the default model used in this repo, recommended alternatives, and how to switch models.

---

## Default Model

| Setting | Value |
|---------|-------|
| Model | `gpt-oss:20b` |
| Parameters | 20 billion |
| Runtime | Ollama (remote hosted server) |
| Best For | Agentic reasoning, instruction following, multi-step tasks |

This model is pre-loaded on the shared Ollama server. No `ollama pull` needed when using the remote server.

---

## Using a Different Model

### On the Remote Server

Ask your server admin which models are available, then set:

```dotenv
# In your .env
OLLAMA_MODEL=llama3.1:8b     # Replace with any model available on the server
```

To list available models on the server:

```bash
curl -H "Authorization: Bearer your_api_key_here" https://your-ollama-server.example.com/api/tags
```

### On Local Ollama

Pull any model from the [Ollama model library](https://ollama.com/library), then set it in `.env`:

```bash
ollama pull llama3.1:8b
```

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=
OLLAMA_MODEL=llama3.1:8b
```

### Overriding Per-Project (In Code)

The `get_llm()` factory accepts a `model` argument to override the env default for a specific call:

```python
from common.llm_factory import get_llm

llm = get_llm()                      # uses OLLAMA_MODEL from .env
llm = get_llm(model="mistral:7b")    # override for this instance only
```

---

## Recommended Models

### LLM Models

| Model | Params | RAM Required | Best For | Pull Command |
|-------|--------|-------------|---------|--------------|
| `gpt-oss:20b` | 20B | ~14 GB | Default — agents, reasoning | *(hosted, no pull needed)* |
| `llama3.1:8b` | 8B | ~8 GB | Agents, good balance | `ollama pull llama3.1:8b` |
| `llama3.2:3b` | 3B | ~4 GB | Fast local prototyping | `ollama pull llama3.2:3b` |
| `llama3.2:1b` | 1B | ~2 GB | Very fast, low resource | `ollama pull llama3.2:1b` |
| `mistral:7b` | 7B | ~5 GB | Instruction following | `ollama pull mistral:7b` |
| `mistral-nemo` | 12B | ~9 GB | Strong reasoning | `ollama pull mistral-nemo` |
| `deepseek-r1:8b` | 8B | ~8 GB | Reasoning / chain-of-thought | `ollama pull deepseek-r1:8b` |
| `gemma3:9b` | 9B | ~8 GB | General tasks | `ollama pull gemma3:9b` |
| `phi4` | 14B | ~10 GB | Microsoft's efficient model | `ollama pull phi4` |

### Embedding Models

| Model | Best For | Pull Command |
|-------|---------|--------------|
| `nomic-embed-text` | Default — general RAG | `ollama pull nomic-embed-text` |
| `mxbai-embed-large` | Higher quality embeddings | `ollama pull mxbai-embed-large` |
| `all-minilm` | Lightweight, fast | `ollama pull all-minilm` |

---

## Browsing All Available Models

Visit the full Ollama model library: [https://ollama.com/library](https://ollama.com/library)

Filter by use case, size, or language support. Any model listed there can be pulled with:

```bash
ollama pull <model-name>
```

and then used by setting `OLLAMA_MODEL=<model-name>` in your `.env`.
