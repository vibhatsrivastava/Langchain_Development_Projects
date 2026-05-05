"""
env_manager.py — Environment variable management for project scaffolding.

Handles .env file generation, Vault integration, and environment validation.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dotenv import dotenv_values

from .config import DEFAULT_ENV_VARS


class EnvManager:
    """
    Manages environment variables for scaffolded projects.
    
    Features:
    - Generate .env.example files with integration-specific variables
    - Validate .env files against required variables
    - Merge default + integration-specific environment variables
    
    Example:
        env_mgr = EnvManager()
        env_vars = env_mgr.get_env_vars(integrations=["pgvector", "langfuse"])
        env_mgr.write_env_example(project_path, env_vars)
    """
    
    def __init__(self):
        """Initialize environment manager."""
        self.default_vars = DEFAULT_ENV_VARS.copy()
    
    def get_env_vars(self, integrations: List[str]) -> Dict[str, str]:
        """
        Get all environment variables for a project with integrations.
        
        Args:
            integrations: List of integration names
        
        Returns:
            Dictionary of environment variables with example values
        """
        from .integrations import get_integration
        
        # Start with default variables
        env_vars = self.default_vars.copy()
        
        # Add integration-specific variables
        for integration_name in integrations:
            integration = get_integration(integration_name)
            if integration:
                integration_vars = integration.get_env_vars()
                env_vars.update(integration_vars)
        
        return env_vars
    
    def write_env_example(
        self,
        project_path: Path,
        env_vars: Dict[str, str],
        header_comment: Optional[str] = None
    ) -> Path:
        """
        Write .env.example file to project directory.
        
        Args:
            project_path: Path to project directory
            env_vars: Dictionary of environment variables
            header_comment: Optional header comment for the file
        
        Returns:
            Path to created .env.example file
        """
        env_file = project_path / ".env.example"
        
        with open(env_file, "w", encoding="utf-8") as f:
            # Write header comment
            if header_comment:
                f.write(f"# {header_comment}\n")
            else:
                f.write("# Environment variables for this project\n")
            f.write("# Copy this file to .env and fill in your actual values\n\n")
            
            # Group variables by category
            default_keys = set(DEFAULT_ENV_VARS.keys())
            integration_keys = set(env_vars.keys()) - default_keys
            
            # Write default variables
            if default_keys:
                f.write("# Base Ollama configuration\n")
                for key in sorted(default_keys):
                    if key in env_vars:
                        value = env_vars[key]
                        f.write(f"{key}={value}\n")
                f.write("\n")
            
            # Write integration-specific variables
            if integration_keys:
                f.write("# Integration-specific variables\n")
                for key in sorted(integration_keys):
                    value = env_vars[key]
                    f.write(f"{key}={value}\n")
                f.write("\n")
        
        return env_file
    
    def validate_env_file(
        self,
        env_file: Path,
        required_vars: List[str]
    ) -> tuple[bool, List[str]]:
        """
        Validate that .env file contains all required variables.
        
        Args:
            env_file: Path to .env file
            required_vars: List of required variable names
        
        Returns:
            Tuple of (is_valid, missing_vars)
        """
        if not env_file.exists():
            return (False, required_vars)
        
        # Load .env file
        env_values = dotenv_values(env_file)
        
        # Check for missing variables
        missing = [var for var in required_vars if var not in env_values]
        
        return (len(missing) == 0, missing)
    
    def get_required_vars(self, integrations: List[str]) -> List[str]:
        """
        Get list of required environment variables for integrations.
        
        Args:
            integrations: List of integration names
        
        Returns:
            List of required variable names
        """
        from .integrations import get_integration
        
        # Always require base Ollama variables
        required = ["OLLAMA_BASE_URL", "OLLAMA_MODEL"]
        
        # Add integration-specific required variables
        for integration_name in integrations:
            integration = get_integration(integration_name)
            if integration:
                env_vars = integration.get_env_vars()
                # Assume all integration env vars are required
                required.extend(env_vars.keys())
        
        return list(set(required))  # Remove duplicates
    
    def merge_env_files(self, base_env: Path, project_env: Path) -> Dict[str, str]:
        """
        Merge base .env with project-specific .env.
        
        Base variables are used unless overridden in project .env.
        
        Args:
            base_env: Path to base .env file (repo root)
            project_env: Path to project-specific .env file
        
        Returns:
            Merged dictionary of environment variables
        """
        # Load base environment
        base_vars = dotenv_values(base_env) if base_env.exists() else {}
        
        # Load project environment
        project_vars = dotenv_values(project_env) if project_env.exists() else {}
        
        # Merge (project vars override base)
        merged = base_vars.copy()
        merged.update(project_vars)
        
        return merged
    
    def format_env_file(self, env_vars: Dict[str, str]) -> str:
        """
        Format environment variables as .env file content.
        
        Args:
            env_vars: Dictionary of environment variables
        
        Returns:
            Formatted .env file content
        """
        lines = []
        
        for key, value in sorted(env_vars.items()):
            # Handle multiline values (quote them)
            if "\n" in value:
                value = f'"{value}"'
            
            lines.append(f"{key}={value}")
        
        return "\n".join(lines) + "\n"
