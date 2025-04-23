"""
Script to refine the prediction algorithm based on model evaluation.

This script analyzes model evaluation results and refines the prediction algorithm
by adjusting feature weights and parameters.
"""
import os
import sys
import json
import logging
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Refine the prediction algorithm.')
    
    # Add arguments
    parser.add_argument('--processed-data-dir', type=str, default=PROCESSED_DATA_DIR,
                        help=f'Directory containing processed data (default: {PROCESSED_DATA_DIR})')
    parser.add_argument('--model-type', type=str, default='RandomForest',
                        choices=['LogisticRegression', 'RandomForest', 'GradientBoosting'],
                        help='Type of model to refine (default: RandomForest)')
    parser.add_argument('--random-state', type=int, default=42,
                        help='Random state for reproducibility (default: 42)')
    parser.add_argument('--output-dir', type=str, default=PROCESSED_DATA_DIR,
                        help=f'Output directory for refined model (default: {PROCESSED_DATA_DIR})')
    
    return parser.parse_args()


def load_training_data(processed_data_dir):
    """Load training data for model refinement."""
    try:
        # Find the most recent training data file
        training_files = [f for f in os.listdir(processed_data_dir) if f.startswith('training_data_') and f.endswith('.csv')]
        
        if not training_files:
            # If no training data file exists, create one using the train_evaluate_models.py script
            logger.info("No training data file found. Creating one...")
            
            # Import the prepare_training_data function
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
            from train_evaluate_models import load_processed_data, prepare_training_data
            
            # Load processed data
            match_data, player_team_features, h2h_features = load_processed_data(processed_data_dir)
            
            # Prepare training data
            training_data = prepare_training_data(match_data, player_team_features, h2h_features)
            
            # Save training data
            training_file = os.path.join(processed_data_dir, f"training_data_{datetime.now().strftime('%Y%m%d')}.csv")
            training_data.to_csv(training_file, index=False)
            
            logger.info(f"Created and saved training data to {training_file}")
            
            return training_data
        
        # Load the most recent training data file
        training_files.sort(reverse=True)
        training_file = os.path.join(processed_data_dir, training_files[0])
        logger.info(f"Loading training data from {training_file}")
        training_data = pd.read_csv(training_file)
        
        return training_data
    
    except Exception as e:
        logger.error(f"Error loading training data: {e}")
        raise


def analyze_feature_importance(model, feature_names):
    """Analyze feature importance from a trained model."""
    try:
        # Get feature importance
        if hasattr(model, 'feature_importances_'):
            # For tree-based models
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # For linear models
            importance = np.abs(model.coef_[0])
        else:
            logger.warning("Model does not provide feature importance")
            return None
        
        # Create DataFrame with feature names and importance
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        })
        
        # Sort by importance
        feature_importance = feature_importance.sort_values('importance', ascending=False)
        
        return feature_importance
    
    except Exception as e:
        logger.error(f"Error analyzing feature importance: {e}")
        raise


def optimize_model_parameters(model_type, X_train, y_train, random_state=42):
    """Optimize model parameters using grid search."""
    try:
        logger.info(f"Optimizing parameters for {model_type}...")
        
        if model_type == 'LogisticRegression':
            # Define parameter grid for logistic regression
            param_grid = {
                'C': [0.001, 0.01, 0.1, 1, 10, 100],
                'penalty': ['l1', 'l2', 'elasticnet', None],
                'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                'max_iter': [1000]
            }
            
            # Create base model
            base_model = LogisticRegression(random_state=random_state)
            
        elif model_type == 'RandomForest':
            # Define parameter grid for random forest
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'bootstrap': [True, False]
            }
            
            # Create base model
            base_model = RandomForestClassifier(random_state=random_state)
            
        elif model_type == 'GradientBoosting':
            # Define parameter grid for gradient boosting
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'subsample': [0.8, 0.9, 1.0]
            }
            
            # Create base model
            base_model = GradientBoostingClassifier(random_state=random_state)
            
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Create grid search
        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            cv=5,
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )
        
        # Fit grid search
        grid_search.fit(X_train, y_train)
        
        # Get best parameters and model
        best_params = grid_search.best_params_
        best_model = grid_search.best_estimator_
        
        logger.info(f"Best parameters: {best_params}")
        logger.info(f"Best accuracy: {grid_search.best_score_:.3f}")
        
        return best_model, best_params
    
    except Exception as e:
        logger.error(f"Error optimizing model parameters: {e}")
        raise


