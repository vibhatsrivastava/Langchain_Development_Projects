"""
common package — shared utilities for all LangChain projects in this monorepo.

Usage from any project:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from common.llm_factory import get_llm, get_embeddings
"""
