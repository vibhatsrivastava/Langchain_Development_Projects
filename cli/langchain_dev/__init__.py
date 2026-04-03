"""
langchain-dev-tools — CLI for scaffolding LangChain projects with composable integrations.

A development SDK that automates project scaffolding, provides built-in production foundations
(rate limiting, retry logic, token counting), and supports composable integration modules
(vector stores, caching, observability).
"""

__version__ = "0.1.0"
__author__ = "Langchain Development Projects Team"
__description__ = "CLI tool for scaffolding production-ready LangChain projects"

from .version import get_version

__all__ = ["__version__", "get_version"]
