"""
llm_factory.py — Reusable builders for LLM and embedding models via Ollama.

The factory reads configuration from environment variables defined in .env:
    OLLAMA_BASE_URL       — Ollama server endpoint (remote or local)
    OLLAMA_API_KEY        — Bearer token for authenticated servers (leave blank for local)
    OLLAMA_MODEL          — Default LLM model name (e.g. gpt-oss:20b)
    OLLAMA_EMBEDDING_MODEL — Default embedding model name (e.g. nomic-embed-text)

Any project can override the model at call time:
    llm = get_llm(model="llama3.1:8b")
"""

import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM, OllamaEmbeddings

load_dotenv()

_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_API_KEY = os.getenv("OLLAMA_API_KEY", "")
_DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
_DEFAULT_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")


def _auth_headers() -> dict:
    """Return Bearer auth headers if an API key is configured."""
    if _API_KEY:
        return {"Authorization": f"Bearer {_API_KEY}"}
    return {}


def get_llm(model: str = None, temperature: float = 0.0) -> OllamaLLM:
    """
    Return a configured OllamaLLM instance.

    Args:
        model:       Ollama model name. Defaults to OLLAMA_MODEL env var.
        temperature: Sampling temperature. 0.0 = deterministic.

    Returns:
        OllamaLLM instance ready for chain/agent use.

    Example:
        from common.llm_factory import get_llm
        llm = get_llm()                        # uses default gpt-oss:20b
        llm = get_llm(model="llama3.1:8b")     # override model
    """
    return OllamaLLM(
        model=model or _DEFAULT_MODEL,
        base_url=_BASE_URL,
        temperature=temperature,
        client_kwargs={"headers": _auth_headers()},
    )


def get_embeddings(model: str = None) -> OllamaEmbeddings:
    """
    Return a configured OllamaEmbeddings instance.

    Args:
        model: Ollama embedding model name. Defaults to OLLAMA_EMBEDDING_MODEL env var.

    Returns:
        OllamaEmbeddings instance ready for RAG / vector store use.

    Example:
        from common.llm_factory import get_embeddings
        embeddings = get_embeddings()
        embeddings = get_embeddings(model="mxbai-embed-large")
    """
    return OllamaEmbeddings(
        model=model or _DEFAULT_EMBEDDING_MODEL,
        base_url=_BASE_URL,
        client_kwargs={"headers": _auth_headers()},
    )
