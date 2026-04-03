"""
Root-level pytest configuration.

This file ensures that the repository root is in sys.path for all tests,
allowing clean imports of the 'common' package from any test file.
It also provides shared fixtures available to all tests across the repository.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock
from langchain_core.messages import AIMessage

# Add repository root to sys.path for clean imports
repo_root = Path(__file__).parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


# ═══════════════════════════════════════════════════════════════
# Shared Fixtures — Available to All Tests
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def mock_llm(monkeypatch):
    """
    Mock OllamaLLM for testing string-based chains.
    
    Returns a Mock object that replaces OllamaLLM instantiation.
    The mock's invoke() method returns a fixed string response.
    
    Usage:
        def test_my_chain(mock_llm):
            mock_llm.invoke.return_value = "Custom response"
            llm = get_llm()  # Returns the mock
            result = llm.invoke("test prompt")
            assert result == "Custom response"
    """
    mock = Mock()
    mock.invoke.return_value = "Mocked LLM response"
    monkeypatch.setattr("langchain_ollama.OllamaLLM", lambda **kwargs: mock)
    return mock


@pytest.fixture
def mock_chat_llm(monkeypatch):
    """
    Mock ChatOllama for testing agentic workflows and chat-based chains.
    
    Returns a Mock object that replaces ChatOllama instantiation.
    The mock's invoke() method returns an AIMessage.
    
    Usage:
        def test_my_agent(mock_chat_llm):
            mock_chat_llm.invoke.return_value = AIMessage(content="Custom response")
            chat = get_chat_llm()  # Returns the mock
            result = chat.invoke([{"role": "user", "content": "test"}])
            assert result.content == "Custom response"
    """
    mock = Mock()
    mock.invoke.return_value = AIMessage(content="Mocked chat response")
    monkeypatch.setattr("langchain_ollama.ChatOllama", lambda **kwargs: mock)
    return mock


@pytest.fixture
def mock_embeddings(monkeypatch):
    """
    Mock OllamaEmbeddings for testing RAG pipelines and vector stores.
    
    Returns a Mock object that replaces OllamaEmbeddings instantiation.
    The mock's embed_documents() and embed_query() methods return fixed vectors.
    
    Usage:
        def test_my_rag(mock_embeddings):
            mock_embeddings.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]
            mock_embeddings.embed_query.return_value = [0.15] * 768
            
            embeddings = get_embeddings()  # Returns the mock
            docs_vectors = embeddings.embed_documents(["doc1", "doc2"])
            query_vector = embeddings.embed_query("query")
    """
    mock = Mock()
    mock.embed_documents.return_value = [[0.1] * 768]  # 768-dim vector (typical for nomic-embed-text)
    mock.embed_query.return_value = [0.1] * 768
    monkeypatch.setattr("langchain_ollama.OllamaEmbeddings", lambda **kwargs: mock)
    return mock


@pytest.fixture
def mock_env(monkeypatch):
    """
    Set common environment variables for tests.
    
    Provides default values for all required environment variables
    so tests don't depend on .env file or actual configuration.
    
    Usage:
        def test_with_env(mock_env):
            # OLLAMA_BASE_URL and other vars are already set
            from common.llm_factory import get_llm
            llm = get_llm()  # Uses mocked env vars
    
    Variables set:
        - OLLAMA_BASE_URL: http://test:11434
        - OLLAMA_API_KEY: (empty, simulates local server)
        - OLLAMA_MODEL: test-model
        - OLLAMA_EMBEDDING_MODEL: test-embed-model
        - LOG_LEVEL: DEBUG
    """
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://test:11434")
    monkeypatch.setenv("OLLAMA_API_KEY", "")  # Empty = local server
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "test-embed-model")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
