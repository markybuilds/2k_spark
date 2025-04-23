"""
Script to train and evaluate different prediction models.

This script uses the processed data to train and evaluate different prediction models
for NBA 2K eSports match outcomes.
"""
import os
import sys
import json
import logging
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evaluation.model_evaluation import calculate_evaluation_metrics, compare_models
from src.config import PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Train and evaluate prediction models.')
    
    # Add arguments
    parser.add_argument('--processed-data-dir', type=str, default=PROCESSED_DATA_DIR,
                        help=f'Directory containing processed data (default: {PROCESSED_DATA_DIR})')
    parser.add_argument('--test-size', type=float, default=0.2,
                        help='Proportion of data to use for testing (default: 0.2)')
    parser.add_argument('--random-state', type=int, default=42,
                        help='Random state for reproducibility (default: 42)')
    parser.add_argument('--output-dir', type=str, default=PROCESSED_DATA_DIR,
                        help=f'Output directory for model results (default: {PROCESSED_DATA_DIR})')
    
    return parser.parse_args()


def load_processed_data(processed_data_dir):
    """Load processed data for model training."""
    try:
        # Find the most recent processed match data file
        match_files = [f for f in os.listdir(processed_data_dir) if f.startswith('processed_matches_') and f.endswith('.csv')]
        if not match_files:
            raise ValueError(f"No processed match data found in {processed_data_dir}")
        
        match_files.sort(reverse=True)  # Sort by name (which includes date) in descending order
        match_file = os.path.join(processed_data_dir, match_files[0])
        logger.info(f"Loading match data from {match_file}")
        match_data = pd.read_csv(match_file)
        
        # Find the most recent player-team features file
        player_team_files = [f for f in os.listdir(processed_data_dir) if f.startswith('player_team_features_') and f.endswith('.csv')]
        if not player_team_files:
            raise ValueError(f"No player-team features found in {processed_data_dir}")
        
        player_team_files.sort(reverse=True)
        player_team_file = os.path.join(processed_data_dir, player_team_files[0])
        logger.info(f"Loading player-team features from {player_team_file}")
        player_team_features = pd.read_csv(player_team_file)
        
        # Find the most recent head-to-head features file
        h2h_files = [f for f in os.listdir(processed_data_dir) if f.startswith('head_to_head_features_') and f.endswith('.csv')]
        if not h2h_files:
            raise ValueError(f"No head-to-head features found in {processed_data_dir}")
        
        h2h_files.sort(reverse=True)
        h2h_file = os.path.join(processed_data_dir, h2h_files[0])
        logger.info(f"Loading head-to-head features from {h2h_file}")
        h2h_features = pd.read_csv(h2h_file)
        
        return match_data, player_team_features, h2h_features
    
    except Exception as e:
        logger.error(f"Error loading processed data: {e}")
        raise


def prepare_training_data(match_data, player_team_features, h2h_features):
    """Prepare training data for model training."""
    try:
        logger.info("Preparing training data...")
        
        # Create a DataFrame to store the training data
        training_data = []
        
        # Process each match
        for _, match in match_data.iterrows():
            try:
                # Extract basic match information
                home_player_id = match['home_player_id']
                away_player_id = match['away_player_id']
                home_team = match['home_team']
                away_team = match['away_team']
                winner_id = match['winner_id']
                
                # Get player-team features for home player
                home_player_team_features = player_team_features[
                    (player_team_features['player_id'] == home_player_id) & 
                    (player_team_features['team'] == home_team)
                ]
                
                # Get player-team features for away player
                away_player_team_features = player_team_features[
                    (player_team_features['player_id'] == away_player_id) & 
                    (player_team_features['team'] == away_team)
                ]
                
                # Skip if player-team features are not available
                if home_player_team_features.empty or away_player_team_features.empty:
                    continue
                
                # Get head-to-head features
                h2h_row = h2h_features[
                    ((h2h_features['player1_id'] == home_player_id) & (h2h_features['player2_id'] == away_player_id)) |
                    ((h2h_features['player1_id'] == away_player_id) & (h2h_features['player2_id'] == home_player_id))
                ]
                
                # Create feature dictionary
                feature_dict = {
                    'match_id': match['match_id'],
                    'home_player_id': home_player_id,
                    'away_player_id': away_player_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    
                    # Home player-team features
                    'home_player_team_matches': home_player_team_features['total_matches'].values[0],
                    'home_player_team_win_rate': home_player_team_features['win_rate'].values[0],
                    'home_player_team_avg_score': home_player_team_features['avg_score'].values[0],
                    'home_player_team_avg_opponent_score': home_player_team_features['avg_opponent_score'].values[0],
                    'home_player_team_avg_score_diff': home_player_team_features['avg_score_diff'].values[0],
                    'home_player_team_recent_win_rate': home_player_team_features['recent_win_rate'].values[0],
                    
                    # Away player-team features
                    'away_player_team_matches': away_player_team_features['total_matches'].values[0],
                    'away_player_team_win_rate': away_player_team_features['win_rate'].values[0],
                    'away_player_team_avg_score': away_player_team_features['avg_score'].values[0],
                    'away_player_team_avg_opponent_score': away_player_team_features['avg_opponent_score'].values[0],
                    'away_player_team_avg_score_diff': away_player_team_features['avg_score_diff'].values[0],
                    'away_player_team_recent_win_rate': away_player_team_features['recent_win_rate'].values[0],
                }
                
                # Add head-to-head features if available
                if not h2h_row.empty:
                    if h2h_row['player1_id'].values[0] == home_player_id:
                        feature_dict.update({
                            'h2h_matches': h2h_row['total_matches'].values[0],
                            'home_player_h2h_wins': h2h_row['player1_wins'].values[0],
                            'away_player_h2h_wins': h2h_row['player2_wins'].values[0],
                            'home_player_h2h_win_rate': h2h_row['player1_win_rate'].values[0],
                            'away_player_h2h_win_rate': h2h_row['player2_win_rate'].values[0]
                        })
                    else:
                        feature_dict.update({
                            'h2h_matches': h2h_row['total_matches'].values[0],
                            'home_player_h2h_wins': h2h_row['player2_wins'].values[0],
                            'away_player_h2h_wins': h2h_row['player1_wins'].values[0],
                            'home_player_h2h_win_rate': h2h_row['player2_win_rate'].values[0],
                            'away_player_h2h_win_rate': h2h_row['player1_win_rate'].values[0]
                        })
                else:
                    # Default values if head-to-head data is not available
                    feature_dict.update({
                        'h2h_matches': 0,
                        'home_player_h2h_wins': 0,
                        'away_player_h2h_wins': 0,
                        'home_player_h2h_win_rate': 0.5,
                        'away_player_h2h_win_rate': 0.5
                    })
                
                # Add target variable (1 if home player won, 0 if away player won)
                feature_dict['home_player_won'] = 1 if winner_id == home_player_id else 0
                
                training_data.append(feature_dict)
            
            except Exception as e:
                logger.warning(f"Error processing match {match['match_id']}: {e}")
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(training_data)
        
        # Handle missing values
        df = df.fillna(0)
        
        logger.info(f"Prepared training data with {len(df)} matches")
        
        return df
    
    except Exception as e:
        logger.error(f"Error preparing training data: {e}")
        raise


