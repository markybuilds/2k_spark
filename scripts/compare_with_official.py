"""
Script to compare our match data with the official schedule.
"""
import os
import sys
import json
import pytz
from datetime import datetime, timedelta
from tabulate import tabulate

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.matches import (
    fetch_upcoming_matches,
    parse_utc_datetime,
    convert_to_local_time,
    format_datetime
)
from src.config import RAW_DATA_DIR

def main():
    """Main function to compare our data with the official schedule."""
    # Fetch upcoming matches for the next 24 hours
    print("Fetching upcoming matches for the next 24 hours...")
    upcoming_matches = fetch_upcoming_matches(hours_ahead=24)
    
    # Save the raw data for reference
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    with open(os.path.join(RAW_DATA_DIR, 'official_comparison.json'), 'w') as f:
        json.dump(upcoming_matches, f, indent=2)
    
    # Sort matches by start time
    sorted_matches = sorted(upcoming_matches, key=lambda x: x.get('fixtureStart', ''))
    
    # Display matches in a format similar to the official schedule
    print("\nUpcoming Matches (Next 24 Hours):")
    print("-" * 100)
    
    # Prepare data for tabulate
    headers = ['Date', 'Time (ET)', 'Home Player', 'Away Player', 'Teams', 'UTC Time']
    table_data = []
    
    for match in sorted_matches:
        # Get the UTC time string
        utc_time_str = match.get('fixtureStart', '')
        
        # Parse the UTC time
        utc_dt = parse_utc_datetime(utc_time_str)
        
        # Convert to local time
        local_dt = convert_to_local_time(utc_dt) if utc_dt else None
        
        # Format the times
        date_formatted = local_dt.strftime('%Y-%m-%d') if local_dt else 'Unknown'
        time_formatted = local_dt.strftime('%H:%M') if local_dt else 'Unknown'
        utc_formatted = utc_dt.strftime('%H:%M') if utc_dt else 'Unknown'
        
        # Format teams
        teams = f"{match.get('homeTeamName', 'Unknown')} vs {match.get('awayTeamName', 'Unknown')}"
        
        table_data.append([
            date_formatted,
            time_formatted,
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
    print(f"Local (ET): {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Instructions for manual comparison
    print("\nTo compare with the official schedule:")
    print("1. Open the official schedule at: https://h2hggl.com/en/ebasketball/schedule")
    print("2. Verify that the match times in our data match the times shown on the official schedule")
    print("3. Check that the player matchups are correct")
    print("4. Confirm that the team matchups are accurate")

if __name__ == "__main__":
    main()
