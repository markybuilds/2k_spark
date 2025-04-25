"""
Score prediction model for NBA 2K25 eSports matches.
"""

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import StackingRegressor
from xgboost import XGBRegressor

from config.settings import DEFAULT_RANDOM_STATE
from config.logging_config import get_score_model_training_logger
from utils.logging import log_execution_time, log_exceptions
from core.models.base import BaseModel

logger = get_score_model_training_logger()


class ScorePredictionModel(BaseModel):
    """
    Model for predicting match scores.
    """
    
    def __init__(self, model_id=None, random_state=DEFAULT_RANDOM_STATE):
        """
        Initialize the score prediction model.
        
        Args:
            model_id (str): Model ID
            random_state (int): Random state for reproducibility
        """
        super().__init__(model_id, random_state)
        
        # Create home and away score models
        self.home_model, self.away_model = self._create_models(random_state)
        
        # Update model info
        self.model_info["parameters"] = {
            "random_state": random_state
        }
        
        # Store both models
        self.model = {
            "home_model": self.home_model,
            "away_model": self.away_model
        }
    
    @log_exceptions(logger)
    def _create_models(self, random_state):
        """
        Create home and away score prediction models.
        
        Args:
            random_state (int): Random state for reproducibility
            
        Returns:
            tuple: (home_model, away_model)
        """
        # Create base models for home score
        xgb_model_home = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=random_state
        )
        
        gb_model_home = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=random_state
        )
        
        ridge_model_home = Ridge(alpha=1.0, random_state=random_state)
        lasso_model_home = Lasso(alpha=0.1, random_state=random_state)
        
        # Create stacking ensemble for home score
        home_stacking_model = StackingRegressor(
            estimators=[
                ('xgb', xgb_model_home),
                ('gb', gb_model_home),
                ('ridge', ridge_model_home),
                ('lasso', lasso_model_home)
            ],
            final_estimator=Ridge(alpha=0.5, random_state=random_state),
            cv=5,
            n_jobs=-1
        )
        
        # Create base models for away score
        xgb_model_away = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=random_state
        )
        
        gb_model_away = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=random_state
        )
        
        ridge_model_away = Ridge(alpha=1.0, random_state=random_state)
        lasso_model_away = Lasso(alpha=0.1, random_state=random_state)
        
        # Create stacking ensemble for away score
        away_stacking_model = StackingRegressor(
            estimators=[
                ('xgb', xgb_model_away),
                ('gb', gb_model_away),
                ('ridge', ridge_model_away),
                ('lasso', lasso_model_away)
            ],
            final_estimator=Ridge(alpha=0.5, random_state=random_state),
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
    
    @log_execution_time(logger)
    @log_exceptions(logger)
    def train(self, player_stats, matches, test_size=0.2):
        """
        Train the model on match data.
        
        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            test_size (float): Proportion of data to use for testing
            
        Returns:
            self: The trained model
        """
        logger.info(f"Training score prediction model with {len(matches)} matches")
        
        # Extract features and labels
        X, y_home, y_away = self._extract_features(player_stats, matches)
        
        if len(X) == 0:
            logger.error("No valid features extracted from matches")
            raise ValueError("No valid features extracted from matches")
        
        logger.info(f"Extracted {len(X)} samples with {X.shape[1]} features")
        
        # Split data into training and testing sets
        X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
            X, y_home, y_away, test_size=test_size, random_state=self.random_state
        )
        
        # Train home score model
        logger.info(f"Training home score model with {len(X_train)} samples")
        self.home_model.fit(X_train, y_home_train)
        
        # Train away score model
        logger.info(f"Training away score model with {len(X_train)} samples")
        self.away_model.fit(X_train, y_away_train)
        
        # Evaluate models
        logger.info("Evaluating models")
        metrics = self._evaluate_models(X_test, y_home_test, y_away_test)
        
        # Update model info
        self.model_info["metrics"] = metrics
        self.model_info["home_score_mae"] = metrics["home_score_mae"]
        self.model_info["away_score_mae"] = metrics["away_score_mae"]
        self.model_info["total_score_mae"] = metrics["total_score_mae"]
        self.model_info["data_files"] = {
            "player_stats": "player_stats.json",
            "match_history": "match_history.json"
        }
        self.model_info["num_samples"] = len(X)
        
        logger.info(f"Models trained with total score MAE: {metrics['total_score_mae']:.4f}")
        return self
    
    @log_exceptions(logger)
    def _extract_features(self, player_stats, matches):
        """
        Extract features from match data.
        
        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            
        Returns:
            tuple: (features, home_scores, away_scores)
        """
        features = []
        home_scores = []
        away_scores = []
        
        for match in matches:
            # Skip matches without scores (upcoming matches)
            if 'homeScore' not in match or 'awayScore' not in match:
                continue
            
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            # Skip if player stats not available
            if home_player_id not in player_stats or away_player_id not in player_stats:
                continue
            
            home_player = player_stats[home_player_id]
            away_player = player_stats[away_player_id]
            
            home_team_id = str(match['homeTeam']['id'])
            away_team_id = str(match['awayTeam']['id'])
            
            # Extract features
            match_features = [
                # Player overall stats
                home_player.get('win_rate', 0),
                away_player.get('win_rate', 0),
                home_player.get('avg_score', 0),
                away_player.get('avg_score', 0),
                home_player.get('total_matches', 0),
                away_player.get('total_matches', 0),
                
                # Team-specific stats
                self._get_team_win_rate(home_player, home_team_id),
                self._get_team_win_rate(away_player, away_team_id),
                self._get_team_avg_score(home_player, home_team_id),
                self._get_team_avg_score(away_player, away_team_id),
                self._get_team_matches(home_player, home_team_id),
                self._get_team_matches(away_player, away_team_id),
                
                # Head-to-head stats
                self._get_h2h_win_rate(home_player, away_player_id),
                self._get_h2h_win_rate(away_player, home_player_id),
                
                # Additional features for score prediction
                self._get_recent_form(home_player),
                self._get_recent_form(away_player),
                self._get_avg_score_against(home_player, away_player_id),
                self._get_avg_score_against(away_player, home_player_id)
            ]
            
            features.append(match_features)
            
            # Labels: home and away scores
            home_scores.append(match['homeScore'])
            away_scores.append(match['awayScore'])
        
        return np.array(features), np.array(home_scores), np.array(away_scores)
    
    @log_exceptions(logger)
    def _get_team_win_rate(self, player, team_id):
        """
        Get a player's win rate with a specific team.
        
        Args:
            player (dict): Player statistics dictionary
            team_id (str): Team ID
            
        Returns:
            float: Win rate
        """
        teams_used = player.get('teams_used', {})
        if team_id in teams_used:
            return teams_used[team_id].get('win_rate', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_team_avg_score(self, player, team_id):
        """
        Get a player's average score with a specific team.
        
        Args:
            player (dict): Player statistics dictionary
            team_id (str): Team ID
            
        Returns:
            float: Average score
        """
        teams_used = player.get('teams_used', {})
        if team_id in teams_used:
            return teams_used[team_id].get('avg_score', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_team_matches(self, player, team_id):
        """
        Get the number of matches a player has played with a specific team.
        
        Args:
            player (dict): Player statistics dictionary
            team_id (str): Team ID
            
        Returns:
            int: Number of matches
        """
        teams_used = player.get('teams_used', {})
        if team_id in teams_used:
            return teams_used[team_id].get('matches', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_h2h_win_rate(self, player, opponent_id):
        """
        Get a player's win rate against a specific opponent.
        
        Args:
            player (dict): Player statistics dictionary
            opponent_id (str): Opponent player ID
            
        Returns:
            float: Win rate
        """
        opponents_faced = player.get('opponents_faced', {})
        if opponent_id in opponents_faced:
            return opponents_faced[opponent_id].get('win_rate', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_recent_form(self, player):
        """
        Get a player's recent form (simplified as win rate).
        
        Args:
            player (dict): Player statistics dictionary
            
        Returns:
            float: Recent form
        """
        # In a real implementation, this would consider recent matches
        # For now, we'll use overall win rate as a proxy
        return player.get('win_rate', 0)
    
    @log_exceptions(logger)
    def _get_avg_score_against(self, player, opponent_id):
        """
        Get a player's average score against a specific opponent.
        
        Args:
            player (dict): Player statistics dictionary
            opponent_id (str): Opponent player ID
            
        Returns:
            float: Average score
        """
        # This would require additional data processing in a real implementation
        # For now, we'll use overall average score as a proxy
        return player.get('avg_score', 0)
    
    @log_exceptions(logger)
    def _evaluate_models(self, X_test, y_home_test, y_away_test):
        """
        Evaluate the models on test data.
        
        Args:
            X_test (numpy.ndarray): Test features
            y_home_test (numpy.ndarray): Test home scores
            y_away_test (numpy.ndarray): Test away scores
            
        Returns:
            dict: Evaluation metrics
        """
        # Make predictions
        y_home_pred = self.home_model.predict(X_test)
        y_away_pred = self.away_model.predict(X_test)
        
        # Calculate metrics for home score
        home_mae = mean_absolute_error(y_home_test, y_home_pred)
        home_mse = mean_squared_error(y_home_test, y_home_pred)
        home_rmse = np.sqrt(home_mse)
        home_r2 = r2_score(y_home_test, y_home_pred)
        
        # Calculate metrics for away score
        away_mae = mean_absolute_error(y_away_test, y_away_pred)
        away_mse = mean_squared_error(y_away_test, y_away_pred)
        away_rmse = np.sqrt(away_mse)
        away_r2 = r2_score(y_away_test, y_away_pred)
        
        # Calculate metrics for total score
        total_score_test = y_home_test + y_away_test
        total_score_pred = y_home_pred + y_away_pred
        total_mae = mean_absolute_error(total_score_test, total_score_pred)
        total_mse = mean_squared_error(total_score_test, total_score_pred)
        total_rmse = np.sqrt(total_mse)
        total_r2 = r2_score(total_score_test, total_score_pred)
        
        # Calculate metrics for score difference
        diff_test = y_home_test - y_away_test
        diff_pred = y_home_pred - y_away_pred
        diff_mae = mean_absolute_error(diff_test, diff_pred)
        diff_mse = mean_squared_error(diff_test, diff_pred)
        diff_rmse = np.sqrt(diff_mse)
        diff_r2 = r2_score(diff_test, diff_pred)
        
        return {
            "home_score_mae": float(home_mae),
            "home_score_mse": float(home_mse),
            "home_score_rmse": float(home_rmse),
            "home_score_r2": float(home_r2),
            
            "away_score_mae": float(away_mae),
            "away_score_mse": float(away_mse),
            "away_score_rmse": float(away_rmse),
            "away_score_r2": float(away_r2),
            
            "total_score_mae": float(total_mae),
            "total_score_mse": float(total_mse),
            "total_score_rmse": float(total_rmse),
            "total_score_r2": float(total_r2),
            
            "score_diff_mae": float(diff_mae),
            "score_diff_mse": float(diff_mse),
            "score_diff_rmse": float(diff_rmse),
            "score_diff_r2": float(diff_r2)
        }
    
    @log_exceptions(logger)
    def predict(self, player_stats, match):
        """
        Predict the score of a match.
        
        Args:
            player_stats (dict): Player statistics dictionary
            match (dict): Match data dictionary
            
        Returns:
            dict: Prediction results
        """
        home_player_id = str(match['homePlayer']['id'])
        away_player_id = str(match['awayPlayer']['id'])
        
        # Check if player stats are available
        if home_player_id not in player_stats or away_player_id not in player_stats:
            logger.warning(f"Player stats not available for {home_player_id} or {away_player_id}")
            return {
                "home_score": 60,
                "away_score": 60,
                "total_score": 120,
                "score_diff": 0
            }
        
        home_player = player_stats[home_player_id]
        away_player = player_stats[away_player_id]
        
        home_team_id = str(match['homeTeam']['id'])
        away_team_id = str(match['awayTeam']['id'])
        
        # Extract features
        features = [
            # Player overall stats
            home_player.get('win_rate', 0),
            away_player.get('win_rate', 0),
            home_player.get('avg_score', 0),
            away_player.get('avg_score', 0),
            home_player.get('total_matches', 0),
            away_player.get('total_matches', 0),
            
            # Team-specific stats
            self._get_team_win_rate(home_player, home_team_id),
            self._get_team_win_rate(away_player, away_team_id),
            self._get_team_avg_score(home_player, home_team_id),
            self._get_team_avg_score(away_player, away_team_id),
            self._get_team_matches(home_player, home_team_id),
            self._get_team_matches(away_player, away_team_id),
            
            # Head-to-head stats
            self._get_h2h_win_rate(home_player, away_player_id),
            self._get_h2h_win_rate(away_player, home_player_id),
            
            # Additional features for score prediction
            self._get_recent_form(home_player),
            self._get_recent_form(away_player),
            self._get_avg_score_against(home_player, away_player_id),
            self._get_avg_score_against(away_player, home_player_id)
        ]
        
        # Make prediction
        features_array = np.array([features])
        home_score = self.home_model.predict(features_array)[0]
        away_score = self.away_model.predict(features_array)[0]
        
        # Round scores to integers
        home_score = round(home_score)
        away_score = round(away_score)
        
        # Ensure scores are positive
        home_score = max(0, home_score)
        away_score = max(0, away_score)
        
        # Calculate total score and difference
        total_score = home_score + away_score
        score_diff = home_score - away_score
        
        return {
            "home_score": int(home_score),
            "away_score": int(away_score),
            "total_score": int(total_score),
            "score_diff": int(score_diff)
        }
    
    @log_exceptions(logger)
    def evaluate(self, player_stats, matches):
        """
        Evaluate the model on match data.
        
        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            
        Returns:
            dict: Evaluation metrics
        """
        # Extract features and labels
        X, y_home, y_away = self._extract_features(player_stats, matches)
        
        if len(X) == 0:
            logger.error("No valid features extracted from matches")
            raise ValueError("No valid features extracted from matches")
        
        # Evaluate models
        return self._evaluate_models(X, y_home, y_away)
