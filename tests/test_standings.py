"""
Unit tests for the standings module.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.standings import (
    fetch_standings,
    get_top_players,
    get_player_by_name,
    get_player_by_id,
    get_head_to_head_stats,
    StandingsDataError
)


class TestStandingsModule(unittest.TestCase):
    """Test cases for the standings module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Load sample standings data from file
        self.sample_data_path = os.path.join(os.path.dirname(__file__), 'sample_data', 'standings.json')
        os.makedirs(os.path.dirname(self.sample_data_path), exist_ok=True)
        
        # Sample data for testing
        self.sample_data = [
            {
                "participantId": 32,
                "participantName": "LANES",
                "matchesWinPct": 71.5366,
                "avgPoints": 67.2872,
                "avgFieldGoalsPercent": 64.769,
                "3PointersPercent": 47.4513,
                "avgAssists": 8.5523,
                "avgSteals": 4.3701,
                "avgBlocks": 1.4274,
                "matchesPlayed": 2512,
                "matchForm": ["loss", "win", "win", "loss", "loss"]
            },
            {
                "participantId": 77,
                "participantName": "TAAPZ",
                "matchesWinPct": 70.9677,
                "avgPoints": 65.7087,
                "avgFieldGoalsPercent": 64.1437,
                "3PointersPercent": 47.9182,
                "avgAssists": 9.7762,
                "avgSteals": 4.0261,
                "avgBlocks": 1.3754,
                "matchesPlayed": 1736,
                "matchForm": ["win", "win", "win", "loss", "loss"]
            },
            {
                "participantId": 33,
                "participantName": "HOGGY",
                "matchesWinPct": 67.0722,
                "avgPoints": 68.204,
                "avgFieldGoalsPercent": 60.5717,
                "3PointersPercent": 45.3176,
                "avgAssists": 10.5454,
                "avgSteals": 4.5098,
                "avgBlocks": 1.7951,
                "matchesPlayed": 3863,
                "matchForm": ["loss", "win", "win", "loss", "loss"]
            }
        ]
        
        # Save sample data to file
        with open(self.sample_data_path, 'w') as f:
            json.dump(self.sample_data, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove sample data file
        if os.path.exists(self.sample_data_path):
            os.remove(self.sample_data_path)
    
    @patch('src.data.standings.get_bearer_token')
    @patch('src.data.standings.requests.get')
    def test_fetch_standings(self, mock_get, mock_get_token):
        """Test fetching standings data."""
        # Set up mocks
        mock_get_token.return_value = "test_token"
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_data
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_standings(tournament_id=1)
        
        # Verify the result
        self.assertEqual(result, self.sample_data)
        
        # Verify the mocks were called correctly
        mock_get_token.assert_called_once_with(force_refresh=False)
        mock_get.assert_called_once()
        
        # Verify the URL and headers
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params'], {'tournament-id': 1})
        self.assertEqual(kwargs['headers']['authorization'], 'Bearer test_token')
    
    def test_get_top_players(self):
        """Test getting top players by win percentage."""
        # Call the function
        result = get_top_players(self.sample_data, limit=2)
        
        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['participantName'], 'LANES')
        self.assertEqual(result[1]['participantName'], 'TAAPZ')
    
    def test_get_player_by_name(self):
        """Test getting a player by name."""
        # Call the function
        result = get_player_by_name(self.sample_data, 'HOGGY')
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['participantId'], 33)
        
        # Test case-insensitive search
        result = get_player_by_name(self.sample_data, 'hoggy')
        self.assertIsNotNone(result)
        self.assertEqual(result['participantId'], 33)
        
        # Test non-existent player
        result = get_player_by_name(self.sample_data, 'NONEXISTENT')
        self.assertIsNone(result)
    
    def test_get_player_by_id(self):
        """Test getting a player by ID."""
        # Call the function
        result = get_player_by_id(self.sample_data, 77)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['participantName'], 'TAAPZ')
        
        # Test non-existent player
        result = get_player_by_id(self.sample_data, 999)
        self.assertIsNone(result)
    
    def test_get_head_to_head_stats(self):
        """Test getting head-to-head statistics."""
        # Get two players
        player1 = get_player_by_name(self.sample_data, 'LANES')
        player2 = get_player_by_name(self.sample_data, 'TAAPZ')
        
        # Call the function
        result = get_head_to_head_stats(player1, player2)
        
        # Verify the result
        self.assertIn('win_percentage', result)
        self.assertIn('avg_points', result)
        self.assertIn('field_goal_percentage', result)
        
        # Check the differences
        self.assertAlmostEqual(result['win_percentage']['difference'], 0.5689, places=4)
        self.assertAlmostEqual(result['avg_points']['difference'], 1.5785, places=4)


if __name__ == '__main__':
    unittest.main()
