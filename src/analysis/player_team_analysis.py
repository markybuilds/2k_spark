"""
Module for analyzing player performance with different NBA teams.

This module provides functions to analyze how players perform with specific NBA teams,
which is crucial for the NBA 2K eSports prediction model.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from src.data.matches import fetch_matches
from src.data.standings import fetch_standings, get_player_by_name

logger = logging.getLogger(__name__)


class PlayerTeamAnalysisError(Exception):
    """Exception raised for errors in the player-team analysis module."""
    pass


def get_player_team_history(player_id: int, tournament_id: int = 1) -> List[Dict[str, Any]]:
    """
    Get a player's match history with information about which teams they used.
    
    Args:
        player_id: The player's ID
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        List of matches with team information
        
    Raises:
        PlayerTeamAnalysisError: If there is an error fetching the data
    """
    try:
        # Fetch all matches for the player
        matches = fetch_matches(
            schedule_type="match",
            from_date="2023-01-01",  # Use a wide date range to get sufficient history
            to_date="2025-12-31",
            tournament_id=tournament_id
        )
        
        # Filter matches for the specific player
        player_matches = []
        for match in matches:
            if match.get('homeParticipantId') == player_id or match.get('awayParticipantId') == player_id:
                # Add a field to indicate if the player was home or away
                if match.get('homeParticipantId') == player_id:
                    match['playerPosition'] = 'home'
                    match['playerTeam'] = match.get('homeTeamName')
                    match['playerTeamId'] = match.get('homeTeamId')
                    match['opponentTeam'] = match.get('awayTeamName')
                    match['opponentTeamId'] = match.get('awayTeamId')
                    match['opponentId'] = match.get('awayParticipantId')
                    match['opponentName'] = match.get('awayParticipantName')
                    match['playerScore'] = match.get('homeScore')
                    match['opponentScore'] = match.get('awayScore')
                else:
                    match['playerPosition'] = 'away'
                    match['playerTeam'] = match.get('awayTeamName')
                    match['playerTeamId'] = match.get('awayTeamId')
                    match['opponentTeam'] = match.get('homeTeamName')
                    match['opponentTeamId'] = match.get('homeTeamId')
                    match['opponentId'] = match.get('homeParticipantId')
                    match['opponentName'] = match.get('homeParticipantName')
                    match['playerScore'] = match.get('awayScore')
                    match['opponentScore'] = match.get('homeScore')
                
                # Determine if the player won
                if match.get('result') == 'home_win' and match.get('homeParticipantId') == player_id:
                    match['playerWon'] = True
                elif match.get('result') == 'away_win' and match.get('awayParticipantId') == player_id:
                    match['playerWon'] = True
                else:
                    match['playerWon'] = False
                
                player_matches.append(match)
        
        logger.info(f"Found {len(player_matches)} matches for player ID {player_id}")
        return player_matches
    
    except Exception as e:
        logger.error(f"Error getting player-team history: {e}")
        raise PlayerTeamAnalysisError(f"Failed to get player-team history: {e}") from e


def calculate_player_team_stats(player_id: int, tournament_id: int = 1) -> Dict[str, Dict[str, Any]]:
    """
    Calculate statistics for a player with each NBA team they've used.
    
    Args:
        player_id: The player's ID
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary mapping team names to statistics
        
    Raises:
        PlayerTeamAnalysisError: If there is an error calculating the statistics
    """
    try:
        # Get the player's match history
        matches = get_player_team_history(player_id, tournament_id)
        
        # Group matches by team
        team_stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'losses': 0,
            'total_score': 0,
            'total_opponent_score': 0,
            'match_list': []
        })
        
        # Calculate statistics for each team
        for match in matches:
            team_name = match.get('playerTeam')
            if not team_name:
                continue
            
            team_stats[team_name]['matches'] += 1
            team_stats[team_name]['match_list'].append(match)
            
            if match.get('playerWon'):
                team_stats[team_name]['wins'] += 1
            else:
                team_stats[team_name]['losses'] += 1
            
            player_score = match.get('playerScore', 0)
            opponent_score = match.get('opponentScore', 0)
            
            if player_score is not None:
                team_stats[team_name]['total_score'] += player_score
            
            if opponent_score is not None:
                team_stats[team_name]['total_opponent_score'] += opponent_score
        
        # Calculate derived statistics
        for team_name, stats in team_stats.items():
            if stats['matches'] > 0:
                stats['win_rate'] = stats['wins'] / stats['matches']
                stats['avg_score'] = stats['total_score'] / stats['matches']
                stats['avg_opponent_score'] = stats['total_opponent_score'] / stats['matches']
                stats['avg_score_diff'] = stats['avg_score'] - stats['avg_opponent_score']
            else:
                stats['win_rate'] = 0
                stats['avg_score'] = 0
                stats['avg_opponent_score'] = 0
                stats['avg_score_diff'] = 0
        
        return dict(team_stats)
    
    except Exception as e:
        logger.error(f"Error calculating player-team statistics: {e}")
        raise PlayerTeamAnalysisError(f"Failed to calculate player-team statistics: {e}") from e


def get_player_best_teams(player_id: int, tournament_id: int = 1, min_matches: int = 3) -> List[Tuple[str, float, int]]:
    """
    Get a player's best teams based on win rate.
    
    Args:
        player_id: The player's ID
        tournament_id: The tournament ID (default: 1)
        min_matches: Minimum number of matches required with a team (default: 3)
        
    Returns:
        List of tuples (team_name, win_rate, matches) sorted by win rate
        
    Raises:
        PlayerTeamAnalysisError: If there is an error getting the best teams
    """
    try:
        # Calculate team statistics
        team_stats = calculate_player_team_stats(player_id, tournament_id)
        
        # Filter teams with minimum number of matches
        qualified_teams = [
            (team_name, stats['win_rate'], stats['matches'])
            for team_name, stats in team_stats.items()
            if stats['matches'] >= min_matches
        ]
        
        # Sort by win rate (descending)
        sorted_teams = sorted(qualified_teams, key=lambda x: x[1], reverse=True)
        
        return sorted_teams
    
    except Exception as e:
        logger.error(f"Error getting player's best teams: {e}")
        raise PlayerTeamAnalysisError(f"Failed to get player's best teams: {e}") from e


def get_player_worst_teams(player_id: int, tournament_id: int = 1, min_matches: int = 3) -> List[Tuple[str, float, int]]:
    """
    Get a player's worst teams based on win rate.
    
    Args:
        player_id: The player's ID
        tournament_id: The tournament ID (default: 1)
        min_matches: Minimum number of matches required with a team (default: 3)
        
    Returns:
        List of tuples (team_name, win_rate, matches) sorted by win rate (ascending)
        
    Raises:
        PlayerTeamAnalysisError: If there is an error getting the worst teams
    """
    try:
        # Calculate team statistics
        team_stats = calculate_player_team_stats(player_id, tournament_id)
        
        # Filter teams with minimum number of matches
        qualified_teams = [
            (team_name, stats['win_rate'], stats['matches'])
            for team_name, stats in team_stats.items()
            if stats['matches'] >= min_matches
        ]
        
        # Sort by win rate (ascending)
        sorted_teams = sorted(qualified_teams, key=lambda x: x[1])
        
        return sorted_teams
    
    except Exception as e:
        logger.error(f"Error getting player's worst teams: {e}")
        raise PlayerTeamAnalysisError(f"Failed to get player's worst teams: {e}") from e


def get_player_team_matchup_stats(player_id: int, team_name: str, tournament_id: int = 1) -> Dict[str, Any]:
    """
    Get statistics for a player using a specific team against all opponents.
    
    Args:
        player_id: The player's ID
        team_name: The NBA team name
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary with matchup statistics
        
    Raises:
        PlayerTeamAnalysisError: If there is an error getting the matchup statistics
    """
    try:
        # Get the player's match history
        matches = get_player_team_history(player_id, tournament_id)
        
        # Filter matches for the specific team
        team_matches = [match for match in matches if match.get('playerTeam') == team_name]
        
        # Group matches by opponent team
        opponent_stats = defaultdict(lambda: {
            'matches': 0,
            'wins': 0,
            'losses': 0,
            'total_score': 0,
            'total_opponent_score': 0
        })
        
        # Calculate statistics for each opponent team
        for match in team_matches:
            opponent_team = match.get('opponentTeam')
            if not opponent_team:
                continue
            
            opponent_stats[opponent_team]['matches'] += 1
            
            if match.get('playerWon'):
                opponent_stats[opponent_team]['wins'] += 1
            else:
                opponent_stats[opponent_team]['losses'] += 1
            
            player_score = match.get('playerScore', 0)
            opponent_score = match.get('opponentScore', 0)
            
            if player_score is not None:
                opponent_stats[opponent_team]['total_score'] += player_score
            
            if opponent_score is not None:
                opponent_stats[opponent_team]['total_opponent_score'] += opponent_score
        
        # Calculate derived statistics
        for opponent_team, stats in opponent_stats.items():
            if stats['matches'] > 0:
                stats['win_rate'] = stats['wins'] / stats['matches']
                stats['avg_score'] = stats['total_score'] / stats['matches']
                stats['avg_opponent_score'] = stats['total_opponent_score'] / stats['matches']
                stats['avg_score_diff'] = stats['avg_score'] - stats['avg_opponent_score']
            else:
                stats['win_rate'] = 0
                stats['avg_score'] = 0
                stats['avg_opponent_score'] = 0
                stats['avg_score_diff'] = 0
        
        # Overall statistics for the team
        overall_stats = {
            'matches': len(team_matches),
            'wins': sum(1 for match in team_matches if match.get('playerWon')),
            'losses': sum(1 for match in team_matches if not match.get('playerWon')),
            'opponent_stats': dict(opponent_stats)
        }
        
        if overall_stats['matches'] > 0:
            overall_stats['win_rate'] = overall_stats['wins'] / overall_stats['matches']
        else:
            overall_stats['win_rate'] = 0
        
        return overall_stats
    
    except Exception as e:
        logger.error(f"Error getting player-team matchup statistics: {e}")
        raise PlayerTeamAnalysisError(f"Failed to get player-team matchup statistics: {e}") from e


def compare_player_team_performance(player_id: int, team1: str, team2: str, tournament_id: int = 1) -> Dict[str, Any]:
    """
    Compare a player's performance with two different teams.
    
    Args:
        player_id: The player's ID
        team1: First NBA team name
        team2: Second NBA team name
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary with comparison statistics
        
    Raises:
        PlayerTeamAnalysisError: If there is an error comparing the teams
    """
    try:
        # Calculate team statistics
        team_stats = calculate_player_team_stats(player_id, tournament_id)
        
        # Get statistics for the specified teams
        team1_stats = team_stats.get(team1, {})
        team2_stats = team_stats.get(team2, {})
        
        # Create comparison dictionary
        comparison = {
            'team1': {
                'name': team1,
                'matches': team1_stats.get('matches', 0),
                'wins': team1_stats.get('wins', 0),
                'losses': team1_stats.get('losses', 0),
                'win_rate': team1_stats.get('win_rate', 0),
                'avg_score': team1_stats.get('avg_score', 0),
                'avg_opponent_score': team1_stats.get('avg_opponent_score', 0),
                'avg_score_diff': team1_stats.get('avg_score_diff', 0)
            },
            'team2': {
                'name': team2,
                'matches': team2_stats.get('matches', 0),
                'wins': team2_stats.get('wins', 0),
                'losses': team2_stats.get('losses', 0),
                'win_rate': team2_stats.get('win_rate', 0),
                'avg_score': team2_stats.get('avg_score', 0),
                'avg_opponent_score': team2_stats.get('avg_opponent_score', 0),
                'avg_score_diff': team2_stats.get('avg_score_diff', 0)
            }
        }
        
        # Calculate differences
        if team1_stats and team2_stats:
            comparison['win_rate_diff'] = team1_stats.get('win_rate', 0) - team2_stats.get('win_rate', 0)
            comparison['avg_score_diff'] = team1_stats.get('avg_score', 0) - team2_stats.get('avg_score', 0)
            comparison['avg_opponent_score_diff'] = team1_stats.get('avg_opponent_score', 0) - team2_stats.get('avg_opponent_score', 0)
            comparison['better_team'] = team1 if comparison['win_rate_diff'] > 0 else team2
        
        return comparison
    
    except Exception as e:
        logger.error(f"Error comparing player-team performance: {e}")
        raise PlayerTeamAnalysisError(f"Failed to compare player-team performance: {e}") from e


def predict_player_team_matchup(
    player1_id: int,
    player2_id: int,
    player1_team: str,
    player2_team: str,
    tournament_id: int = 1
) -> Dict[str, Any]:
    """
    Predict the outcome of a matchup between two players with specific teams.
    
    Args:
        player1_id: First player's ID
        player2_id: Second player's ID
        player1_team: NBA team for first player
        player2_team: NBA team for second player
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary with prediction information
        
    Raises:
        PlayerTeamAnalysisError: If there is an error making the prediction
    """
    try:
        # Get player names
        standings = fetch_standings(tournament_id)
        player1_data = next((p for p in standings if p.get('participantId') == player1_id), None)
        player2_data = next((p for p in standings if p.get('participantId') == player2_id), None)
        
        player1_name = player1_data.get('participantName', f"Player {player1_id}") if player1_data else f"Player {player1_id}"
        player2_name = player2_data.get('participantName', f"Player {player2_id}") if player2_data else f"Player {player2_id}"
        
        # Get team statistics for both players
        player1_team_stats = calculate_player_team_stats(player1_id, tournament_id)
        player2_team_stats = calculate_player_team_stats(player2_id, tournament_id)
        
        # Get specific team stats
        player1_with_team = player1_team_stats.get(player1_team, {})
        player2_with_team = player2_team_stats.get(player2_team, {})
        
        # Calculate basic prediction factors
        player1_win_rate = player1_with_team.get('win_rate', 0)
        player2_win_rate = player2_with_team.get('win_rate', 0)
        
        player1_avg_score = player1_with_team.get('avg_score', 0)
        player2_avg_score = player2_with_team.get('avg_score', 0)
        
        player1_matches = player1_with_team.get('matches', 0)
        player2_matches = player2_with_team.get('matches', 0)
        
        # Calculate confidence based on number of matches
        confidence_factor = min(1.0, (player1_matches + player2_matches) / 20)
        
        # Simple prediction model (can be enhanced later)
        player1_strength = player1_win_rate * (1 + player1_avg_score / 100)
        player2_strength = player2_win_rate * (1 + player2_avg_score / 100)
        
        total_strength = player1_strength + player2_strength
        if total_strength > 0:
            player1_win_probability = player1_strength / total_strength
        else:
            player1_win_probability = 0.5  # Default to 50% if no data
        
        player2_win_probability = 1 - player1_win_probability
        
        # Create prediction result
        prediction = {
            'player1': {
                'id': player1_id,
                'name': player1_name,
                'team': player1_team,
                'matches_with_team': player1_matches,
                'win_rate_with_team': player1_win_rate,
                'avg_score_with_team': player1_avg_score
            },
            'player2': {
                'id': player2_id,
                'name': player2_name,
                'team': player2_team,
                'matches_with_team': player2_matches,
                'win_rate_with_team': player2_win_rate,
                'avg_score_with_team': player2_avg_score
            },
            'prediction': {
                'player1_win_probability': player1_win_probability,
                'player2_win_probability': player2_win_probability,
                'confidence': confidence_factor,
                'predicted_winner': player1_name if player1_win_probability > player2_win_probability else player2_name
            }
        }
        
        return prediction
    
    except Exception as e:
        logger.error(f"Error predicting player-team matchup: {e}")
        raise PlayerTeamAnalysisError(f"Failed to predict player-team matchup: {e}") from e
