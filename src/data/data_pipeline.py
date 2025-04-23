"""
Data pipeline module for NBA 2K eSports prediction model.

This module provides functions to collect, process, and store data for the prediction model.
"""
import os
import json
import logging
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from src.data.matches import fetch_matches
from src.data.standings import fetch_standings
from src.analysis.player_team_analysis import get_player_team_history
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)


class DataPipelineError(Exception):
    """Exception raised for errors in the data pipeline module."""
    pass


def collect_historical_data(
    start_date: str,
    end_date: str,
    tournament_id: int = 1,
    save_to_file: bool = True
) -> Dict[str, Any]:
    """
    Collect historical match and standings data.
    
    Args:
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        tournament_id: The tournament ID (default: 1)
        save_to_file: Whether to save the data to files (default: True)
        
    Returns:
        Dictionary with collected data
        
    Raises:
        DataPipelineError: If there is an error collecting the data
    """
    try:
        logger.info(f"Collecting historical data from {start_date} to {end_date}")
        
        # Fetch match data
        matches = fetch_matches(
            schedule_type="match",
            from_date=start_date,
            to_date=end_date,
            tournament_id=tournament_id
        )
        
        # Fetch standings data
        standings = fetch_standings(tournament_id)
        
        # Create data dictionary
        data = {
            'matches': matches,
            'standings': standings,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'tournament_id': tournament_id,
                'collection_time': datetime.now().isoformat(),
                'match_count': len(matches),
                'player_count': len(standings)
            }
        }
        
        # Save to file if requested
        if save_to_file:
            # Ensure directories exist
            os.makedirs(RAW_DATA_DIR, exist_ok=True)
            
            # Create filenames
            matches_filename = f"matches_{start_date}_to_{end_date}.json"
            standings_filename = f"standings_{datetime.now().strftime('%Y%m%d')}.json"
            metadata_filename = f"metadata_{start_date}_to_{end_date}.json"
            
            # Save files
            with open(os.path.join(RAW_DATA_DIR, matches_filename), 'w') as f:
                json.dump(matches, f, indent=2)
            
            with open(os.path.join(RAW_DATA_DIR, standings_filename), 'w') as f:
                json.dump(standings, f, indent=2)
            
            with open(os.path.join(RAW_DATA_DIR, metadata_filename), 'w') as f:
                json.dump(data['metadata'], f, indent=2)
            
            logger.info(f"Saved {len(matches)} matches to {matches_filename}")
            logger.info(f"Saved {len(standings)} player standings to {standings_filename}")
        
        return data
    
    except Exception as e:
        logger.error(f"Error collecting historical data: {e}")
        raise DataPipelineError(f"Failed to collect historical data: {e}") from e


