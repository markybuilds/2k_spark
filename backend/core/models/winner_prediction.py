"""
Winner prediction model for NBA 2K25 eSports matches.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.feature_selection import SelectFromModel
from xgboost import XGBClassifier

from config.settings import DEFAULT_RANDOM_STATE
from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions
from core.models.base import BaseModel
from core.models.feature_engineering import FeatureEngineer

logger = get_model_tuning_logger()


class WinnerPredictionModel(BaseModel):
    """
    Model for predicting match winners.
    """

    def __init__(self, model_id=None, random_state=DEFAULT_RANDOM_STATE, n_estimators=100, max_depth=10, feature_config=None):
        """
        Initialize the winner prediction model.

        Args:
            model_id (str): Model ID
            random_state (int): Random state for reproducibility
            n_estimators (int): Number of trees in the forest
            max_depth (int): Maximum depth of the trees
            feature_config (dict): Feature configuration dictionary
        """
        super().__init__(model_id, random_state)
        self.n_estimators = n_estimators
        self.max_depth = max_depth

        # Create feature engineer
        self.feature_engineer = FeatureEngineer(feature_config)

        # Update model info
        self.model_info["parameters"] = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": random_state,
            "feature_config": feature_config
        }

        # Initialize model
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight='balanced',
            random_state=random_state
        )

        # Initialize feature selector
        self.feature_selector = None

    @log_execution_time(logger)
    @log_exceptions(logger)
    def train(self, player_stats, matches, test_size=0.2, min_samples=100, cv_folds=5):
        """
        Train the model on match data.

        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            test_size (float): Proportion of data to use for testing
            min_samples (int): Minimum number of samples required for training
            cv_folds (int): Number of cross-validation folds

        Returns:
            self: The trained model
        """
        logger.info(f"Training winner prediction model with {len(matches)} matches")

        # Extract features and labels using the feature engineer
        X, y = self.feature_engineer.extract_features(
            player_stats, matches, for_score_prediction=False
        )

        if len(X) == 0:
            logger.error("No valid features extracted from matches")
            raise ValueError("No valid features extracted from matches")

        # Check if we have enough samples
        if len(X) < min_samples:
            logger.error(f"Insufficient samples for training: {len(X)} < {min_samples}")
            raise ValueError(f"Insufficient samples for training: {len(X)} < {min_samples}")

        logger.info(f"Extracted {len(X)} samples with {X.shape[1]} features")

        # Feature selection
        logger.info("Performing feature selection")
        self.feature_selector = SelectFromModel(
            XGBClassifier(n_estimators=100, random_state=self.random_state),
            threshold="median"
        )
        X_selected = self.feature_selector.fit_transform(X, y)

        # Perform cross-validation
        logger.info(f"Performing {cv_folds}-fold cross-validation")
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(self.model, X_selected, y, cv=cv, scoring='accuracy')

        logger.info(f"Cross-validation scores: {cv_scores}")
        logger.info(f"Mean CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X_selected, y, test_size=test_size, random_state=self.random_state, stratify=y
        )

        # Train model with selected features
        logger.info(f"Training model with {len(X_train)} samples and {X_selected.shape[1]} selected features")
        self.model.fit(X_train, y_train)

        # Evaluate model
        logger.info("Evaluating model")
        metrics = self._evaluate_model(X_test, y_test)

        # Add cross-validation results to metrics
        metrics["cv_scores"] = cv_scores.tolist()
        metrics["cv_mean_accuracy"] = float(cv_scores.mean())
        metrics["cv_std_accuracy"] = float(cv_scores.std())

        # Update model info
        self.model_info["metrics"] = metrics
        self.model_info["accuracy"] = metrics["accuracy"]
        self.model_info["cv_accuracy"] = metrics["cv_mean_accuracy"]
        self.model_info["data_files"] = {
            "player_stats": "player_stats.json",
            "match_history": "match_history.json"
        }
        self.model_info["num_samples"] = len(X)
        self.model_info["num_features"] = {
            "original": X.shape[1],
            "selected": X_selected.shape[1]
        }
        self.model_info["validation_method"] = f"{cv_folds}-fold cross-validation"

        logger.info(f"Model trained with accuracy: {metrics['accuracy']:.4f}")
        return self



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
                "confidence": 0.5,
                "prediction_method": "fallback_random"
            }

        # Create a single-match list for feature extraction
        match_list = [match]

        # Extract features using the feature engineer
        try:
            X, _ = self.feature_engineer.extract_features(
                player_stats, match_list, for_score_prediction=False
            )

            if len(X) == 0:
                raise ValueError("No features extracted")

            # Apply feature selection if available
            if self.feature_selector is not None:
                X_selected = self.feature_selector.transform(X)
                prediction_method = "model_with_feature_selection"
            else:
                logger.warning("Feature selector not available, using raw features")
                X_selected = X
                prediction_method = "model_without_feature_selection"

            # Make prediction
            probabilities = self.model.predict_proba(X_selected)[0]

        except Exception as e:
            logger.error(f"Error predicting winner: {str(e)}")
            # Fallback to a simpler prediction method
            home_player = player_stats[home_player_id]
            away_player = player_stats[away_player_id]

            # Use win rates as fallback
            home_win_rate = home_player.get('win_rate', 0.5)
            away_win_rate = away_player.get('win_rate', 0.5)

            # Normalize win rates to probabilities
            total = home_win_rate + away_win_rate
            if total > 0:
                home_prob = home_win_rate / total
                away_prob = away_win_rate / total
            else:
                home_prob = 0.5
                away_prob = 0.5

            probabilities = [away_prob, home_prob]
            prediction_method = "fallback_win_rates"

        home_win_probability = probabilities[1]
        away_win_probability = probabilities[0]

        predicted_winner = "home" if home_win_probability > away_win_probability else "away"
        confidence = max(home_win_probability, away_win_probability)

        return {
            "home_win_probability": float(home_win_probability),
            "away_win_probability": float(away_win_probability),
            "predicted_winner": predicted_winner,
            "confidence": float(confidence),
            "prediction_method": prediction_method
        }

    @log_exceptions(logger)
    def evaluate(self, player_stats, matches, min_samples=100, cv_folds=5):
        """
        Evaluate the model on match data.

        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            min_samples (int): Minimum number of samples required for evaluation
            cv_folds (int): Number of cross-validation folds

        Returns:
            dict: Evaluation metrics
        """
        # Extract features and labels using the feature engineer
        X, y = self.feature_engineer.extract_features(
            player_stats, matches, for_score_prediction=False
        )

        if len(X) == 0:
            logger.error("No valid features extracted from matches")
            raise ValueError("No valid features extracted from matches")

        # Check if we have enough samples
        if len(X) < min_samples:
            logger.warning(f"Insufficient samples for reliable evaluation: {len(X)} < {min_samples}")
            logger.warning("Evaluation results may not be statistically significant")

        # Apply feature selection if available
        if self.feature_selector is not None:
            X_selected = self.feature_selector.transform(X)
        else:
            logger.warning("Feature selector not available, using raw features")
            X_selected = X

        # Perform cross-validation if we have enough samples
        if len(X) >= cv_folds * 2:  # Ensure at least 2 samples per fold
            logger.info(f"Performing {cv_folds}-fold cross-validation")
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
            cv_scores = cross_val_score(self.model, X_selected, y, cv=cv, scoring='accuracy')

            logger.info(f"Cross-validation scores: {cv_scores}")
            logger.info(f"Mean CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

            # Get standard metrics
            metrics = self._evaluate_model(X_selected, y)

            # Add cross-validation results
            metrics["cv_scores"] = cv_scores.tolist()
            metrics["cv_mean_accuracy"] = float(cv_scores.mean())
            metrics["cv_std_accuracy"] = float(cv_scores.std())
            metrics["validation_method"] = f"{cv_folds}-fold cross-validation"

            return metrics
        else:
            logger.warning(f"Insufficient samples for {cv_folds}-fold cross-validation, using standard evaluation")
            return self._evaluate_model(X_selected, y)
