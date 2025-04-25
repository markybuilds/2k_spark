"""
Player statistics processor for match data.
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from config.settings import PLAYER_STATS_FILE
from config.logging_config import get_data_fetcher_logger
from utils.logging import log_execution_time, log_exceptions

logger = get_data_fetcher_logger()


class PlayerStatsProcessor:
    """
    Processes match data to calculate player statistics.
    """

    def __init__(self, output_file=PLAYER_STATS_FILE):
        """
        Initialize the PlayerStatsProcessor.

        Args:
            output_file (str or Path): Output file path
        """
        self.output_file = Path(output_file)

    @log_execution_time(logger)
    @log_exceptions(logger)
    def calculate_player_stats(self, matches, save_to_file=True):
        """
        Calculate player statistics from match data.

        Args:
            matches (list): List of match data dictionaries
            save_to_file (bool): Whether to save the stats to a file

        Returns:
            dict: Dictionary of player statistics
        """
        logger.info(f"Calculating player statistics from {len(matches)} matches")

        # Initialize player stats dictionary
        player_stats = {}

        # Process each match
        for match in matches:
            # Skip matches without scores (upcoming matches)
            if 'homeScore' not in match or 'awayScore' not in match:
                continue

            # Extract match data
            home_player_id = str(match['homePlayer']['id'])
            home_player_name = match['homePlayer']['name']
            away_player_id = str(match['awayPlayer']['id'])
            away_player_name = match['awayPlayer']['name']

            home_team_id = str(match['homeTeam']['id'])
            home_team_name = match['homeTeam']['name']
            away_team_id = str(match['awayTeam']['id'])
            away_team_name = match['awayTeam']['name']

            home_score = match['homeScore']
            away_score = match['awayScore']

            # Determine winner
            home_win = home_score > away_score

            # Update home player stats
            if home_player_id not in player_stats:
                player_stats[home_player_id] = {
                    'player_name': home_player_name,
                    'total_matches': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_score': 0,
                    'scores_list': [],  # List of all scores for variance calculation
                    'last_5_matches': [],  # Recent matches data
                    'teams_used': {},
                    'opponents_faced': {},
                    'match_history': []  # Detailed match history
                }

            # Update home player match data
            player_stats[home_player_id]['total_matches'] += 1
            player_stats[home_player_id]['total_score'] += home_score
            player_stats[home_player_id]['scores_list'].append(home_score)

            # Add match to history with timestamp if available
            match_date = match.get('date') or match.get('startTime', '').split('T')[0] if 'startTime' in match else None
            match_info = {
                'date': match_date,
                'opponent_id': away_player_id,
                'opponent_name': away_player_name,
                'team_id': home_team_id,
                'team_name': home_team_name,
                'score': home_score,
                'opponent_score': away_score,
                'win': home_win
            }
            player_stats[home_player_id]['match_history'].append(match_info)

            # Update last 5 matches (keep only the most recent 5)
            player_stats[home_player_id]['last_5_matches'].append(match_info)
            if len(player_stats[home_player_id]['last_5_matches']) > 5:
                player_stats[home_player_id]['last_5_matches'] = player_stats[home_player_id]['last_5_matches'][-5:]

            if home_win:
                player_stats[home_player_id]['wins'] += 1
            else:
                player_stats[home_player_id]['losses'] += 1

            # Update team usage stats
            if home_team_id not in player_stats[home_player_id]['teams_used']:
                player_stats[home_player_id]['teams_used'][home_team_id] = {
                    'team_name': home_team_name,
                    'matches': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_score': 0
                }

            # Update team stats
            player_stats[home_player_id]['teams_used'][home_team_id]['matches'] += 1
            player_stats[home_player_id]['teams_used'][home_team_id]['total_score'] += home_score

            if home_win:
                player_stats[home_player_id]['teams_used'][home_team_id]['wins'] += 1
            else:
                player_stats[home_player_id]['teams_used'][home_team_id]['losses'] += 1

            # Update opponent stats
            if away_player_id not in player_stats[home_player_id]['opponents_faced']:
                player_stats[home_player_id]['opponents_faced'][away_player_id] = {
                    'matches': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_score': 0,
                    'scores_against': []
                }

            player_stats[home_player_id]['opponents_faced'][away_player_id]['matches'] += 1
            player_stats[home_player_id]['opponents_faced'][away_player_id]['total_score'] += home_score
            player_stats[home_player_id]['opponents_faced'][away_player_id]['scores_against'].append(away_score)
            if home_win:
                player_stats[home_player_id]['opponents_faced'][away_player_id]['wins'] += 1
            else:
                player_stats[home_player_id]['opponents_faced'][away_player_id]['losses'] += 1

            # Update away player stats (similar to home player)
            if away_player_id not in player_stats:
                player_stats[away_player_id] = {
                    'player_name': away_player_name,
                    'total_matches': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_score': 0,
                    'scores_list': [],  # List of all scores for variance calculation
                    'last_5_matches': [],  # Recent matches data
                    'teams_used': {},
                    'opponents_faced': {},
                    'match_history': []  # Detailed match history
                }

            # Update away player match data
            player_stats[away_player_id]['total_matches'] += 1
            player_stats[away_player_id]['total_score'] += away_score
            player_stats[away_player_id]['scores_list'].append(away_score)

            # Add match to history with timestamp if available
            match_date = match.get('date') or match.get('startTime', '').split('T')[0] if 'startTime' in match else None
            match_info = {
                'date': match_date,
                'opponent_id': home_player_id,
                'opponent_name': home_player_name,
                'team_id': away_team_id,
                'team_name': away_team_name,
                'score': away_score,
                'opponent_score': home_score,
                'win': not home_win
            }
            player_stats[away_player_id]['match_history'].append(match_info)

            # Update last 5 matches (keep only the most recent 5)
            player_stats[away_player_id]['last_5_matches'].append(match_info)
            if len(player_stats[away_player_id]['last_5_matches']) > 5:
                player_stats[away_player_id]['last_5_matches'] = player_stats[away_player_id]['last_5_matches'][-5:]

            if not home_win:
                player_stats[away_player_id]['wins'] += 1
            else:
                player_stats[away_player_id]['losses'] += 1

            # Update team usage stats
            if away_team_id not in player_stats[away_player_id]['teams_used']:
                player_stats[away_player_id]['teams_used'][away_team_id] = {
                    'team_name': away_team_name,
                    'matches': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_score': 0
                }

            # Update team stats
            player_stats[away_player_id]['teams_used'][away_team_id]['matches'] += 1
            player_stats[away_player_id]['teams_used'][away_team_id]['total_score'] += away_score

            if not home_win:
                player_stats[away_player_id]['teams_used'][away_team_id]['wins'] += 1
            else:
                player_stats[away_player_id]['teams_used'][away_team_id]['losses'] += 1

            # Update opponent stats
            if home_player_id not in player_stats[away_player_id]['opponents_faced']:
                player_stats[away_player_id]['opponents_faced'][home_player_id] = {
                    'matches': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_score': 0,
                    'scores_against': []
                }

            player_stats[away_player_id]['opponents_faced'][home_player_id]['matches'] += 1
            player_stats[away_player_id]['opponents_faced'][home_player_id]['total_score'] += away_score
            player_stats[away_player_id]['opponents_faced'][home_player_id]['scores_against'].append(home_score)
            if not home_win:
                player_stats[away_player_id]['opponents_faced'][home_player_id]['wins'] += 1
            else:
                player_stats[away_player_id]['opponents_faced'][home_player_id]['losses'] += 1

        # Calculate derived stats
        for player_id, stats in player_stats.items():
            # Calculate win rate
            stats['win_rate'] = stats['wins'] / stats['total_matches'] if stats['total_matches'] > 0 else 0

            # Calculate average score
            stats['avg_score'] = stats['total_score'] / stats['total_matches'] if stats['total_matches'] > 0 else 0

            # Calculate score variance (consistency)
            scores_list = stats.get('scores_list', [])
            stats['score_variance'] = float(np.var(scores_list)) if len(scores_list) > 1 else 0
            stats['score_std'] = float(np.std(scores_list)) if len(scores_list) > 1 else 0

            # Calculate recent form (last 5 matches)
            last_5_matches = stats.get('last_5_matches', [])
            if last_5_matches:
                recent_wins = sum(1 for match in last_5_matches if match.get('win', False))
                recent_total = len(last_5_matches)
                stats['recent_win_rate'] = recent_wins / recent_total if recent_total > 0 else 0

                recent_scores = [match.get('score', 0) for match in last_5_matches]
                stats['recent_avg_score'] = sum(recent_scores) / len(recent_scores) if recent_scores else 0
            else:
                stats['recent_win_rate'] = 0
                stats['recent_avg_score'] = 0

            # Calculate momentum (trend in performance)
            if len(last_5_matches) >= 2:
                # Weight more recent matches higher
                weighted_sum = 0
                weight_sum = 0
                for i, match in enumerate(last_5_matches):
                    weight = i + 1  # More recent matches have higher weight
                    weighted_sum += weight * (1 if match.get('win', False) else 0)
                    weight_sum += weight

                weighted_win_rate = weighted_sum / weight_sum if weight_sum > 0 else 0
                stats['momentum'] = weighted_win_rate - stats['recent_win_rate']
            else:
                stats['momentum'] = 0

            # Calculate team-specific stats
            for team_id, team_stats in stats['teams_used'].items():
                team_matches = team_stats['matches']
                team_stats['win_rate'] = team_stats['wins'] / team_matches if team_matches > 0 else 0
                team_stats['avg_score'] = team_stats['total_score'] / team_matches if team_matches > 0 else 0

            # Calculate opponent-specific stats
            for opponent_id, opponent_stats in stats['opponents_faced'].items():
                opponent_matches = opponent_stats['matches']
                opponent_stats['win_rate'] = opponent_stats['wins'] / opponent_matches if opponent_matches > 0 else 0

                # Calculate average score against this opponent
                opponent_stats['avg_score'] = opponent_stats['total_score'] / opponent_matches if opponent_matches > 0 else 0

                # Calculate average score conceded against this opponent
                scores_against = opponent_stats.get('scores_against', [])
                opponent_stats['avg_score_against'] = sum(scores_against) / len(scores_against) if scores_against else 0

        logger.info(f"Successfully calculated statistics for {len(player_stats)} players")

        # Save to file if requested
        if save_to_file:
            self._save_to_file(player_stats)

        return player_stats

    @log_exceptions(logger)
    def _save_to_file(self, player_stats):
        """
        Save player statistics to a file.

        Args:
            player_stats (dict): Dictionary of player statistics
        """
        logger.info(f"Saving player statistics for {len(player_stats)} players to {self.output_file}")

        # Create directory if it doesn't exist
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(player_stats, f, indent=2)

        logger.info(f"Successfully saved player statistics to {self.output_file}")

    @log_exceptions(logger)
    def load_from_file(self):
        """
        Load player statistics from a file.

        Returns:
            dict: Dictionary of player statistics
        """
        logger.info(f"Loading player statistics from {self.output_file}")

        if not self.output_file.exists():
            logger.warning(f"Player statistics file {self.output_file} does not exist")
            return {}

        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                player_stats = json.load(f)

            logger.info(f"Successfully loaded statistics for {len(player_stats)} players from {self.output_file}")
            return player_stats

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error loading player statistics from file: {str(e)}")
            return {}
