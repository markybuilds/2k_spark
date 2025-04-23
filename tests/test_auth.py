"""
Unit tests for the authentication module.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import json
from datetime import datetime, timedelta

from src.auth import TokenManager, get_bearer_token


class TestTokenManager(unittest.TestCase):
    """Test cases for the TokenManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary token cache file path for testing
        self.test_cache_file = "test_token_cache.txt"

        # Create a TokenManager instance for testing with the test cache file
        self.token_manager = TokenManager(cache_file=self.test_cache_file)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the test cache file if it exists
        if os.path.exists(self.test_cache_file):
            os.remove(self.test_cache_file)

    def test_cache_token(self):
        """Test that tokens are cached correctly."""
        test_token = "test_token_123"
        self.token_manager._cache_token(test_token)

        # Check that the cache file exists
        self.assertTrue(os.path.exists(self.test_cache_file))

        # Check that the token is correctly stored in the cache file
        with open(self.test_cache_file, 'r') as f:
            cache_data = json.load(f)

        self.assertEqual(cache_data['token'], test_token)
        self.assertTrue('expiry' in cache_data)

    def test_get_cached_token_valid(self):
        """Test retrieving a valid cached token."""
        test_token = "test_token_456"
        expiry_time = datetime.now() + timedelta(hours=1)

        # Create a cache file with a valid token
        cache_data = {
            'token': test_token,
            'expiry': expiry_time.isoformat()
        }

        with open(self.test_cache_file, 'w') as f:
            json.dump(cache_data, f)

        # Get the cached token
        cached_token = self.token_manager._get_cached_token()

        self.assertEqual(cached_token, test_token)

    def test_get_cached_token_expired(self):
        """Test retrieving an expired cached token."""
        test_token = "test_token_789"
        expiry_time = datetime.now() - timedelta(hours=1)  # Expired

        # Create a cache file with an expired token
        cache_data = {
            'token': test_token,
            'expiry': expiry_time.isoformat()
        }

        with open(self.test_cache_file, 'w') as f:
            json.dump(cache_data, f)

        # Get the cached token
        cached_token = self.token_manager._get_cached_token()

        self.assertIsNone(cached_token)

    @patch('src.auth.TokenManager._retrieve_token_from_website')
    def test_get_token_force_refresh(self, mock_retrieve):
        """Test forcing a token refresh."""
        # Set up the mock
        mock_retrieve.return_value = "new_token_123"

        # Create a cache file with a valid token
        test_token = "test_token_abc"
        expiry_time = datetime.now() + timedelta(hours=1)

        cache_data = {
            'token': test_token,
            'expiry': expiry_time.isoformat()
        }

        with open(self.test_cache_file, 'w') as f:
            json.dump(cache_data, f)

        # Get a token with force_refresh=True
        token = self.token_manager.get_token(force_refresh=True)

        # Check that the token was retrieved from the website
        mock_retrieve.assert_called_once()
        self.assertEqual(token, "new_token_123")


class TestGetBearerToken(unittest.TestCase):
    """Test cases for the get_bearer_token function."""

    @patch('src.auth.TokenManager')
    def test_get_bearer_token(self, mock_token_manager):
        """Test the get_bearer_token function."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.get_token.return_value = "test_token_xyz"
        mock_token_manager.return_value = mock_instance

        # Call the function
        token = get_bearer_token()

        # Check that the token manager was used correctly
        mock_token_manager.assert_called_once()
        mock_instance.get_token.assert_called_once_with(force_refresh=False)
        self.assertEqual(token, "test_token_xyz")

    @patch('src.auth.TokenManager')
    def test_get_bearer_token_force_refresh(self, mock_token_manager):
        """Test the get_bearer_token function with force_refresh=True."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.get_token.return_value = "new_token_xyz"
        mock_token_manager.return_value = mock_instance

        # Call the function with force_refresh=True
        token = get_bearer_token(force_refresh=True)

        # Check that the token manager was used correctly
        mock_token_manager.assert_called_once()
        mock_instance.get_token.assert_called_once_with(force_refresh=True)
        self.assertEqual(token, "new_token_xyz")


if __name__ == '__main__':
    unittest.main()
