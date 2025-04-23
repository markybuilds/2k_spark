"""
Module for fetching and processing match data from h2hggl.com.
"""
import logging
import requests
import pytz
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from src.config import DEFAULT_TIMEZONE

from src.auth import get_bearer_token, AuthenticationError

logger = logging.getLogger(__name__)


class MatchDataError(Exception):
    """Exception raised for errors in the match data module."""
    pass


def parse_utc_datetime(date_str: str) -> Union[datetime, None]:
    """
    Parse a UTC datetime string into a datetime object.

    Args:
        date_str: UTC datetime string in format 'YYYY-MM-DDThh:mm:ssZ'

    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None

    try:
        # Parse the UTC datetime string
        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        # Make it timezone-aware (UTC)
        dt = pytz.utc.localize(dt)
        return dt
    except ValueError as e:
        logger.warning(f"Failed to parse datetime string '{date_str}': {e}")
        return None


def convert_to_local_time(dt: datetime) -> datetime:
    """
    Convert a UTC datetime to local time.

    Args:
        dt: UTC datetime object (timezone-aware)

    Returns:
        Local datetime object
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        # If datetime is naive, assume it's UTC
        dt = pytz.utc.localize(dt)

    # Get the local timezone from config
    local_tz = pytz.timezone(DEFAULT_TIMEZONE)

    # Convert to local time
    local_dt = dt.astimezone(local_tz)
    return local_dt


def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M', use_12h: bool = False) -> str:
    """
    Format a datetime object as a string.

    Args:
        dt: datetime object
        format_str: format string (default: '%Y-%m-%d %H:%M')
        use_12h: If True, use 12-hour format with AM/PM

    Returns:
        Formatted datetime string
    """
    if dt is None:
        return 'Unknown'

    try:
        if use_12h:
            # Use 12-hour format with AM/PM
            if format_str == '%Y-%m-%d %H:%M':
                # Default format, convert to 12-hour with AM/PM
                return dt.strftime('%Y-%m-%d %I:%M %p')
            else:
                # Custom format, use as is
                return dt.strftime(format_str)
        else:
            # Use the specified format
            return dt.strftime(format_str)
    except Exception as e:
        logger.warning(f"Failed to format datetime: {e}")
        return 'Unknown'


def format_date_for_display(dt: datetime) -> str:
    """
    Format a date for display in the official schedule format.

    Args:
        dt: datetime object

    Returns:
        Formatted date string (e.g., 'Wed, Apr 23, 2025')
    """
    if dt is None:
        return 'Unknown'

    try:
        return dt.strftime('%a, %b %d, %Y')
    except Exception as e:
        logger.warning(f"Failed to format date for display: {e}")
        return 'Unknown'


def format_time_for_display(dt: datetime, use_12h: bool = True) -> str:
    """
    Format a time for display in the official schedule format.

    Args:
        dt: datetime object
        use_12h: If True, use 12-hour format with AM/PM

    Returns:
        Formatted time string (e.g., '06:11 AM' or '06:11')
    """
    if dt is None:
        return 'Unknown'

    try:
        if use_12h:
            return dt.strftime('%I:%M %p')  # 12-hour format with AM/PM
        else:
            return dt.strftime('%H:%M')  # 24-hour format
    except Exception as e:
        logger.warning(f"Failed to format time for display: {e}")
        return 'Unknown'


