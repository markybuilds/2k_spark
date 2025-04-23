"""
Authentication module for retrieving and managing tokens for the h2hggl.com website.

This module provides functionality to authenticate with the h2hggl.com website
by retrieving a bearer token from the website's localStorage using Selenium.
It includes token caching to minimize the need for browser automation.
"""
from __future__ import annotations

import os
import time
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException

from src.config import (
    H2HGGL_PLAYERS_URL,
    TOKEN_CACHE_FILE,
    TOKEN_CACHE_DURATION,
    SELENIUM_TIMEOUT,
    MAX_RETRY_ATTEMPTS,
    RETRY_DELAY
)

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Exception raised for authentication-related errors."""
    pass


class TokenManager:
    """
    Manages authentication tokens for the h2hggl.com website.

    This class handles token retrieval, caching, and validation. It uses Selenium
    to retrieve tokens from the website's localStorage and provides methods to
    cache tokens for later use.

    Attributes:
        _cache_file (str): Path to the token cache file.
    """

    def __init__(self, cache_file: str = TOKEN_CACHE_FILE) -> None:
        """
        Initialize the TokenManager.

        Args:
            cache_file: Path to the token cache file. Defaults to the value from config.
        """
        self._cache_file = cache_file
        self._ensure_cache_dir_exists()

    def _ensure_cache_dir_exists(self) -> None:
        """Ensure the cache directory exists."""
        cache_dir = os.path.dirname(self._cache_file)
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

    def get_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid authentication token.

        This method first checks for a valid cached token unless force_refresh is True.
        If no valid cached token is found or force_refresh is True, it retrieves a new
        token from the website.

        Args:
            force_refresh: If True, force a new token retrieval even if a cached token exists.

        Returns:
            The authentication token.

        Raises:
            AuthenticationError: If token retrieval fails.
        """
        # Check if we have a valid cached token
        if not force_refresh:
            cached_token = self._get_cached_token()
            if cached_token:
                logger.info("Using cached token")
                return cached_token

        # If no valid cached token, retrieve a new one
        logger.info("Retrieving new token from website")
        try:
            token = self._retrieve_token_from_website()

            # Cache the new token
            self._cache_token(token)

            return token
        except Exception as e:
            logger.error(f"Failed to retrieve token: {e}")
            raise AuthenticationError(f"Failed to authenticate with h2hggl.com: {e}") from e

    def _get_cached_token(self) -> Optional[str]:
        """
        Retrieve a cached token if it exists and is still valid.

        Returns:
            The cached token if valid, None otherwise.
        """
        if not os.path.exists(self._cache_file):
            logger.info("No token cache file found")
            return None

        try:
            with open(self._cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check if token is expired
            expiry_time = datetime.fromisoformat(cache_data['expiry'])
            if datetime.now() >= expiry_time:
                logger.info("Cached token has expired")
                return None

            return cache_data['token']

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Error reading token cache: {e}")
            return None

    def _cache_token(self, token: str) -> None:
        """
        Cache the token with an expiry time.

        Args:
            token: The token to cache.
        """
        expiry_time = datetime.now() + timedelta(seconds=TOKEN_CACHE_DURATION)
        cache_data: Dict[str, Union[str, Any]] = {
            'token': token,
            'expiry': expiry_time.isoformat(),
            'created_at': datetime.now().isoformat()
        }

        try:
            with open(self._cache_file, 'w') as f:
                json.dump(cache_data, f)
            logger.info("Token cached successfully")
        except Exception as e:
            logger.error(f"Failed to cache token: {e}")

    def _retrieve_token_from_website(self) -> str:
        """
        Retrieve a new token from the website using Selenium.

        Returns:
            The retrieved token.

        Raises:
            AuthenticationError: If token retrieval fails after maximum attempts.
        """
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode (no GUI)
        chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
        chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems

        # Initialize the Chrome driver
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except WebDriverException as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise AuthenticationError(f"Failed to initialize Chrome driver: {e}") from e

        try:
            # Visit the website
            logger.info(f"Navigating to {H2HGGL_PLAYERS_URL}")
            driver.get(H2HGGL_PLAYERS_URL)

            # Wait for the token to be set in local storage
            WebDriverWait(driver, SELENIUM_TIMEOUT)  # Initialize wait object to ensure page is loaded
            token = None
            attempt = 0

            while attempt < MAX_RETRY_ATTEMPTS and token is None:
                try:
                    token = driver.execute_script("return localStorage.getItem('sis-hudstats-token')")
                    if not token:
                        logger.info(f"Token not found on attempt {attempt + 1}, retrying...")
                        time.sleep(RETRY_DELAY)
                        attempt += 1
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    attempt += 1
                    time.sleep(RETRY_DELAY)

            if token is None:
                raise AuthenticationError("Failed to retrieve bearer token after maximum attempts")

            logger.info("Successfully retrieved token")
            return token

        except TimeoutException as e:
            logger.error(f"Timeout while retrieving token: {e}")
            raise AuthenticationError(f"Timeout while retrieving token: {e}") from e

        except Exception as e:
            logger.error(f"Error retrieving token: {e}")
            raise AuthenticationError(f"Error retrieving token: {e}") from e

        finally:
            driver.quit()


def get_bearer_token(force_refresh: bool = False) -> str:
    """
    Convenience function to get a bearer token.

    This function creates a TokenManager instance and uses it to retrieve a token.

    Args:
        force_refresh: If True, force a new token retrieval.

    Returns:
        The authentication token.

    Raises:
        AuthenticationError: If token retrieval fails.
    """
    token_manager = TokenManager()
    return token_manager.get_token(force_refresh=force_refresh)
