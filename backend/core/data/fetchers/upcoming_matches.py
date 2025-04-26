"""
Upcoming matches fetcher for the H2H GG League API.
"""

import json
import requests
import datetime
from pathlib import Path

from config.settings import H2H_BASE_URL, H2H_DEFAULT_TOURNAMENT_ID, UPCOMING_MATCHES_FILE, UPCOMING_MATCHES_DAYS, API_DATE_FORMAT
from config.logging_config import get_data_fetcher_logger
from utils.time import format_datetime, get_current_time
from utils.logging import log_execution_time, log_exceptions
from utils.validation import validate_match_data
from core.data.fetchers import TokenFetcher

logger = get_data_fetcher_logger()


class UpcomingMatchesFetcher:
    """
    Fetches upcoming matches data from the H2H GG League API.
    """

    def __init__(self, base_url=H2H_BASE_URL, tournament_id=H2H_DEFAULT_TOURNAMENT_ID,
                 output_file=UPCOMING_MATCHES_FILE, days_forward=UPCOMING_MATCHES_DAYS):
        """
        Initialize the UpcomingMatchesFetcher.

        Args:
            base_url (str): Base URL for the API
            tournament_id (int): Tournament ID
            output_file (str or Path): Output file path
            days_forward (int): Number of days to look ahead
        """
        self.base_url = base_url
        self.tournament_id = tournament_id
        self.output_file = Path(output_file)
        self.days_forward = days_forward
        self.token_fetcher = TokenFetcher()

    @log_execution_time(logger)
    @log_exceptions(logger)
    def fetch_upcoming_matches(self, save_to_file=True):
        """
        Fetch upcoming matches data.

        Args:
            save_to_file (bool): Whether to save the data to a file

        Returns:
            list: List of upcoming match data dictionaries
        """
        logger.info("Fetching upcoming matches for the next 24 hours")

        # Get current date and time
        now = get_current_time()

        # Set the from_date to current time
        from_date_dt = now

        # Set the to_date to current time + 24 hours (regardless of days_forward setting)
        to_date_dt = from_date_dt + datetime.timedelta(hours=24)

        # Format the dates for the API request
        from_date = format_datetime(from_date_dt, API_DATE_FORMAT)
        to_date = format_datetime(to_date_dt, API_DATE_FORMAT)

        logger.info(f"Using date range format: from {from_date} (now) to {to_date} (24 hours from now)")

        # Get authentication headers
        headers = self.token_fetcher.get_auth_headers()

        # Prepare request parameters
        params = {
            'schedule-type': 'fixture',  # Changed from 'match' to 'fixture' to match the official website
            'from': from_date,
            'to': to_date,
            'order': 'asc',
            'tournament-id': self.tournament_id,
            # Add limit parameter to get more matches
            'limit': 100
        }

        logger.info(f"Using date range: from {from_date} to {to_date}")

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
            logger.info(f"Total matches in API response: {len(data)}")

            # Validate and transform match data
            matches = []
            for match in data:
                if validate_match_data(match):
                    # Transform the match data to our expected format
                    # Log the raw match data for debugging
                    logger.info(f"Raw match data: {json.dumps(match)[:1000]}...")

                    # Extract all possible player and team name fields
                    home_player_name = match.get('homeParticipantName', match.get('homePlayerName', match.get('homeName', '')))
                    away_player_name = match.get('awayParticipantName', match.get('awayPlayerName', match.get('awayName', '')))
                    home_team_name = match.get('homeTeamName', home_player_name)
                    away_team_name = match.get('awayTeamName', away_player_name)

                    transformed_match = {
                        'id': match.get('fixtureId', match.get('id')),
                        'homePlayer': {
                            'id': match.get('homeParticipantId', match.get('homePlayerId', '')),
                            'name': home_player_name
                        },
                        'awayPlayer': {
                            'id': match.get('awayParticipantId', match.get('awayPlayerId', '')),
                            'name': away_player_name
                        },
                        'homeTeam': {
                            'id': match.get('homeTeamId', ''),
                            'name': home_team_name
                        },
                        'awayTeam': {
                            'id': match.get('awayTeamId', ''),
                            'name': away_team_name
                        },
                        'fixtureStart': match.get('fixtureStart'),
                        'raw_data': match  # Store the raw data for debugging
                    }
                    matches.append(transformed_match)
                else:
                    logger.warning(f"Skipping invalid match data: {match.get('id', match.get('fixtureId', 'unknown'))}")

            logger.info(f"Successfully fetched {len(matches)} upcoming matches")

            # Save to file if requested
            if save_to_file:
                self._save_to_file(matches)

            return matches

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching upcoming matches: {str(e)}")
            raise

    @log_exceptions(logger)
    def _save_to_file(self, matches):
        """
        Save match data to a file.

        Args:
            matches (list): List of match data dictionaries
        """
        logger.info(f"Saving {len(matches)} upcoming matches to {self.output_file}")

        # Create directory if it doesn't exist
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2)

        logger.info(f"Successfully saved upcoming matches to {self.output_file}")

    @log_exceptions(logger)
    def load_from_file(self):
        """
        Load match data from a file.

        Returns:
            list: List of match data dictionaries
        """
        logger.info(f"Loading upcoming matches from {self.output_file}")

        if not self.output_file.exists():
            logger.warning(f"Upcoming matches file {self.output_file} does not exist")
            return []

        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                matches = json.load(f)

            logger.info(f"Successfully loaded {len(matches)} upcoming matches from {self.output_file}")
            return matches

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error loading upcoming matches from file: {str(e)}")
            return []
