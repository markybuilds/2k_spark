"""
Example script demonstrating how to use the advanced prediction module.
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from tabulate import tabulate

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.standings import fetch_standings, get_player_by_name
from src.prediction.advanced_predictor import (
    calculate_player_recent_form,
    calculate_head_to_head_stats,
    calculate_team_matchup_advantage,
    advanced_match_prediction,
    predict_upcoming_matches_advanced
)
from src.config import RAW_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_predictions_to_file(predictions, filename):
    """Save predictions to a JSON file in the raw data directory."""
    # Ensure the raw data directory exists
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    # Create the full file path
    file_path = os.path.join(RAW_DATA_DIR, filename)
    
    # Save the data
    with open(file_path, 'w') as f:
        json.dump(predictions, f, indent=2)
    logger.info(f"Saved predictions to {file_path}")


def display_player_form(player_name, form_data):
    """Display a player's recent form."""
    print(f"\nRecent Form for {player_name}:")
    
    # Prepare data for tabulate
    headers = ['Matches', 'Wins', 'Losses', 'Win Rate', 'Avg Score', 'Avg Opp Score', 'Score Diff', 'Trend']
    table_data = [[
        form_data.get('matches', 0),
        form_data.get('wins', 0),
        form_data.get('losses', 0),
        f"{form_data.get('win_rate', 0):.3f}",
        f"{form_data.get('avg_score', 0):.1f}",
        f"{form_data.get('avg_opponent_score', 0):.1f}",
        f"{form_data.get('avg_score_diff', 0):.1f}",
        form_data.get('trend', 'neutral')
    ]]
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display last 5 matches
    print("\nLast 5 Matches:")
    last_matches = form_data.get('last_matches', [])
    
    if last_matches:
        for i, match in enumerate(last_matches):
            print(f"{i+1}. vs {match.get('opponent', 'Unknown')}: {match.get('result', 'unknown')}")
    else:
        print("No recent matches found.")


def display_head_to_head(player1_name, player2_name, h2h_data):
    """Display head-to-head statistics between two players."""
    print(f"\nHead-to-Head: {player1_name} vs {player2_name}")
    
    # Prepare data for tabulate
    headers = ['Matches', f'{player1_name} Wins', f'{player2_name} Wins', f'{player1_name} Win Rate', f'{player2_name} Win Rate', 'Avg Score Diff', 'Recent Winner']
    table_data = [[
        h2h_data.get('matches', 0),
        h2h_data.get('player1_wins', 0),
        h2h_data.get('player2_wins', 0),
        f"{h2h_data.get('player1_win_rate', 0):.3f}",
        f"{h2h_data.get('player2_win_rate', 0):.3f}",
        f"{h2h_data.get('avg_score_diff', 0):.1f}",
        'Player 1' if h2h_data.get('recent_winner') == 'player1' else 'Player 2' if h2h_data.get('recent_winner') == 'player2' else 'N/A'
    ]]
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display team matchups
    team_matchups = h2h_data.get('team_matchups', {})
    
    if team_matchups:
        print("\nTeam Matchups:")
        
        # Prepare data for tabulate
        team_headers = ['Matchup', 'Matches', f'{player1_name} Wins', f'{player2_name} Wins', f'{player1_name} Win Rate', f'{player2_name} Win Rate']
        team_table = []
        
        for matchup, stats in team_matchups.items():
            team_table.append([
                matchup,
                stats.get('matches', 0),
                stats.get('player1_wins', 0),
                stats.get('player2_wins', 0),
                f"{stats.get('player1_win_rate', 0):.3f}",
                f"{stats.get('player2_win_rate', 0):.3f}"
            ])
        
        # Sort by number of matches (descending)
        team_table.sort(key=lambda x: x[1], reverse=True)
        
        # Display the table
        print(tabulate(team_table, headers=team_headers, tablefmt='grid'))
    else:
        print("\nNo team matchup data available.")


