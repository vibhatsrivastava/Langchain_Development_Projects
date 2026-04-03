"""
utils.py — Common helper utilities shared across projects.
"""

import logging
import os
from dotenv import load_dotenv

load_dotenv()


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Args:
        name: Logger name, typically __name__ from the calling module.

    Example:
        from common.utils import get_logger
        logger = get_logger(__name__)
        logger.info("Starting...")
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        level=getattr(logging, level, logging.INFO),
        force=True,  # Reconfigure even if handlers already exist (Python 3.8+)
    )
    return logging.getLogger(name)


def require_env(key: str) -> str:
    """
    Return an environment variable value, raising a clear error if missing.

    Args:
        key: Environment variable name.

    Raises:
        EnvironmentError: If the variable is not set or empty.

    Example:
        base_url = require_env("OLLAMA_BASE_URL")
    """
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Copy .env.example to .env and fill in the value."
        )
    return value
