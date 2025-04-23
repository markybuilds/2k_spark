"""
Module for predicting NBA 2K eSports match outcomes.

This module provides functions to predict the outcomes of upcoming matches
based on player performance with specific NBA teams.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from src.data.matches import fetch_upcoming_matches, parse_utc_datetime, convert_to_local_time
from src.data.standings import fetch_standings
from src.analysis.player_team_analysis import predict_player_team_matchup

logger = logging.getLogger(__name__)


class PredictionError(Exception):
    """Exception raised for errors in the prediction module."""
    pass


def predict_upcoming_matches(hours_ahead: int = 24, tournament_id: int = 1) -> List[Dict[str, Any]]:
    """
    Predict outcomes for upcoming matches.
    
    Args:
        hours_ahead: Number of hours ahead to fetch matches for (default: 24)
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        List of matches with predictions
        
    Raises:
        PredictionError: If there is an error making predictions
    """
    try:
        # Fetch upcoming matches
        upcoming_matches = fetch_upcoming_matches(hours_ahead=hours_ahead, tournament_id=tournament_id)
        
        # Fetch standings data for player information
        standings_data = fetch_standings(tournament_id=tournament_id)
        
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
                prediction = predict_player_team_matchup(
                    home_player_id,
                    away_player_id,
                    home_team,
                    away_team,
                    tournament_id
                )
                
                # Format match time
                fixture_start = match.get('fixtureStart')
                utc_dt = parse_utc_datetime(fixture_start)
                local_dt = convert_to_local_time(utc_dt) if utc_dt else None
                
                # Add match information to prediction
                prediction_with_match = {
                    'match_id': match.get('fixtureId'),
                    'fixture_start': fixture_start,
                    'local_time': local_dt.strftime('%Y-%m-%d %I:%M %p') if local_dt else 'Unknown',
                    'home_player_id': home_player_id,
                    'home_player_name': match.get('homeParticipantName'),
                    'away_player_id': away_player_id,
                    'away_player_name': match.get('awayParticipantName'),
                    'home_team': home_team,
                    'away_team': away_team,
                    'prediction': prediction.get('prediction', {})
                }
                
                predictions.append(prediction_with_match)
                
            except Exception as e:
                logger.warning(f"Could not make prediction for match {match.get('fixtureId')}: {e}")
                continue
        
        return predictions
    
    except Exception as e:
        logger.error(f"Error predicting upcoming matches: {e}")
        raise PredictionError(f"Failed to predict upcoming matches: {e}") from e


def get_high_confidence_predictions(predictions: List[Dict[str, Any]], min_confidence: float = 0.5) -> List[Dict[str, Any]]:
    """
    Filter predictions to only include those with high confidence.
    
    Args:
        predictions: List of match predictions
        min_confidence: Minimum confidence threshold (default: 0.5)
        
    Returns:
        List of high-confidence predictions
    """
    high_confidence = []
    
    for prediction in predictions:
        confidence = prediction.get('prediction', {}).get('confidence', 0)
        
        if confidence >= min_confidence:
            high_confidence.append(prediction)
    
    return high_confidence


def get_predictions_for_player(predictions: List[Dict[str, Any]], player_id: int) -> List[Dict[str, Any]]:
    """
    Filter predictions to only include matches involving a specific player.
    
    Args:
        predictions: List of match predictions
        player_id: The player's ID
        
    Returns:
        List of predictions for the player
    """
    player_predictions = []
    
    for prediction in predictions:
        home_player_id = prediction.get('home_player_id')
        away_player_id = prediction.get('away_player_id')
        
        if home_player_id == player_id or away_player_id == player_id:
            player_predictions.append(prediction)
    
    return player_predictions


def get_predictions_for_date(predictions: List[Dict[str, Any]], date: datetime) -> List[Dict[str, Any]]:
    """
    Filter predictions to only include matches on a specific date.
    
    Args:
        predictions: List of match predictions
        date: The date to filter by
        
    Returns:
        List of predictions for the date
    """
    date_predictions = []
    date_str = date.strftime('%Y-%m-%d')
    
    for prediction in predictions:
        local_time = prediction.get('local_time', '')
        
        if local_time.startswith(date_str):
            date_predictions.append(prediction)
    
    return date_predictions