def calculate_optimal_feature_weights(feature_importance):
    """Calculate optimal feature weights based on feature importance."""
    try:
        # Normalize feature importance to sum to 1
        total_importance = feature_importance['importance'].sum()
        normalized_importance = feature_importance['importance'] / total_importance
        
        # Create dictionary mapping feature names to weights
        feature_weights = dict(zip(feature_importance['feature'], normalized_importance))
        
        return feature_weights
    
    except Exception as e:
        logger.error(f"Error calculating optimal feature weights: {e}")
        raise


def save_refined_algorithm(model, feature_weights, best_params, output_dir):
    """Save the refined prediction algorithm."""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename for model
        model_file = os.path.join(output_dir, f"refined_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")
        
        # Save model using pickle
        import pickle
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Saved refined model to {model_file}")
        
        # Create algorithm configuration
        algorithm_config = {
            'model_file': model_file,
            'feature_weights': feature_weights,
            'model_parameters': best_params,
            'refinement_time': datetime.now().isoformat()
        }
        
        # Save algorithm configuration
        config_file = os.path.join(output_dir, f"algorithm_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(config_file, 'w') as f:
            json.dump(algorithm_config, f, indent=2)
        
        logger.info(f"Saved algorithm configuration to {config_file}")
        
        return config_file
    
    except Exception as e:
        logger.error(f"Error saving refined algorithm: {e}")
        raise


def update_prediction_module(config_file):
    """Update the prediction module with the refined algorithm."""
    try:
        # Load algorithm configuration
        with open(config_file, 'r') as f:
            algorithm_config = json.load(f)
        
        # Create the refined_algorithm.py file
        refined_algorithm_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'prediction', 'refined_algorithm.py')
        
        # Write the refined algorithm module
        with open(refined_algorithm_file, 'w') as f:
            f.write(f'''"""
Refined prediction algorithm for NBA 2K eSports match outcomes.

This module provides a refined prediction algorithm based on model evaluation
and parameter optimization.
"""
import os
import pickle
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.data.matches import fetch_upcoming_matches
from src.data.standings import fetch_standings
from src.analysis.player_team_analysis import calculate_player_team_stats

logger = logging.getLogger(__name__)


# Load the trained model
MODEL_FILE = "{algorithm_config['model_file'].replace('\\\\', '/')}"
try:
    with open(MODEL_FILE, 'rb') as f:
        MODEL = pickle.load(f)
except Exception as e:
    logger.error(f"Error loading model: {{e}}")
    MODEL = None

# Feature weights
FEATURE_WEIGHTS = {algorithm_config['feature_weights']}


def prepare_match_features(
    home_player_id: int,
    away_player_id: int,
    home_team: str,
    away_team: str,
    tournament_id: int = 1
) -> Dict[str, float]:
    """
    Prepare features for a match prediction.
    
    Args:
        home_player_id: Home player's ID
        away_player_id: Away player's ID
        home_team: Home team name
        away_team: Away team name
        tournament_id: Tournament ID (default: 1)
        
    Returns:
        Dictionary with match features
    """
    try:
        # Get player-team statistics
        home_player_stats = calculate_player_team_stats(home_player_id, tournament_id)
        away_player_stats = calculate_player_team_stats(away_player_id, tournament_id)
        
        # Get team-specific statistics
        home_player_team_stats = home_player_stats.get(home_team, {{}})
        away_player_team_stats = away_player_stats.get(away_team, {{}})
        
        # Create feature dictionary
        features = {{
            'home_player_team_matches': home_player_team_stats.get('matches', 0),
            'home_player_team_win_rate': home_player_team_stats.get('win_rate', 0),
            'home_player_team_avg_score': home_player_team_stats.get('avg_score', 0),
            'home_player_team_avg_opponent_score': home_player_team_stats.get('avg_opponent_score', 0),
            'home_player_team_avg_score_diff': home_player_team_stats.get('avg_score_diff', 0),
            'home_player_team_recent_win_rate': home_player_team_stats.get('recent_win_rate', 0),
            
            'away_player_team_matches': away_player_team_stats.get('matches', 0),
            'away_player_team_win_rate': away_player_team_stats.get('win_rate', 0),
            'away_player_team_avg_score': away_player_team_stats.get('avg_score', 0),
            'away_player_team_avg_opponent_score': away_player_team_stats.get('avg_opponent_score', 0),
            'away_player_team_avg_score_diff': away_player_team_stats.get('avg_score_diff', 0),
            'away_player_team_recent_win_rate': away_player_team_stats.get('recent_win_rate', 0),
            
            # Default values for head-to-head features
            'h2h_matches': 0,
            'home_player_h2h_wins': 0,
            'away_player_h2h_wins': 0,
            'home_player_h2h_win_rate': 0.5,
            'away_player_h2h_win_rate': 0.5
        }}
        
        # TODO: Add head-to-head features if available
        
        return features
    
    except Exception as e:
        logger.error(f"Error preparing match features: {{e}}")
        return {{}}


def predict_match(
    home_player_id: int,
    away_player_id: int,
    home_team: str,
    away_team: str,
    tournament_id: int = 1
) -> Dict[str, Any]:
    """
    Predict the outcome of a match using the refined algorithm.
    
    Args:
        home_player_id: Home player's ID
        away_player_id: Away player's ID
        home_team: Home team name
        away_team: Away team name
        tournament_id: Tournament ID (default: 1)
        
    Returns:
        Dictionary with prediction results
    """
    try:
        # Check if model is loaded
        if MODEL is None:
            raise ValueError("Model not loaded")
        
        # Get player names
        standings = fetch_standings(tournament_id)
        home_player = next((p for p in standings if p.get('participantId') == home_player_id), {{}})
        away_player = next((p for p in standings if p.get('participantId') == away_player_id), {{}})
        
        home_player_name = home_player.get('participantName', f"Player {{home_player_id}}")
        away_player_name = away_player.get('participantName', f"Player {{away_player_id}}")
        
        # Prepare features
        features = prepare_match_features(home_player_id, away_player_id, home_team, away_team, tournament_id)
        
        # Convert features to array
        feature_array = np.array([[
            features['home_player_team_matches'],
            features['home_player_team_win_rate'],
            features['home_player_team_avg_score'],
            features['home_player_team_avg_opponent_score'],
            features['home_player_team_avg_score_diff'],
            features['home_player_team_recent_win_rate'],
            features['away_player_team_matches'],
            features['away_player_team_win_rate'],
            features['away_player_team_avg_score'],
            features['away_player_team_avg_opponent_score'],
            features['away_player_team_avg_score_diff'],
            features['away_player_team_recent_win_rate'],
            features['h2h_matches'],
            features['home_player_h2h_wins'],
            features['away_player_h2h_wins'],
            features['home_player_h2h_win_rate'],
            features['away_player_h2h_win_rate']
        ]])
        
        # Make prediction
        prediction_proba = MODEL.predict_proba(feature_array)[0]
        home_win_probability = prediction_proba[1]
        away_win_probability = prediction_proba[0]
        
        # Determine predicted winner
        if home_win_probability > away_win_probability:
            predicted_winner = home_player_name
            predicted_winner_id = home_player_id
        else:
            predicted_winner = away_player_name
            predicted_winner_id = away_player_id
        
        # Calculate confidence
        confidence = max(home_win_probability, away_win_probability)
        
        # Create prediction result
        prediction = {{
            'home_player_id': home_player_id,
            'home_player_name': home_player_name,
            'away_player_id': away_player_id,
            'away_player_name': away_player_name,
            'home_team': home_team,
            'away_team': away_team,
            'home_win_probability': float(home_win_probability),
            'away_win_probability': float(away_win_probability),
            'predicted_winner': predicted_winner,
            'predicted_winner_id': predicted_winner_id,
            'confidence': float(confidence),
            'prediction_time': datetime.now().isoformat()
        }}
        
        return prediction
    
    except Exception as e:
        logger.error(f"Error predicting match: {{e}}")
        return {{}}


def predict_upcoming_matches(hours_ahead: int = 24, tournament_id: int = 1) -> List[Dict[str, Any]]:
    """
    Predict outcomes for upcoming matches using the refined algorithm.
    
    Args:
        hours_ahead: Number of hours ahead to fetch matches for (default: 24)
        tournament_id: Tournament ID (default: 1)
        
    Returns:
        List of dictionaries with prediction results
    """
    try:
        # Fetch upcoming matches
        upcoming_matches = fetch_upcoming_matches(hours_ahead=hours_ahead, tournament_id=tournament_id)
        
        # Make predictions for each match
        predictions = []
        
        for match in upcoming_matches:
            # Extract player and team information
            home_player_id = match.get('homeParticipantId')
            away_player_id = match.get('awayParticipantId')
            home_team = match.get('homeTeamName')
            away_team = match.get('awayTeamName')
            
            if not all([home_player_id, away_player_id, home_team, away_team]):
                logger.warning(f"Skipping match {{match.get('fixtureId')}} due to missing data")
                continue
            
            # Make prediction
            try:
                prediction = predict_match(home_player_id, away_player_id, home_team, away_team, tournament_id)
                
                # Add match information to prediction
                prediction_with_match = {{
                    'match_id': match.get('fixtureId'),
                    'fixture_start': match.get('fixtureStart'),
                    'prediction': prediction
                }}
                
                predictions.append(prediction_with_match)
                
            except Exception as e:
                logger.warning(f"Could not make prediction for match {{match.get('fixtureId')}}: {{e}}")
                continue
        
        return predictions
    
    except Exception as e:
        logger.error(f"Error predicting upcoming matches: {{e}}")
        return []
''')
        
        logger.info(f"Updated prediction module with refined algorithm: {refined_algorithm_file}")
        
        return refined_algorithm_file
    
    except Exception as e:
        logger.error(f"Error updating prediction module: {e}")
        raise


def main():
    """Main function to refine the prediction algorithm."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load training data
        training_data = load_training_data(args.processed_data_dir)
        
        # Split into features and target
        X = training_data.drop(['match_id', 'home_player_id', 'away_player_id', 'home_team', 'away_team', 'home_player_won'], axis=1)
        y = training_data['home_player_won']
        
        # Get feature names
        feature_names = X.columns.tolist()
        
        # Optimize model parameters
        best_model, best_params = optimize_model_parameters(args.model_type, X, y, args.random_state)
        
        # Analyze feature importance
        feature_importance = analyze_feature_importance(best_model, feature_names)
        
        # Display feature importance
        logger.info("Feature Importance:")
        for i, row in feature_importance.iterrows():
            logger.info(f"{row['feature']}: {row['importance']:.4f}")
        
        # Calculate optimal feature weights
        feature_weights = calculate_optimal_feature_weights(feature_importance)
        
        # Save refined algorithm
        config_file = save_refined_algorithm(best_model, feature_weights, best_params, args.output_dir)
        
        # Update prediction module
        refined_algorithm_file = update_prediction_module(config_file)
        
        logger.info("Prediction algorithm refinement completed successfully.")
        
    except Exception as e:
        logger.error(f"Error refining prediction algorithm: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
