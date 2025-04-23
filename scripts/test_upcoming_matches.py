"""
Script to test the API endpoint for upcoming matches.
"""
import os
import sys
import requests
import json
import logging
from datetime import datetime, timedelta

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import RAW_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_upcoming_matches_api():
    """Test the API endpoint for upcoming matches."""
    # API endpoint
    url = 'https://api-sis-stats.hudstats.com/v1/schedule'
    
    # Get current date and time
    now = datetime.now()
    
    # Format dates with time
    from_datetime = now.strftime('%Y-%m-%d %H:%M')
    to_datetime = (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
    
    # Query parameters
    params = {
        'schedule-type': 'fixture',
        'from': from_datetime,
        'to': to_datetime,
        'order': 'asc',
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
        
        # Pretty print the response (first 3 items only)
        logger.info("Response received successfully")
        if isinstance(data, list) and len(data) > 0:
            print(json.dumps(data[:3], indent=2))
            logger.info(f"Retrieved {len(data)} upcoming matches")
        else:
            print(json.dumps(data, indent=2))
        
        # Ensure the raw data directory exists
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        
        # Save the data to a file
        file_path = os.path.join(RAW_DATA_DIR, 'upcoming_matches.json')
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved data to {file_path}")
        
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
    """Test the API endpoint for upcoming matches using the auth module."""
    try:
        from src.auth import get_bearer_token
        
        logger.info("Testing with auth module...")
        
        # Get authentication token
        token = get_bearer_token()
        logger.info(f"Retrieved token: {token[:20]}...")
        
        # Get current date and time
        now = datetime.now()
        
        # Format dates with time
        from_datetime = now.strftime('%Y-%m-%d %H:%M')
        to_datetime = (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
        
        # API endpoint
        url = 'https://api-sis-stats.hudstats.com/v1/schedule'
        
        # Query parameters
        params = {
            'schedule-type': 'fixture',
            'from': from_datetime,
            'to': to_datetime,
            'order': 'asc',
            'tournament-id': 1
        }
        
        # Headers
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': f'Bearer {token}',
            'origin': 'https://h2hggl.com',
            'referer': 'https://h2hggl.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
        
        # Make the request
        logger.info(f"Making request to {url} with params {params}")
        response = requests.get(url, params=params, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Pretty print the response (first 3 items only)
        logger.info("Response received successfully")
        if isinstance(data, list) and len(data) > 0:
            print(json.dumps(data[:3], indent=2))
            logger.info(f"Retrieved {len(data)} upcoming matches")
        else:
            print(json.dumps(data, indent=2))
        
        return data
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test with direct API call
    test_upcoming_matches_api()
    
    print("\n" + "="*80 + "\n")
    
    # Test with auth module
    test_with_auth_module()