def fetch_matches(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    tournament_id: int = 1,
    schedule_type: str = "match",
    force_refresh_token: bool = False,
    include_time: bool = False,
    order_asc: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch match data from h2hggl.com.

    Args:
        from_date: Start date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' if include_time=True (default: 30 days ago)
        to_date: End date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' if include_time=True (default: today)
        tournament_id: The tournament ID to fetch matches for (default: 1)
        schedule_type: Type of schedule to fetch ('match' for past matches, 'fixture' for upcoming matches)
        force_refresh_token: If True, force a new token retrieval.
        include_time: If True, include time in the date parameters and use 'from'/'to' instead of 'from-date'/'to-date'
        order_asc: If True, order results in ascending order by start time (useful for upcoming matches)

    Returns:
        List of match data dictionaries.

    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    try:
        # Set default dates if not provided
        now = datetime.now()
        if from_date is None:
            if include_time:
                from_date = now.strftime('%Y-%m-%d %H:%M')
            else:
                from_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')

        if to_date is None:
            if include_time:
                to_date = (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
            else:
                to_date = now.strftime('%Y-%m-%d')

        # Get authentication token
        token = get_bearer_token(force_refresh=force_refresh_token)

        # API endpoint
        url = 'https://api-sis-stats.hudstats.com/v1/schedule'

        # Query parameters
        params = {
            'schedule-type': schedule_type,
            'tournament-id': tournament_id
        }

        # Add date parameters based on whether time is included
        if include_time:
            params['from'] = from_date
            params['to'] = to_date
        else:
            params['from-date'] = from_date
            params['to-date'] = to_date

        # Add order parameter if specified
        if order_asc:
            params['order'] = 'asc'

        # Headers
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': f'Bearer {token}',
            'origin': 'https://h2hggl.com',
            'referer': 'https://h2hggl.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        logger.info(f"Fetching {schedule_type} data from {from_date} to {to_date} for tournament ID {tournament_id}")
        response = requests.get(url, params=params, headers=headers)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()
        logger.info(f"Successfully retrieved {len(data)} matches")

        return data

    except AuthenticationError as e:
        logger.error(f"Authentication error while fetching match data: {e}")
        raise MatchDataError(f"Failed to authenticate: {e}") from e
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching match data: {e}")
        raise MatchDataError(f"HTTP error: {e}") from e
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error while fetching match data: {e}")
        raise MatchDataError(f"Connection error: {e}") from e
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout while fetching match data: {e}")
        raise MatchDataError(f"Timeout: {e}") from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching match data: {e}")
        raise MatchDataError(f"Request error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error while fetching match data: {e}")
        raise MatchDataError(f"Unexpected error: {e}") from e


def fetch_upcoming_matches(
    hours_ahead: int = 24,
    days_ahead: int = 0,
    tournament_id: int = 1,
    force_refresh_token: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch upcoming matches from h2hggl.com.

    Args:
        hours_ahead: Number of hours ahead to fetch matches for (default: 24)
        days_ahead: Additional number of days ahead to fetch matches for (default: 0)
        tournament_id: The tournament ID to fetch matches for (default: 1)
        force_refresh_token: If True, force a new token retrieval.

    Returns:
        List of upcoming match data dictionaries.

    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    now = datetime.now()
    from_datetime = now.strftime('%Y-%m-%d %H:%M')
    to_datetime = (now + timedelta(days=days_ahead, hours=hours_ahead)).strftime('%Y-%m-%d %H:%M')

    return fetch_matches(
        from_date=from_datetime,
        to_date=to_datetime,
        tournament_id=tournament_id,
        schedule_type='fixture',
        force_refresh_token=force_refresh_token,
        include_time=True,
        order_asc=True
    )


def fetch_todays_matches(
    tournament_id: int = 1,
    force_refresh_token: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch today's matches from h2hggl.com.

    Args:
        tournament_id: The tournament ID to fetch matches for (default: 1)
        force_refresh_token: If True, force a new token retrieval.

    Returns:
        List of today's match data dictionaries.

    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999).strftime('%Y-%m-%d %H:%M')

    return fetch_matches(
        from_date=today_start,
        to_date=today_end,
        tournament_id=tournament_id,
        schedule_type='fixture',
        force_refresh_token=force_refresh_token,
        include_time=True,
        order_asc=True
    )


def fetch_player_match_history(
    player_id: int,
    days_back: int = 90,
    tournament_id: int = 1,
    force_refresh_token: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch match history for a specific player.

    Args:
        player_id: The player ID to fetch match history for
        days_back: Number of days back to fetch matches for (default: 90)
        tournament_id: The tournament ID to fetch matches for (default: 1)
        force_refresh_token: If True, force a new token retrieval.

    Returns:
        List of match data dictionaries for the player.

    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    today = datetime.now()
    from_date = (today - timedelta(days=days_back)).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    try:
        # Fetch all matches for the period
        matches = fetch_matches(
            from_date=from_date,
            to_date=to_date,
            tournament_id=tournament_id,
            schedule_type='match',
            force_refresh_token=force_refresh_token
        )

        # Filter matches for the specific player
        player_matches = [
            match for match in matches
            if match.get('homeParticipantId') == player_id or match.get('awayParticipantId') == player_id
        ]

        logger.info(f"Found {len(player_matches)} matches for player ID {player_id}")
        return player_matches

    except Exception as e:
        logger.error(f"Error fetching match history for player ID {player_id}: {e}")
        raise MatchDataError(f"Error fetching match history: {e}") from e


def get_head_to_head_matches(
    player1_id: int,
    player2_id: int,
    days_back: int = 365,
    tournament_id: int = 1,
    force_refresh_token: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch head-to-head matches between two players.

    Args:
        player1_id: The first player ID
        player2_id: The second player ID
        days_back: Number of days back to fetch matches for (default: 365)
        tournament_id: The tournament ID to fetch matches for (default: 1)
        force_refresh_token: If True, force a new token retrieval.

    Returns:
        List of head-to-head match data dictionaries.

    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    today = datetime.now()
    from_date = (today - timedelta(days=days_back)).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    try:
        # Fetch all matches for the period
        matches = fetch_matches(
            from_date=from_date,
            to_date=to_date,
            tournament_id=tournament_id,
            schedule_type='match',
            force_refresh_token=force_refresh_token
        )

        # Filter matches for head-to-head between the two players
        h2h_matches = [
            match for match in matches
            if (match.get('homeParticipantId') == player1_id and match.get('awayParticipantId') == player2_id) or
               (match.get('homeParticipantId') == player2_id and match.get('awayParticipantId') == player1_id)
        ]

        logger.info(f"Found {len(h2h_matches)} head-to-head matches between player IDs {player1_id} and {player2_id}")
        return h2h_matches

    except Exception as e:
        logger.error(f"Error fetching head-to-head matches between player IDs {player1_id} and {player2_id}: {e}")
        raise MatchDataError(f"Error fetching head-to-head matches: {e}") from e


def calculate_player_win_rate(matches: List[Dict[str, Any]], player_id: int) -> float:
    """
    Calculate the win rate for a player based on their match history.

    Args:
        matches: List of match data dictionaries
        player_id: The player ID to calculate win rate for

    Returns:
        Win rate as a percentage (0-100)
    """
    if not matches:
        return 0.0

    wins = 0
    total_matches = 0

    for match in matches:
        if match.get('homeParticipantId') == player_id:
            # Player was home
            if match.get('result') == 'home_win':
                wins += 1
            total_matches += 1
        elif match.get('awayParticipantId') == player_id:
            # Player was away
            if match.get('result') == 'away_win':
                wins += 1
            total_matches += 1

    if total_matches == 0:
        return 0.0

    return (wins / total_matches) * 100


def calculate_player_average_score(matches: List[Dict[str, Any]], player_id: int) -> float:
    """
    Calculate the average score for a player based on their match history.

    Args:
        matches: List of match data dictionaries
        player_id: The player ID to calculate average score for

    Returns:
        Average score
    """
    if not matches:
        return 0.0

    total_score = 0
    total_matches = 0

    for match in matches:
        if match.get('homeParticipantId') == player_id:
            # Player was home
            total_score += match.get('homeScore', 0)
            total_matches += 1
        elif match.get('awayParticipantId') == player_id:
            # Player was away
            total_score += match.get('awayScore', 0)
            total_matches += 1

    if total_matches == 0:
        return 0.0

    return total_score / total_matches


def get_player_form(matches: List[Dict[str, Any]], player_id: int, num_matches: int = 5) -> List[str]:
    """
    Get the recent form of a player based on their match history.

    Args:
        matches: List of match data dictionaries
        player_id: The player ID to get form for
        num_matches: Number of recent matches to consider (default: 5)

    Returns:
        List of results ('win', 'loss', 'draw')
    """
    # Filter matches for the player
    player_matches = [
        match for match in matches
        if match.get('homeParticipantId') == player_id or match.get('awayParticipantId') == player_id
    ]

    # Sort matches by date (most recent first)
    player_matches.sort(key=lambda x: x.get('startDate', ''), reverse=True)

    # Get the most recent matches
    recent_matches = player_matches[:num_matches]

    # Determine results
    form = []
    for match in recent_matches:
        if match.get('homeParticipantId') == player_id:
            # Player was home
            if match.get('result') == 'home_win':
                form.append('win')
            elif match.get('result') == 'away_win':
                form.append('loss')
            else:
                form.append('draw')
        elif match.get('awayParticipantId') == player_id:
            # Player was away
            if match.get('result') == 'away_win':
                form.append('win')
            elif match.get('result') == 'home_win':
                form.append('loss')
            else:
                form.append('draw')

    return form


def fetch_player_upcoming_matches(
    player_id: int,
    hours_ahead: int = 24,
    days_ahead: int = 0,
    tournament_id: int = 1,
    force_refresh_token: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch upcoming matches for a specific player.

    Args:
        player_id: The player ID to fetch upcoming matches for
        hours_ahead: Number of hours ahead to fetch matches for (default: 24)
        days_ahead: Additional number of days ahead to fetch matches for (default: 0)
        tournament_id: The tournament ID to fetch matches for (default: 1)
        force_refresh_token: If True, force a new token retrieval.

    Returns:
        List of upcoming match data dictionaries for the player.

    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    try:
        # Fetch all upcoming matches
        upcoming_matches = fetch_upcoming_matches(
            hours_ahead=hours_ahead,
            days_ahead=days_ahead,
            tournament_id=tournament_id,
            force_refresh_token=force_refresh_token
        )

        # Filter matches for the specific player
        player_matches = [
            match for match in upcoming_matches
            if match.get('homeParticipantId') == player_id or match.get('awayParticipantId') == player_id
        ]

        logger.info(f"Found {len(player_matches)} upcoming matches for player ID {player_id}")
        return player_matches

    except Exception as e:
        logger.error(f"Error fetching upcoming matches for player ID {player_id}: {e}")
        raise MatchDataError(f"Error fetching upcoming matches: {e}") from e


def get_player_matches_for_date(
    player_id: int,
    date: Optional[datetime] = None,
    tournament_id: int = 1,
    force_refresh_token: bool = False
) -> List[Dict[str, Any]]:
    """
    Get matches for a specific player on a specific date.

    Args:
        player_id: The player ID to fetch matches for
        date: The date to fetch matches for (default: today)
        tournament_id: The tournament ID to fetch matches for (default: 1)
        force_refresh_token: If True, force a new token retrieval.

    Returns:
        List of match data dictionaries for the player on the specified date.

    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    try:
        # Set default date if not provided
        if date is None:
            date = datetime.now()

        # Format date range for the entire day
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999).strftime('%Y-%m-%d %H:%M')

        # Fetch matches for the date
        matches = fetch_matches(
            from_date=date_start,
            to_date=date_end,
            tournament_id=tournament_id,
            schedule_type='fixture',  # Use fixture to get scheduled matches
            force_refresh_token=force_refresh_token,
            include_time=True,
            order_asc=True
        )

        # Filter matches for the specific player
        player_matches = [
            match for match in matches
            if match.get('homeParticipantId') == player_id or match.get('awayParticipantId') == player_id
        ]

        logger.info(f"Found {len(player_matches)} matches for player ID {player_id} on {date.strftime('%Y-%m-%d')}")
        return player_matches

    except Exception as e:
        logger.error(f"Error fetching matches for player ID {player_id} on {date.strftime('%Y-%m-%d')}: {e}")
        raise MatchDataError(f"Error fetching matches for date: {e}") from e
