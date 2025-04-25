"""
Refresh service for updating predictions.
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

from config.settings import (
    MATCH_HISTORY_FILE, PLAYER_STATS_FILE, UPCOMING_MATCHES_FILE,
    PREDICTIONS_FILE, PREDICTION_HISTORY_FILE, MATCH_HISTORY_DAYS,
    UPCOMING_MATCHES_DAYS
)
from config.logging_config import get_prediction_refresh_logger
from utils.logging import log_execution_time, log_exceptions
from utils.time import get_current_time, format_datetime
from core.data.fetchers.token import TokenFetcher
from core.data.fetchers.match_history import MatchHistoryFetcher
from core.data.fetchers.upcoming_matches import UpcomingMatchesFetcher
from core.data.processors.player_stats import PlayerStatsProcessor
from core.models.registry import ModelRegistry, ScoreModelRegistry
from core.models.winner_prediction import WinnerPredictionModel
from core.models.score_prediction import ScorePredictionModel

logger = get_prediction_refresh_logger()


class RefreshService:
    """
    Service for refreshing data and predictions.
    """

    def __init__(self):
        """
        Initialize the refresh service.
        """
        self.token_fetcher = TokenFetcher()
        self.match_history_fetcher = MatchHistoryFetcher(days_back=MATCH_HISTORY_DAYS)
        self.upcoming_matches_fetcher = UpcomingMatchesFetcher(days_forward=UPCOMING_MATCHES_DAYS)
        self.player_stats_processor = PlayerStatsProcessor()
        self.winner_model_registry = ModelRegistry()
        self.score_model_registry = ScoreModelRegistry()

    @log_execution_time(logger)
    @log_exceptions(logger)
    def refresh_data(self):
        """
        Refresh all data (match history, upcoming matches, player stats).

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting data refresh")

        try:
            # Get authentication token
            token = self.token_fetcher.get_token()
            if not token:
                logger.error("Failed to retrieve authentication token")
                return False

            # Fetch match history
            logger.info("Fetching match history")
            matches = self.match_history_fetcher.fetch_match_history()
            if not matches:
                logger.error("Failed to fetch match history")
                return False

            # Calculate player statistics
            logger.info("Calculating player statistics")
            player_stats = self.player_stats_processor.calculate_player_stats(matches)
            if not player_stats:
                logger.error("Failed to calculate player statistics")
                return False

            # Fetch upcoming matches
            logger.info("Fetching upcoming matches")
            upcoming_matches = self.upcoming_matches_fetcher.fetch_upcoming_matches()
            if not upcoming_matches:
                logger.error("Failed to fetch upcoming matches")
                return False

            logger.info("Data refresh completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error during data refresh: {str(e)}")
            return False

    @log_execution_time(logger)
    @log_exceptions(logger)
    def refresh_predictions(self):
        """
        Refresh predictions for upcoming matches.

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting prediction refresh")

        try:
            # Load player statistics
            player_stats = self.player_stats_processor.load_from_file()
            if not player_stats:
                logger.error("Failed to load player statistics")
                return False

            # Load upcoming matches
            upcoming_matches = self.upcoming_matches_fetcher.load_from_file()
            if not upcoming_matches:
                logger.error("Failed to load upcoming matches")
                return False

            # Get all winner prediction models
            winner_models = self.winner_model_registry.list_models()
            if not winner_models:
                logger.error("No winner prediction models available")
                return False

            # Use the most recently trained model
            winner_models.sort(key=lambda x: x.get("model_id", 0), reverse=True)
            winner_model_info = winner_models[0]
            logger.info(f"Using winner prediction model {winner_model_info.get('model_id')}")

            # Load winner prediction model
            winner_model = WinnerPredictionModel.load(
                winner_model_info.get("model_path"),
                winner_model_info.get("info_path")
            )

            # Get all score prediction models
            score_models = self.score_model_registry.list_models()
            if not score_models:
                logger.error("No score prediction models available")
                return False

            # Use the most recently trained model
            score_models.sort(key=lambda x: x.get("model_id", 0), reverse=True)
            score_model_info = score_models[0]
            logger.info(f"Using score prediction model {score_model_info.get('model_id')}")

            # Load score prediction model
            score_model = ScorePredictionModel.load(
                score_model_info.get("model_path"),
                score_model_info.get("info_path")
            )

            # Generate predictions
            logger.info(f"Generating predictions for {len(upcoming_matches)} upcoming matches")
            predictions = []

            for match in upcoming_matches:
                # Generate winner prediction
                winner_prediction = winner_model.predict(player_stats, match)

                # Generate score prediction
                score_prediction = score_model.predict(player_stats, match)

                # Create prediction object
                prediction = {
                    "fixtureId": match.get("id"),
                    "homePlayer": match.get("homePlayer"),
                    "awayPlayer": match.get("awayPlayer"),
                    "homeTeam": match.get("homeTeam"),
                    "awayTeam": match.get("awayTeam"),
                    "fixtureStart": match.get("fixtureStart"),
                    "prediction": winner_prediction,
                    "score_prediction": score_prediction,
                    "generated_at": format_datetime(get_current_time())
                }

                predictions.append(prediction)

            # Save predictions
            logger.info(f"Saving {len(predictions)} predictions")
            with open(PREDICTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(predictions, f, indent=2)

            # Update prediction history
            self._update_prediction_history(predictions)

            logger.info("Prediction refresh completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error during prediction refresh: {str(e)}")
            return False

    @log_exceptions(logger)
    def _update_prediction_history(self, predictions):
        """
        Update prediction history with new predictions.

        Args:
            predictions (list): List of prediction dictionaries
        """
        logger.info("Updating prediction history")

        # Load existing prediction history
        history = []
        if Path(PREDICTION_HISTORY_FILE).exists():
            try:
                with open(PREDICTION_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Error loading prediction history: {str(e)}")

        # Add timestamp to predictions
        timestamped_predictions = []
        for prediction in predictions:
            prediction_copy = prediction.copy()
            prediction_copy["saved_at"] = format_datetime(get_current_time())
            timestamped_predictions.append(prediction_copy)

        # Append new predictions to history
        history.extend(timestamped_predictions)

        # Save updated history
        with open(PREDICTION_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)

        logger.info(f"Prediction history updated with {len(timestamped_predictions)} new predictions")


@log_execution_time(logger)
@log_exceptions(logger)
def refresh_predictions():
    """
    Refresh data and predictions.

    Returns:
        bool: True if successful, False otherwise
    """
    service = RefreshService()

    # Refresh data from H2H GG League API
    if not service.refresh_data():
        logger.error("Data refresh failed")
        return False

    # Refresh predictions
    if not service.refresh_predictions():
        logger.error("Prediction refresh failed")
        return False

    return True
