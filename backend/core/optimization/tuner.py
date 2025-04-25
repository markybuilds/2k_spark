"""
Base tuner class for model hyperparameter tuning.
"""

from abc import ABC, abstractmethod
import numpy as np
from datetime import datetime

from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions

logger = get_model_tuning_logger()


class BaseTuner(ABC):
    """
    Base class for model hyperparameter tuners.
    """
    
    def __init__(self, model_class, param_space, random_state=42):
        """
        Initialize the tuner.
        
        Args:
            model_class: Model class to tune
            param_space (dict): Parameter space to search
            random_state (int): Random state for reproducibility
        """
        self.model_class = model_class
        self.param_space = param_space
        self.random_state = random_state
        self.best_params = None
        self.best_score = None
        self.best_model = None
        self.results = []
        
    @abstractmethod
    def optimize(self, player_stats, matches, n_trials=50, test_size=0.2, scoring='neg_mean_absolute_error'):
        """
        Optimize model hyperparameters.
        
        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            n_trials (int): Number of optimization trials
            test_size (float): Proportion of data to use for testing
            scoring (str): Scoring metric to optimize
            
        Returns:
            tuple: (best_params, best_score, best_model)
        """
        pass
    
    @log_exceptions(logger)
    def _evaluate_params(self, params, player_stats, matches, test_size=0.2, scoring='neg_mean_absolute_error'):
        """
        Evaluate a set of hyperparameters.
        
        Args:
            params (dict): Hyperparameters to evaluate
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            test_size (float): Proportion of data to use for testing
            scoring (str): Scoring metric to optimize
            
        Returns:
            float: Score for the given parameters
        """
        # Create model with the given parameters
        model = self.model_class(**params)
        
        try:
            # Train the model
            model.train(player_stats, matches, test_size=test_size)
            
            # Get evaluation metrics
            metrics = model.model_info.get("metrics", {})
            
            # Extract the relevant score based on the scoring metric
            if scoring == 'neg_mean_absolute_error':
                # For score prediction model
                if 'total_score_mae' in metrics:
                    # Convert to negative MAE (higher is better)
                    score = -metrics['total_score_mae']
                else:
                    # Fallback to average of home and away MAE
                    home_mae = metrics.get('home_score_mae', 0)
                    away_mae = metrics.get('away_score_mae', 0)
                    score = -(home_mae + away_mae) / 2
            elif scoring == 'accuracy':
                # For winner prediction model
                score = metrics.get('accuracy', 0)
            else:
                # Default to a generic metric if available
                score = metrics.get(scoring, 0)
            
            # Store the result
            result = {
                'params': params,
                'score': score,
                'metrics': metrics,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.results.append(result)
            
            # Update best parameters if this is the best score
            if self.best_score is None or score > self.best_score:
                self.best_params = params
                self.best_score = score
                self.best_model = model
                
                logger.info(f"New best parameters found: {params}")
                logger.info(f"New best score: {score}")
            
            return score
        except Exception as e:
            logger.error(f"Error evaluating parameters {params}: {e}")
            return float('-inf')  # Return worst possible score on error
    
    def get_best_params(self):
        """
        Get the best hyperparameters found.
        
        Returns:
            dict: Best hyperparameters
        """
        return self.best_params
    
    def get_best_score(self):
        """
        Get the best score found.
        
        Returns:
            float: Best score
        """
        return self.best_score
    
    def get_best_model(self):
        """
        Get the best model found.
        
        Returns:
            object: Best model
        """
        return self.best_model
    
    def get_results(self):
        """
        Get all optimization results.
        
        Returns:
            list: List of optimization results
        """
        return self.results
