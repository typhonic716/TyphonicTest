"""
Configuration management for the AI Agent System
Handles cross-platform paths and environment-specific settings
"""

import os
from pathlib import Path
from typing import Dict, Any
import json

class Config:
    """Centralized configuration management"""

    def __init__(self, config_path: str = None):
        self.base_dir = Path.home() / "AI_Agent_System"

        # Cross-platform directory structure
        self.directories = {
            'base': self.base_dir,
            'models': self.base_dir / 'models',
            'memory': self.base_dir / 'memory',
            'logs': self.base_dir / 'logs',
            'data': self.base_dir / 'data',
        }

        # Create directories if they don't exist
        for dir_path in self.directories.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Default configuration
        self.config = {
            # Model settings
            'model': {
                'path': str(self.directories['models'] / 'llama-3.2-3b-instruct.gguf'),
                'n_gpu_layers': 50,
                'n_batch': 512,
                'n_ctx': 8192,
                'temperature': 0.7,
                'top_p': 0.95,
                'max_tokens': 2048,
            },

            # Memory settings
            'memory': {
                'persist_directory': str(self.directories['memory']),
                'embedding_model': 'all-MiniLM-L6-v2',
                'learning_threshold': 0.75,
                'max_conversations': 1000,
            },

            # Security settings
            'security': {
                'enable_command_execution': False,  # Disabled by default
                'enable_python_exec': False,  # Disabled by default
                'allowed_file_paths': [str(self.directories['data'])],
                'blocked_commands': ['format', 'del', 'rm -rf', 'shutdown', 'reboot', 'mkfs'],
            },

            # Web interface settings
            'web': {
                'host': '127.0.0.1',  # Changed from 0.0.0.0 for security
                'port': 7860,
                'share': False,
                'auth': None,  # Can be set to ('username', 'password')
            },

            # Logging settings
            'logging': {
                'level': 'INFO',
                'file': str(self.directories['logs'] / 'agent.log'),
                'max_bytes': 10485760,  # 10MB
                'backup_count': 5,
            },

            # Tool settings
            'tools': {
                'web_search_max_results': 5,
                'wikipedia_summary_length': 1000,
                'command_timeout': 30,
                'file_read_limit': 2000,
            }
        }

        # Load custom config if provided
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)

    def load_config(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
                self._deep_update(self.config, custom_config)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")

    def save_config(self, config_path: str = None):
        """Save current configuration to JSON file"""
        if config_path is None:
            config_path = self.directories['base'] / 'config.json'

        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config to {config_path}: {e}")

    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> Dict:
        """Recursively update nested dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                base_dict[key] = self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
        return base_dict

    def get(self, *keys, default=None) -> Any:
        """Get nested configuration value"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, *keys, value):
        """Set nested configuration value"""
        config = self.config
        for key in keys[:-1]:
            config = config.setdefault(key, {})
        config[keys[-1]] = value

    def validate_model_exists(self) -> bool:
        """Check if the model file exists"""
        model_path = self.get('model', 'path')
        return os.path.exists(model_path)

    def get_safe_file_path(self, requested_path: str) -> Path:
        """
        Validate and return safe file path
        Prevents path traversal attacks
        """
        requested_path = Path(requested_path).resolve()
        allowed_paths = self.get('security', 'allowed_file_paths', default=[])

        for allowed in allowed_paths:
            allowed = Path(allowed).resolve()
            try:
                requested_path.relative_to(allowed)
                return requested_path
            except ValueError:
                continue

        raise PermissionError(f"Access to {requested_path} is not allowed")

    def is_command_safe(self, command: str) -> bool:
        """Check if command is safe to execute"""
        blocked = self.get('security', 'blocked_commands', default=[])
        command_lower = command.lower()
        return not any(blocked_cmd in command_lower for blocked_cmd in blocked)


# Global config instance
_config = None

def get_config(config_path: str = None) -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