def display_team_matchup(team1, team2, matchup_data):
    """Display team matchup advantage."""
    print(f"\nTeam Matchup: {team1} vs {team2}")
    
    # Prepare data for tabulate
    headers = ['Matches', f'{team1} Wins', f'{team2} Wins', f'{team1} Win Rate', f'{team2} Win Rate', 'Avg Score Diff', 'Advantage']
    table_data = [[
        matchup_data.get('matches', 0),
        matchup_data.get('team1_wins', 0),
        matchup_data.get('team2_wins', 0),
        f"{matchup_data.get('team1_win_rate', 0):.3f}",
        f"{matchup_data.get('team2_win_rate', 0):.3f}",
        f"{matchup_data.get('avg_score_diff', 0):.1f}",
        'Team 1' if matchup_data.get('advantage') == 'team1' else 'Team 2' if matchup_data.get('advantage') == 'team2' else 'Neutral'
    ]]
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_advanced_prediction(prediction):
    """Display an advanced prediction for a match."""
    player1 = prediction.get('player1', {})
    player2 = prediction.get('player2', {})
    h2h = prediction.get('head_to_head', {})
    team_matchup = prediction.get('team_matchup', {})
    pred = prediction.get('prediction', {})
    
    print(f"\nAdvanced Prediction:")
    print(f"{player1.get('name', 'Player 1')} ({player1.get('team', 'Unknown')}) vs {player2.get('name', 'Player 2')} ({player2.get('team', 'Unknown')})")
    
    # Prepare data for tabulate
    headers = ['Metric', player1.get('name', 'Player 1'), player2.get('name', 'Player 2')]
    table_data = [
        ['Team', player1.get('team', 'Unknown'), player2.get('team', 'Unknown')],
        ['Matches with Team', player1.get('matches_with_team', 0), player2.get('matches_with_team', 0)],
        ['Win Rate with Team', f"{player1.get('win_rate_with_team', 0):.3f}", f"{player2.get('win_rate_with_team', 0):.3f}"],
        ['Recent Form', player1.get('recent_form', 'neutral'), player2.get('recent_form', 'neutral')],
        ['Recent Win Rate', f"{player1.get('recent_win_rate', 0):.3f}", f"{player2.get('recent_win_rate', 0):.3f}"],
        ['H2H Win Rate', f"{h2h.get('player1_win_rate', 0):.3f}", f"{h2h.get('player2_win_rate', 0):.3f}"],
        ['Win Probability', f"{pred.get('player1_win_probability', 0):.3f}", f"{pred.get('player2_win_probability', 0):.3f}"]
    ]
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display the prediction
    predicted_winner = pred.get('predicted_winner', 'Unknown')
    confidence = pred.get('confidence', 0)
    print(f"\nPredicted Winner: {predicted_winner}")
    print(f"Confidence: {confidence:.2f}")
    
    # Display feature contributions
    contributions = pred.get('feature_contributions', {})
    
    if contributions:
        print("\nFeature Contributions:")
        for feature, value in contributions.items():
            print(f"{feature}: {value:.3f}")


def display_upcoming_predictions(predictions):
    """Display predictions for upcoming matches."""
    print(f"\nUpcoming Match Predictions:")
    
    if not predictions:
        print("No predictions available.")
        return
    
    # Prepare data for tabulate
    headers = ['Time', 'Home Player', 'Away Player', 'Teams', 'Predicted Winner', 'Win Prob', 'Confidence']
    table_data = []
    
    for pred in predictions:
        # Get basic match info
        home_player = pred.get('home_player_name', 'Unknown')
        away_player = pred.get('away_player_name', 'Unknown')
        home_team = pred.get('home_team', 'Unknown')
        away_team = pred.get('away_team', 'Unknown')
        
        # Format teams
        teams = f"{home_team} vs {away_team}"
        
        # Get prediction details
        prediction_data = pred.get('prediction', {}).get('prediction', {})
        predicted_winner = prediction_data.get('predicted_winner', 'Unknown')
        
        # Determine win probability
        if predicted_winner == home_player:
            win_prob = prediction_data.get('player1_win_probability', 0)
        else:
            win_prob = prediction_data.get('player2_win_probability', 0)
        
        confidence = prediction_data.get('confidence', 0)
        
        # Format time
        fixture_start = pred.get('fixture_start', '')
        time_str = fixture_start
        
        table_data.append([
            time_str,
            home_player,
            away_player,
            teams,
            predicted_winner,
            f"{win_prob:.3f}",
            f"{confidence:.2f}"
        ])
    
    # Sort by time
    table_data.sort(key=lambda x: x[0])
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def main():
    """Main function to demonstrate the advanced prediction module."""
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
        
        # Calculate player recent form
        logger.info(f"Calculating recent form for {player1_name}...")
        player1_form = calculate_player_recent_form(player1_id)
        
        # Display player form
        display_player_form(player1_name, player1_form)
        
        # Calculate head-to-head statistics
        logger.info(f"Calculating head-to-head statistics for {player1_name} vs {player2_name}...")
        h2h_stats = calculate_head_to_head_stats(player1_id, player2_id)
        
        # Display head-to-head statistics
        display_head_to_head(player1_name, player2_name, h2h_stats)
        
        # Calculate team matchup advantage
        team1 = "Boston Celtics"
        team2 = "Milwaukee Bucks"
        
        logger.info(f"Calculating team matchup advantage for {team1} vs {team2}...")
        team_matchup = calculate_team_matchup_advantage(team1, team2)
        
        # Display team matchup advantage
        display_team_matchup(team1, team2, team_matchup)
        
        # Make an advanced prediction
        logger.info(f"Making advanced prediction for {player1_name} vs {player2_name}...")
        prediction = advanced_match_prediction(player1_id, player2_id, team1, team2)
        
        # Display advanced prediction
        display_advanced_prediction(prediction)
        
        # Save prediction to file
        save_predictions_to_file(prediction, f"advanced_prediction_{player1_name}_vs_{player2_name}.json")
        
        # Predict upcoming matches
        logger.info("Predicting upcoming matches...")
        upcoming_predictions = predict_upcoming_matches_advanced(hours_ahead=24)
        
        # Save upcoming predictions to file
        save_predictions_to_file(upcoming_predictions, "advanced_upcoming_predictions.json")
        
        # Display upcoming predictions
        display_upcoming_predictions(upcoming_predictions)
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
