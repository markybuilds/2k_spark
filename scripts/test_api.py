"""
Script to test the API endpoint for player standings.
"""
import os
import sys
import requests
import json
import logging

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_standings_api():
    """Test the standings API endpoint."""
    url = 'https://api-sis-stats.hudstats.com/v1/standings/participant'
    
    # Query parameters
    params = {
        'tournament-id': 1
    }
    
    # Headers
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyLWlkIjo5LCJuYW1lIjoiZ3Vlc3QiLCJyb2xlIjoidmlld2VyIiwidGVhbS1pZCI6bnVsbCwiZXhwIjoxNzQ1NDk4NzgzfQ.5P57S-vqZVNdV1NAJ8NkUiujbh3b7pCKIKGQF0MRSek',
        'origin': 'https://h2hggl.com',
        'referer': 'https://h2hggl.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }
    
    try:
        # Make the request
        logger.info(f"Making request to {url} with params {params}")
        response = requests.get(url, params=params, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Pretty print the response
        logger.info("Response received successfully")
        print(json.dumps(data[:3], indent=2))  # Print only the first 3 items to avoid overwhelming output
        logger.info(f"Retrieved {len(data)} participants")
        
        return data
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        logger.error(f"Response content: {response.text}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout Error: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Exception: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e}")
        logger.error(f"Response content: {response.text}")
    
    return None

def test_with_auth_module():
    """Test the standings API endpoint using the auth module."""
    try:
        from src.auth import get_bearer_token
        from src.data.standings import fetch_standings
        
        logger.info("Testing with auth module...")
        
        # Get authentication token
        token = get_bearer_token()
        logger.info(f"Retrieved token: {token[:20]}...")
        
        # Fetch standings data
        standings_data = fetch_standings(tournament_id=1)
        logger.info(f"Retrieved {len(standings_data)} participants")
        
        # Print the first 3 items
        print(json.dumps(standings_data[:3], indent=2))
        
        return standings_data
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test with direct API call
    test_standings_api()
    
    print("\n" + "="*80 + "\n")
    
    # Test with auth module
    test_with_auth_module()
