"""
Script to optimize the score prediction model using Bayesian optimization.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import StackingRegressor
from xgboost import XGBRegressor

# Add parent directory to path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

from config.settings import (
    PLAYER_STATS_FILE, MATCH_HISTORY_FILE, MODELS_DIR, DEFAULT_RANDOM_STATE
)
from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions
from core.models.score_prediction import ScorePredictionModel
from core.models.registry import ScoreModelRegistry
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
def optimize_score_model(n_trials=50, test_size=0.2, random_state=DEFAULT_RANDOM_STATE):
    """
    Optimize the score prediction model using Bayesian optimization.

    Args:
        n_trials (int): Number of optimization trials
        test_size (float): Proportion of data to use for testing
        random_state (int): Random state for reproducibility

    Returns:
        tuple: (best_params, best_score, best_model)
    """
    # Load data
    player_stats, matches = load_data()

    # Define parameter space for score prediction model
    param_space = {
        # XGBoost parameters for home model
        'xgb_home_n_estimators': {
            'type': 'integer',
            'low': 50,
            'high': 500
        },
        'xgb_home_learning_rate': {
            'type': 'real',
            'low': 0.01,
            'high': 0.3,
            'prior': 'log-uniform'
        },
        'xgb_home_max_depth': {
            'type': 'integer',
            'low': 3,
            'high': 10
        },
        'xgb_home_subsample': {
            'type': 'real',
            'low': 0.5,
            'high': 1.0
        },
        'xgb_home_colsample_bytree': {
            'type': 'real',
            'low': 0.5,
            'high': 1.0
        },

        # Gradient Boosting parameters for home model
        'gb_home_n_estimators': {
            'type': 'integer',
            'low': 50,
            'high': 500
        },
        'gb_home_learning_rate': {
            'type': 'real',
            'low': 0.01,
            'high': 0.3,
            'prior': 'log-uniform'
        },
        'gb_home_max_depth': {
            'type': 'integer',
            'low': 3,
            'high': 10
        },
        'gb_home_subsample': {
            'type': 'real',
            'low': 0.5,
            'high': 1.0
        },

        # Ridge parameters for home model
        'ridge_home_alpha': {
            'type': 'real',
            'low': 0.01,
            'high': 10.0,
            'prior': 'log-uniform'
        },

        # Lasso parameters for home model
        'lasso_home_alpha': {
            'type': 'real',
            'low': 0.001,
            'high': 1.0,
            'prior': 'log-uniform'
        },

        # Final estimator parameters for home model
        'final_home_alpha': {
            'type': 'real',
            'low': 0.01,
            'high': 10.0,
            'prior': 'log-uniform'
        },

        # XGBoost parameters for away model
        'xgb_away_n_estimators': {
            'type': 'integer',
            'low': 50,
            'high': 500
        },
        'xgb_away_learning_rate': {
            'type': 'real',
            'low': 0.01,
            'high': 0.3,
            'prior': 'log-uniform'
        },
        'xgb_away_max_depth': {
            'type': 'integer',
            'low': 3,
            'high': 10
        },
        'xgb_away_subsample': {
            'type': 'real',
            'low': 0.5,
            'high': 1.0
        },
        'xgb_away_colsample_bytree': {
            'type': 'real',
            'low': 0.5,
            'high': 1.0
        },

        # Gradient Boosting parameters for away model
        'gb_away_n_estimators': {
            'type': 'integer',
            'low': 50,
            'high': 500
        },
        'gb_away_learning_rate': {
            'type': 'real',
            'low': 0.01,
            'high': 0.3,
            'prior': 'log-uniform'
        },
        'gb_away_max_depth': {
            'type': 'integer',
            'low': 3,
            'high': 10
        },
        'gb_away_subsample': {
            'type': 'real',
            'low': 0.5,
            'high': 1.0
        },

        # Ridge parameters for away model
        'ridge_away_alpha': {
            'type': 'real',
            'low': 0.01,
            'high': 10.0,
            'prior': 'log-uniform'
        },

        # Lasso parameters for away model
        'lasso_away_alpha': {
            'type': 'real',
            'low': 0.001,
            'high': 1.0,
            'prior': 'log-uniform'
        },

        # Final estimator parameters for away model
        'final_away_alpha': {
            'type': 'real',
            'low': 0.01,
            'high': 10.0,
            'prior': 'log-uniform'
        }
    }

    # Create optimizer
    optimizer = BayesianOptimizer(
        model_class=OptimizedScorePredictionModel,
        param_space=param_space,
        random_state=random_state
    )

    # Run optimization
    best_params, best_score, best_model = optimizer.optimize(
        player_stats=player_stats,
        matches=matches,
        n_trials=n_trials,
        test_size=test_size,
        scoring='neg_mean_absolute_error'
    )

    # Save the best model
    model_path = os.path.join(MODELS_DIR, f"optimized_score_model_{best_model.model_id}.pkl")
    info_path = os.path.join(MODELS_DIR, f"optimized_score_model_info_{best_model.model_id}.json")
    best_model.save(model_path, info_path)

    # Update model registry
    registry = ScoreModelRegistry(MODELS_DIR)
    registry.add_model(
        model_id=best_model.model_id,
        model_path=model_path,
        info_path=info_path,
        total_score_mae=-best_score  # Convert back to positive MAE
    )

    return best_params, best_score, best_model


class OptimizedScorePredictionModel(ScorePredictionModel):
    """
    Score prediction model with optimized hyperparameters.
    """

    def __init__(
        self,
        model_id=None,
        random_state=DEFAULT_RANDOM_STATE,
        xgb_home_n_estimators=100,
        xgb_home_learning_rate=0.1,
        xgb_home_max_depth=5,
        xgb_home_subsample=0.8,
        xgb_home_colsample_bytree=0.8,
        gb_home_n_estimators=100,
        gb_home_learning_rate=0.1,
        gb_home_max_depth=5,
        gb_home_subsample=0.8,
        ridge_home_alpha=1.0,
        lasso_home_alpha=0.1,
        final_home_alpha=0.5,
        xgb_away_n_estimators=100,
        xgb_away_learning_rate=0.1,
        xgb_away_max_depth=5,
        xgb_away_subsample=0.8,
        xgb_away_colsample_bytree=0.8,
        gb_away_n_estimators=100,
        gb_away_learning_rate=0.1,
        gb_away_max_depth=5,
        gb_away_subsample=0.8,
        ridge_away_alpha=1.0,
        lasso_away_alpha=0.1,
        final_away_alpha=0.5
    ):
        """
        Initialize the optimized score prediction model.

        Args:
            model_id (str): Model ID
            random_state (int): Random state for reproducibility
            xgb_home_n_estimators (int): Number of estimators for home XGBoost model
            xgb_home_learning_rate (float): Learning rate for home XGBoost model
            xgb_home_max_depth (int): Maximum depth for home XGBoost model
            xgb_home_subsample (float): Subsample ratio for home XGBoost model
            xgb_home_colsample_bytree (float): Column subsample ratio for home XGBoost model
            gb_home_n_estimators (int): Number of estimators for home Gradient Boosting model
            gb_home_learning_rate (float): Learning rate for home Gradient Boosting model
            gb_home_max_depth (int): Maximum depth for home Gradient Boosting model
            gb_home_subsample (float): Subsample ratio for home Gradient Boosting model
            ridge_home_alpha (float): Alpha for home Ridge model
            lasso_home_alpha (float): Alpha for home Lasso model
            final_home_alpha (float): Alpha for home final estimator
            xgb_away_n_estimators (int): Number of estimators for away XGBoost model
            xgb_away_learning_rate (float): Learning rate for away XGBoost model
            xgb_away_max_depth (int): Maximum depth for away XGBoost model
            xgb_away_subsample (float): Subsample ratio for away XGBoost model
            xgb_away_colsample_bytree (float): Column subsample ratio for away XGBoost model
            gb_away_n_estimators (int): Number of estimators for away Gradient Boosting model
            gb_away_learning_rate (float): Learning rate for away Gradient Boosting model
            gb_away_max_depth (int): Maximum depth for away Gradient Boosting model
            gb_away_subsample (float): Subsample ratio for away Gradient Boosting model
            ridge_away_alpha (float): Alpha for away Ridge model
            lasso_away_alpha (float): Alpha for away Lasso model
            final_away_alpha (float): Alpha for away final estimator
        """
        # Initialize base class
        super().__init__(model_id, random_state)

        # Store hyperparameters
        self.xgb_home_n_estimators = xgb_home_n_estimators
        self.xgb_home_learning_rate = xgb_home_learning_rate
        self.xgb_home_max_depth = xgb_home_max_depth
        self.xgb_home_subsample = xgb_home_subsample
        self.xgb_home_colsample_bytree = xgb_home_colsample_bytree
        self.gb_home_n_estimators = gb_home_n_estimators
        self.gb_home_learning_rate = gb_home_learning_rate
        self.gb_home_max_depth = gb_home_max_depth
        self.gb_home_subsample = gb_home_subsample
        self.ridge_home_alpha = ridge_home_alpha
        self.lasso_home_alpha = lasso_home_alpha
        self.final_home_alpha = final_home_alpha
        self.xgb_away_n_estimators = xgb_away_n_estimators
        self.xgb_away_learning_rate = xgb_away_learning_rate
        self.xgb_away_max_depth = xgb_away_max_depth
        self.xgb_away_subsample = xgb_away_subsample
        self.xgb_away_colsample_bytree = xgb_away_colsample_bytree
        self.gb_away_n_estimators = gb_away_n_estimators
        self.gb_away_learning_rate = gb_away_learning_rate
        self.gb_away_max_depth = gb_away_max_depth
        self.gb_away_subsample = gb_away_subsample
        self.ridge_away_alpha = ridge_away_alpha
        self.lasso_away_alpha = lasso_away_alpha
        self.final_away_alpha = final_away_alpha

        # Create home and away score models with optimized hyperparameters
        self.home_model, self.away_model = self._create_optimized_models()

        # Update model info
        self.model_info["parameters"] = {
            "random_state": random_state,
            "xgb_home_n_estimators": xgb_home_n_estimators,
            "xgb_home_learning_rate": xgb_home_learning_rate,
            "xgb_home_max_depth": xgb_home_max_depth,
            "xgb_home_subsample": xgb_home_subsample,
            "xgb_home_colsample_bytree": xgb_home_colsample_bytree,
            "gb_home_n_estimators": gb_home_n_estimators,
            "gb_home_learning_rate": gb_home_learning_rate,
            "gb_home_max_depth": gb_home_max_depth,
            "gb_home_subsample": gb_home_subsample,
            "ridge_home_alpha": ridge_home_alpha,
            "lasso_home_alpha": lasso_home_alpha,
            "final_home_alpha": final_home_alpha,
            "xgb_away_n_estimators": xgb_away_n_estimators,
            "xgb_away_learning_rate": xgb_away_learning_rate,
            "xgb_away_max_depth": xgb_away_max_depth,
            "xgb_away_subsample": xgb_away_subsample,
            "xgb_away_colsample_bytree": xgb_away_colsample_bytree,
            "gb_away_n_estimators": gb_away_n_estimators,
            "gb_away_learning_rate": gb_away_learning_rate,
            "gb_away_max_depth": gb_away_max_depth,
            "gb_away_subsample": gb_away_subsample,
            "ridge_away_alpha": ridge_away_alpha,
            "lasso_away_alpha": lasso_away_alpha,
            "final_away_alpha": final_away_alpha
        }

        # Store both models
        self.model = {
            "home_model": self.home_model,
            "away_model": self.away_model
        }

    @log_exceptions(logger)
    def _create_optimized_models(self):
        """
        Create home and away score prediction models with optimized hyperparameters.

        Returns:
            tuple: (home_model, away_model)
        """
        # Create base models for home score
        xgb_model_home = XGBRegressor(
            n_estimators=self.xgb_home_n_estimators,
            learning_rate=self.xgb_home_learning_rate,
            max_depth=self.xgb_home_max_depth,
            subsample=self.xgb_home_subsample,
            colsample_bytree=self.xgb_home_colsample_bytree,
            random_state=self.random_state
        )

        gb_model_home = GradientBoostingRegressor(
            n_estimators=self.gb_home_n_estimators,
            learning_rate=self.gb_home_learning_rate,
            max_depth=self.gb_home_max_depth,
            subsample=self.gb_home_subsample,
            random_state=self.random_state
        )

        ridge_model_home = Ridge(alpha=self.ridge_home_alpha, random_state=self.random_state)
        lasso_model_home = Lasso(alpha=self.lasso_home_alpha, random_state=self.random_state)

        # Create stacking ensemble for home score
        home_stacking_model = StackingRegressor(
            estimators=[
                ('xgb', xgb_model_home),
                ('gb', gb_model_home),
                ('ridge', ridge_model_home),
                ('lasso', lasso_model_home)
            ],
            final_estimator=Ridge(alpha=self.final_home_alpha, random_state=self.random_state),
            cv=5,
            n_jobs=-1
        )

        # Create base models for away score
        xgb_model_away = XGBRegressor(
            n_estimators=self.xgb_away_n_estimators,
            learning_rate=self.xgb_away_learning_rate,
            max_depth=self.xgb_away_max_depth,
            subsample=self.xgb_away_subsample,
            colsample_bytree=self.xgb_away_colsample_bytree,
            random_state=self.random_state
        )

        gb_model_away = GradientBoostingRegressor(
            n_estimators=self.gb_away_n_estimators,
            learning_rate=self.gb_away_learning_rate,
            max_depth=self.gb_away_max_depth,
            subsample=self.gb_away_subsample,
            random_state=self.random_state
        )

        ridge_model_away = Ridge(alpha=self.ridge_away_alpha, random_state=self.random_state)
        lasso_model_away = Lasso(alpha=self.lasso_away_alpha, random_state=self.random_state)

        # Create stacking ensemble for away score
        away_stacking_model = StackingRegressor(
            estimators=[
                ('xgb', xgb_model_away),
                ('gb', gb_model_away),
                ('ridge', ridge_model_away),
                ('lasso', lasso_model_away)
            ],
            final_estimator=Ridge(alpha=self.final_away_alpha, random_state=self.random_state),
            cv=5,
            n_jobs=-1
        )

        # Create feature scaling and model pipeline
        home_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', home_stacking_model)
        ])

        away_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', away_stacking_model)
        ])

        return home_pipeline, away_pipeline


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Optimize score prediction model")
    parser.add_argument("--n-trials", type=int, default=50, help="Number of optimization trials")
    parser.add_argument("--test-size", type=float, default=0.2, help="Proportion of data to use for testing")
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE, help="Random state for reproducibility")
    args = parser.parse_args()

    # Create models directory if it doesn't exist
    Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)

    # Run optimization
    best_params, best_score, best_model = optimize_score_model(
        n_trials=args.n_trials,
        test_size=args.test_size,
        random_state=args.random_state
    )

    # Print results
    print(f"Best parameters: {best_params}")
    print(f"Best score (negative MAE): {best_score}")
    print(f"Best model ID: {best_model.model_id}")
    print(f"Best model saved to: {os.path.join(MODELS_DIR, f'optimized_score_model_{best_model.model_id}.pkl')}")
    print(f"Best model info saved to: {os.path.join(MODELS_DIR, f'optimized_score_model_info_{best_model.model_id}.json')}")