def collect_player_team_data(
    player_ids: List[int],
    tournament_id: int = 1,
    save_to_file: bool = True
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Collect player-team data for specific players.
    
    Args:
        player_ids: List of player IDs
        tournament_id: The tournament ID (default: 1)
        save_to_file: Whether to save the data to files (default: True)
        
    Returns:
        Dictionary mapping player IDs to their match history
        
    Raises:
        DataPipelineError: If there is an error collecting the data
    """
    try:
        logger.info(f"Collecting player-team data for {len(player_ids)} players")
        
        # Fetch player data
        player_data = {}
        
        for player_id in player_ids:
            try:
                # Get player's match history
                matches = get_player_team_history(player_id, tournament_id)
                player_data[player_id] = matches
                
                logger.info(f"Collected {len(matches)} matches for player ID {player_id}")
                
                # Save to file if requested
                if save_to_file:
                    # Ensure directory exists
                    os.makedirs(RAW_DATA_DIR, exist_ok=True)
                    
                    # Create filename
                    filename = f"player_{player_id}_matches.json"
                    
                    # Save file
                    with open(os.path.join(RAW_DATA_DIR, filename), 'w') as f:
                        json.dump(matches, f, indent=2)
                    
                    logger.info(f"Saved player data to {filename}")
            
            except Exception as e:
                logger.warning(f"Error collecting data for player ID {player_id}: {e}")
                continue
        
        return player_data
    
    except Exception as e:
        logger.error(f"Error collecting player-team data: {e}")
        raise DataPipelineError(f"Failed to collect player-team data: {e}") from e


def process_match_data(
    matches: List[Dict[str, Any]],
    save_to_file: bool = True
) -> pd.DataFrame:
    """
    Process raw match data into a structured DataFrame.
    
    Args:
        matches: List of match data dictionaries
        save_to_file: Whether to save the processed data to a file (default: True)
        
    Returns:
        DataFrame with processed match data
        
    Raises:
        DataPipelineError: If there is an error processing the data
    """
    try:
        logger.info(f"Processing {len(matches)} matches")
        
        # Create list to store processed matches
        processed_matches = []
        
        for match in matches:
            try:
                # Extract basic match information
                match_id = match.get('matchId')
                start_date = match.get('startDate')
                
                if not match_id or not start_date:
                    continue
                
                # Extract home player information
                home_player_id = match.get('homeParticipantId')
                home_player_name = match.get('homeParticipantName')
                home_team = match.get('homeTeamName')
                home_score = match.get('homeScore')
                
                # Extract away player information
                away_player_id = match.get('awayParticipantId')
                away_player_name = match.get('awayParticipantName')
                away_team = match.get('awayTeamName')
                away_score = match.get('awayScore')
                
                # Determine winner
                result = match.get('result')
                
                if result == 'home_win':
                    winner_id = home_player_id
                    winner_name = home_player_name
                    winner_team = home_team
                    winner_score = home_score
                    loser_id = away_player_id
                    loser_name = away_player_name
                    loser_team = away_team
                    loser_score = away_score
                else:
                    winner_id = away_player_id
                    winner_name = away_player_name
                    winner_team = away_team
                    winner_score = away_score
                    loser_id = home_player_id
                    loser_name = home_player_name
                    loser_team = home_team
                    loser_score = home_score
                
                # Create processed match dictionary
                processed_match = {
                    'match_id': match_id,
                    'start_date': start_date,
                    'home_player_id': home_player_id,
                    'home_player_name': home_player_name,
                    'home_team': home_team,
                    'home_score': home_score,
                    'away_player_id': away_player_id,
                    'away_player_name': away_player_name,
                    'away_team': away_team,
                    'away_score': away_score,
                    'result': result,
                    'winner_id': winner_id,
                    'winner_name': winner_name,
                    'winner_team': winner_team,
                    'winner_score': winner_score,
                    'loser_id': loser_id,
                    'loser_name': loser_name,
                    'loser_team': loser_team,
                    'loser_score': loser_score,
                    'score_difference': winner_score - loser_score if winner_score is not None and loser_score is not None else None
                }
                
                processed_matches.append(processed_match)
            
            except Exception as e:
                logger.warning(f"Error processing match {match.get('matchId')}: {e}")
                continue
        
        # Create DataFrame
        df = pd.DataFrame(processed_matches)
        
        # Convert date column to datetime
        if 'start_date' in df.columns:
            df['start_date'] = pd.to_datetime(df['start_date'])
        
        # Save to file if requested
        if save_to_file:
            # Ensure directory exists
            os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
            
            # Create filename
            filename = f"processed_matches_{datetime.now().strftime('%Y%m%d')}.csv"
            
            # Save file
            df.to_csv(os.path.join(PROCESSED_DATA_DIR, filename), index=False)
            
            logger.info(f"Saved processed match data to {filename}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error processing match data: {e}")
        raise DataPipelineError(f"Failed to process match data: {e}") from e


def create_player_team_features(
    player_data: Dict[int, List[Dict[str, Any]]],
    save_to_file: bool = True
) -> pd.DataFrame:
    """
    Create features for player-team combinations.
    
    Args:
        player_data: Dictionary mapping player IDs to their match history
        save_to_file: Whether to save the features to a file (default: True)
        
    Returns:
        DataFrame with player-team features
        
    Raises:
        DataPipelineError: If there is an error creating the features
    """
    try:
        logger.info(f"Creating player-team features for {len(player_data)} players")
        
        # Create list to store player-team features
        player_team_features = []
        
        for player_id, matches in player_data.items():
            # Group matches by team
            team_matches = {}
            
            for match in matches:
                team = match.get('playerTeam')
                
                if not team:
                    continue
                
                if team not in team_matches:
                    team_matches[team] = []
                
                team_matches[team].append(match)
            
            # Calculate features for each team
            for team, team_match_list in team_matches.items():
                if len(team_match_list) < 3:
                    continue  # Skip teams with too few matches
                
                # Calculate basic statistics
                total_matches = len(team_match_list)
                wins = sum(1 for match in team_match_list if match.get('playerWon'))
                losses = total_matches - wins
                win_rate = wins / total_matches if total_matches > 0 else 0
                
                # Calculate scoring statistics
                scores = [match.get('playerScore') for match in team_match_list if match.get('playerScore') is not None]
                opponent_scores = [match.get('opponentScore') for match in team_match_list if match.get('opponentScore') is not None]
                
                avg_score = sum(scores) / len(scores) if scores else 0
                avg_opponent_score = sum(opponent_scores) / len(opponent_scores) if opponent_scores else 0
                avg_score_diff = avg_score - avg_opponent_score
                
                # Calculate recent performance (last 5 matches)
                recent_matches = sorted(team_match_list, key=lambda x: x.get('startDate', ''), reverse=True)[:5]
                recent_wins = sum(1 for match in recent_matches if match.get('playerWon'))
                recent_win_rate = recent_wins / len(recent_matches) if recent_matches else 0
                
                # Create feature dictionary
                feature = {
                    'player_id': player_id,
                    'team': team,
                    'total_matches': total_matches,
                    'wins': wins,
                    'losses': losses,
                    'win_rate': win_rate,
                    'avg_score': avg_score,
                    'avg_opponent_score': avg_opponent_score,
                    'avg_score_diff': avg_score_diff,
                    'recent_win_rate': recent_win_rate,
                    'last_updated': datetime.now().isoformat()
                }
                
                player_team_features.append(feature)
        
        # Create DataFrame
        df = pd.DataFrame(player_team_features)
        
        # Save to file if requested
        if save_to_file:
            # Ensure directory exists
            os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
            
            # Create filename
            filename = f"player_team_features_{datetime.now().strftime('%Y%m%d')}.csv"
            
            # Save file
            df.to_csv(os.path.join(PROCESSED_DATA_DIR, filename), index=False)
            
            logger.info(f"Saved player-team features to {filename}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error creating player-team features: {e}")
        raise DataPipelineError(f"Failed to create player-team features: {e}") from e


def create_head_to_head_features(
    matches: List[Dict[str, Any]],
    save_to_file: bool = True
) -> pd.DataFrame:
    """
    Create features for head-to-head matchups between players.
    
    Args:
        matches: List of match data dictionaries
        save_to_file: Whether to save the features to a file (default: True)
        
    Returns:
        DataFrame with head-to-head features
        
    Raises:
        DataPipelineError: If there is an error creating the features
    """
    try:
        logger.info(f"Creating head-to-head features from {len(matches)} matches")
        
        # Create dictionary to store head-to-head matchups
        h2h_matchups = {}
        
        for match in matches:
            home_player_id = match.get('homeParticipantId')
            away_player_id = match.get('awayParticipantId')
            
            if not home_player_id or not away_player_id:
                continue
            
            # Create a unique key for the matchup (smaller ID first)
            if home_player_id < away_player_id:
                matchup_key = f"{home_player_id}_{away_player_id}"
                player1_id = home_player_id
                player2_id = away_player_id
            else:
                matchup_key = f"{away_player_id}_{home_player_id}"
                player1_id = away_player_id
                player2_id = home_player_id
            
            # Initialize matchup if not exists
            if matchup_key not in h2h_matchups:
                h2h_matchups[matchup_key] = {
                    'player1_id': player1_id,
                    'player2_id': player2_id,
                    'matches': [],
                    'player1_wins': 0,
                    'player2_wins': 0
                }
            
            # Add match to matchup
            h2h_matchups[matchup_key]['matches'].append(match)
            
            # Update win counts
            result = match.get('result')
            
            if result == 'home_win':
                if home_player_id == player1_id:
                    h2h_matchups[matchup_key]['player1_wins'] += 1
                else:
                    h2h_matchups[matchup_key]['player2_wins'] += 1
            else:  # away_win
                if away_player_id == player1_id:
                    h2h_matchups[matchup_key]['player1_wins'] += 1
                else:
                    h2h_matchups[matchup_key]['player2_wins'] += 1
        
        # Create list to store head-to-head features
        h2h_features = []
        
        for matchup_key, matchup_data in h2h_matchups.items():
            player1_id = matchup_data['player1_id']
            player2_id = matchup_data['player2_id']
            matches_list = matchup_data['matches']
            player1_wins = matchup_data['player1_wins']
            player2_wins = matchup_data['player2_wins']
            
            total_matches = len(matches_list)
            
            if total_matches < 3:
                continue  # Skip matchups with too few matches
            
            # Calculate win rates
            player1_win_rate = player1_wins / total_matches if total_matches > 0 else 0
            player2_win_rate = player2_wins / total_matches if total_matches > 0 else 0
            
            # Calculate team-specific matchups
            team_matchups = {}
            
            for match in matches_list:
                home_player_id = match.get('homeParticipantId')
                away_player_id = match.get('awayParticipantId')
                home_team = match.get('homeTeamName')
                away_team = match.get('awayTeamName')
                
                if not home_team or not away_team:
                    continue
                
                # Create a unique key for the team matchup
                if home_player_id == player1_id:
                    team_matchup_key = f"{home_team}_{away_team}"
                    player1_team = home_team
                    player2_team = away_team
                else:
                    team_matchup_key = f"{away_team}_{home_team}"
                    player1_team = away_team
                    player2_team = home_team
                
                # Initialize team matchup if not exists
                if team_matchup_key not in team_matchups:
                    team_matchups[team_matchup_key] = {
                        'player1_team': player1_team,
                        'player2_team': player2_team,
                        'matches': 0,
                        'player1_wins': 0,
                        'player2_wins': 0
                    }
                
                # Update team matchup
                team_matchups[team_matchup_key]['matches'] += 1
                
                result = match.get('result')
                
                if result == 'home_win':
                    if home_player_id == player1_id:
                        team_matchups[team_matchup_key]['player1_wins'] += 1
                    else:
                        team_matchups[team_matchup_key]['player2_wins'] += 1
                else:  # away_win
                    if away_player_id == player1_id:
                        team_matchups[team_matchup_key]['player1_wins'] += 1
                    else:
                        team_matchups[team_matchup_key]['player2_wins'] += 1
            
            # Create feature dictionary
            feature = {
                'player1_id': player1_id,
                'player2_id': player2_id,
                'total_matches': total_matches,
                'player1_wins': player1_wins,
                'player2_wins': player2_wins,
                'player1_win_rate': player1_win_rate,
                'player2_win_rate': player2_win_rate,
                'team_matchups': team_matchups,
                'last_updated': datetime.now().isoformat()
            }
            
            h2h_features.append(feature)
        
        # Create DataFrame (excluding team_matchups which is a nested dictionary)
        df_data = []
        
        for feature in h2h_features:
            feature_copy = feature.copy()
            feature_copy.pop('team_matchups')
            df_data.append(feature_copy)
        
        df = pd.DataFrame(df_data)
        
        # Save to file if requested
        if save_to_file:
            # Ensure directory exists
            os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
            
            # Create filename
            filename = f"head_to_head_features_{datetime.now().strftime('%Y%m%d')}.csv"
            
            # Save file
            df.to_csv(os.path.join(PROCESSED_DATA_DIR, filename), index=False)
            
            # Also save the full features with team matchups as JSON
            json_filename = f"head_to_head_features_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(os.path.join(PROCESSED_DATA_DIR, json_filename), 'w') as f:
                json.dump(h2h_features, f, indent=2)
            
            logger.info(f"Saved head-to-head features to {filename} and {json_filename}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error creating head-to-head features: {e}")
        raise DataPipelineError(f"Failed to create head-to-head features: {e}") from e


def run_full_pipeline(
    start_date: str,
    end_date: str,
    tournament_id: int = 1
) -> Dict[str, Any]:
    """
    Run the full data pipeline.
    
    Args:
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        tournament_id: The tournament ID (default: 1)
        
    Returns:
        Dictionary with pipeline results
        
    Raises:
        DataPipelineError: If there is an error running the pipeline
    """
    try:
        logger.info(f"Running full data pipeline from {start_date} to {end_date}")
        
        # Step 1: Collect historical data
        data = collect_historical_data(start_date, end_date, tournament_id)
        
        # Step 2: Process match data
        processed_matches = process_match_data(data['matches'])
        
        # Step 3: Collect player-team data for all players in standings
        player_ids = [player.get('participantId') for player in data['standings'] if player.get('participantId')]
        player_data = collect_player_team_data(player_ids, tournament_id)
        
        # Step 4: Create player-team features
        player_team_features = create_player_team_features(player_data)
        
        # Step 5: Create head-to-head features
        h2h_features = create_head_to_head_features(data['matches'])
        
        # Return pipeline results
        return {
            'raw_data': data,
            'processed_matches': processed_matches,
            'player_team_features': player_team_features,
            'head_to_head_features': h2h_features,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'tournament_id': tournament_id,
                'pipeline_run_time': datetime.now().isoformat(),
                'match_count': len(data['matches']),
                'player_count': len(data['standings']),
                'processed_match_count': len(processed_matches),
                'player_team_feature_count': len(player_team_features),
                'head_to_head_feature_count': len(h2h_features)
            }
        }
    
    except Exception as e:
        logger.error(f"Error running full data pipeline: {e}")
        raise DataPipelineError(f"Failed to run full data pipeline: {e}") from e
