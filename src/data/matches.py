"""
Module for fetching and processing match data from h2hggl.com.
"""
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from src.auth import get_bearer_token, AuthenticationError

logger = logging.getLogger(__name__)


class MatchDataError(Exception):
    """Exception raised for errors in the match data module."""
    pass


def fetch_matches(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    tournament_id: int = 1,
    schedule_type: str = "match",
    force_refresh_token: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch match data from h2hggl.com.
    
    Args:
        from_date: Start date in format 'YYYY-MM-DD' (default: 30 days ago)
        to_date: End date in format 'YYYY-MM-DD' (default: today)
        tournament_id: The tournament ID to fetch matches for (default: 1)
        schedule_type: Type of schedule to fetch ('match' for past matches, 'fixture' for upcoming matches)
        force_refresh_token: If True, force a new token retrieval.
        
    Returns:
        List of match data dictionaries.
        
    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    try:
        # Set default dates if not provided
        if from_date is None:
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if to_date is None:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get authentication token
        token = get_bearer_token(force_refresh=force_refresh_token)
        
        # API endpoint
        url = 'https://api-sis-stats.hudstats.com/v1/schedule'
        
        # Query parameters
        params = {
            'schedule-type': schedule_type,
            'from-date': from_date,
            'to-date': to_date,
            'tournament-id': tournament_id
        }
        
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
    days_ahead: int = 7,
    tournament_id: int = 1,
    force_refresh_token: bool = False
) -> List[Dict[str, Any]]:
    """
    Fetch upcoming matches from h2hggl.com.
    
    Args:
        days_ahead: Number of days ahead to fetch matches for (default: 7)
        tournament_id: The tournament ID to fetch matches for (default: 1)
        force_refresh_token: If True, force a new token retrieval.
        
    Returns:
        List of upcoming match data dictionaries.
        
    Raises:
        MatchDataError: If there is an error fetching match data.
    """
    today = datetime.now()
    from_date = today.strftime('%Y-%m-%d')
    to_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    return fetch_matches(
        from_date=from_date,
        to_date=to_date,
        tournament_id=tournament_id,
        schedule_type='fixture',
        force_refresh_token=force_refresh_token
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
