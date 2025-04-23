"""
Example script demonstrating how to use the player-team analysis module.
"""
import os
import sys
import json
import logging
from tabulate import tabulate

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.standings import fetch_standings, get_player_by_name
from src.analysis.player_team_analysis import (
    get_player_team_history,
    calculate_player_team_stats,
    get_player_best_teams,
    get_player_worst_teams,
    get_player_team_matchup_stats,
    compare_player_team_performance,
    predict_player_team_matchup
)
from src.config import RAW_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_data_to_file(data, filename):
    """Save data to a JSON file in the raw data directory."""
    # Ensure the raw data directory exists
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    # Create the full file path
    file_path = os.path.join(RAW_DATA_DIR, filename)
    
    # Save the data
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved data to {file_path}")


def display_player_team_stats(player_name, team_stats):
    """Display a player's performance with different teams."""
    print(f"\nTeam Performance for {player_name}:")
    
    # Prepare data for tabulate
    headers = ['Team', 'Matches', 'Wins', 'Losses', 'Win Rate', 'Avg Score', 'Avg Opp Score', 'Score Diff']
    table_data = []
    
    for team_name, stats in team_stats.items():
        table_data.append([
            team_name,
            stats.get('matches', 0),
            stats.get('wins', 0),
            stats.get('losses', 0),
            f"{stats.get('win_rate', 0):.3f}",
            f"{stats.get('avg_score', 0):.1f}",
            f"{stats.get('avg_opponent_score', 0):.1f}",
            f"{stats.get('avg_score_diff', 0):.1f}"
        ])
    
    # Sort by number of matches (descending)
    table_data.sort(key=lambda x: x[1], reverse=True)
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_best_worst_teams(player_name, best_teams, worst_teams):
    """Display a player's best and worst teams."""
    print(f"\nBest Teams for {player_name}:")
    
    # Prepare data for tabulate
    headers = ['Team', 'Win Rate', 'Matches']
    best_table = []
    
    for team_name, win_rate, matches in best_teams:
        best_table.append([
            team_name,
            f"{win_rate:.3f}",
            matches
        ])
    
    # Display the table
    print(tabulate(best_table, headers=headers, tablefmt='grid'))
    
    print(f"\nWorst Teams for {player_name}:")
    
    worst_table = []
    
    for team_name, win_rate, matches in worst_teams:
        worst_table.append([
            team_name,
            f"{win_rate:.3f}",
            matches
        ])
    
    # Display the table
    print(tabulate(worst_table, headers=headers, tablefmt='grid'))


def display_team_matchup_stats(player_name, team_name, matchup_stats):
    """Display a player's performance with a specific team against all opponents."""
    print(f"\nMatchup Statistics for {player_name} with {team_name}:")
    print(f"Overall: {matchup_stats.get('matches', 0)} matches, {matchup_stats.get('wins', 0)} wins, {matchup_stats.get('losses', 0)} losses")
    print(f"Win Rate: {matchup_stats.get('win_rate', 0):.3f}")
    
    # Prepare data for tabulate
    headers = ['Opponent Team', 'Matches', 'Wins', 'Losses', 'Win Rate', 'Avg Score', 'Avg Opp Score', 'Score Diff']
    table_data = []
    
    for opponent_team, stats in matchup_stats.get('opponent_stats', {}).items():
        table_data.append([
            opponent_team,
            stats.get('matches', 0),
            stats.get('wins', 0),
            stats.get('losses', 0),
            f"{stats.get('win_rate', 0):.3f}",
            f"{stats.get('avg_score', 0):.1f}",
            f"{stats.get('avg_opponent_score', 0):.1f}",
            f"{stats.get('avg_score_diff', 0):.1f}"
        ])
    
    # Sort by number of matches (descending)
    table_data.sort(key=lambda x: x[1], reverse=True)
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_team_comparison(player_name, comparison):
    """Display a comparison of a player's performance with two different teams."""
    team1 = comparison.get('team1', {})
    team2 = comparison.get('team2', {})
    
    print(f"\nTeam Comparison for {player_name}:")
    print(f"{team1.get('name', 'Team 1')} vs {team2.get('name', 'Team 2')}")
    
    # Prepare data for tabulate
    headers = ['Metric', team1.get('name', 'Team 1'), team2.get('name', 'Team 2'), 'Difference']
    table_data = [
        ['Matches', team1.get('matches', 0), team2.get('matches', 0), team1.get('matches', 0) - team2.get('matches', 0)],
        ['Wins', team1.get('wins', 0), team2.get('wins', 0), team1.get('wins', 0) - team2.get('wins', 0)],
        ['Losses', team1.get('losses', 0), team2.get('losses', 0), team1.get('losses', 0) - team2.get('losses', 0)],
        ['Win Rate', f"{team1.get('win_rate', 0):.3f}", f"{team2.get('win_rate', 0):.3f}", f"{comparison.get('win_rate_diff', 0):.3f}"],
        ['Avg Score', f"{team1.get('avg_score', 0):.1f}", f"{team2.get('avg_score', 0):.1f}", f"{comparison.get('avg_score_diff', 0):.1f}"],
        ['Avg Opp Score', f"{team1.get('avg_opponent_score', 0):.1f}", f"{team2.get('avg_opponent_score', 0):.1f}", f"{comparison.get('avg_opponent_score_diff', 0):.1f}"]
    ]
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display the better team
    better_team = comparison.get('better_team', 'Unknown')
    print(f"\nBetter Team: {better_team}")


