"""
Configuration module for Orange Intelligence.
This file provides backward compatibility for code that imports from config.py.
The actual configuration is now managed by core/config_manager.py.
"""

import os
import sys
import tempfile
from core.config_manager import CONFIG, load_config, save_config, get_logging_config

# These constants are kept for backward compatibility
LOGGING_LEVEL = CONFIG.get("logging", {}).get("level", "DEBUG")
