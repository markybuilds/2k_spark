"""
Feature engineering module for prediction models.
"""

import numpy as np
from datetime import datetime
from collections import defaultdict

from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions

logger = get_model_tuning_logger()


class FeatureEngineer:
    """
    Feature engineering for prediction models.
    """
    
    def __init__(self, feature_config=None):
        """
        Initialize the feature engineer.
        
        Args:
            feature_config (dict): Feature configuration dictionary
        """
        self.feature_config = feature_config or {
            "use_basic_features": True,
            "use_team_features": True,
            "use_h2h_features": True,
            "use_recent_form": True,
            "use_advanced_features": True,
            "use_temporal_features": True,
            "recent_matches_window": 5
        }
    
    @log_execution_time(logger)
    @log_exceptions(logger)
    def extract_features(self, player_stats, matches, for_score_prediction=True):
        """
        Extract features from match data.
        
        Args:
            player_stats (dict): Player statistics dictionary
            matches (list): List of match data dictionaries
            for_score_prediction (bool): Whether to extract features for score prediction
            
        Returns:
            tuple: Features and labels
        """
        features = []
        
        if for_score_prediction:
            home_scores = []
            away_scores = []
        else:
            labels = []
        
        # Process each match
        for match in matches:
            # Skip matches without scores
            if 'homeScore' not in match or 'awayScore' not in match:
                continue
            
            # Extract player and team IDs
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            # Skip if player stats not available
            if home_player_id not in player_stats or away_player_id not in player_stats:
                continue
            
            home_player = player_stats[home_player_id]
            away_player = player_stats[away_player_id]
            
            home_team_id = str(match['homeTeam']['id'])
            away_team_id = str(match['awayTeam']['id'])
            
            # Get match date
            match_date = self._parse_match_date(match)
            
            # Get previous matches before this one
            prev_matches = self._get_previous_matches(matches, match, match_date)
            
            # Extract features
            match_features = []
            
            # Basic player features
            if self.feature_config["use_basic_features"]:
                basic_features = self._extract_basic_features(home_player, away_player)
                match_features.extend(basic_features)
            
            # Team-specific features
            if self.feature_config["use_team_features"]:
                team_features = self._extract_team_features(
                    home_player, away_player, home_team_id, away_team_id
                )
                match_features.extend(team_features)
            
            # Head-to-head features
            if self.feature_config["use_h2h_features"]:
                h2h_features = self._extract_h2h_features(
                    home_player, away_player, home_player_id, away_player_id
                )
                match_features.extend(h2h_features)
            
            # Recent form features
            if self.feature_config["use_recent_form"]:
                recent_form_features = self._extract_recent_form_features(
                    home_player_id, away_player_id, prev_matches, 
                    self.feature_config["recent_matches_window"]
                )
                match_features.extend(recent_form_features)
            
            # Advanced features
            if self.feature_config["use_advanced_features"]:
                advanced_features = self._extract_advanced_features(
                    home_player, away_player, home_team_id, away_team_id,
                    home_player_id, away_player_id, prev_matches
                )
                match_features.extend(advanced_features)
            
            # Temporal features
            if self.feature_config["use_temporal_features"]:
                temporal_features = self._extract_temporal_features(match_date, prev_matches)
                match_features.extend(temporal_features)
            
            features.append(match_features)
            
            # Extract labels
            if for_score_prediction:
                home_scores.append(match['homeScore'])
                away_scores.append(match['awayScore'])
            else:
                # 1 if home win, 0 if away win
                home_score = match['homeScore']
                away_score = match['awayScore']
                label = 1 if home_score > away_score else 0
                labels.append(label)
        
        if for_score_prediction:
            return np.array(features), np.array(home_scores), np.array(away_scores)
        else:
            return np.array(features), np.array(labels)
    
    @log_exceptions(logger)
    def _parse_match_date(self, match):
        """
        Parse match date from match data.
        
        Args:
            match (dict): Match data dictionary
            
        Returns:
            datetime: Match date
        """
        try:
            # Try to parse date from match data
            if 'date' in match:
                return datetime.strptime(match['date'], "%Y-%m-%d")
            elif 'startTime' in match:
                return datetime.strptime(match['startTime'].split('T')[0], "%Y-%m-%d")
            else:
                # Default to current date if not available
                return datetime.now()
        except (ValueError, TypeError):
            # Default to current date if parsing fails
            return datetime.now()
    
    @log_exceptions(logger)
    def _get_previous_matches(self, all_matches, current_match, current_date):
        """
        Get previous matches before the current match.
        
        Args:
            all_matches (list): List of all match data dictionaries
            current_match (dict): Current match data dictionary
            current_date (datetime): Current match date
            
        Returns:
            list: List of previous match data dictionaries
        """
        prev_matches = []
        
        for match in all_matches:
            # Skip matches without scores
            if 'homeScore' not in match or 'awayScore' not in match:
                continue
            
            # Skip the current match
            if match == current_match:
                continue
            
            # Get match date
            match_date = self._parse_match_date(match)
            
            # Only include matches before the current match
            if match_date < current_date:
                prev_matches.append(match)
        
        return prev_matches
    
    @log_exceptions(logger)
    def _extract_basic_features(self, home_player, away_player):
        """
        Extract basic player features.
        
        Args:
            home_player (dict): Home player statistics dictionary
            away_player (dict): Away player statistics dictionary
            
        Returns:
            list: Basic player features
        """
        return [
            # Player overall stats
            home_player.get('win_rate', 0),
            away_player.get('win_rate', 0),
            home_player.get('avg_score', 0),
            away_player.get('avg_score', 0),
            home_player.get('total_matches', 0),
            away_player.get('total_matches', 0)
        ]
    
    @log_exceptions(logger)
    def _extract_team_features(self, home_player, away_player, home_team_id, away_team_id):
        """
        Extract team-specific features.
        
        Args:
            home_player (dict): Home player statistics dictionary
            away_player (dict): Away player statistics dictionary
            home_team_id (str): Home team ID
            away_team_id (str): Away team ID
            
        Returns:
            list: Team-specific features
        """
        # Get team stats
        home_team_win_rate = self._get_team_win_rate(home_player, home_team_id)
        away_team_win_rate = self._get_team_win_rate(away_player, away_team_id)
        home_team_avg_score = self._get_team_avg_score(home_player, home_team_id)
        away_team_avg_score = self._get_team_avg_score(away_player, away_team_id)
        home_team_matches = self._get_team_matches(home_player, home_team_id)
        away_team_matches = self._get_team_matches(away_player, away_team_id)
        
        # Calculate team experience ratio (how often the player uses this team)
        home_team_exp_ratio = home_team_matches / max(home_player.get('total_matches', 1), 1)
        away_team_exp_ratio = away_team_matches / max(away_player.get('total_matches', 1), 1)
        
        # Calculate team performance relative to overall performance
        home_team_rel_win_rate = home_team_win_rate - home_player.get('win_rate', 0)
        away_team_rel_win_rate = away_team_win_rate - away_player.get('win_rate', 0)
        home_team_rel_avg_score = home_team_avg_score - home_player.get('avg_score', 0)
        away_team_rel_avg_score = away_team_avg_score - away_player.get('avg_score', 0)
        
        return [
            # Team-specific stats
            home_team_win_rate,
            away_team_win_rate,
            home_team_avg_score,
            away_team_avg_score,
            home_team_matches,
            away_team_matches,
            
            # Team experience ratio
            home_team_exp_ratio,
            away_team_exp_ratio,
            
            # Team performance relative to overall
            home_team_rel_win_rate,
            away_team_rel_win_rate,
            home_team_rel_avg_score,
            away_team_rel_avg_score
        ]
    
    @log_exceptions(logger)
    def _extract_h2h_features(self, home_player, away_player, home_player_id, away_player_id):
        """
        Extract head-to-head features.
        
        Args:
            home_player (dict): Home player statistics dictionary
            away_player (dict): Away player statistics dictionary
            home_player_id (str): Home player ID
            away_player_id (str): Away player ID
            
        Returns:
            list: Head-to-head features
        """
        # Get head-to-head stats
        home_h2h_win_rate = self._get_h2h_win_rate(home_player, away_player_id)
        away_h2h_win_rate = self._get_h2h_win_rate(away_player, home_player_id)
        home_h2h_matches = self._get_h2h_matches(home_player, away_player_id)
        away_h2h_matches = self._get_h2h_matches(away_player, home_player_id)
        
        # Calculate head-to-head score stats
        home_h2h_avg_score = self._get_avg_score_against(home_player, away_player_id)
        away_h2h_avg_score = self._get_avg_score_against(away_player, home_player_id)
        
        # Calculate head-to-head win rate difference
        h2h_win_rate_diff = home_h2h_win_rate - away_h2h_win_rate
        
        # Calculate head-to-head score difference
        h2h_score_diff = home_h2h_avg_score - away_h2h_avg_score
        
        return [
            # Head-to-head stats
            home_h2h_win_rate,
            away_h2h_win_rate,
            home_h2h_matches,
            away_h2h_matches,
            home_h2h_avg_score,
            away_h2h_avg_score,
            h2h_win_rate_diff,
            h2h_score_diff
        ]
    
    @log_exceptions(logger)
    def _extract_recent_form_features(self, home_player_id, away_player_id, prev_matches, window_size=5):
        """
        Extract recent form features.
        
        Args:
            home_player_id (str): Home player ID
            away_player_id (str): Away player ID
            prev_matches (list): List of previous match data dictionaries
            window_size (int): Number of recent matches to consider
            
        Returns:
            list: Recent form features
        """
        # Get recent matches for each player
        home_recent_matches = self._get_player_recent_matches(home_player_id, prev_matches, window_size)
        away_recent_matches = self._get_player_recent_matches(away_player_id, prev_matches, window_size)
        
        # Calculate recent win rates
        home_recent_win_rate = self._calculate_recent_win_rate(home_player_id, home_recent_matches)
        away_recent_win_rate = self._calculate_recent_win_rate(away_player_id, away_recent_matches)
        
        # Calculate recent average scores
        home_recent_avg_score = self._calculate_recent_avg_score(home_player_id, home_recent_matches)
        away_recent_avg_score = self._calculate_recent_avg_score(away_player_id, away_recent_matches)
        
        # Calculate recent score variance (consistency)
        home_recent_score_var = self._calculate_recent_score_variance(home_player_id, home_recent_matches)
        away_recent_score_var = self._calculate_recent_score_variance(away_player_id, away_recent_matches)
        
        # Calculate momentum (trend in recent performance)
        home_momentum = self._calculate_momentum(home_player_id, home_recent_matches)
        away_momentum = self._calculate_momentum(away_player_id, away_recent_matches)
        
        return [
            # Recent form stats
            home_recent_win_rate,
            away_recent_win_rate,
            home_recent_avg_score,
            away_recent_avg_score,
            home_recent_score_var,
            away_recent_score_var,
            home_momentum,
            away_momentum
        ]
    
    @log_exceptions(logger)
    def _extract_advanced_features(self, home_player, away_player, home_team_id, away_team_id, 
                                  home_player_id, away_player_id, prev_matches):
        """
        Extract advanced features.
        
        Args:
            home_player (dict): Home player statistics dictionary
            away_player (dict): Away player statistics dictionary
            home_team_id (str): Home team ID
            away_team_id (str): Away team ID
            home_player_id (str): Home player ID
            away_player_id (str): Away player ID
            prev_matches (list): List of previous match data dictionaries
            
        Returns:
            list: Advanced features
        """
        # Calculate win rate difference
        win_rate_diff = home_player.get('win_rate', 0) - away_player.get('win_rate', 0)
        
        # Calculate average score difference
        avg_score_diff = home_player.get('avg_score', 0) - away_player.get('avg_score', 0)
        
        # Calculate experience difference (total matches)
        exp_diff = home_player.get('total_matches', 0) - away_player.get('total_matches', 0)
        
        # Calculate team win rate difference
        team_win_rate_diff = (self._get_team_win_rate(home_player, home_team_id) - 
                             self._get_team_win_rate(away_player, away_team_id))
        
        # Calculate team average score difference
        team_avg_score_diff = (self._get_team_avg_score(home_player, home_team_id) - 
                              self._get_team_avg_score(away_player, away_team_id))
        
        # Calculate team experience difference
        team_exp_diff = (self._get_team_matches(home_player, home_team_id) - 
                        self._get_team_matches(away_player, away_team_id))
        
        # Calculate home court advantage
        home_advantage = self._calculate_home_advantage(prev_matches)
        
        # Calculate player consistency (variance in scores)
        home_consistency = self._calculate_player_consistency(home_player_id, prev_matches)
        away_consistency = self._calculate_player_consistency(away_player_id, prev_matches)
        
        return [
            # Advanced stats
            win_rate_diff,
            avg_score_diff,
            exp_diff,
            team_win_rate_diff,
            team_avg_score_diff,
            team_exp_diff,
            home_advantage,
            home_consistency,
            away_consistency
        ]
    
    @log_exceptions(logger)
    def _extract_temporal_features(self, match_date, prev_matches):
        """
        Extract temporal features.
        
        Args:
            match_date (datetime): Match date
            prev_matches (list): List of previous match data dictionaries
            
        Returns:
            list: Temporal features
        """
        # Calculate day of week (0-6, Monday is 0)
        day_of_week = match_date.weekday()
        
        # Calculate month of year (1-12)
        month = match_date.month
        
        # Calculate weekend indicator (1 if weekend, 0 otherwise)
        is_weekend = 1 if day_of_week >= 5 else 0
        
        return [
            # Temporal features
            day_of_week / 6,  # Normalize to [0, 1]
            month / 12,  # Normalize to [0, 1]
            is_weekend
        ]
    
    @log_exceptions(logger)
    def _get_team_win_rate(self, player, team_id):
        """
        Get a player's win rate with a specific team.
        
        Args:
            player (dict): Player statistics dictionary
            team_id (str): Team ID
            
        Returns:
            float: Win rate
        """
        teams_used = player.get('teams_used', {})
        if team_id in teams_used:
            return teams_used[team_id].get('win_rate', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_team_avg_score(self, player, team_id):
        """
        Get a player's average score with a specific team.
        
        Args:
            player (dict): Player statistics dictionary
            team_id (str): Team ID
            
        Returns:
            float: Average score
        """
        teams_used = player.get('teams_used', {})
        if team_id in teams_used:
            return teams_used[team_id].get('avg_score', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_team_matches(self, player, team_id):
        """
        Get a player's number of matches with a specific team.
        
        Args:
            player (dict): Player statistics dictionary
            team_id (str): Team ID
            
        Returns:
            int: Number of matches
        """
        teams_used = player.get('teams_used', {})
        if team_id in teams_used:
            return teams_used[team_id].get('matches', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_h2h_win_rate(self, player, opponent_id):
        """
        Get a player's win rate against a specific opponent.
        
        Args:
            player (dict): Player statistics dictionary
            opponent_id (str): Opponent player ID
            
        Returns:
            float: Win rate
        """
        opponents_faced = player.get('opponents_faced', {})
        if opponent_id in opponents_faced:
            return opponents_faced[opponent_id].get('win_rate', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_h2h_matches(self, player, opponent_id):
        """
        Get a player's number of matches against a specific opponent.
        
        Args:
            player (dict): Player statistics dictionary
            opponent_id (str): Opponent player ID
            
        Returns:
            int: Number of matches
        """
        opponents_faced = player.get('opponents_faced', {})
        if opponent_id in opponents_faced:
            return opponents_faced[opponent_id].get('matches', 0)
        return 0
    
    @log_exceptions(logger)
    def _get_avg_score_against(self, player, opponent_id):
        """
        Get a player's average score against a specific opponent.
        
        Args:
            player (dict): Player statistics dictionary
            opponent_id (str): Opponent player ID
            
        Returns:
            float: Average score
        """
        opponents_faced = player.get('opponents_faced', {})
        if opponent_id in opponents_faced:
            total_score = opponents_faced[opponent_id].get('total_score', 0)
            matches = opponents_faced[opponent_id].get('matches', 0)
            if matches > 0:
                return total_score / matches
        return 0
    
    @log_exceptions(logger)
    def _get_player_recent_matches(self, player_id, matches, window_size=5):
        """
        Get a player's recent matches.
        
        Args:
            player_id (str): Player ID
            matches (list): List of match data dictionaries
            window_size (int): Number of recent matches to consider
            
        Returns:
            list: List of recent match data dictionaries
        """
        player_matches = []
        
        for match in matches:
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            if home_player_id == player_id or away_player_id == player_id:
                player_matches.append(match)
        
        # Sort by date (most recent first)
        player_matches.sort(key=lambda m: self._parse_match_date(m), reverse=True)
        
        # Return the most recent matches
        return player_matches[:window_size]
    
    @log_exceptions(logger)
    def _calculate_recent_win_rate(self, player_id, recent_matches):
        """
        Calculate a player's recent win rate.
        
        Args:
            player_id (str): Player ID
            recent_matches (list): List of recent match data dictionaries
            
        Returns:
            float: Recent win rate
        """
        if not recent_matches:
            return 0
        
        wins = 0
        
        for match in recent_matches:
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            home_score = match['homeScore']
            away_score = match['awayScore']
            
            if home_player_id == player_id and home_score > away_score:
                wins += 1
            elif away_player_id == player_id and away_score > home_score:
                wins += 1
        
        return wins / len(recent_matches)
    
    @log_exceptions(logger)
    def _calculate_recent_avg_score(self, player_id, recent_matches):
        """
        Calculate a player's recent average score.
        
        Args:
            player_id (str): Player ID
            recent_matches (list): List of recent match data dictionaries
            
        Returns:
            float: Recent average score
        """
        if not recent_matches:
            return 0
        
        total_score = 0
        
        for match in recent_matches:
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            if home_player_id == player_id:
                total_score += match['homeScore']
            elif away_player_id == player_id:
                total_score += match['awayScore']
        
        return total_score / len(recent_matches)
    
    @log_exceptions(logger)
    def _calculate_recent_score_variance(self, player_id, recent_matches):
        """
        Calculate a player's recent score variance.
        
        Args:
            player_id (str): Player ID
            recent_matches (list): List of recent match data dictionaries
            
        Returns:
            float: Recent score variance
        """
        if not recent_matches or len(recent_matches) < 2:
            return 0
        
        scores = []
        
        for match in recent_matches:
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            if home_player_id == player_id:
                scores.append(match['homeScore'])
            elif away_player_id == player_id:
                scores.append(match['awayScore'])
        
        if not scores:
            return 0
        
        return np.var(scores)
    
    @log_exceptions(logger)
    def _calculate_momentum(self, player_id, recent_matches):
        """
        Calculate a player's momentum (trend in recent performance).
        
        Args:
            player_id (str): Player ID
            recent_matches (list): List of recent match data dictionaries
            
        Returns:
            float: Momentum
        """
        if not recent_matches or len(recent_matches) < 2:
            return 0
        
        # Calculate weighted win rate (more recent matches have higher weight)
        total_weight = 0
        weighted_wins = 0
        
        for i, match in enumerate(recent_matches):
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            home_score = match['homeScore']
            away_score = match['awayScore']
            
            # Weight is inversely proportional to recency (most recent has highest weight)
            weight = len(recent_matches) - i
            total_weight += weight
            
            if home_player_id == player_id and home_score > away_score:
                weighted_wins += weight
            elif away_player_id == player_id and away_score > home_score:
                weighted_wins += weight
        
        if total_weight == 0:
            return 0
        
        weighted_win_rate = weighted_wins / total_weight
        
        # Calculate unweighted win rate
        unweighted_win_rate = self._calculate_recent_win_rate(player_id, recent_matches)
        
        # Momentum is the difference between weighted and unweighted win rates
        return weighted_win_rate - unweighted_win_rate
    
    @log_exceptions(logger)
    def _calculate_home_advantage(self, matches):
        """
        Calculate home court advantage.
        
        Args:
            matches (list): List of match data dictionaries
            
        Returns:
            float: Home court advantage
        """
        if not matches:
            return 0
        
        home_wins = 0
        
        for match in matches:
            home_score = match['homeScore']
            away_score = match['awayScore']
            
            if home_score > away_score:
                home_wins += 1
        
        return home_wins / len(matches)
    
    @log_exceptions(logger)
    def _calculate_player_consistency(self, player_id, matches):
        """
        Calculate a player's consistency (inverse of score variance).
        
        Args:
            player_id (str): Player ID
            matches (list): List of match data dictionaries
            
        Returns:
            float: Consistency
        """
        player_matches = []
        
        for match in matches:
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            if home_player_id == player_id or away_player_id == player_id:
                player_matches.append(match)
        
        if not player_matches or len(player_matches) < 2:
            return 0
        
        scores = []
        
        for match in player_matches:
            home_player_id = str(match['homePlayer']['id'])
            away_player_id = str(match['awayPlayer']['id'])
            
            if home_player_id == player_id:
                scores.append(match['homeScore'])
            elif away_player_id == player_id:
                scores.append(match['awayScore'])
        
        if not scores:
            return 0
        
        # Consistency is the inverse of variance (normalized to [0, 1])
        variance = np.var(scores)
        if variance == 0:
            return 1  # Perfect consistency
        
        # Normalize using a reasonable maximum variance (e.g., 100)
        max_variance = 100
        normalized_variance = min(variance / max_variance, 1)
        
        return 1 - normalized_variance
