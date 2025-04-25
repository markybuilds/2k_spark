"""
Script to optimize the winner prediction model using Bayesian optimization.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier

# Add parent directory to path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

from config.settings import (
    PLAYER_STATS_FILE, MATCH_HISTORY_FILE, MODELS_DIR, DEFAULT_RANDOM_STATE
)
from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions
from core.models.winner_prediction import WinnerPredictionModel
from core.models.registry import ModelRegistry
from core.optimization.bayesian_optimizer import BayesianOptimizer

logger = get_model_tuning_logger()


@log_execution_time(logger)
@log_exceptions(logger)
def load_data():
    """
    Load player stats and match history data.
    
    Returns:
        tuple: (player_stats, matches)
    """
    logger.info(f"Loading player stats from {PLAYER_STATS_FILE}")
    with open(PLAYER_STATS_FILE, 'r', encoding='utf-8') as f:
        player_stats = json.load(f)
    
    logger.info(f"Loading match history from {MATCH_HISTORY_FILE}")
    with open(MATCH_HISTORY_FILE, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    return player_stats, matches


@log_execution_time(logger)
@log_exceptions(logger)
def optimize_winner_model(n_trials=50, test_size=0.2, random_state=DEFAULT_RANDOM_STATE):
    """
    Optimize the winner prediction model using Bayesian optimization.
    
    Args:
        n_trials (int): Number of optimization trials
        test_size (float): Proportion of data to use for testing
        random_state (int): Random state for reproducibility
        
    Returns:
        tuple: (best_params, best_score, best_model)
    """
    # Load data
    player_stats, matches = load_data()
    
    # Define parameter space for winner prediction model
    param_space = {
        # Random Forest parameters
        'n_estimators': {
            'type': 'integer',
            'low': 50,
            'high': 500
        },
        'max_depth': {
            'type': 'integer',
            'low': 3,
            'high': 20
        },
        'min_samples_split': {
            'type': 'integer',
            'low': 2,
            'high': 20
        },
        'min_samples_leaf': {
            'type': 'integer',
            'low': 1,
            'high': 10
        },
        'max_features': {
            'type': 'categorical',
            'categories': ['sqrt', 'log2', None]
        },
        'bootstrap': {
            'type': 'categorical',
            'categories': [True, False]
        },
        'class_weight': {
            'type': 'categorical',
            'categories': ['balanced', 'balanced_subsample', None]
        }
    }
    
    # Create optimizer
    optimizer = BayesianOptimizer(
        model_class=OptimizedWinnerPredictionModel,
        param_space=param_space,
        random_state=random_state
    )
    
    # Run optimization
    best_params, best_score, best_model = optimizer.optimize(
        player_stats=player_stats,
        matches=matches,
        n_trials=n_trials,
        test_size=test_size,
        scoring='accuracy'
    )
    
    # Save the best model
    model_path = os.path.join(MODELS_DIR, f"optimized_winner_model_{best_model.model_id}.pkl")
    info_path = os.path.join(MODELS_DIR, f"optimized_winner_model_info_{best_model.model_id}.json")
    best_model.save(model_path, info_path)
    
    # Update model registry
    registry = ModelRegistry(MODELS_DIR)
    registry.add_model(
        model_id=best_model.model_id,
        model_path=model_path,
        info_path=info_path,
        accuracy=best_score
    )
    
    return best_params, best_score, best_model


class OptimizedWinnerPredictionModel(WinnerPredictionModel):
    """
    Winner prediction model with optimized hyperparameters.
    """
    
    def __init__(
        self,
        model_id=None,
        random_state=DEFAULT_RANDOM_STATE,
        n_estimators=100,
        max_depth=10,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features='sqrt',
        bootstrap=True,
        class_weight=None,
        feature_config=None
    ):
        """
        Initialize the optimized winner prediction model.
        
        Args:
            model_id (str): Model ID
            random_state (int): Random state for reproducibility
            n_estimators (int): Number of trees in the forest
            max_depth (int): Maximum depth of the trees
            min_samples_split (int): Minimum number of samples required to split an internal node
            min_samples_leaf (int): Minimum number of samples required to be at a leaf node
            max_features (str): Number of features to consider when looking for the best split
            bootstrap (bool): Whether bootstrap samples are used when building trees
            class_weight (str): Weights associated with classes
            feature_config (dict): Feature configuration dictionary
        """
        # Initialize base class with basic parameters
        super().__init__(
            model_id=model_id,
            random_state=random_state,
            n_estimators=n_estimators,
            max_depth=max_depth,
            feature_config=feature_config
        )
        
        # Store additional hyperparameters
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.bootstrap = bootstrap
        self.class_weight = class_weight
        
        # Update model info
        self.model_info["parameters"].update({
            "min_samples_split": min_samples_split,
            "min_samples_leaf": min_samples_leaf,
            "max_features": max_features,
            "bootstrap": bootstrap,
            "class_weight": class_weight
        })
        
        # Initialize model with all hyperparameters
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            bootstrap=bootstrap,
            class_weight=class_weight,
            random_state=random_state
        )


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Optimize winner prediction model")
    parser.add_argument("--n-trials", type=int, default=50, help="Number of optimization trials")
    parser.add_argument("--test-size", type=float, default=0.2, help="Proportion of data to use for testing")
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE, help="Random state for reproducibility")
    args = parser.parse_args()
    
    # Create models directory if it doesn't exist
    Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)
    
    # Run optimization
    best_params, best_score, best_model = optimize_winner_model(
        n_trials=args.n_trials,
        test_size=args.test_size,
        random_state=args.random_state
    )
    
    # Print results
    print(f"Best parameters: {best_params}")
    print(f"Best score (accuracy): {best_score}")
    print(f"Best model ID: {best_model.model_id}")
    print(f"Best model saved to: {os.path.join(MODELS_DIR, f'optimized_winner_model_{best_model.model_id}.pkl')}")
    print(f"Best model info saved to: {os.path.join(MODELS_DIR, f'optimized_winner_model_info_{best_model.model_id}.json')}")