def display_matchup_prediction(prediction):
    """Display a prediction for a matchup between two players with specific teams."""
    player1 = prediction.get('player1', {})
    player2 = prediction.get('player2', {})
    pred = prediction.get('prediction', {})
    
    print(f"\nMatchup Prediction:")
    print(f"{player1.get('name', 'Player 1')} ({player1.get('team', 'Unknown')}) vs {player2.get('name', 'Player 2')} ({player2.get('team', 'Unknown')})")
    
    # Prepare data for tabulate
    headers = ['Metric', player1.get('name', 'Player 1'), player2.get('name', 'Player 2')]
    table_data = [
        ['Team', player1.get('team', 'Unknown'), player2.get('team', 'Unknown')],
        ['Matches with Team', player1.get('matches_with_team', 0), player2.get('matches_with_team', 0)],
        ['Win Rate with Team', f"{player1.get('win_rate_with_team', 0):.3f}", f"{player2.get('win_rate_with_team', 0):.3f}"],
        ['Avg Score with Team', f"{player1.get('avg_score_with_team', 0):.1f}", f"{player2.get('avg_score_with_team', 0):.1f}"],
        ['Win Probability', f"{pred.get('player1_win_probability', 0):.3f}", f"{pred.get('player2_win_probability', 0):.3f}"]
    ]
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display the prediction
    predicted_winner = pred.get('predicted_winner', 'Unknown')
    confidence = pred.get('confidence', 0)
    print(f"\nPredicted Winner: {predicted_winner}")
    print(f"Confidence: {confidence:.2f}")


def main():
    """Main function to demonstrate the player-team analysis module."""
    try:
        # Fetch standings data
        logger.info("Fetching standings data...")
        standings_data = fetch_standings(tournament_id=1)
        
        # Get player data for a few players
        player1_name = "SPARKZ"
        player2_name = "HOGGY"
        
        player1 = get_player_by_name(standings_data, player1_name)
        player2 = get_player_by_name(standings_data, player2_name)
        
        if not player1 or not player2:
            logger.error("Could not find players in standings data")
            return
        
        player1_id = player1.get('participantId')
        player2_id = player2.get('participantId')
        
        logger.info(f"Analyzing player-team performance for {player1_name} (ID: {player1_id})...")
        
        # Get player-team history
        player1_history = get_player_team_history(player1_id)
        save_data_to_file(player1_history, f"{player1_name.lower()}_team_history.json")
        
        # Calculate player-team statistics
        player1_team_stats = calculate_player_team_stats(player1_id)
        save_data_to_file(player1_team_stats, f"{player1_name.lower()}_team_stats.json")
        
        # Display player-team statistics
        display_player_team_stats(player1_name, player1_team_stats)
        
        # Get best and worst teams
        best_teams = get_player_best_teams(player1_id, min_matches=3)
        worst_teams = get_player_worst_teams(player1_id, min_matches=3)
        
        # Display best and worst teams
        display_best_worst_teams(player1_name, best_teams, worst_teams)
        
        # Get team matchup statistics
        if best_teams:
            best_team = best_teams[0][0]
            matchup_stats = get_player_team_matchup_stats(player1_id, best_team)
            
            # Display team matchup statistics
            display_team_matchup_stats(player1_name, best_team, matchup_stats)
        
        # Compare team performance
        if len(best_teams) >= 1 and len(worst_teams) >= 1:
            best_team = best_teams[0][0]
            worst_team = worst_teams[0][0]
            
            comparison = compare_player_team_performance(player1_id, best_team, worst_team)
            
            # Display team comparison
            display_team_comparison(player1_name, comparison)
        
        # Repeat for player 2
        logger.info(f"Analyzing player-team performance for {player2_name} (ID: {player2_id})...")
        
        # Calculate player-team statistics
        player2_team_stats = calculate_player_team_stats(player2_id)
        save_data_to_file(player2_team_stats, f"{player2_name.lower()}_team_stats.json")
        
        # Display player-team statistics
        display_player_team_stats(player2_name, player2_team_stats)
        
        # Get best and worst teams
        player2_best_teams = get_player_best_teams(player2_id, min_matches=3)
        player2_worst_teams = get_player_worst_teams(player2_id, min_matches=3)
        
        # Display best and worst teams
        display_best_worst_teams(player2_name, player2_best_teams, player2_worst_teams)
        
        # Predict matchup
        if best_teams and player2_best_teams:
            player1_best_team = best_teams[0][0]
            player2_best_team = player2_best_teams[0][0]
            
            prediction = predict_player_team_matchup(
                player1_id,
                player2_id,
                player1_best_team,
                player2_best_team
            )
            
            # Display matchup prediction
            display_matchup_prediction(prediction)
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
