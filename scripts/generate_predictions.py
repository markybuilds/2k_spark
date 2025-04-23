"""
Script to generate predictions for upcoming matches.

This script uses the refined prediction algorithm to generate predictions
for upcoming NBA 2K eSports matches.
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the refined prediction algorithm if available
try:
    from src.prediction.refined_algorithm import predict_upcoming_matches as refined_predict
    USING_REFINED = True
except ImportError:
    from src.prediction.advanced_predictor import predict_upcoming_matches_advanced as refined_predict
    USING_REFINED = False

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate predictions for upcoming matches.')
    
    # Add arguments
    parser.add_argument('--hours', type=int, default=24,
                        help='Number of hours ahead to predict matches for (default: 24)')
    parser.add_argument('--days', type=int, default=0,
                        help='Number of days ahead to predict matches for (default: 0)')
    parser.add_argument('--tournament-id', type=int, default=1,
                        help='Tournament ID (default: 1)')
    parser.add_argument('--min-confidence', type=float, default=0.6,
                        help='Minimum confidence threshold for high-confidence predictions (default: 0.6)')
    parser.add_argument('--output-dir', type=str, default=PROCESSED_DATA_DIR,
                        help=f'Output directory (default: {PROCESSED_DATA_DIR})')
    parser.add_argument('--format', type=str, choices=['json', 'csv', 'text'], default='text',
                        help='Output format (default: text)')
    
    return parser.parse_args()


def save_predictions(predictions, output_dir, format_type):
    """Save predictions to a file."""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'json':
            # Save as JSON
            filename = os.path.join(output_dir, f"predictions_{timestamp}.json")
            with open(filename, 'w') as f:
                json.dump(predictions, f, indent=2)
        
        elif format_type == 'csv':
            # Convert to DataFrame and save as CSV
            import pandas as pd
            
            # Flatten predictions
            flattened = []
            
            for pred in predictions:
                flat_pred = {
                    'match_id': pred.get('match_id'),
                    'fixture_start': pred.get('fixture_start')
                }
                
                # Add prediction details
                prediction_data = pred.get('prediction', {})
                if USING_REFINED:
                    flat_pred.update({
                        'home_player_id': prediction_data.get('home_player_id'),
                        'home_player_name': prediction_data.get('home_player_name'),
                        'away_player_id': prediction_data.get('away_player_id'),
                        'away_player_name': prediction_data.get('away_player_name'),
                        'home_team': prediction_data.get('home_team'),
                        'away_team': prediction_data.get('away_team'),
                        'home_win_probability': prediction_data.get('home_win_probability'),
                        'away_win_probability': prediction_data.get('away_win_probability'),
                        'predicted_winner': prediction_data.get('predicted_winner'),
                        'confidence': prediction_data.get('confidence')
                    })
                else:
                    # Handle advanced predictor format
                    pred_details = prediction_data.get('prediction', {})
                    flat_pred.update({
                        'home_player_id': pred.get('home_player_id'),
                        'home_player_name': pred.get('home_player_name'),
                        'away_player_id': pred.get('away_player_id'),
                        'away_player_name': pred.get('away_player_name'),
                        'home_team': pred.get('home_team'),
                        'away_team': pred.get('away_team'),
                        'home_win_probability': pred_details.get('player1_win_probability'),
                        'away_win_probability': pred_details.get('player2_win_probability'),
                        'predicted_winner': pred_details.get('predicted_winner'),
                        'confidence': pred_details.get('confidence')
                    })
                
                flattened.append(flat_pred)
            
            # Convert to DataFrame
            df = pd.DataFrame(flattened)
            
            # Save as CSV
            filename = os.path.join(output_dir, f"predictions_{timestamp}.csv")
            df.to_csv(filename, index=False)
        
        else:  # text format
            # Save as formatted text
            filename = os.path.join(output_dir, f"predictions_{timestamp}.txt")
            
            with open(filename, 'w') as f:
                f.write(f"NBA 2K eSports Match Predictions\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Prepare data for tabulate
                headers = ['Time', 'Home Player', 'Away Player', 'Teams', 'Predicted Winner', 'Win Prob', 'Confidence']
                table_data = []
                
                for pred in predictions:
                    # Get basic match info
                    if USING_REFINED:
                        prediction_data = pred.get('prediction', {})
                        home_player = prediction_data.get('home_player_name', 'Unknown')
                        away_player = prediction_data.get('away_player_name', 'Unknown')
                        home_team = prediction_data.get('home_team', 'Unknown')
                        away_team = prediction_data.get('away_team', 'Unknown')
                        predicted_winner = prediction_data.get('predicted_winner', 'Unknown')
                        
                        # Determine win probability
                        if predicted_winner == home_player:
                            win_prob = prediction_data.get('home_win_probability', 0)
                        else:
                            win_prob = prediction_data.get('away_win_probability', 0)
                        
                        confidence = prediction_data.get('confidence', 0)
                    else:
                        # Handle advanced predictor format
                        home_player = pred.get('home_player_name', 'Unknown')
                        away_player = pred.get('away_player_name', 'Unknown')
                        home_team = pred.get('home_team', 'Unknown')
                        away_team = pred.get('away_team', 'Unknown')
                        
                        prediction_details = pred.get('prediction', {}).get('prediction', {})
                        predicted_winner = prediction_details.get('predicted_winner', 'Unknown')
                        
                        # Determine win probability
                        if predicted_winner == home_player:
                            win_prob = prediction_details.get('player1_win_probability', 0)
                        else:
                            win_prob = prediction_details.get('player2_win_probability', 0)
                        
                        confidence = prediction_details.get('confidence', 0)
                    
                    # Format teams
                    teams = f"{home_team} vs {away_team}"
                    
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
                
                # Write the table
                f.write(tabulate(table_data, headers=headers, tablefmt='grid'))
                
                # Add high confidence predictions
                high_confidence = [p for p in predictions if 
                                  (USING_REFINED and p.get('prediction', {}).get('confidence', 0) >= args.min_confidence) or
                                  (not USING_REFINED and p.get('prediction', {}).get('prediction', {}).get('confidence', 0) >= args.min_confidence)]
                
                if high_confidence:
                    f.write(f"\n\nHigh Confidence Predictions (Confidence >= {args.min_confidence}):\n")
                    
                    # Prepare data for high confidence table
                    high_conf_data = []
                    
                    for pred in high_confidence:
                        if USING_REFINED:
                            prediction_data = pred.get('prediction', {})
                            home_player = prediction_data.get('home_player_name', 'Unknown')
                            away_player = prediction_data.get('away_player_name', 'Unknown')
                            teams = f"{prediction_data.get('home_team', 'Unknown')} vs {prediction_data.get('away_team', 'Unknown')}"
                            predicted_winner = prediction_data.get('predicted_winner', 'Unknown')
                            
                            # Determine win probability
                            if predicted_winner == home_player:
                                win_prob = prediction_data.get('home_win_probability', 0)
                            else:
                                win_prob = prediction_data.get('away_win_probability', 0)
                            
                            confidence = prediction_data.get('confidence', 0)
                        else:
                            # Handle advanced predictor format
                            home_player = pred.get('home_player_name', 'Unknown')
                            away_player = pred.get('away_player_name', 'Unknown')
                            teams = f"{pred.get('home_team', 'Unknown')} vs {pred.get('away_team', 'Unknown')}"
                            
                            prediction_details = pred.get('prediction', {}).get('prediction', {})
                            predicted_winner = prediction_details.get('predicted_winner', 'Unknown')
                            
                            # Determine win probability
                            if predicted_winner == home_player:
                                win_prob = prediction_details.get('player1_win_probability', 0)
                            else:
                                win_prob = prediction_details.get('player2_win_probability', 0)
                            
                            confidence = prediction_details.get('confidence', 0)
                        
                        # Format time
                        fixture_start = pred.get('fixture_start', '')
                        time_str = fixture_start
                        
                        high_conf_data.append([
                            time_str,
                            f"{home_player} vs {away_player}",
                            teams,
                            predicted_winner,
                            f"{win_prob:.3f}",
                            f"{confidence:.2f}"
                        ])
                    
                    # Sort by confidence (descending)
                    high_conf_data.sort(key=lambda x: float(x[5]), reverse=True)
                    
                    # Write the high confidence table
                    f.write(tabulate(high_conf_data, 
                                    headers=['Time', 'Matchup', 'Teams', 'Predicted Winner', 'Win Prob', 'Confidence'],
                                    tablefmt='grid'))
        
        logger.info(f"Saved predictions to {filename}")
        
        return filename
    
    except Exception as e:
        logger.error(f"Error saving predictions: {e}")
        raise


def display_predictions(predictions, min_confidence):
    """Display predictions in the console."""
    try:
        print("\nNBA 2K eSports Match Predictions")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Prepare data for tabulate
        headers = ['Time', 'Home Player', 'Away Player', 'Teams', 'Predicted Winner', 'Win Prob', 'Confidence']
        table_data = []
        
        for pred in predictions:
            # Get basic match info
            if USING_REFINED:
                prediction_data = pred.get('prediction', {})
                home_player = prediction_data.get('home_player_name', 'Unknown')
                away_player = prediction_data.get('away_player_name', 'Unknown')
                home_team = prediction_data.get('home_team', 'Unknown')
                away_team = prediction_data.get('away_team', 'Unknown')
                predicted_winner = prediction_data.get('predicted_winner', 'Unknown')
                
                # Determine win probability
                if predicted_winner == home_player:
                    win_prob = prediction_data.get('home_win_probability', 0)
                else:
                    win_prob = prediction_data.get('away_win_probability', 0)
                
                confidence = prediction_data.get('confidence', 0)
            else:
                # Handle advanced predictor format
                home_player = pred.get('home_player_name', 'Unknown')
                away_player = pred.get('away_player_name', 'Unknown')
                home_team = pred.get('home_team', 'Unknown')
                away_team = pred.get('away_team', 'Unknown')
                
                prediction_details = pred.get('prediction', {}).get('prediction', {})
                predicted_winner = prediction_details.get('predicted_winner', 'Unknown')
                
                # Determine win probability
                if predicted_winner == home_player:
                    win_prob = prediction_details.get('player1_win_probability', 0)
                else:
                    win_prob = prediction_details.get('player2_win_probability', 0)
                
                confidence = prediction_details.get('confidence', 0)
            
            # Format teams
            teams = f"{home_team} vs {away_team}"
            
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
        
        # Display high confidence predictions
        high_confidence = [p for p in predictions if 
                          (USING_REFINED and p.get('prediction', {}).get('confidence', 0) >= min_confidence) or
                          (not USING_REFINED and p.get('prediction', {}).get('prediction', {}).get('confidence', 0) >= min_confidence)]
        
        if high_confidence:
            print(f"\nHigh Confidence Predictions (Confidence >= {min_confidence}):")
            
            # Prepare data for high confidence table
            high_conf_data = []
            
            for pred in high_confidence:
                if USING_REFINED:
                    prediction_data = pred.get('prediction', {})
                    home_player = prediction_data.get('home_player_name', 'Unknown')
                    away_player = prediction_data.get('away_player_name', 'Unknown')
                    teams = f"{prediction_data.get('home_team', 'Unknown')} vs {prediction_data.get('away_team', 'Unknown')}"
                    predicted_winner = prediction_data.get('predicted_winner', 'Unknown')
                    
                    # Determine win probability
                    if predicted_winner == home_player:
                        win_prob = prediction_data.get('home_win_probability', 0)
                    else:
                        win_prob = prediction_data.get('away_win_probability', 0)
                    
                    confidence = prediction_data.get('confidence', 0)
                else:
                    # Handle advanced predictor format
                    home_player = pred.get('home_player_name', 'Unknown')
                    away_player = pred.get('away_player_name', 'Unknown')
                    teams = f"{pred.get('home_team', 'Unknown')} vs {pred.get('away_team', 'Unknown')}"
                    
                    prediction_details = pred.get('prediction', {}).get('prediction', {})
                    predicted_winner = prediction_details.get('predicted_winner', 'Unknown')
                    
                    # Determine win probability
                    if predicted_winner == home_player:
                        win_prob = prediction_details.get('player1_win_probability', 0)
                    else:
                        win_prob = prediction_details.get('player2_win_probability', 0)
                    
                    confidence = prediction_details.get('confidence', 0)
                
                # Format time
                fixture_start = pred.get('fixture_start', '')
                time_str = fixture_start
                
                high_conf_data.append([
                    time_str,
                    f"{home_player} vs {away_player}",
                    teams,
                    predicted_winner,
                    f"{win_prob:.3f}",
                    f"{confidence:.2f}"
                ])
            
            # Sort by confidence (descending)
            high_conf_data.sort(key=lambda x: float(x[5]), reverse=True)
            
            # Display the high confidence table
            print(tabulate(high_conf_data, 
                          headers=['Time', 'Matchup', 'Teams', 'Predicted Winner', 'Win Prob', 'Confidence'],
                          tablefmt='grid'))
        
    except Exception as e:
        logger.error(f"Error displaying predictions: {e}")


def main():
    """Main function to generate predictions for upcoming matches."""
    try:
        # Parse arguments
        global args
        args = parse_arguments()
        
        # Log parameters
        logger.info(f"Generating predictions with the following parameters:")
        logger.info(f"Hours Ahead: {args.hours}")
        logger.info(f"Days Ahead: {args.days}")
        logger.info(f"Tournament ID: {args.tournament_id}")
        logger.info(f"Minimum Confidence: {args.min_confidence}")
        logger.info(f"Output Directory: {args.output_dir}")
        logger.info(f"Output Format: {args.format}")
        logger.info(f"Using Refined Algorithm: {USING_REFINED}")
        
        # Calculate total hours
        total_hours = args.hours + (args.days * 24)
        
        # Generate predictions
        logger.info(f"Generating predictions for the next {total_hours} hours...")
        
        if USING_REFINED:
            predictions = refined_predict(hours_ahead=total_hours, tournament_id=args.tournament_id)
        else:
            predictions = refined_predict(hours_ahead=total_hours, tournament_id=args.tournament_id)
        
        logger.info(f"Generated {len(predictions)} predictions")
        
        # Save predictions
        if args.format != 'text':
            save_predictions(predictions, args.output_dir, args.format)
        
        # Display predictions
        display_predictions(predictions, args.min_confidence)
        
        # Save predictions as text (always do this for reference)
        save_predictions(predictions, args.output_dir, 'text')
        
        logger.info("Prediction generation completed successfully.")
        
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