def train_models(X_train, y_train, random_state=42):
    """Train different prediction models."""
    try:
        logger.info("Training prediction models...")
        
        # Initialize models
        models = {
            'Logistic Regression': LogisticRegression(random_state=random_state, max_iter=1000),
            'Random Forest': RandomForestClassifier(random_state=random_state, n_estimators=100),
            'Gradient Boosting': GradientBoostingClassifier(random_state=random_state, n_estimators=100)
        }
        
        # Train models
        trained_models = {}
        
        for name, model in models.items():
            logger.info(f"Training {name}...")
            model.fit(X_train, y_train)
            trained_models[name] = model
            logger.info(f"Finished training {name}")
        
        return trained_models
    
    except Exception as e:
        logger.error(f"Error training models: {e}")
        raise


def evaluate_models(models, X_test, y_test):
    """Evaluate trained models on test data."""
    try:
        logger.info("Evaluating prediction models...")
        
        # Initialize results
        results = []
        
        # Evaluate each model
        for name, model in models.items():
            logger.info(f"Evaluating {name}...")
            
            # Make predictions
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_prob)
            
            # Create result dictionary
            result = {
                'model_name': name,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'auc': auc,
                'evaluation_time': datetime.now().isoformat()
            }
            
            # Add to results
            results.append(result)
            
            logger.info(f"{name} - Accuracy: {accuracy:.3f}, AUC: {auc:.3f}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error evaluating models: {e}")
        raise


def save_model_results(results, output_dir):
    """Save model evaluation results."""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        filename = os.path.join(output_dir, f"model_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Save results
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved model evaluation results to {filename}")
        
        return filename
    
    except Exception as e:
        logger.error(f"Error saving model results: {e}")
        raise


def main():
    """Main function to train and evaluate prediction models."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load processed data
        match_data, player_team_features, h2h_features = load_processed_data(args.processed_data_dir)
        
        # Prepare training data
        training_data = prepare_training_data(match_data, player_team_features, h2h_features)
        
        # Split into features and target
        X = training_data.drop(['match_id', 'home_player_id', 'away_player_id', 'home_team', 'away_team', 'home_player_won'], axis=1)
        y = training_data['home_player_won']
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=args.random_state
        )
        
        logger.info(f"Training set size: {len(X_train)}")
        logger.info(f"Testing set size: {len(X_test)}")
        
        # Train models
        trained_models = train_models(X_train, y_train, args.random_state)
        
        # Evaluate models
        evaluation_results = evaluate_models(trained_models, X_test, y_test)
        
        # Save model results
        results_file = save_model_results(evaluation_results, args.output_dir)
        
        # Compare models
        comparison = compare_models(evaluation_results)
        
        # Save model comparison
        comparison_file = os.path.join(args.output_dir, f"model_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info(f"Saved model comparison to {comparison_file}")
        
        # Log best model
        logger.info(f"Best model: {comparison['best_model']} with accuracy {comparison['best_accuracy']:.3f}")
        
    except Exception as e:
        logger.error(f"Error training and evaluating models: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
