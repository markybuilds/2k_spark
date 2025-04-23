"""
Configuration settings for the NBA 2K prediction model.

This module contains all configuration settings for the application, including
logging, API endpoints, and authentication settings.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any

# Determine the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Environment settings
ENV = 'development'  # Fixed to development mode
DEBUG = True

# Logging configuration
def setup_logging() -> None:
    """Set up logging configuration based on the environment."""
    log_level = logging.DEBUG if DEBUG else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_file = os.path.join(PROJECT_ROOT, 'app.log')

    handlers = [logging.StreamHandler()]
    # Always log to file as well
    handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )

# Initialize logging
setup_logging()

# Website URLs
H2HGGL_BASE_URL = 'https://www.h2hggl.com'
H2HGGL_PLAYERS_URL = f"{H2HGGL_BASE_URL}/en/ebasketball/players/"

# Directory settings
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# Cache settings
TOKEN_CACHE_FILE = os.path.join(CACHE_DIR, "token.txt")
TOKEN_CACHE_DURATION = 3600  # Cache token for 1 hour (in seconds)

# Selenium settings
SELENIUM_TIMEOUT = 10  # seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds

# Create a dictionary of all settings for easy access
config: Dict[str, Any] = {
    'env': ENV,
    'debug': DEBUG,
    'project_root': PROJECT_ROOT,
    'cache_dir': CACHE_DIR,
    'data_dir': DATA_DIR,
    'raw_data_dir': RAW_DATA_DIR,
    'processed_data_dir': PROCESSED_DATA_DIR,
    'h2hggl': {
        'base_url': H2HGGL_BASE_URL,
        'players_url': H2HGGL_PLAYERS_URL,
    },
    'token': {
        'cache_file': TOKEN_CACHE_FILE,
        'cache_duration': TOKEN_CACHE_DURATION,
    },
    'selenium': {
        'timeout': SELENIUM_TIMEOUT,
        'max_retry_attempts': MAX_RETRY_ATTEMPTS,
        'retry_delay': RETRY_DELAY,
    }
}
