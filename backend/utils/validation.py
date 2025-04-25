"""
Validation utility functions for the 2K Flash application.
"""

import json
import os
from pathlib import Path


def validate_json_file(file_path):
    """
    Validate that a file exists and contains valid JSON.

    Args:
        file_path (str or Path): Path to the JSON file

    Returns:
        bool: True if the file exists and contains valid JSON, False otherwise
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False


def validate_match_data(match):
    """
    Validate that a match data dictionary contains all required fields.

    Args:
        match (dict): Match data dictionary

    Returns:
        bool: True if the match data is valid, False otherwise
    """
    # Check for required fields in the H2H GG League API format
    required_fields = [
        'fixtureId',  # or 'id'
        'homeParticipantId',
        'homeParticipantName',
        'awayParticipantId',
        'awayParticipantName',
        'homeTeamId',
        'homeTeamName',
        'awayTeamId',
        'awayTeamName',
        'fixtureStart'
    ]

    # Map API fields to our expected format
    field_mapping = {
        'fixtureId': ['fixtureId', 'id'],
        'homeParticipantId': ['homeParticipantId'],
        'homeParticipantName': ['homeParticipantName'],
        'awayParticipantId': ['awayParticipantId'],
        'awayParticipantName': ['awayParticipantName'],
        'homeTeamId': ['homeTeamId'],
        'homeTeamName': ['homeTeamName'],
        'awayTeamId': ['awayTeamId'],
        'awayTeamName': ['awayTeamName'],
        'fixtureStart': ['fixtureStart']
    }

    # Check that all required fields are present using the mapping
    for field, possible_names in field_mapping.items():
        field_present = False
        for name in possible_names:
            if name in match:
                field_present = True
                break
        if not field_present:
            return False

    # For completed matches, check that scores are present
    if 'result' in match or 'matchEnded' in match:
        if 'homeScore' not in match or 'awayScore' not in match:
            return False

    return True


def validate_player_stats(player_stats):
    """
    Validate that a player stats dictionary contains all required fields.

    Args:
        player_stats (dict): Player stats dictionary

    Returns:
        bool: True if the player stats are valid, False otherwise
    """
    required_fields = [
        'player_name',
        'total_matches',
        'wins',
        'losses',
        'total_score',
        'win_rate',
        'avg_score',
        'teams_used',
        'opponents_faced'
    ]

    # Check that all required fields are present
    for field in required_fields:
        if field not in player_stats:
            return False

    return True


def validate_prediction(prediction):
    """
    Validate that a prediction dictionary contains all required fields.

    Args:
        prediction (dict): Prediction dictionary

    Returns:
        bool: True if the prediction is valid, False otherwise
    """
    required_fields = [
        'fixtureId',
        'homePlayer',
        'awayPlayer',
        'homeTeam',
        'awayTeam',
        'fixtureStart',
        'prediction',
        'score_prediction'
    ]

    # Check that all required fields are present
    for field in required_fields:
        if field not in prediction:
            return False

    # Check that prediction object has required fields
    prediction_fields = [
        'home_win_probability',
        'away_win_probability',
        'predicted_winner',
        'confidence'
    ]

    for field in prediction_fields:
        if field not in prediction['prediction']:
            return False

    # Check that score prediction object has required fields
    score_fields = [
        'home_score',
        'away_score',
        'total_score'
    ]

    for field in score_fields:
        if field not in prediction['score_prediction']:
            return False

    return True
