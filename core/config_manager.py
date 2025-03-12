"""
Configuration manager for Orange Intelligence.
Handles loading, saving, and managing application configurations.
"""

import os
import sys
import yaml
import json
import logging
import tempfile
import keyring
from typing import Dict, Any, Optional

# Set up logger
logger = logging.getLogger(__name__)

# Default configuration directory
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".orange-intelligence")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")

# App name for keyring service
KEYRING_SERVICE = "orange-intelligence"

# Default configuration values
DEFAULT_CONFIG = {
    "app": {
        "name": "orange-ai",
        "icon": "assets/icon.png",
    },
    "variables": {
        "import_bash_profile": False,
    },
    "ui": {
        "enabled_tabs": {
            "basics": True,
            "google_gemini": True,
            "ollama": True,
            "openai": True,
            "variables": True,
        }
    },
    "ollama": {
        "name": "ollama",
        "url": "https://ollama.com",
        "default_model": "llama3.1",
    },
    "openai": {
        "default_model": "gpt-3.5-turbo"
    },
    "google_gemini": {
        "default_model": "gemini-2.0-flash"
    },
    "logging": {
        "level": "DEBUG"
    }
}

# In-memory representation of the config
_config_cache = None


def ensure_config_dir() -> None:
    """Ensure the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def create_default_config() -> None:
    """Create a default configuration file if none exists."""
    ensure_config_dir()
    save_config(DEFAULT_CONFIG)
    logger.info(f"Created default configuration at {CONFIG_FILE}")


def load_config() -> Dict[str, Any]:
    """Load configuration from the YAML file."""
    global _config_cache
    
    # Return cached config if available
    if _config_cache is not None:
        return _config_cache
    
    ensure_config_dir()
    
    # Create default config if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        create_default_config()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
            
        # Ensure all sections from default config exist
        for section, values in DEFAULT_CONFIG.items():
            if section not in config:
                config[section] = values
                
        # Cache the config
        _config_cache = config
        
        # Load API keys from keyring
        _load_api_keys(config)
        
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        # Return default config in case of failure
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save the configuration to the YAML file."""
    global _config_cache
    
    ensure_config_dir()
    
    # Create a copy of the config to avoid modifying the original
    config_to_save = config.copy()
    
    # Save API keys to keyring
    _save_api_keys(config)

    # Don't save API keys to the YAML file
    if "openai" in config_to_save and "api_key" in config_to_save["openai"]:
        del config_to_save["openai"]["api_key"]
    
    if "google_gemini" in config_to_save and "api_key" in config_to_save["google_gemini"]:
        del config_to_save["google_gemini"]["api_key"]
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config_to_save, f, default_flow_style=False)
        
        # Update the cache
        _config_cache = config
        
        logger.debug(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")


def get_api_key(service: str) -> Optional[str]:
    """Get an API key from the keyring or environment variables."""
    # Try environment variables first
    env_var_map = {
        "openai": "OPENAI_API_KEY",
        "google_gemini": "GOOGLE_GEMINI_KEY"
    }
    
    if service in env_var_map and os.environ.get(env_var_map[service]):
        return os.environ.get(env_var_map[service])
    
    # Then try the keyring
    try:
        key = keyring.get_password(KEYRING_SERVICE, service)
        return key if key else None
    except Exception as e:
        logger.error(f"Error retrieving API key for {service}: {e}")
        return None


def set_api_key(service: str, api_key: str) -> None:
    """Set an API key in the keyring."""
    try:
        keyring.set_password(KEYRING_SERVICE, service, api_key)
        logger.debug(f"API key for {service} saved to keyring")
    except Exception as e:
        logger.error(f"Error saving API key for {service}: {e}")


def _load_api_keys(config: Dict[str, Any]) -> None:
    """Load API keys from keyring and add them to the config."""
    # Load OpenAI API key
    if "openai" in config:
        openai_key = get_api_key("openai")
        if openai_key:
            config["openai"]["api_key"] = openai_key
    
    # Load Google Gemini API key
    if "google_gemini" in config:
        gemini_key = get_api_key("google_gemini")
        if gemini_key:
            config["google_gemini"]["api_key"] = gemini_key


def _save_api_keys(config: Dict[str, Any]) -> None:
    """Save API keys from the config to the keyring."""
    # Save OpenAI API key
    if "openai" in config and "api_key" in config["openai"] and config["openai"]["api_key"]:
        set_api_key("openai", config["openai"]["api_key"])
    
    # Save Google Gemini API key
    if "google_gemini" in config and "api_key" in config["google_gemini"] and config["google_gemini"]["api_key"]:
        set_api_key("google_gemini", config["google_gemini"]["api_key"])


def get_logging_config() -> Dict[str, Any]:
    """Generate logging configuration based on the current settings."""
    config = load_config()
    log_level = config.get("logging", {}).get("level", "DEBUG")
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            },
        },
        "handlers": {
            "stream": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "detailed",
            },
            "file": {
                "level": log_level,
                "class": "logging.FileHandler",
                "filename": os.path.join(CONFIG_DIR, "orange-intelligence.log"),
                "formatter": "detailed",
            },
        },
        "loggers": {
            "": {
                "handlers": ['stream', 'file'],
                "level": log_level,
                "propagate": True,
            },
        },
    }


# Initialize the config cache
CONFIG = load_config()
