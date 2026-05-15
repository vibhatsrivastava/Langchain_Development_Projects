"""
langfuse_tracing.py — Langfuse observability integration for automatic LLM tracing.

Provides transparent, always-on-by-default tracing for all LLM calls across the framework.
Supports HashiCorp Vault integration with .env fallback for API keys.

Configuration (in root .env):
    LANGFUSE_ENABLED       — Enable/disable tracing (default: "true")
    LANGFUSE_PUBLIC_KEY    — Public API key from Langfuse dashboard
    LANGFUSE_SECRET_KEY    — Secret API key from Langfuse dashboard
    LANGFUSE_HOST          — Langfuse server URL (default: "https://cloud.langfuse.com")

When VAULT_ENABLED=true, keys are fetched from Vault with fallback to .env.
See docs/vault.md and docs/langfuse.md for setup instructions.
"""

import os
import logging
from typing import Optional

from common.vault import get_secret

logger = logging.getLogger(__name__)

# Module-level cache for callback handler (initialized once per process)
_CALLBACK_HANDLER: Optional[object] = None
_INITIALIZATION_ATTEMPTED: bool = False


def get_langfuse_callback_handler():
    """
    Return a configured Langfuse callback handler for LangChain tracing.
    
    This function is called by llm_factory.py builders to automatically attach
    Langfuse tracing to all LLM instances. Tracing is enabled by default and
    can be disabled via LANGFUSE_ENABLED=false in .env.
    
    Features:
    - Always-on by default (set LANGFUSE_ENABLED=false to disable)
    - Vault integration with .env fallback for API keys
    - Graceful degradation (returns None if disabled or dependencies missing)
    - Lazy initialization (handler created once per process)
    - Transparent to user code (no callback configuration needed)
    
    Returns:
        CallbackHandler instance if tracing is enabled and configured, None otherwise.
        
    Example:
        # Called automatically by llm_factory.py - no user code needed
        handler = get_langfuse_callback_handler()
        llm = ChatOllama(..., callbacks=[handler] if handler else [])
        
    Configuration:
        # In root .env
        LANGFUSE_ENABLED=true
        LANGFUSE_PUBLIC_KEY=pk-lf-...
        LANGFUSE_SECRET_KEY=sk-lf-...
        LANGFUSE_HOST=http://10.0.0.15:3000
        
        # Optional: Vault integration (when VAULT_ENABLED=true)
        # Keys fetched from Vault path "langfuse" with fallback to .env
    """
    global _CALLBACK_HANDLER, _INITIALIZATION_ATTEMPTED
    
    # Return cached handler if already initialized
    if _INITIALIZATION_ATTEMPTED:
        return _CALLBACK_HANDLER
    
    _INITIALIZATION_ATTEMPTED = True
    
    # Check if Langfuse tracing is enabled (default: true for always-on behavior)
    enabled = os.getenv("LANGFUSE_ENABLED", "true").lower() in ("true", "1", "yes")
    if not enabled:
        logger.info("Langfuse tracing is disabled (LANGFUSE_ENABLED=false)")
        return None
    
    # Check if langfuse library is installed
    try:
        # Langfuse 4.x uses langchain module for LangChain integration
        from langfuse.langchain import CallbackHandler
    except ImportError:
        logger.warning(
            "Langfuse tracing is enabled but langfuse library is not installed. "
            "Install with: uv pip install -e ./common (includes langfuse>=2.0.0). "
            "LLMs will work normally without tracing."
        )
        return None
    
    # Fetch API keys via Vault (with .env fallback)
    # When VAULT_ENABLED=true, this tries Vault first, then falls back to .env
    public_key = get_secret(
        vault_key="LANGFUSE_PUBLIC_KEY",
        env_fallback_key="LANGFUSE_PUBLIC_KEY",
        default="",
        vault_path="langfuse"  # Store Langfuse keys under "langfuse" path in Vault
    )
    
    secret_key = get_secret(
        vault_key="LANGFUSE_SECRET_KEY",
        env_fallback_key="LANGFUSE_SECRET_KEY",
        default="",
        vault_path="langfuse"
    )
    
    # Validate API keys are configured
    if not public_key or not secret_key:
        logger.warning(
            "Langfuse tracing is enabled but API keys are not configured. "
            "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .env or Vault. "
            "LLMs will work normally without tracing. "
            "See docs/langfuse.md for setup instructions."
        )
        return None
    
    # Get Langfuse host URL
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # Initialize Langfuse callback handler
    try:
        # Langfuse 4.x requires initializing the global client first
        # Set environment variables for the Langfuse client
        if not os.getenv("LANGFUSE_PUBLIC_KEY"):
            os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
        if not os.getenv("LANGFUSE_SECRET_KEY"):
            os.environ["LANGFUSE_SECRET_KEY"] = secret_key
        if not os.getenv("LANGFUSE_HOST"):
            os.environ["LANGFUSE_HOST"] = host
            
        # Import and initialize the Langfuse client (required for 4.x)
        from langfuse import Langfuse
        
        # Initialize the global Langfuse client
        Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
            
        # Create callback handler (will use the initialized global client)
        _CALLBACK_HANDLER = CallbackHandler()
        logger.info(f"Successfully initialized Langfuse callback handler (host: {host})")
        return _CALLBACK_HANDLER
        
    except Exception as e:
        logger.error(
            f"Failed to initialize Langfuse callback handler: {e}. "
            f"LLMs will work normally without tracing. "
            f"Check LANGFUSE_HOST ({host}) is accessible and keys are valid."
        )
        return None


def reset_handler() -> None:
    """
    Reset the cached callback handler (for testing only).
    
    This forces re-initialization on the next call to get_langfuse_callback_handler().
    Do NOT use in production code.
    """
    global _CALLBACK_HANDLER, _INITIALIZATION_ATTEMPTED
    _CALLBACK_HANDLER = None
    _INITIALIZATION_ATTEMPTED = False
