"""
Script to match our data with the official schedule format.
"""
import os
import sys
import json
import pytz
import requests
from datetime import datetime, timedelta
from tabulate import tabulate
from bs4 import BeautifulSoup

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.matches import (
    fetch_upcoming_matches,
    parse_utc_datetime,
    convert_to_local_time,
    format_datetime
)
from src.auth import get_bearer_token
from src.config import RAW_DATA_DIR

def fetch_official_schedule():
    """Fetch the official schedule from the website."""
    try:
        # Get authentication token
        token = get_bearer_token()
        
        # Headers
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': f'Bearer {token}',
            'origin': 'https://h2hggl.com',
            'referer': 'https://h2hggl.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
        
        # Get current date and time
        now = datetime.now()
        
        # Format dates with time for the next 24 hours
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
        
        # Make the request
        print(f"Fetching official schedule from {url} with params {params}")
        response = requests.get(url, params=params, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Save the raw data for reference
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        with open(os.path.join(RAW_DATA_DIR, 'official_schedule_raw.json'), 'w') as f:
            json.dump(data, f, indent=2)
        
        return data
    
    except Exception as e:
        print(f"Error fetching official schedule: {e}")
        return []

def main():
    """Main function to match our data with the official schedule format."""
    # Fetch the official schedule
    official_data = fetch_official_schedule()
    
    if not official_data:
        print("Failed to fetch official schedule. Exiting.")
        return
    
    # Sort matches by start time
    sorted_matches = sorted(official_data, key=lambda x: x.get('fixtureStart', ''))
    
    # Display matches in a format similar to the official schedule
    print("\nUpcoming Matches (Next 24 Hours) - Official Format:")
    print("-" * 100)
    
    # Prepare data for tabulate
    headers = ['Date', 'Time (12h)', 'Time (24h)', 'Home Player', 'Away Player', 'Teams', 'UTC Time']
    table_data = []
    
    for match in sorted_matches:
        # Get the UTC time string
        utc_time_str = match.get('fixtureStart', '')
        
        # Parse the UTC time
        utc_dt = parse_utc_datetime(utc_time_str)
        
        # Convert to local time
        local_dt = convert_to_local_time(utc_dt) if utc_dt else None
        
        # Format the times
        date_formatted = local_dt.strftime('%a, %b %d, %Y') if local_dt else 'Unknown'  # e.g., "Tue, Apr 23, 2025"
        time_12h = local_dt.strftime('%I:%M %p') if local_dt else 'Unknown'  # e.g., "06:11 AM"
        time_24h = local_dt.strftime('%H:%M') if local_dt else 'Unknown'  # e.g., "06:11"
        utc_formatted = utc_dt.strftime('%H:%M') if utc_dt else 'Unknown'
        
        # Format teams
        teams = f"{match.get('homeTeamName', 'Unknown')} vs {match.get('awayTeamName', 'Unknown')}"
        
        table_data.append([
            date_formatted,
            time_12h,
            time_24h,
            match.get('homeParticipantName', 'Unknown'),
            match.get('awayParticipantName', 'Unknown'),
            teams,
            utc_formatted
        ])
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display time zone information
    print("\nTime Zone Information:")
    print(f"UTC Offset: {datetime.now(pytz.timezone('America/New_York')).strftime('%z')}")
    print(f"Time Zone: {datetime.now(pytz.timezone('America/New_York')).tzname()}")
    
    # Display current time in both UTC and local time
    now_utc = datetime.now(pytz.UTC)
    now_local = now_utc.astimezone(pytz.timezone('America/New_York'))
    print(f"\nCurrent Time:")
    print(f"UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Local (ET): {now_local.strftime('%Y-%m-%d %I:%M:%S %p')}")  # 12-hour format with AM/PM
    
    # Instructions for manual comparison
    print("\nTo compare with the official schedule:")
    print("1. Open the official schedule at: https://h2hggl.com/en/ebasketball/schedule")
    print("2. Verify that the match times in our data match the times shown on the official schedule")
    print("3. Check that the player matchups are correct")
    print("4. Confirm that the team matchups are accurate")

if __name__ == "__main__":
    main()
