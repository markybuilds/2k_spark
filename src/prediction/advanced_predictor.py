"""
Advanced prediction module for NBA 2K eSports match outcomes.

This module provides more sophisticated prediction algorithms that incorporate
additional features and machine learning techniques.
"""
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from src.data.matches import fetch_matches, fetch_upcoming_matches
from src.data.standings import fetch_standings
from src.analysis.player_team_analysis import (
    get_player_team_history,
    calculate_player_team_stats,
    get_player_team_matchup_stats
)

logger = logging.getLogger(__name__)


class AdvancedPredictionError(Exception):
    """Exception raised for errors in the advanced prediction module."""
    pass


def calculate_player_recent_form(player_id: int, num_matches: int = 10, tournament_id: int = 1) -> Dict[str, Any]:
    """
    Calculate a player's recent form based on their last N matches.
    
    Args:
        player_id: The player's ID
        num_matches: Number of recent matches to consider (default: 10)
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary with recent form statistics
        
    Raises:
        AdvancedPredictionError: If there is an error calculating recent form
    """
    try:
        # Get player's match history
        matches = get_player_team_history(player_id, tournament_id)
        
        # Sort matches by date (most recent first)
        sorted_matches = sorted(matches, key=lambda x: x.get('startDate', ''), reverse=True)
        
        # Take the most recent N matches
        recent_matches = sorted_matches[:num_matches]
        
        if not recent_matches:
            return {
                'matches': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'avg_score': 0,
                'avg_opponent_score': 0,
                'avg_score_diff': 0,
                'trend': 'neutral'
            }
        
        # Calculate statistics
        wins = sum(1 for match in recent_matches if match.get('playerWon'))
        losses = sum(1 for match in recent_matches if not match.get('playerWon'))
        total_score = sum(match.get('playerScore', 0) for match in recent_matches if match.get('playerScore') is not None)
        total_opponent_score = sum(match.get('opponentScore', 0) for match in recent_matches if match.get('opponentScore') is not None)
        
        # Calculate win rate and averages
        win_rate = wins / len(recent_matches) if recent_matches else 0
        avg_score = total_score / len(recent_matches) if recent_matches else 0
        avg_opponent_score = total_opponent_score / len(recent_matches) if recent_matches else 0
        avg_score_diff = avg_score - avg_opponent_score
        
        # Calculate trend (improving, declining, or neutral)
        if len(recent_matches) >= 5:
            # Split into two halves
            first_half = recent_matches[len(recent_matches)//2:]
            second_half = recent_matches[:len(recent_matches)//2]
            
            first_half_wins = sum(1 for match in first_half if match.get('playerWon'))
            second_half_wins = sum(1 for match in second_half if match.get('playerWon'))
            
            first_half_win_rate = first_half_wins / len(first_half) if first_half else 0
            second_half_win_rate = second_half_wins / len(second_half) if second_half else 0
            
            if second_half_win_rate > first_half_win_rate + 0.1:
                trend = 'improving'
            elif second_half_win_rate < first_half_win_rate - 0.1:
                trend = 'declining'
            else:
                trend = 'neutral'
        else:
            trend = 'neutral'
        
        return {
            'matches': len(recent_matches),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_score': avg_score,
            'avg_opponent_score': avg_opponent_score,
            'avg_score_diff': avg_score_diff,
            'trend': trend,
            'last_matches': [{'opponent': m.get('opponentName'), 'result': 'win' if m.get('playerWon') else 'loss'} for m in recent_matches[:5]]
        }
    
    except Exception as e:
        logger.error(f"Error calculating player recent form: {e}")
        raise AdvancedPredictionError(f"Failed to calculate player recent form: {e}") from e


def calculate_head_to_head_stats(player1_id: int, player2_id: int, tournament_id: int = 1) -> Dict[str, Any]:
    """
    Calculate head-to-head statistics between two players.
    
    Args:
        player1_id: First player's ID
        player2_id: Second player's ID
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary with head-to-head statistics
        
    Raises:
        AdvancedPredictionError: If there is an error calculating head-to-head statistics
    """
    try:
        # Get player1's match history
        player1_matches = get_player_team_history(player1_id, tournament_id)
        
        # Filter matches against player2
        h2h_matches = [
            match for match in player1_matches 
            if match.get('opponentId') == player2_id
        ]
        
        if not h2h_matches:
            return {
                'matches': 0,
                'player1_wins': 0,
                'player2_wins': 0,
                'player1_win_rate': 0,
                'player2_win_rate': 0,
                'avg_score_diff': 0,
                'recent_winner': None,
                'team_matchups': {}
            }
        
        # Calculate statistics
        player1_wins = sum(1 for match in h2h_matches if match.get('playerWon'))
        player2_wins = len(h2h_matches) - player1_wins
        
        # Calculate win rates
        player1_win_rate = player1_wins / len(h2h_matches) if h2h_matches else 0
        player2_win_rate = player2_wins / len(h2h_matches) if h2h_matches else 0
        
        # Calculate average score difference
        score_diffs = [
            match.get('playerScore', 0) - match.get('opponentScore', 0)
            for match in h2h_matches
            if match.get('playerScore') is not None and match.get('opponentScore') is not None
        ]
        avg_score_diff = sum(score_diffs) / len(score_diffs) if score_diffs else 0
        
        # Determine recent winner
        if h2h_matches:
            # Sort by date (most recent first)
            sorted_matches = sorted(h2h_matches, key=lambda x: x.get('startDate', ''), reverse=True)
            recent_winner = 'player1' if sorted_matches[0].get('playerWon') else 'player2'
        else:
            recent_winner = None
        
        # Analyze team matchups
        team_matchups = defaultdict(lambda: {'matches': 0, 'player1_wins': 0, 'player2_wins': 0})
        
        for match in h2h_matches:
            player1_team = match.get('playerTeam')
            player2_team = match.get('opponentTeam')
            
            if not player1_team or not player2_team:
                continue
            
            matchup_key = f"{player1_team} vs {player2_team}"
            team_matchups[matchup_key]['matches'] += 1
            
            if match.get('playerWon'):
                team_matchups[matchup_key]['player1_wins'] += 1
            else:
                team_matchups[matchup_key]['player2_wins'] += 1
        
        # Calculate win rates for each team matchup
        for matchup, stats in team_matchups.items():
            if stats['matches'] > 0:
                stats['player1_win_rate'] = stats['player1_wins'] / stats['matches']
                stats['player2_win_rate'] = stats['player2_wins'] / stats['matches']
            else:
                stats['player1_win_rate'] = 0
                stats['player2_win_rate'] = 0
        
        return {
            'matches': len(h2h_matches),
            'player1_wins': player1_wins,
            'player2_wins': player2_wins,
            'player1_win_rate': player1_win_rate,
            'player2_win_rate': player2_win_rate,
            'avg_score_diff': avg_score_diff,
            'recent_winner': recent_winner,
            'team_matchups': dict(team_matchups)
        }
    
    except Exception as e:
        logger.error(f"Error calculating head-to-head statistics: {e}")
        raise AdvancedPredictionError(f"Failed to calculate head-to-head statistics: {e}") from e


def calculate_team_matchup_advantage(team1: str, team2: str, tournament_id: int = 1) -> Dict[str, Any]:
    """
    Calculate the advantage one NBA team has over another based on historical matchups.
    
    Args:
        team1: First NBA team name
        team2: Second NBA team name
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary with team matchup statistics
        
    Raises:
        AdvancedPredictionError: If there is an error calculating team matchup advantage
    """
    try:
        # Fetch all matches
        matches = fetch_matches(
            schedule_type="match",
            from_date="2023-01-01",
            to_date="2025-12-31",
            tournament_id=tournament_id
        )
        
        # Filter matches between the two teams
        team_matchups = [
            match for match in matches
            if (match.get('homeTeamName') == team1 and match.get('awayTeamName') == team2) or
               (match.get('homeTeamName') == team2 and match.get('awayTeamName') == team1)
        ]
        
        if not team_matchups:
            return {
                'matches': 0,
                'team1_wins': 0,
                'team2_wins': 0,
                'team1_win_rate': 0,
                'team2_win_rate': 0,
                'avg_score_diff': 0,
                'advantage': 'neutral'
            }
        
        # Calculate statistics
        team1_wins = sum(1 for match in team_matchups 
                         if (match.get('homeTeamName') == team1 and match.get('result') == 'home_win') or
                            (match.get('awayTeamName') == team1 and match.get('result') == 'away_win'))
        
        team2_wins = sum(1 for match in team_matchups 
                         if (match.get('homeTeamName') == team2 and match.get('result') == 'home_win') or
                            (match.get('awayTeamName') == team2 and match.get('result') == 'away_win'))
        
        # Calculate win rates
        team1_win_rate = team1_wins / len(team_matchups) if team_matchups else 0
        team2_win_rate = team2_wins / len(team_matchups) if team_matchups else 0
        
        # Calculate average score difference
        score_diffs = []
        
        for match in team_matchups:
            if match.get('homeTeamName') == team1:
                if match.get('homeScore') is not None and match.get('awayScore') is not None:
                    score_diffs.append(match.get('homeScore', 0) - match.get('awayScore', 0))
            else:
                if match.get('homeScore') is not None and match.get('awayScore') is not None:
                    score_diffs.append(match.get('awayScore', 0) - match.get('homeScore', 0))
        
        avg_score_diff = sum(score_diffs) / len(score_diffs) if score_diffs else 0
        
        # Determine advantage
        if team1_win_rate > team2_win_rate + 0.1:
            advantage = 'team1'
        elif team2_win_rate > team1_win_rate + 0.1:
            advantage = 'team2'
        else:
            advantage = 'neutral'
        
        return {
            'matches': len(team_matchups),
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'team1_win_rate': team1_win_rate,
            'team2_win_rate': team2_win_rate,
            'avg_score_diff': avg_score_diff,
            'advantage': advantage
        }
    
    except Exception as e:
        logger.error(f"Error calculating team matchup advantage: {e}")
        raise AdvancedPredictionError(f"Failed to calculate team matchup advantage: {e}") from e


def calculate_feature_weights() -> Dict[str, float]:
    """
    Calculate weights for different prediction features.
    
    Returns:
        Dictionary mapping feature names to weights
    """
    # These weights could be learned from data, but for now we'll use fixed values
    return {
        'player_team_win_rate': 0.35,      # Player's win rate with their assigned team
        'head_to_head': 0.25,              # Head-to-head record between the players
        'recent_form': 0.20,               # Player's recent performance
        'team_matchup': 0.10,              # How the teams match up against each other
        'overall_player_skill': 0.10       # Player's overall skill level
    }


def advanced_match_prediction(
    player1_id: int,
    player2_id: int,
    player1_team: str,
    player2_team: str,
    tournament_id: int = 1
) -> Dict[str, Any]:
    """
    Make an advanced prediction for a match between two players with specific teams.
    
    Args:
        player1_id: First player's ID
        player2_id: Second player's ID
        player1_team: NBA team for first player
        player2_team: NBA team for second player
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary with detailed prediction information
        
    Raises:
        AdvancedPredictionError: If there is an error making the prediction
    """
    try:
        # Get player names
        standings = fetch_standings(tournament_id)
        player1_data = next((p for p in standings if p.get('participantId') == player1_id), None)
        player2_data = next((p for p in standings if p.get('participantId') == player2_id), None)
        
        player1_name = player1_data.get('participantName', f"Player {player1_id}") if player1_data else f"Player {player1_id}"
        player2_name = player2_data.get('participantName', f"Player {player2_id}") if player2_data else f"Player {player2_id}"
        
        # Calculate feature values
        
        # 1. Player-team statistics
        player1_team_stats = calculate_player_team_stats(player1_id, tournament_id)
        player2_team_stats = calculate_player_team_stats(player2_id, tournament_id)
        
        player1_with_team = player1_team_stats.get(player1_team, {})
        player2_with_team = player2_team_stats.get(player2_team, {})
        
        player1_team_win_rate = player1_with_team.get('win_rate', 0)
        player2_team_win_rate = player2_with_team.get('win_rate', 0)
        
        player1_team_matches = player1_with_team.get('matches', 0)
        player2_team_matches = player2_with_team.get('matches', 0)
        
        # 2. Head-to-head statistics
        h2h_stats = calculate_head_to_head_stats(player1_id, player2_id, tournament_id)
        
        # 3. Recent form
        player1_form = calculate_player_recent_form(player1_id, tournament_id=tournament_id)
        player2_form = calculate_player_recent_form(player2_id, tournament_id=tournament_id)
        
        # 4. Team matchup advantage
        team_matchup = calculate_team_matchup_advantage(player1_team, player2_team, tournament_id)
        
        # 5. Overall player skill (from standings)
        player1_rank = player1_data.get('position', 0) if player1_data else 0
        player2_rank = player2_data.get('position', 0) if player2_data else 0
        
        # Normalize ranks to [0, 1] where 1 is better
        max_rank = 100  # Assuming there are at most 100 players
        player1_skill = 1 - (player1_rank / max_rank) if player1_rank > 0 else 0.5
        player2_skill = 1 - (player2_rank / max_rank) if player2_rank > 0 else 0.5
        
        # Get feature weights
        weights = calculate_feature_weights()
        
        # Calculate weighted scores
        player1_score = (
            weights['player_team_win_rate'] * player1_team_win_rate +
            weights['head_to_head'] * h2h_stats.get('player1_win_rate', 0) +
            weights['recent_form'] * player1_form.get('win_rate', 0) +
            weights['team_matchup'] * (1 if team_matchup.get('advantage') == 'team1' else 0.5) +
            weights['overall_player_skill'] * player1_skill
        )
        
        player2_score = (
            weights['player_team_win_rate'] * player2_team_win_rate +
            weights['head_to_head'] * h2h_stats.get('player2_win_rate', 0) +
            weights['recent_form'] * player2_form.get('win_rate', 0) +
            weights['team_matchup'] * (1 if team_matchup.get('advantage') == 'team2' else 0.5) +
            weights['overall_player_skill'] * player2_skill
        )
        
        # Calculate win probabilities
        total_score = player1_score + player2_score
        if total_score > 0:
            player1_win_probability = player1_score / total_score
        else:
            player1_win_probability = 0.5  # Default to 50% if no data
        
        player2_win_probability = 1 - player1_win_probability
        
        # Calculate confidence based on amount of data
        data_points = (
            player1_team_matches + 
            player2_team_matches + 
            h2h_stats.get('matches', 0) + 
            player1_form.get('matches', 0) + 
            player2_form.get('matches', 0) + 
            team_matchup.get('matches', 0)
        )
        
        confidence_factor = min(1.0, data_points / 100)  # Cap at 1.0
        
        # Create prediction result
        prediction = {
            'player1': {
                'id': player1_id,
                'name': player1_name,
                'team': player1_team,
                'matches_with_team': player1_team_matches,
                'win_rate_with_team': player1_team_win_rate,
                'recent_form': player1_form.get('trend', 'neutral'),
                'recent_win_rate': player1_form.get('win_rate', 0)
            },
            'player2': {
                'id': player2_id,
                'name': player2_name,
                'team': player2_team,
                'matches_with_team': player2_team_matches,
                'win_rate_with_team': player2_team_win_rate,
                'recent_form': player2_form.get('trend', 'neutral'),
                'recent_win_rate': player2_form.get('win_rate', 0)
            },
            'head_to_head': {
                'matches': h2h_stats.get('matches', 0),
                'player1_wins': h2h_stats.get('player1_wins', 0),
                'player2_wins': h2h_stats.get('player2_wins', 0),
                'player1_win_rate': h2h_stats.get('player1_win_rate', 0),
                'player2_win_rate': h2h_stats.get('player2_win_rate', 0)
            },
            'team_matchup': {
                'advantage': team_matchup.get('advantage', 'neutral'),
                'team1_win_rate': team_matchup.get('team1_win_rate', 0),
                'team2_win_rate': team_matchup.get('team2_win_rate', 0)
            },
            'prediction': {
                'player1_win_probability': player1_win_probability,
                'player2_win_probability': player2_win_probability,
                'confidence': confidence_factor,
                'predicted_winner': player1_name if player1_win_probability > player2_win_probability else player2_name,
                'feature_contributions': {
                    'player1_team_win_rate': weights['player_team_win_rate'] * player1_team_win_rate,
                    'player2_team_win_rate': weights['player_team_win_rate'] * player2_team_win_rate,
                    'head_to_head': weights['head_to_head'] * h2h_stats.get('player1_win_rate', 0),
                    'recent_form': weights['recent_form'] * player1_form.get('win_rate', 0),
                    'team_matchup': weights['team_matchup'] * (1 if team_matchup.get('advantage') == 'team1' else 0.5),
                    'overall_player_skill': weights['overall_player_skill'] * player1_skill
                }
            }
        }
        
        return prediction
    
    except Exception as e:
        logger.error(f"Error making advanced prediction: {e}")
        raise AdvancedPredictionError(f"Failed to make advanced prediction: {e}") from e


def predict_upcoming_matches_advanced(hours_ahead: int = 24, tournament_id: int = 1) -> List[Dict[str, Any]]:
    """
    Make advanced predictions for upcoming matches.
    
    Args:
        hours_ahead: Number of hours ahead to fetch matches for (default: 24)
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        List of matches with advanced predictions
        
    Raises:
        AdvancedPredictionError: If there is an error making predictions
    """
    try:
        # Fetch upcoming matches
        upcoming_matches = fetch_upcoming_matches(hours_ahead=hours_ahead, tournament_id=tournament_id)
        
        # Make predictions for each match
        predictions = []
        
        for match in upcoming_matches:
            # Extract player and team information
            home_player_id = match.get('homeParticipantId')
            away_player_id = match.get('awayParticipantId')
            home_team = match.get('homeTeamName')
            away_team = match.get('awayTeamName')
            
            if not all([home_player_id, away_player_id, home_team, away_team]):
                logger.warning(f"Skipping match {match.get('fixtureId')} due to missing data")
                continue
            
            # Make prediction
            try:
                prediction = advanced_match_prediction(
                    home_player_id,
                    away_player_id,
                    home_team,
                    away_team,
                    tournament_id
                )
                
                # Add match information to prediction
                prediction_with_match = {
                    'match_id': match.get('fixtureId'),
                    'fixture_start': match.get('fixtureStart'),
                    'home_player_id': home_player_id,
                    'home_player_name': match.get('homeParticipantName'),
                    'away_player_id': away_player_id,
                    'away_player_name': match.get('awayParticipantName'),
                    'home_team': home_team,
                    'away_team': away_team,
                    'prediction': prediction
                }
                
                predictions.append(prediction_with_match)
                
            except Exception as e:
                logger.warning(f"Could not make prediction for match {match.get('fixtureId')}: {e}")
                continue
        
        return predictions
    
    except Exception as e:
        logger.error(f"Error predicting upcoming matches: {e}")
        raise AdvancedPredictionError(f"Failed to predict upcoming matches: {e}") from e
