"""
Example script demonstrating how to use the matches module.
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
    fetch_matches,
    fetch_upcoming_matches,
    calculate_player_win_rate,
    calculate_player_average_score,
    get_player_form
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


def save_matches_to_file(matches_data, filename='matches.json'):
    """Save matches data to a JSON file in the raw data directory."""
    # Ensure the raw data directory exists
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Create the full file path
    file_path = os.path.join(RAW_DATA_DIR, filename)

    # Save the data
    with open(file_path, 'w') as f:
        json.dump(matches_data, f, indent=2)
    logger.info(f"Saved matches data to {file_path}")


def display_recent_matches(matches_data, limit=10):
    """Display recent matches in a formatted table."""
    # Sort matches by date (most recent first)
    sorted_matches = sorted(matches_data, key=lambda x: x.get('startDate', ''), reverse=True)

    # Take only the most recent matches
    recent_matches = sorted_matches[:limit]

    # Prepare data for tabulate
    headers = ['Date', 'Home Player', 'Score', 'Away Player', 'Result']
    table_data = []

    for match in recent_matches:
        # Format date
        date_str = match.get('startDate', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                date_formatted = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                date_formatted = date_str
        else:
            date_formatted = 'Unknown'

        # Format score
        score = f"{match.get('homeScore', 0)} - {match.get('awayScore', 0)}"

        # Format result
        result = match.get('result', '')
        if result == 'home_win':
            result = 'Home Win'
        elif result == 'away_win':
            result = 'Away Win'
        else:
            result = 'Draw'

        table_data.append([
            date_formatted,
            match.get('homeParticipantName', 'Unknown'),
            score,
            match.get('awayParticipantName', 'Unknown'),
            result
        ])

    # Display the table
    print("\nRecent Matches:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_player_stats(player_name, matches_data, standings_data):
    """Display statistics for a specific player."""
    # Find the player in the standings data
    player = get_player_by_name(standings_data, player_name)

    if not player:
        logger.error(f"Player '{player_name}' not found in standings data")
        return

    player_id = player.get('participantId')

    # Get player's match history
    player_matches = [
        match for match in matches_data
        if match.get('homeParticipantId') == player_id or match.get('awayParticipantId') == player_id
    ]

    # Calculate statistics
    win_rate = calculate_player_win_rate(player_matches, player_id)
    avg_score = calculate_player_average_score(player_matches, player_id)
    form = get_player_form(player_matches, player_id)

    # Display player information
    print(f"\nPlayer: {player_name} (ID: {player_id})")
    print(f"Matches Played: {len(player_matches)}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Average Score: {avg_score:.2f}")
    print(f"Recent Form: {' '.join(form)}")

    # Display recent matches
    player_matches.sort(key=lambda x: x.get('startDate', ''), reverse=True)
    recent_matches = player_matches[:5]

    headers = ['Date', 'Opponent', 'Score', 'Result']
    table_data = []

    for match in recent_matches:
        # Format date
        date_str = match.get('startDate', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                date_formatted = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                date_formatted = date_str
        else:
            date_formatted = 'Unknown'

        # Determine opponent and score
        if match.get('homeParticipantId') == player_id:
            # Player was home
            opponent = match.get('awayParticipantName', 'Unknown')
            score = f"{match.get('homeScore', 0)} - {match.get('awayScore', 0)}"
            result = 'Win' if match.get('result') == 'home_win' else 'Loss'
        else:
            # Player was away
            opponent = match.get('homeParticipantName', 'Unknown')
            score = f"{match.get('awayScore', 0)} - {match.get('homeScore', 0)}"
            result = 'Win' if match.get('result') == 'away_win' else 'Loss'

        table_data.append([
            date_formatted,
            opponent,
            score,
            result
        ])

    print("\nRecent Matches:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_head_to_head(player1_name, player2_name, matches_data, standings_data):
    """Display head-to-head statistics between two players."""
    # Find the players in the standings data
    player1 = get_player_by_name(standings_data, player1_name)
    player2 = get_player_by_name(standings_data, player2_name)

    if not player1:
        logger.error(f"Player '{player1_name}' not found in standings data")
        return

    if not player2:
        logger.error(f"Player '{player2_name}' not found in standings data")
        return

    player1_id = player1.get('participantId')
    player2_id = player2.get('participantId')

    # Get head-to-head matches
    h2h_matches = [
        match for match in matches_data
        if (match.get('homeParticipantId') == player1_id and match.get('awayParticipantId') == player2_id) or
           (match.get('homeParticipantId') == player2_id and match.get('awayParticipantId') == player1_id)
    ]

    # Sort matches by date (most recent first)
    h2h_matches.sort(key=lambda x: x.get('startDate', ''), reverse=True)

    # Calculate head-to-head statistics
    player1_wins = 0
    player2_wins = 0

    for match in h2h_matches:
        if match.get('homeParticipantId') == player1_id and match.get('result') == 'home_win':
            player1_wins += 1
        elif match.get('awayParticipantId') == player1_id and match.get('result') == 'away_win':
            player1_wins += 1
        elif match.get('homeParticipantId') == player2_id and match.get('result') == 'home_win':
            player2_wins += 1
        elif match.get('awayParticipantId') == player2_id and match.get('result') == 'away_win':
            player2_wins += 1

    # Display head-to-head information
    print(f"\nHead-to-Head: {player1_name} vs {player2_name}")
    print(f"Total Matches: {len(h2h_matches)}")
    print(f"{player1_name} Wins: {player1_wins}")
    print(f"{player2_name} Wins: {player2_wins}")

    # Display head-to-head matches
    headers = ['Date', 'Home', 'Score', 'Away', 'Winner']
    table_data = []

    for match in h2h_matches:
        # Format date
        date_str = match.get('startDate', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                date_formatted = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                date_formatted = date_str
        else:
            date_formatted = 'Unknown'

        # Format score
        score = f"{match.get('homeScore', 0)} - {match.get('awayScore', 0)}"

        # Determine winner
        if match.get('result') == 'home_win':
            winner = match.get('homeParticipantName', 'Unknown')
        elif match.get('result') == 'away_win':
            winner = match.get('awayParticipantName', 'Unknown')
        else:
            winner = 'Draw'

        table_data.append([
            date_formatted,
            match.get('homeParticipantName', 'Unknown'),
            score,
            match.get('awayParticipantName', 'Unknown'),
            winner
        ])

    print("\nHead-to-Head Matches:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def main():
    """Main function to demonstrate the matches module."""
    try:
        # Fetch standings data
        logger.info("Fetching standings data...")
        standings_data = fetch_standings(tournament_id=1)

        # Fetch match data for the last 30 days
        logger.info("Fetching match data for the last 30 days...")
        today = datetime.now()
        from_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        to_date = today.strftime('%Y-%m-%d')

        matches_data = fetch_matches(
            from_date=from_date,
            to_date=to_date,
            tournament_id=1,
            schedule_type='match'
        )

        # Save to file
        save_matches_to_file(matches_data, 'recent_matches.json')

        # Display recent matches
        display_recent_matches(matches_data, limit=10)

        # Display player statistics
        display_player_stats('SPARKZ', matches_data, standings_data)

        # Display head-to-head statistics
        display_head_to_head('SPARKZ', 'SAINT JR', matches_data, standings_data)

        # Fetch upcoming matches
        logger.info("Fetching upcoming matches...")
        upcoming_matches = fetch_upcoming_matches(days_ahead=7, tournament_id=1)

        # Display upcoming matches
        if upcoming_matches:
            print("\nUpcoming Matches:")
            headers = ['Date', 'Home Player', 'Away Player']
            table_data = []

            for match in upcoming_matches:
                # Format date
                date_str = match.get('fixtureStart', '')
                if date_str:
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                        date_formatted = date_obj.strftime('%Y-%m-%d %H:%M')
                    except ValueError:
                        date_formatted = date_str
                else:
                    date_formatted = 'Unknown'

                table_data.append([
                    date_formatted,
                    match.get('homeParticipantName', 'Unknown'),
                    match.get('awayParticipantName', 'Unknown')
                ])

            print(tabulate(table_data, headers=headers, tablefmt='grid'))
        else:
            print("\nNo upcoming matches found.")

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
