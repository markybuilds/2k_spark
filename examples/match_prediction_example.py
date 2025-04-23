"""
Example script demonstrating how to use the match prediction module.
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
from src.prediction.match_predictor import (
    predict_upcoming_matches,
    get_high_confidence_predictions,
    get_predictions_for_player,
    get_predictions_for_date
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


def display_predictions(predictions, title="Match Predictions"):
    """Display match predictions in a formatted table."""
    print(f"\n{title}:")
    
    if not predictions:
        print("No predictions available.")
        return
    
    # Prepare data for tabulate
    headers = ['Time', 'Home Player', 'Away Player', 'Teams', 'Predicted Winner', 'Confidence']
    table_data = []
    
    for pred in predictions:
        # Format teams
        teams = f"{pred.get('home_team', 'Unknown')} vs {pred.get('away_team', 'Unknown')}"
        
        # Get prediction details
        prediction_data = pred.get('prediction', {})
        predicted_winner = prediction_data.get('predicted_winner', 'Unknown')
        confidence = prediction_data.get('confidence', 0)
        
        table_data.append([
            pred.get('local_time', 'Unknown'),
            pred.get('home_player_name', 'Unknown'),
            pred.get('away_player_name', 'Unknown'),
            teams,
            predicted_winner,
            f"{confidence:.2f}"
        ])
    
    # Sort by time
    table_data.sort(key=lambda x: x[0])
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_player_predictions(player_name, predictions):
    """Display predictions for a specific player."""
    print(f"\nPredictions for {player_name}:")
    
    if not predictions:
        print(f"No predictions available for {player_name}.")
        return
    
    # Prepare data for tabulate
    headers = ['Time', 'Opponent', 'Home/Away', 'Teams', 'Predicted Winner', 'Win Probability', 'Confidence']
    table_data = []
    
    for pred in predictions:
        # Determine if player is home or away
        home_player = pred.get('home_player_name', 'Unknown')
        away_player = pred.get('away_player_name', 'Unknown')
        
        if home_player == player_name:
            # Player is home
            opponent = away_player
            home_away = 'Home'
            player_win_prob = pred.get('prediction', {}).get('player1_win_probability', 0)
        else:
            # Player is away
            opponent = home_player
            home_away = 'Away'
            player_win_prob = pred.get('prediction', {}).get('player2_win_probability', 0)
        
        # Format teams
        teams = f"{pred.get('home_team', 'Unknown')} vs {pred.get('away_team', 'Unknown')}"
        
        # Get prediction details
        prediction_data = pred.get('prediction', {})
        predicted_winner = prediction_data.get('predicted_winner', 'Unknown')
        confidence = prediction_data.get('confidence', 0)
        
        table_data.append([
            pred.get('local_time', 'Unknown'),
            opponent,
            home_away,
            teams,
            predicted_winner,
            f"{player_win_prob:.3f}",
            f"{confidence:.2f}"
        ])
    
    # Sort by time
    table_data.sort(key=lambda x: x[0])
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def main():
    """Main function to demonstrate the match prediction module."""
    try:
        # Fetch standings data
        logger.info("Fetching standings data...")
        standings_data = fetch_standings(tournament_id=1)
        
        # Predict upcoming matches
        logger.info("Predicting upcoming matches...")
        predictions = predict_upcoming_matches(hours_ahead=24)
        
        # Save predictions to file
        save_predictions_to_file(predictions, "upcoming_match_predictions.json")
        
        # Display all predictions
        display_predictions(predictions, "Upcoming Match Predictions (Next 24 Hours)")
        
        # Get high confidence predictions
        high_confidence = get_high_confidence_predictions(predictions, min_confidence=0.6)
        display_predictions(high_confidence, "High Confidence Predictions (Confidence >= 0.6)")
        
        # Get predictions for specific players
        player_names = ["SPARKZ", "HOGGY"]
        
        for player_name in player_names:
            player = get_player_by_name(standings_data, player_name)
            
            if player:
                player_id = player.get('participantId')
                player_predictions = get_predictions_for_player(predictions, player_id)
                display_player_predictions(player_name, player_predictions)
        
        # Get predictions for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_predictions = get_predictions_for_date(predictions, tomorrow)
        display_predictions(tomorrow_predictions, f"Predictions for {tomorrow.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
