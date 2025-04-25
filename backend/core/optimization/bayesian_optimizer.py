"""
Bayesian optimizer for model hyperparameter tuning.
"""

import numpy as np
from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args

from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions
from .tuner import BaseTuner

logger = get_model_tuning_logger()


class BayesianOptimizer(BaseTuner):
    """
    Bayesian optimizer for model hyperparameter tuning.
    """
    
    def __init__(self, model_class, param_space, random_state=42):
        """
        Initialize the Bayesian optimizer.
        
        Args:
            model_class: Model class to tune
            param_space (dict): Parameter space to search
            random_state (int): Random state for reproducibility
        """
        super().__init__(model_class, param_space, random_state)
        
        # Convert parameter space to skopt space
        self.skopt_space = self._convert_param_space(param_space)
    
    @log_exceptions(logger)
    def _convert_param_space(self, param_space):
        """
        Convert parameter space to skopt space.
        
        Args:
            param_space (dict): Parameter space to convert
            
        Returns:
            list: skopt space
        """
        skopt_space = []
        
        for param_name, param_config in param_space.items():
            param_type = param_config['type']
            
            if param_type == 'real':
                skopt_space.append(
                    Real(
                        param_config['low'],
                        param_config['high'],
                        prior=param_config.get('prior', 'uniform'),
                        name=param_name
                    )
                )
            elif param_type == 'integer':
                skopt_space.append(
                    Integer(
                        param_config['low'],
                        param_config['high'],
                        name=param_name
                    )
                )
            elif param_type == 'categorical':
                skopt_space.append(
                    Categorical(
                        param_config['categories'],
                        name=param_name
                    )
                )
        
        return skopt_space
    
    @log_execution_time(logger)
    @log_exceptions(logger)
    def optimize(self, player_stats, matches, n_trials=50, test_size=0.2, scoring='neg_mean_absolute_error'):
        """
        Optimize model hyperparameters using Bayesian optimization.
        
        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            n_trials (int): Number of optimization trials
            test_size (float): Proportion of data to use for testing
            scoring (str): Scoring metric to optimize
            
        Returns:
            tuple: (best_params, best_score, best_model)
        """
        logger.info(f"Starting Bayesian optimization with {n_trials} trials")
        
        # Define the objective function
        @use_named_args(self.skopt_space)
        def objective(**params):
            # Add fixed parameters
            params['random_state'] = self.random_state
            
            # Evaluate the parameters
            score = self._evaluate_params(params, player_stats, matches, test_size, scoring)
            
            # Return negative score for minimization
            return -score
        
        # Run Bayesian optimization
        result = gp_minimize(
            objective,
            self.skopt_space,
            n_calls=n_trials,
            random_state=self.random_state,
            verbose=True,
            n_jobs=-1
        )
        
        # Convert best parameters to dictionary
        best_params = {dim.name: value for dim, value in zip(self.skopt_space, result.x)}
        best_params['random_state'] = self.random_state
        
        # Store best parameters and score
        self.best_params = best_params
        self.best_score = -result.fun  # Convert back to positive score
        
        # Create and train the best model
        if self.best_model is None:
            self.best_model = self.model_class(**best_params)
            self.best_model.train(player_stats, matches, test_size=test_size)
        
        logger.info(f"Bayesian optimization completed")
        logger.info(f"Best parameters: {best_params}")
        logger.info(f"Best score: {self.best_score}")
        
        return best_params, self.best_score, self.best_model
