"""
Score prediction model for NBA 2K25 eSports matches.
"""

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import StackingRegressor
from sklearn.feature_selection import SelectFromModel
from xgboost import XGBRegressor

from config.settings import DEFAULT_RANDOM_STATE
from config.logging_config import get_score_model_training_logger
from utils.logging import log_execution_time, log_exceptions
from core.models.base import BaseModel
from core.models.feature_engineering import FeatureEngineer

logger = get_score_model_training_logger()


class ScorePredictionModel(BaseModel):
    """
    Model for predicting match scores.
    """

    def __init__(self, model_id=None, random_state=DEFAULT_RANDOM_STATE, feature_config=None):
        """
        Initialize the score prediction model.

        Args:
            model_id (str): Model ID
            random_state (int): Random state for reproducibility
            feature_config (dict): Feature configuration dictionary
        """
        super().__init__(model_id, random_state)

        # Create feature engineer
        self.feature_engineer = FeatureEngineer(feature_config)

        # Create home and away score models
        self.home_model, self.away_model = self._create_models(random_state)

        # Update model info
        self.model_info["parameters"] = {
            "random_state": random_state,
            "feature_config": feature_config
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

        # Extract features and labels using the feature engineer
        X, y_home, y_away = self.feature_engineer.extract_features(
            player_stats, matches, for_score_prediction=True
        )

        if len(X) == 0:
            logger.error("No valid features extracted from matches")
            raise ValueError("No valid features extracted from matches")

        logger.info(f"Extracted {len(X)} samples with {X.shape[1]} features")

        # Split data into training and testing sets
        X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
            X, y_home, y_away, test_size=test_size, random_state=self.random_state
        )

        # Feature selection for home model
        logger.info("Performing feature selection for home model")
        home_selector = SelectFromModel(
            XGBRegressor(n_estimators=100, random_state=self.random_state),
            threshold="median"
        )
        X_train_home = home_selector.fit_transform(X_train, y_home_train)
        X_test_home = home_selector.transform(X_test)

        # Feature selection for away model
        logger.info("Performing feature selection for away model")
        away_selector = SelectFromModel(
            XGBRegressor(n_estimators=100, random_state=self.random_state),
            threshold="median"
        )
        X_train_away = away_selector.fit_transform(X_train, y_away_train)
        X_test_away = away_selector.transform(X_test)

        # Train home score model
        logger.info(f"Training home score model with {len(X_train_home)} samples")
        self.home_model.fit(X_train_home, y_home_train)

        # Train away score model
        logger.info(f"Training away score model with {len(X_train_away)} samples")
        self.away_model.fit(X_train_away, y_away_train)

        # Evaluate models
        logger.info("Evaluating models")
        metrics = self._evaluate_models(
            X_test_home, X_test_away, y_home_test, y_away_test
        )

        # Store feature selectors
        self.home_selector = home_selector
        self.away_selector = away_selector

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
        self.model_info["num_features"] = {
            "original": X.shape[1],
            "home_selected": X_train_home.shape[1],
            "away_selected": X_train_away.shape[1]
        }

        logger.info(f"Models trained with total score MAE: {metrics['total_score_mae']:.4f}")
        return self

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
        # Extract features and labels using the feature engineer
        X, y_home, y_away = self.feature_engineer.extract_features(
            player_stats, matches, for_score_prediction=True
        )

        if len(X) == 0:
            logger.error("No valid features extracted from matches")
            raise ValueError("No valid features extracted from matches")

        # Apply feature selection
        X_home = self.home_selector.transform(X)
        X_away = self.away_selector.transform(X)

        # Evaluate models
        return self._evaluate_models(X_home, X_away, y_home, y_away)

    @log_exceptions(logger)
    def _evaluate_models(self, X_test_home, X_test_away, y_home_test, y_away_test):
        """
        Evaluate the models on test data.

        Args:
            X_test_home (numpy.ndarray): Test features for home model
            X_test_away (numpy.ndarray): Test features for away model
            y_home_test (numpy.ndarray): Test home scores
            y_away_test (numpy.ndarray): Test away scores

        Returns:
            dict: Evaluation metrics
        """
        # Make predictions
        y_home_pred = self.home_model.predict(X_test_home)
        y_away_pred = self.away_model.predict(X_test_away)

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

        # Create a single-match list for feature extraction
        match_list = [match]

        # Extract features using the feature engineer
        try:
            X, _, _ = self.feature_engineer.extract_features(
                player_stats, match_list, for_score_prediction=True
            )

            if len(X) == 0:
                raise ValueError("No features extracted")

            # Apply feature selection
            X_home = self.home_selector.transform(X)
            X_away = self.away_selector.transform(X)

            # Make prediction
            home_score = self.home_model.predict(X_home)[0]
            away_score = self.away_model.predict(X_away)[0]

        except Exception as e:
            logger.error(f"Error predicting score: {str(e)}")
            # Fallback to a simpler prediction method
            home_player = player_stats[home_player_id]
            away_player = player_stats[away_player_id]

            # Use average scores as fallback
            home_score = home_player.get('avg_score', 60)
            away_score = away_player.get('avg_score', 60)

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
