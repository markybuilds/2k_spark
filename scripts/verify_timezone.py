"""
Script to verify time zone conversion for upcoming matches.
"""
import os
import sys
import json
import pytz
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.matches import (
    fetch_upcoming_matches,
    parse_utc_datetime,
    convert_to_local_time,
    format_datetime
)

def main():
    """Main function to verify time zone conversion."""
    # Fetch upcoming matches for the next 24 hours
    print("Fetching upcoming matches for the next 24 hours...")
    upcoming_matches = fetch_upcoming_matches(hours_ahead=24)
    
    # Take the first 5 matches
    matches = upcoming_matches[:5]
    
    # Display detailed time information
    print("\nDetailed Time Information for Upcoming Matches:")
    print("-" * 80)
    print(f"{'UTC Time':<20} {'Local Time':<20} {'Home Player':<15} {'Away Player':<15}")
    print("-" * 80)
    
    for match in matches:
        # Get the UTC time string
        utc_time_str = match.get('fixtureStart', '')
        
        # Parse the UTC time
        utc_dt = parse_utc_datetime(utc_time_str)
        
        # Convert to local time
        local_dt = convert_to_local_time(utc_dt) if utc_dt else None
        
        # Format the times
        utc_formatted = utc_dt.strftime('%Y-%m-%d %H:%M') if utc_dt else 'Unknown'
        local_formatted = local_dt.strftime('%Y-%m-%d %H:%M') if local_dt else 'Unknown'
        
        # Display the information
        print(f"{utc_formatted:<20} {local_formatted:<20} {match.get('homeParticipantName', 'Unknown'):<15} {match.get('awayParticipantName', 'Unknown'):<15}")
    
    # Display time zone information
    print("\nTime Zone Information:")
    print(f"UTC Offset: {datetime.now(pytz.timezone('America/New_York')).strftime('%z')}")
    print(f"Time Zone: {datetime.now(pytz.timezone('America/New_York')).tzname()}")
    
    # Display current time in both UTC and local time
    now_utc = datetime.now(pytz.UTC)
    now_local = now_utc.astimezone(pytz.timezone('America/New_York'))
    print(f"\nCurrent Time:")
    print(f"UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Local: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
