"""
Example script demonstrating how to use the standings module.
"""
import os
import sys
import json
import logging
from tabulate import tabulate

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.standings import (
    fetch_standings,
    get_top_players,
    get_player_by_name,
    get_head_to_head_stats
)
from src.config import RAW_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_standings_to_file(standings_data, filename='standings.json'):
    """Save standings data to a JSON file in the raw data directory."""
    # Ensure the raw data directory exists
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Create the full file path
    file_path = os.path.join(RAW_DATA_DIR, filename)

    # Save the data
    with open(file_path, 'w') as f:
        json.dump(standings_data, f, indent=2)
    logger.info(f"Saved standings data to {file_path}")


def display_top_players(standings_data, limit=10):
    """Display the top players in a formatted table."""
    top_players = get_top_players(standings_data, limit=limit)

    # Prepare data for tabulate
    headers = ['Rank', 'Name', 'Win %', 'Avg Points', 'FG %', '3PT %', 'Matches']
    table_data = []

    for i, player in enumerate(top_players, 1):
        table_data.append([
            i,
            player.get('participantName', 'Unknown'),
            f"{player.get('matchesWinPct', 0):.2f}%",
            f"{player.get('avgPoints', 0):.2f}",
            f"{player.get('avgFieldGoalsPercent', 0):.2f}%",
            f"{player.get('3PointersPercent', 0):.2f}%",
            player.get('matchesPlayed', 0)
        ])

    # Display the table
    print("\nTop Players:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_head_to_head(standings_data, player1_name, player2_name):
    """Display head-to-head comparison between two players."""
    player1 = get_player_by_name(standings_data, player1_name)
    player2 = get_player_by_name(standings_data, player2_name)

    if not player1:
        logger.error(f"Player '{player1_name}' not found")
        return

    if not player2:
        logger.error(f"Player '{player2_name}' not found")
        return

    stats = get_head_to_head_stats(player1, player2)

    # Prepare data for tabulate
    headers = ['Statistic', player1_name, player2_name, 'Difference']
    table_data = []

    for stat_name, stat_values in stats.items():
        if stat_name == 'recent_form':
            continue  # Skip recent form for the table

        table_data.append([
            stat_name.replace('_', ' ').title(),
            f"{stat_values['player1']:.2f}",
            f"{stat_values['player2']:.2f}",
            f"{stat_values['difference']:.2f}"
        ])

    # Display the table
    print(f"\nHead-to-Head Comparison: {player1_name} vs {player2_name}")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

    # Display recent form
    print(f"\nRecent Form:")
    print(f"{player1_name}: {' '.join(stats['recent_form']['player1'])}")
    print(f"{player2_name}: {' '.join(stats['recent_form']['player2'])}")


def main():
    """Main function to demonstrate the standings module."""
    try:
        # Fetch standings data
        logger.info("Fetching standings data...")
        standings_data = fetch_standings(tournament_id=1)

        # Save to file
        save_standings_to_file(standings_data)

        # Display top players
        display_top_players(standings_data, limit=10)

        # Display head-to-head comparison
        display_head_to_head(standings_data, 'LANES', 'TAAPZ')

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
