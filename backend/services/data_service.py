"""
Data service for managing data operations.
"""

from config.settings import MATCH_HISTORY_DAYS, UPCOMING_MATCHES_DAYS
from config.logging_config import get_data_fetcher_logger
from utils.logging import log_execution_time, log_exceptions
from core.data.fetchers import TokenFetcher
from core.data.fetchers.match_history import MatchHistoryFetcher
from core.data.fetchers.upcoming_matches import UpcomingMatchesFetcher
from core.data.processors.player_stats import PlayerStatsProcessor

logger = get_data_fetcher_logger()


class DataService:
    """
    Service for managing data operations.
    """

    def __init__(self):
        """
        Initialize the data service.
        """
        self.token_fetcher = TokenFetcher()
        self.match_history_fetcher = MatchHistoryFetcher(days_back=MATCH_HISTORY_DAYS)
        self.upcoming_matches_fetcher = UpcomingMatchesFetcher(days_forward=UPCOMING_MATCHES_DAYS)
        self.player_stats_processor = PlayerStatsProcessor()

    @log_execution_time(logger)
    @log_exceptions(logger)
    def fetch_token(self, force_refresh=False):
        """
        Fetch authentication token.

        Args:
            force_refresh (bool): Whether to force a token refresh

        Returns:
            str: Authentication token or None if failed
        """
        logger.info("Fetching authentication token")

        try:
            token = self.token_fetcher.get_token(force_refresh=force_refresh)
            if not token:
                logger.error("Failed to retrieve authentication token")
                return None

            logger.info("Successfully fetched authentication token")
            return token

        except Exception as e:
            logger.error(f"Error fetching authentication token: {str(e)}")
            return None

    @log_execution_time(logger)
    @log_exceptions(logger)
    def fetch_match_history(self, days_back=None):
        """
        Fetch match history data.

        Args:
            days_back (int): Number of days of history to fetch

        Returns:
            list: List of match data dictionaries or None if failed
        """
        logger.info(f"Fetching match history for the past {days_back or MATCH_HISTORY_DAYS} days")

        try:
            # Update days_back if provided
            if days_back is not None:
                self.match_history_fetcher.days_back = days_back

            # Fetch match history
            matches = self.match_history_fetcher.fetch_match_history()
            if not matches:
                logger.error("Failed to fetch match history")
                return None

            logger.info(f"Successfully fetched {len(matches)} matches")
            return matches

        except Exception as e:
            logger.error(f"Error fetching match history: {str(e)}")
            return None

    @log_execution_time(logger)
    @log_exceptions(logger)
    def fetch_upcoming_matches(self, days_forward=None):
        """
        Fetch upcoming matches data.

        Args:
            days_forward (int): Number of days to look ahead

        Returns:
            list: List of upcoming match data dictionaries or None if failed
        """
        logger.info(f"Fetching upcoming matches for the next {days_forward or UPCOMING_MATCHES_DAYS} days")

        try:
            # Update days_forward if provided
            if days_forward is not None:
                self.upcoming_matches_fetcher.days_forward = days_forward

            # Fetch upcoming matches
            matches = self.upcoming_matches_fetcher.fetch_upcoming_matches()
            if not matches:
                logger.error("Failed to fetch upcoming matches")
                return None

            logger.info(f"Successfully fetched {len(matches)} upcoming matches")
            return matches

        except Exception as e:
            logger.error(f"Error fetching upcoming matches: {str(e)}")
            return None

    @log_execution_time(logger)
    @log_exceptions(logger)
    def calculate_player_stats(self, matches=None):
        """
        Calculate player statistics.

        Args:
            matches (list): List of match data dictionaries

        Returns:
            dict: Dictionary of player statistics or None if failed
        """
        logger.info("Calculating player statistics")

        try:
            # Load match history if not provided
            if matches is None:
                matches = self.match_history_fetcher.load_from_file()
                if not matches:
                    logger.error("Failed to load match history")
                    return None

            # Calculate player statistics
            player_stats = self.player_stats_processor.calculate_player_stats(matches)
            if not player_stats:
                logger.error("Failed to calculate player statistics")
                return None

            logger.info(f"Successfully calculated statistics for {len(player_stats)} players")
            return player_stats

        except Exception as e:
            logger.error(f"Error calculating player statistics: {str(e)}")
            return None

    @log_execution_time(logger)
    @log_exceptions(logger)
    def get_player_stats(self):
        """
        Get player statistics from file.

        Returns:
            dict: Dictionary of player statistics or None if failed
        """
        logger.info("Getting player statistics")

        try:
            # Load player statistics
            player_stats = self.player_stats_processor.load_from_file()
            if not player_stats:
                logger.error("Failed to load player statistics")
                return None

            logger.info(f"Successfully loaded statistics for {len(player_stats)} players")
            return player_stats

        except Exception as e:
            logger.error(f"Error getting player statistics: {str(e)}")
            return None

    @log_execution_time(logger)
    @log_exceptions(logger)
    def get_match_history(self):
        """
        Get match history from file.

        Returns:
            list: List of match data dictionaries or None if failed
        """
        logger.info("Getting match history")

        try:
            # Load match history
            matches = self.match_history_fetcher.load_from_file()
            if not matches:
                logger.error("Failed to load match history")
                return None

            logger.info(f"Successfully loaded {len(matches)} matches")
            return matches

        except Exception as e:
            logger.error(f"Error getting match history: {str(e)}")
            return None

    @log_execution_time(logger)
    @log_exceptions(logger)
    def get_upcoming_matches(self):
        """
        Get upcoming matches from file.

        Returns:
            list: List of upcoming match data dictionaries or None if failed
        """
        logger.info("Getting upcoming matches")

        try:
            # Load upcoming matches
            matches = self.upcoming_matches_fetcher.load_from_file()
            if not matches:
                logger.error("Failed to load upcoming matches")
                return None

            logger.info(f"Successfully loaded {len(matches)} upcoming matches")
            return matches

        except Exception as e:
            logger.error(f"Error getting upcoming matches: {str(e)}")
            return None
