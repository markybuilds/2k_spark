"""
Example script demonstrating how to use the matches module to fetch upcoming matches.
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from tabulate import tabulate

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.matches import (
    fetch_upcoming_matches,
    fetch_todays_matches,
    fetch_player_upcoming_matches,
    get_player_matches_for_date
)
from src.data.standings import (
    fetch_standings,
    get_player_by_name
)
from src.config import RAW_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_matches_to_file(matches_data, filename):
    """Save matches data to a JSON file in the raw data directory."""
    # Ensure the raw data directory exists
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    # Create the full file path
    file_path = os.path.join(RAW_DATA_DIR, filename)
    
    # Save the data
    with open(file_path, 'w') as f:
        json.dump(matches_data, f, indent=2)
    logger.info(f"Saved matches data to {file_path}")


def display_upcoming_matches(matches_data, limit=10):
    """Display upcoming matches in a formatted table."""
    # Sort matches by start time
    sorted_matches = sorted(matches_data, key=lambda x: x.get('fixtureStart', ''))
    
    # Take only the specified number of matches
    limited_matches = sorted_matches[:limit]
    
    # Prepare data for tabulate
    headers = ['Date', 'Time', 'Home Player', 'Away Player', 'Teams']
    table_data = []
    
    for match in limited_matches:
        # Format date and time
        date_str = match.get('fixtureStart', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                date_formatted = date_obj.strftime('%Y-%m-%d')
                time_formatted = date_obj.strftime('%H:%M')
            except ValueError:
                date_formatted = 'Unknown'
                time_formatted = 'Unknown'
        else:
            date_formatted = 'Unknown'
            time_formatted = 'Unknown'
        
        # Format teams
        teams = f"{match.get('homeTeamName', 'Unknown')} vs {match.get('awayTeamName', 'Unknown')}"
        
        table_data.append([
            date_formatted,
            time_formatted,
            match.get('homeParticipantName', 'Unknown'),
            match.get('awayParticipantName', 'Unknown'),
            teams
        ])
    
    # Display the table
    print("\nUpcoming Matches:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_player_upcoming_matches(player_name, standings_data):
    """Display upcoming matches for a specific player."""
    # Find the player in the standings data
    player = get_player_by_name(standings_data, player_name)
    
    if not player:
        logger.error(f"Player '{player_name}' not found in standings data")
        return
    
    player_id = player.get('participantId')
    
    # Get player's upcoming matches
    player_matches = fetch_player_upcoming_matches(player_id, hours_ahead=48)
    
    # Display player information
    print(f"\nUpcoming Matches for {player_name} (ID: {player_id}):")
    
    if not player_matches:
        print("No upcoming matches found for this player in the next 48 hours.")
        return
    
    # Prepare data for tabulate
    headers = ['Date', 'Time', 'Opponent', 'Home/Away', 'Teams']
    table_data = []
    
    for match in player_matches:
        # Format date and time
        date_str = match.get('fixtureStart', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                date_formatted = date_obj.strftime('%Y-%m-%d')
                time_formatted = date_obj.strftime('%H:%M')
            except ValueError:
                date_formatted = 'Unknown'
                time_formatted = 'Unknown'
        else:
            date_formatted = 'Unknown'
            time_formatted = 'Unknown'
        
        # Determine opponent and home/away status
        if match.get('homeParticipantId') == player_id:
            # Player is home
            opponent = match.get('awayParticipantName', 'Unknown')
            home_away = 'Home'
        else:
            # Player is away
            opponent = match.get('homeParticipantName', 'Unknown')
            home_away = 'Away'
        
        # Format teams
        teams = f"{match.get('homeTeamName', 'Unknown')} vs {match.get('awayTeamName', 'Unknown')}"
        
        table_data.append([
            date_formatted,
            time_formatted,
            opponent,
            home_away,
            teams
        ])
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_todays_matches():
    """Display today's matches."""
    # Get today's matches
    todays_matches = fetch_todays_matches()
    
    # Display today's matches
    print(f"\nToday's Matches ({datetime.now().strftime('%Y-%m-%d')}):")
    
    if not todays_matches:
        print("No matches scheduled for today.")
        return
    
    # Display the matches
    display_upcoming_matches(todays_matches)


def main():
    """Main function to demonstrate the matches module for upcoming matches."""
    try:
        # Fetch standings data
        logger.info("Fetching standings data...")
        standings_data = fetch_standings(tournament_id=1)
        
        # Fetch upcoming matches for the next 24 hours
        logger.info("Fetching upcoming matches for the next 24 hours...")
        upcoming_matches = fetch_upcoming_matches(hours_ahead=24)
        
        # Save to file
        save_matches_to_file(upcoming_matches, 'upcoming_matches_24h.json')
        
        # Display upcoming matches
        display_upcoming_matches(upcoming_matches, limit=15)
        
        # Fetch upcoming matches for the next 7 days
        logger.info("Fetching upcoming matches for the next 7 days...")
        weekly_matches = fetch_upcoming_matches(hours_ahead=0, days_ahead=7)
        
        # Save to file
        save_matches_to_file(weekly_matches, 'upcoming_matches_7d.json')
        
        # Display today's matches
        display_todays_matches()
        
        # Display upcoming matches for specific players
        display_player_upcoming_matches('SPARKZ', standings_data)
        display_player_upcoming_matches('HOGGY', standings_data)
        
        # Get matches for a specific player on a specific date
        tomorrow = datetime.now() + timedelta(days=1)
        player = get_player_by_name(standings_data, 'SPARKZ')
        if player:
            logger.info(f"Fetching matches for SPARKZ on {tomorrow.strftime('%Y-%m-%d')}...")
            tomorrow_matches = get_player_matches_for_date(player.get('participantId'), date=tomorrow)
            
            if tomorrow_matches:
                print(f"\nMatches for SPARKZ on {tomorrow.strftime('%Y-%m-%d')}:")
                # Prepare data for tabulate
                headers = ['Time', 'Opponent', 'Home/Away', 'Teams']
                table_data = []
                
                for match in tomorrow_matches:
                    # Format time
                    date_str = match.get('fixtureStart', '')
                    if date_str:
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                            time_formatted = date_obj.strftime('%H:%M')
                        except ValueError:
                            time_formatted = 'Unknown'
                    else:
                        time_formatted = 'Unknown'
                    
                    # Determine opponent and home/away status
                    if match.get('homeParticipantId') == player.get('participantId'):
                        # Player is home
                        opponent = match.get('awayParticipantName', 'Unknown')
                        home_away = 'Home'
                    else:
                        # Player is away
                        opponent = match.get('homeParticipantName', 'Unknown')
                        home_away = 'Away'
                    
                    # Format teams
                    teams = f"{match.get('homeTeamName', 'Unknown')} vs {match.get('awayTeamName', 'Unknown')}"
                    
                    table_data.append([
                        time_formatted,
                        opponent,
                        home_away,
                        teams
                    ])
                
                # Display the table
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            else:
                print(f"\nNo matches found for SPARKZ on {tomorrow.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
