"""
Token fetcher for the H2H GG League API (Render-compatible version).
This version uses a pre-fetched token for deployment environments.
"""

import time
import os
from config.logging_config import get_data_fetcher_logger
from utils.logging import log_execution_time, log_exceptions

logger = get_data_fetcher_logger()

# Default token that can be overridden by environment variable
DEFAULT_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyLWlkIjo5LCJuYW1lIjoiZ3Vlc3QiLCJyb2xlIjoidmlld2VyIiwidGVhbS1pZCI6bnVsbCwiZXhwIjoxNzQ1NzEzMzY4fQ.KrrapVSa6hGnU--WM0Ks40ELNTvvzydd2clTb4EgFqw"

class TokenFetcher:
    """
    Provides a pre-fetched authentication token for H2H GG League API.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the TokenFetcher.
        """
        self.token = os.environ.get("H2H_TOKEN", DEFAULT_TOKEN)
        self.token_timestamp = time.time()
    
    @log_execution_time(logger)
    @log_exceptions(logger)
    def get_token(self, force_refresh=False):
        """
        Get the authentication token.
        
        Args:
            force_refresh (bool): Whether to force a token refresh (ignored in this implementation)
            
        Returns:
            str: Authentication token
        """
        logger.info("Using pre-configured authentication token for deployment environment")
        return self.token
    
    @log_exceptions(logger)
    def get_auth_headers(self):
        """
        Get the authentication headers for API requests.
        
        Returns:
            dict: Headers dictionary with authentication token
        """
        token = self.get_token()
        return {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': f'Bearer {token}',
            'origin': 'https://www.h2hggl.com',
            'referer': 'https://www.h2hggl.com/'
        }
