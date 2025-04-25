"""
Token fetcher for the H2H GG League API.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

from config.settings import H2H_WEBSITE_URL, H2H_TOKEN_LOCALSTORAGE_KEY, SELENIUM_HEADLESS, SELENIUM_TIMEOUT
from config.logging_config import get_data_fetcher_logger
from utils.logging import log_execution_time, log_exceptions

logger = get_data_fetcher_logger()


class TokenFetcher:
    """
    Fetches authentication token from H2H GG League website using Selenium.
    """
    
    def __init__(self, website_url=H2H_WEBSITE_URL, token_key=H2H_TOKEN_LOCALSTORAGE_KEY, 
                 headless=SELENIUM_HEADLESS, timeout=SELENIUM_TIMEOUT):
        """
        Initialize the TokenFetcher.
        
        Args:
            website_url (str): URL of the website to fetch token from
            token_key (str): LocalStorage key for the token
            headless (bool): Whether to run Chrome in headless mode
            timeout (int): Timeout in seconds for waiting for token
        """
        self.website_url = website_url
        self.token_key = token_key
        self.headless = headless
        self.timeout = timeout
        self.token = None
        self.token_timestamp = None
    
    @log_execution_time(logger)
    @log_exceptions(logger)
    def get_token(self, force_refresh=False):
        """
        Get the authentication token.
        
        Args:
            force_refresh (bool): Whether to force a token refresh
            
        Returns:
            str: Authentication token
        """
        # Check if we already have a valid token
        if not force_refresh and self.token and self.token_timestamp:
            # Token is considered valid for 1 hour
            if time.time() - self.token_timestamp < 3600:
                logger.debug("Using cached token")
                return self.token
        
        logger.info("Fetching new authentication token")
        
        # Set up Chrome options
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = None
        try:
            # Initialize Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
            
            # Visit the website
            logger.debug(f"Navigating to {self.website_url}")
            driver.get(self.website_url)
            
            # Wait for page to load
            wait = WebDriverWait(driver, self.timeout)
            
            # Wait a bit for JavaScript to execute and set the token
            time.sleep(5)
            
            # Get token from local storage
            token = driver.execute_script(f"return localStorage.getItem('{self.token_key}')")
            
            if not token:
                logger.error("Failed to retrieve token from local storage")
                raise ValueError("Token not found in local storage")
            
            logger.info("Successfully retrieved authentication token")
            self.token = token
            self.token_timestamp = time.time()
            
            return token
            
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Error during token retrieval: {str(e)}")
            raise
        finally:
            if driver:
                driver.quit()
    
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
