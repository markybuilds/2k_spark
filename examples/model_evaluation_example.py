"""
Example script demonstrating how to use the model evaluation module.
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from tabulate import tabulate

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evaluation.model_evaluation import (
    load_predictions,
    load_actual_results,
    match_predictions_with_results,
    calculate_evaluation_metrics,
    evaluate_model,
    compare_models,
    track_model_performance_over_time
)
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sample_predictions(save_to_file=True):
    """Create sample predictions for demonstration purposes."""
    # Sample predictions
    predictions = [
        {
            "match_id": 1,
            "home_player_name": "SPARKZ",
            "away_player_name": "HOGGY",
            "home_team": "Boston Celtics",
            "away_team": "Milwaukee Bucks",
            "prediction": {
                "predicted_winner": "SPARKZ",
                "confidence": 0.75,
                "player1_win_probability": 0.75,
                "player2_win_probability": 0.25
            }
        },
        {
            "match_id": 2,
            "home_player_name": "OREZ",
            "away_player_name": "CARNAGE",
            "home_team": "Dallas Mavericks",
            "away_team": "Phoenix Suns",
            "prediction": {
                "predicted_winner": "CARNAGE",
                "confidence": 0.65,
                "player1_win_probability": 0.35,
                "player2_win_probability": 0.65
            }
        },
        {
            "match_id": 3,
            "home_player_name": "KJMR",
            "away_player_name": "DIMES",
            "home_team": "Golden State Warriors",
            "away_team": "Los Angeles Lakers",
            "prediction": {
                "predicted_winner": "KJMR",
                "confidence": 0.55,
                "player1_win_probability": 0.55,
                "player2_win_probability": 0.45
            }
        }
    ]
    
    # Save to file if requested
    if save_to_file:
        # Ensure directory exists
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        
        # Create filename
        filename = os.path.join(RAW_DATA_DIR, "sample_predictions.json")
        
        # Save file
        with open(filename, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        logger.info(f"Saved sample predictions to {filename}")
    
    return predictions


def create_sample_results(save_to_file=True):
    """Create sample match results for demonstration purposes."""
    # Sample results
    results = [
        {
            "matchId": 1,
            "homeParticipantId": 23,
            "homeParticipantName": "SPARKZ",
            "awayParticipantId": 33,
            "awayParticipantName": "HOGGY",
            "homeScore": 65,
            "awayScore": 58,
            "result": "home_win",
            "homeTeamName": "Boston Celtics",
            "awayTeamName": "Milwaukee Bucks"
        },
        {
            "matchId": 2,
            "homeParticipantId": 18,
            "homeParticipantName": "OREZ",
            "awayParticipantId": 14,
            "awayParticipantName": "CARNAGE",
            "homeScore": 72,
            "awayScore": 68,
            "result": "home_win",
            "homeTeamName": "Dallas Mavericks",
            "awayTeamName": "Phoenix Suns"
        },
        {
            "matchId": 3,
            "homeParticipantId": 105,
            "homeParticipantName": "KJMR",
            "awayParticipantId": 27,
            "awayParticipantName": "DIMES",
            "homeScore": 61,
            "awayScore": 59,
            "result": "home_win",
            "homeTeamName": "Golden State Warriors",
            "awayTeamName": "Los Angeles Lakers"
        }
    ]
    
    # Save to file if requested
    if save_to_file:
        # Ensure directory exists
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        
        # Create filename
        filename = os.path.join(RAW_DATA_DIR, "sample_results.json")
        
        # Save file
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved sample results to {filename}")
    
    return results


def display_matched_data(matched_data):
    """Display matched predictions and results."""
    print("\nMatched Predictions and Results:")
    
    # Prepare data for tabulate
    headers = ['Match ID', 'Home Player', 'Away Player', 'Teams', 'Predicted Winner', 'Actual Winner', 'Correct?']
    table_data = []
    
    for entry in matched_data:
        # Format teams
        teams = f"{entry.get('home_team', 'Unknown')} vs {entry.get('away_team', 'Unknown')}"
        
        table_data.append([
            entry.get('match_id', 'Unknown'),
            entry.get('home_player_name', 'Unknown'),
            entry.get('away_player_name', 'Unknown'),
            teams,
            entry.get('predicted_winner', 'Unknown'),
            entry.get('actual_winner_name', 'Unknown'),
            'Yes' if entry.get('prediction_correct') else 'No'
        ])
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_evaluation_metrics(metrics):
    """Display evaluation metrics."""
    print("\nEvaluation Metrics:")
    
    # Display overall metrics
    print(f"Total Matches: {metrics.get('total_matches', 0)}")
    print(f"Correct Predictions: {metrics.get('correct_predictions', 0)}")
    print(f"Incorrect Predictions: {metrics.get('incorrect_predictions', 0)}")
    print(f"Accuracy: {metrics.get('accuracy', 0):.3f}")
    
    # Display metrics by confidence threshold
    threshold_metrics = metrics.get('confidence_threshold_metrics', {})
    
    if threshold_metrics:
        print("\nMetrics by Confidence Threshold:")
        
        # Prepare data for tabulate
        headers = ['Threshold', 'Total Matches', 'Correct', 'Incorrect', 'Accuracy']
        table_data = []
        
        for threshold, threshold_data in threshold_metrics.items():
            table_data.append([
                threshold,
                threshold_data.get('total_matches', 0),
                threshold_data.get('correct_predictions', 0),
                threshold_data.get('incorrect_predictions', 0),
                f"{threshold_data.get('accuracy', 0):.3f}"
            ])
        
        # Sort by threshold
        table_data.sort(key=lambda x: float(x[0]))
        
        # Display the table
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display metrics by team matchup
    team_metrics = metrics.get('team_matchup_metrics', {})
    
    if team_metrics:
        print("\nMetrics by Team Matchup:")
        
        # Prepare data for tabulate
        headers = ['Team Matchup', 'Total Matches', 'Correct', 'Incorrect', 'Accuracy']
        table_data = []
        
        for matchup, matchup_data in team_metrics.items():
            table_data.append([
                matchup,
                matchup_data.get('total_matches', 0),
                matchup_data.get('correct_predictions', 0),
                matchup_data.get('incorrect_predictions', 0),
                f"{matchup_data.get('accuracy', 0):.3f}"
            ])
        
        # Sort by accuracy (descending)
        table_data.sort(key=lambda x: x[4], reverse=True)
        
        # Display the table
        print(tabulate(table_data, headers=headers, tablefmt='grid'))


def display_model_comparison(comparison):
    """Display model comparison results."""
    print("\nModel Comparison:")
    
    # Prepare data for tabulate
    headers = ['Model', 'Accuracy', 'Total Matches', 'Correct', 'Incorrect', 'Evaluation Time']
    table_data = []
    
    for model in comparison.get('models', []):
        table_data.append([
            model.get('model_name', 'Unknown'),
            f"{model.get('accuracy', 0):.3f}",
            model.get('total_matches', 0),
            model.get('correct_predictions', 0),
            model.get('incorrect_predictions', 0),
            model.get('evaluation_time', 'Unknown')
        ])
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display best model
    print(f"\nBest Model: {comparison.get('best_model', 'Unknown')}")
    print(f"Best Accuracy: {comparison.get('best_accuracy', 0):.3f}")


def display_model_tracking(tracking):
    """Display model performance tracking results."""
    print(f"\nModel Performance Tracking: {tracking.get('model_name', 'Unknown')}")
    
    # Prepare data for tabulate
    headers = ['Evaluation Time', 'Accuracy', 'Total Matches', 'Correct', 'Incorrect']
    table_data = []
    
    for eval_entry in tracking.get('evaluations', []):
        table_data.append([
            eval_entry.get('evaluation_time', 'Unknown'),
            f"{eval_entry.get('accuracy', 0):.3f}",
            eval_entry.get('total_matches', 0),
            eval_entry.get('correct_predictions', 0),
            eval_entry.get('incorrect_predictions', 0)
        ])
    
    # Display the table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display trend
    print(f"\nAccuracy Change: {tracking.get('accuracy_change', 0):.3f}")
    print(f"Trend: {tracking.get('trend', 'unknown')}")


def main():
    """Main function to demonstrate the model evaluation module."""
    try:
        # Create sample data
        logger.info("Creating sample predictions and results...")
        predictions = create_sample_predictions()
        results = create_sample_results()
        
        # Match predictions with results
        logger.info("Matching predictions with results...")
        matched_data = match_predictions_with_results(predictions, results)
        
        # Display matched data
        display_matched_data(matched_data)
        
        # Calculate evaluation metrics
        logger.info("Calculating evaluation metrics...")
        metrics = calculate_evaluation_metrics(matched_data)
        
        # Display evaluation metrics
        display_evaluation_metrics(metrics)
        
        # Evaluate model
        logger.info("Evaluating model...")
        prediction_file = os.path.join(RAW_DATA_DIR, "sample_predictions.json")
        result_file = os.path.join(RAW_DATA_DIR, "sample_results.json")
        
        evaluation = evaluate_model(prediction_file, result_file)
        
        # Create sample evaluations for multiple models
        logger.info("Creating sample evaluations for multiple models...")
        
        # Create evaluations with different accuracies
        evaluations = [
            {
                'model_name': 'Basic Model',
                'metrics': {
                    'accuracy': 0.65,
                    'total_matches': 100,
                    'correct_predictions': 65,
                    'incorrect_predictions': 35
                },
                'evaluation_time': (datetime.now() - timedelta(days=7)).isoformat()
            },
            {
                'model_name': 'Advanced Model',
                'metrics': {
                    'accuracy': 0.72,
                    'total_matches': 100,
                    'correct_predictions': 72,
                    'incorrect_predictions': 28
                },
                'evaluation_time': (datetime.now() - timedelta(days=3)).isoformat()
            },
            {
                'model_name': 'Ensemble Model',
                'metrics': {
                    'accuracy': 0.78,
                    'total_matches': 100,
                    'correct_predictions': 78,
                    'incorrect_predictions': 22
                },
                'evaluation_time': datetime.now().isoformat()
            }
        ]
        
        # Compare models
        logger.info("Comparing models...")
        comparison = compare_models(evaluations)
        
        # Display model comparison
        display_model_comparison(comparison)
        
        # Create sample evaluations for tracking
        logger.info("Creating sample evaluations for tracking...")
        
        # Create evaluations with different accuracies over time
        tracking_evaluations = [
            {
                'metrics': {
                    'accuracy': 0.65,
                    'total_matches': 50,
                    'correct_predictions': 32,
                    'incorrect_predictions': 18
                },
                'evaluation_time': (datetime.now() - timedelta(days=30)).isoformat()
            },
            {
                'metrics': {
                    'accuracy': 0.68,
                    'total_matches': 50,
                    'correct_predictions': 34,
                    'incorrect_predictions': 16
                },
                'evaluation_time': (datetime.now() - timedelta(days=20)).isoformat()
            },
            {
                'metrics': {
                    'accuracy': 0.72,
                    'total_matches': 50,
                    'correct_predictions': 36,
                    'incorrect_predictions': 14
                },
                'evaluation_time': (datetime.now() - timedelta(days=10)).isoformat()
            },
            {
                'metrics': {
                    'accuracy': 0.76,
                    'total_matches': 50,
                    'correct_predictions': 38,
                    'incorrect_predictions': 12
                },
                'evaluation_time': datetime.now().isoformat()
            }
        ]
        
        # Track model performance
        logger.info("Tracking model performance...")
        tracking = track_model_performance_over_time('Advanced Model', tracking_evaluations)
        
        # Display model tracking
        display_model_tracking(tracking)
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
