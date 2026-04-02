"""
Shared pytest fixtures for all tests in the repository.

These fixtures are automatically available to all test files.
Import them in test files as needed.
"""

import pytest
from unittest.mock import Mock
from langchain_core.messages import AIMessage


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
    
    Example:
        def test_simple_chain(mock_llm):
            from common.llm_factory import get_llm
            from langchain_core.prompts import PromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            mock_llm.invoke.return_value = "Mocked LLM response"
            
            prompt = PromptTemplate.from_template("Q: {q}")
            chain = prompt | get_llm() | StrOutputParser()
            
            result = chain.invoke({"q": "test"})
            assert result == "Mocked LLM response"
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
    
    Example:
        def test_agent_execution(mock_chat_llm):
            from common.llm_factory import get_chat_llm
            from langgraph.prebuilt import create_react_agent
            from langchain_core.tools import tool
            
            @tool
            def test_tool(input: str) -> str:
                '''Test tool.'''
                return f"Tool result: {input}"
            
            mock_chat_llm.invoke.return_value = AIMessage(content="Final answer")
            
            agent = create_react_agent(model=get_chat_llm(), tools=[test_tool])
            result = agent.invoke({"messages": [{"role": "user", "content": "test"}]})
            
            assert "Final answer" in result["messages"][-1].content
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
    
    Example:
        def test_vectorstore_retrieval(mock_embeddings):
            from common.llm_factory import get_embeddings
            from langchain_community.vectorstores import FAISS
            from langchain_core.documents import Document
            
            mock_embeddings.embed_documents.return_value = [[0.1] * 768]
            mock_embeddings.embed_query.return_value = [0.1] * 768
            
            docs = [Document(page_content="Test doc", metadata={"id": 1})]
            vectorstore = FAISS.from_documents(docs, get_embeddings())
            
            results = vectorstore.similarity_search("query", k=1)
            assert len(results) == 1
            assert results[0].page_content == "Test doc"
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
    
    Example:
        def test_require_env_with_mocked_vars(mock_env):
            from common.utils import require_env
            
            base_url = require_env("OLLAMA_BASE_URL")
            assert base_url == "http://test:11434"
    """
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://test:11434")
    monkeypatch.setenv("OLLAMA_API_KEY", "")  # Empty = local server
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "test-embed-model")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
