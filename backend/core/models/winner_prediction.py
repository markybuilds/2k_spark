"""
Winner prediction model for NBA 2K25 eSports matches.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from config.settings import DEFAULT_RANDOM_STATE
from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions
from core.models.base import BaseModel

logger = get_model_tuning_logger()


class WinnerPredictionModel(BaseModel):
    """
    Model for predicting match winners.
    """
    
    def __init__(self, model_id=None, random_state=DEFAULT_RANDOM_STATE, n_estimators=100, max_depth=10):
        """
        Initialize the winner prediction model.
        
        Args:
            model_id (str): Model ID
            random_state (int): Random state for reproducibility
            n_estimators (int): Number of trees in the forest
            max_depth (int): Maximum depth of the trees
        """
        super().__init__(model_id, random_state)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        
        # Update model info
        self.model_info["parameters"] = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": random_state
        }
        
        # Initialize model
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
    
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
        logger.info(f"Training winner prediction model with {len(matches)} matches")
        
        # Extract features and labels
        X, y = self._extract_features(player_stats, matches)
        
        if len(X) == 0:
            logger.error("No valid features extracted from matches")
            raise ValueError("No valid features extracted from matches")
        
        logger.info(f"Extracted {len(X)} samples with {X.shape[1]} features")
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        
        # Train model
        logger.info(f"Training model with {len(X_train)} samples")
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        logger.info("Evaluating model")
        metrics = self._evaluate_model(X_test, y_test)
        
        # Update model info
        self.model_info["metrics"] = metrics
        self.model_info["accuracy"] = metrics["accuracy"]
        self.model_info["data_files"] = {
            "player_stats": "player_stats.json",
            "match_history": "match_history.json"
        }
        self.model_info["num_samples"] = len(X)
        
        logger.info(f"Model trained with accuracy: {metrics['accuracy']:.4f}")
        return self
    
    @log_exceptions(logger)
    def _extract_features(self, player_stats, matches):
        """
        Extract features from match data.
        
        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            
        Returns:
            tuple: (features, labels)
        """
        features = []
        labels = []
        
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
            ]
            
            features.append(match_features)
            
            # Label: 1 if home win, 0 if away win
            home_score = match['homeScore']
            away_score = match['awayScore']
            label = 1 if home_score > away_score else 0
            labels.append(label)
        
        return np.array(features), np.array(labels)
    
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
    def _evaluate_model(self, X_test, y_test):
        """
        Evaluate the model on test data.
        
        Args:
            X_test (numpy.ndarray): Test features
            y_test (numpy.ndarray): Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        # Make predictions
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        
        # Feature importance
        feature_importance = self.model.feature_importances_
        
        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "roc_auc": float(roc_auc),
            "feature_importance": feature_importance.tolist()
        }
    
    @log_exceptions(logger)
    def predict(self, player_stats, match):
        """
        Predict the winner of a match.
        
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
                "home_win_probability": 0.5,
                "away_win_probability": 0.5,
                "predicted_winner": "home" if np.random.random() > 0.5 else "away",
                "confidence": 0.5
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
        ]
        
        # Make prediction
        features_array = np.array([features])
        probabilities = self.model.predict_proba(features_array)[0]
        
        home_win_probability = probabilities[1]
        away_win_probability = probabilities[0]
        
        predicted_winner = "home" if home_win_probability > away_win_probability else "away"
        confidence = max(home_win_probability, away_win_probability)
        
        return {
            "home_win_probability": float(home_win_probability),
            "away_win_probability": float(away_win_probability),
            "predicted_winner": predicted_winner,
            "confidence": float(confidence)
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
        X, y = self._extract_features(player_stats, matches)
        
        if len(X) == 0:
            logger.error("No valid features extracted from matches")
            raise ValueError("No valid features extracted from matches")
        
        # Evaluate model
        return self._evaluate_model(X, y)
