"""
Module for fetching and processing player standings data from h2hggl.com.
"""
import logging
import requests
from typing import Dict, List, Any, Optional

from src.auth import get_bearer_token, AuthenticationError

logger = logging.getLogger(__name__)


class StandingsDataError(Exception):
    """Exception raised for errors in the standings data module."""
    pass


def fetch_standings(tournament_id: int = 1, force_refresh_token: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch player standings data from h2hggl.com.
    
    Args:
        tournament_id: The tournament ID to fetch standings for (default: 1)
        force_refresh_token: If True, force a new token retrieval.
        
    Returns:
        List of player standings data dictionaries.
        
    Raises:
        StandingsDataError: If there is an error fetching standings data.
    """
    try:
        # Get authentication token
        token = get_bearer_token(force_refresh=force_refresh_token)
        
        # API endpoint
        url = 'https://api-sis-stats.hudstats.com/v1/standings/participant'
        
        # Query parameters
        params = {
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
        
        logger.info(f"Fetching standings data for tournament ID {tournament_id}")
        response = requests.get(url, params=params, headers=headers)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        logger.info(f"Successfully retrieved standings data for {len(data)} participants")
        
        return data
        
    except AuthenticationError as e:
        logger.error(f"Authentication error while fetching standings data: {e}")
        raise StandingsDataError(f"Failed to authenticate: {e}") from e
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching standings data: {e}")
        raise StandingsDataError(f"HTTP error: {e}") from e
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error while fetching standings data: {e}")
        raise StandingsDataError(f"Connection error: {e}") from e
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout while fetching standings data: {e}")
        raise StandingsDataError(f"Timeout: {e}") from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching standings data: {e}")
        raise StandingsDataError(f"Request error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error while fetching standings data: {e}")
        raise StandingsDataError(f"Unexpected error: {e}") from e


def get_top_players(standings_data: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the top players from the standings data based on win percentage.
    
    Args:
        standings_data: The standings data from fetch_standings()
        limit: The number of top players to return (default: 10)
        
    Returns:
        List of top player data dictionaries.
    """
    # Sort by win percentage (matchesWinPct) in descending order
    sorted_data = sorted(standings_data, key=lambda x: x.get('matchesWinPct', 0), reverse=True)
    
    # Return the top players
    return sorted_data[:limit]


def get_player_by_name(standings_data: List[Dict[str, Any]], player_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a player's data by their name.
    
    Args:
        standings_data: The standings data from fetch_standings()
        player_name: The name of the player to find (case-insensitive)
        
    Returns:
        The player's data dictionary, or None if not found.
    """
    player_name = player_name.upper()
    for player in standings_data:
        if player.get('participantName', '').upper() == player_name:
            return player
    return None


def get_player_by_id(standings_data: List[Dict[str, Any]], player_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a player's data by their ID.
    
    Args:
        standings_data: The standings data from fetch_standings()
        player_id: The ID of the player to find
        
    Returns:
        The player's data dictionary, or None if not found.
    """
    for player in standings_data:
        if player.get('participantId') == player_id:
            return player
    return None


def get_head_to_head_stats(player1: Dict[str, Any], player2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two players and return their head-to-head statistics.
    
    Args:
        player1: The first player's data dictionary
        player2: The second player's data dictionary
        
    Returns:
        A dictionary containing comparative statistics.
    """
    # Extract key statistics for comparison
    stats = {
        'win_percentage': {
            'player1': player1.get('matchesWinPct', 0),
            'player2': player2.get('matchesWinPct', 0),
            'difference': player1.get('matchesWinPct', 0) - player2.get('matchesWinPct', 0)
        },
        'avg_points': {
            'player1': player1.get('avgPoints', 0),
            'player2': player2.get('avgPoints', 0),
            'difference': player1.get('avgPoints', 0) - player2.get('avgPoints', 0)
        },
        'field_goal_percentage': {
            'player1': player1.get('avgFieldGoalsPercent', 0),
            'player2': player2.get('avgFieldGoalsPercent', 0),
            'difference': player1.get('avgFieldGoalsPercent', 0) - player2.get('avgFieldGoalsPercent', 0)
        },
        'three_point_percentage': {
            'player1': player1.get('3PointersPercent', 0),
            'player2': player2.get('3PointersPercent', 0),
            'difference': player1.get('3PointersPercent', 0) - player2.get('3PointersPercent', 0)
        },
        'avg_assists': {
            'player1': player1.get('avgAssists', 0),
            'player2': player2.get('avgAssists', 0),
            'difference': player1.get('avgAssists', 0) - player2.get('avgAssists', 0)
        },
        'avg_steals': {
            'player1': player1.get('avgSteals', 0),
            'player2': player2.get('avgSteals', 0),
            'difference': player1.get('avgSteals', 0) - player2.get('avgSteals', 0)
        },
        'avg_blocks': {
            'player1': player1.get('avgBlocks', 0),
            'player2': player2.get('avgBlocks', 0),
            'difference': player1.get('avgBlocks', 0) - player2.get('avgBlocks', 0)
        },
        'matches_played': {
            'player1': player1.get('matchesPlayed', 0),
            'player2': player2.get('matchesPlayed', 0),
            'difference': player1.get('matchesPlayed', 0) - player2.get('matchesPlayed', 0)
        },
        'recent_form': {
            'player1': player1.get('matchForm', []),
            'player2': player2.get('matchForm', [])
        }
    }
    
    return stats
