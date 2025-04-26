"""
Match history fetcher for the H2H GG League API.
"""

import json
import requests
import time
from pathlib import Path

from config.settings import H2H_BASE_URL, H2H_DEFAULT_TOURNAMENT_ID, MATCH_HISTORY_FILE, MATCH_HISTORY_DAYS
from config.logging_config import get_data_fetcher_logger
from utils.time import format_api_date_range
from utils.logging import log_execution_time, log_exceptions
from utils.validation import validate_match_data
from core.data.fetchers import TokenFetcher

logger = get_data_fetcher_logger()


class MatchHistoryFetcher:
    """
    Fetches match history data from the H2H GG League API.
    """

    def __init__(self, base_url=H2H_BASE_URL, tournament_id=H2H_DEFAULT_TOURNAMENT_ID,
                 output_file=MATCH_HISTORY_FILE, days_back=MATCH_HISTORY_DAYS):
        """
        Initialize the MatchHistoryFetcher.

        Args:
            base_url (str): Base URL for the API
            tournament_id (int): Tournament ID
            output_file (str or Path): Output file path
            days_back (int): Number of days of history to fetch
        """
        self.base_url = base_url
        self.tournament_id = tournament_id
        self.output_file = Path(output_file)
        self.days_back = days_back
        self.token_fetcher = TokenFetcher()

    @log_execution_time(logger)
    @log_exceptions(logger)
    def fetch_match_history(self, save_to_file=True):
        """
        Fetch match history data.

        Args:
            save_to_file (bool): Whether to save the data to a file

        Returns:
            list: List of match data dictionaries
        """
        logger.info(f"Fetching match history for the past {self.days_back} days")

        # Get date range for API request
        from_date, to_date = format_api_date_range(self.days_back)

        # Get authentication headers
        headers = self.token_fetcher.get_auth_headers()

        # Prepare request parameters
        params = {
            'schedule-type': 'match',
            'from': from_date,
            'to': to_date,
            'order': 'desc',
            'tournament-id': self.tournament_id
        }

        # Make API request
        url = f"{self.base_url}/schedule"
        logger.debug(f"Making API request to {url} with params: {params}")

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Log the API response for debugging
            logger.info(f"API response: {json.dumps(data)[:1000]}...")

            # Validate and transform match data
            matches = []
            for match in data:
                if validate_match_data(match):
                    # Transform the match data to our expected format
                    transformed_match = {
                        'id': match.get('fixtureId', match.get('id')),
                        'homePlayer': {
                            'id': match.get('homeParticipantId'),
                            'name': match.get('homeParticipantName')
                        },
                        'awayPlayer': {
                            'id': match.get('awayParticipantId'),
                            'name': match.get('awayParticipantName')
                        },
                        'homeTeam': {
                            'id': match.get('homeTeamId'),
                            'name': match.get('homeTeamName')
                        },
                        'awayTeam': {
                            'id': match.get('awayTeamId'),
                            'name': match.get('awayTeamName')
                        },
                        'fixtureStart': match.get('fixtureStart'),
                        'homeScore': match.get('homeScore'),
                        'awayScore': match.get('awayScore'),
                        'result': match.get('result')
                    }
                    matches.append(transformed_match)
                else:
                    logger.warning(f"Skipping invalid match data: {match.get('id', match.get('fixtureId', 'unknown'))}")

            logger.info(f"Successfully fetched {len(matches)} matches")

            # Save to file if requested
            if save_to_file:
                self._save_to_file(matches)

            return matches

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching match history: {str(e)}")
            raise

    @log_exceptions(logger)
    def _save_to_file(self, matches):
        """
        Save match data to a file.

        Args:
            matches (list): List of match data dictionaries
        """
        logger.info(f"Saving {len(matches)} matches to {self.output_file}")

        # Create directory if it doesn't exist
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2)

        logger.info(f"Successfully saved match history to {self.output_file}")

    @log_exceptions(logger)
    def load_from_file(self):
        """
        Load match data from a file.

        Returns:
            list: List of match data dictionaries
        """
        logger.info(f"Loading match history from {self.output_file}")

        if not self.output_file.exists():
            logger.warning(f"Match history file {self.output_file} does not exist")
            return []

        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                matches = json.load(f)

            logger.info(f"Successfully loaded {len(matches)} matches from {self.output_file}")
            return matches

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error loading match history from file: {str(e)}")
            return []
