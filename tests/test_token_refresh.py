"""
Script to test the token retrieval functionality with force refresh.
"""
import logging
import unittest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.auth import get_bearer_token, AuthenticationError


class TestTokenRefresh(unittest.TestCase):
    """Test case for token refresh functionality."""
    
    def test_token_refresh(self):
        """Test that token refresh works correctly."""
        # Get the current cached token
        current_token = get_bearer_token()
        self.assertIsNotNone(current_token, "Failed to get current token")
        
        # Force a refresh to get a new token
        new_token = get_bearer_token(force_refresh=True)
        self.assertIsNotNone(new_token, "Failed to get new token")
        
        # Note: We don't assert that tokens are different because the server
        # might return the same token in some cases


def main():
    """Run the test manually."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Testing token retrieval with force refresh...")
    
    try:
        # Get the current cached token
        current_token = get_bearer_token()
        logger.info(f"Current token: {current_token[:20]}...")
        
        # Force a refresh to get a new token
        logger.info("Forcing token refresh...")
        new_token = get_bearer_token(force_refresh=True)
        logger.info(f"New token: {new_token[:20]}...")
        
        # Check if the tokens are different
        if current_token != new_token:
            logger.info("SUCCESS: Token was successfully refreshed (tokens are different)")
        else:
            logger.warning("WARNING: Tokens are identical after refresh. This might be normal if the server returns the same token.")
            
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    # If run directly, run the manual test
    main()
