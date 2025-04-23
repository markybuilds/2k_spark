"""
Unit tests for the matches module.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from datetime import datetime, timedelta

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.matches import (
    fetch_matches,
    fetch_upcoming_matches,
    fetch_todays_matches,
    fetch_player_match_history,
    fetch_player_upcoming_matches,
    get_head_to_head_matches,
    get_player_matches_for_date,
    calculate_player_win_rate,
    calculate_player_average_score,
    get_player_form,
    MatchDataError
)


class TestMatchesModule(unittest.TestCase):
    """Test cases for the matches module."""

    def setUp(self):
        """Set up test fixtures."""
        # Load sample match data from file
        self.sample_data_path = os.path.join(os.path.dirname(__file__), 'sample_data', 'matches.json')
        os.makedirs(os.path.dirname(self.sample_data_path), exist_ok=True)

        # Sample data for testing
        self.sample_data = [
            {
                "matchId": 1,
                "homeParticipantId": 23,
                "homeParticipantName": "SPARKZ",
                "awayParticipantId": 18,
                "awayParticipantName": "OREZ",
                "homeScore": 66,
                "awayScore": 60,
                "result": "home_win",
                "startDate": "2023-08-09T21:40:11Z"
            },
            {
                "matchId": 2,
                "homeParticipantId": 26,
                "homeParticipantName": "SHINIGAMI",
                "awayParticipantId": 31,
                "awayParticipantName": "ENIGMA",
                "homeScore": 78,
                "awayScore": 79,
                "result": "away_win",
                "startDate": "2023-08-09T21:50:15Z"
            },
            {
                "matchId": 3,
                "homeParticipantId": 39,
                "homeParticipantName": "PRINCE",
                "awayParticipantId": 24,
                "awayParticipantName": "SAINT JR",
                "homeScore": 53,
                "awayScore": 63,
                "result": "away_win",
                "startDate": "2023-08-09T22:00:15Z"
            },
            {
                "matchId": 4,
                "homeParticipantId": 23,
                "homeParticipantName": "SPARKZ",
                "awayParticipantId": 24,
                "awayParticipantName": "SAINT JR",
                "homeScore": 70,
                "awayScore": 65,
                "result": "home_win",
                "startDate": "2023-08-10T21:40:11Z"
            },
            {
                "matchId": 5,
                "homeParticipantId": 24,
                "homeParticipantName": "SAINT JR",
                "awayParticipantId": 23,
                "awayParticipantName": "SPARKZ",
                "homeScore": 68,
                "awayScore": 72,
                "result": "away_win",
                "startDate": "2023-08-11T21:40:11Z"
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

    @patch('src.data.matches.get_bearer_token')
    @patch('src.data.matches.requests.get')
    def test_fetch_matches(self, mock_get, mock_get_token):
        """Test fetching match data."""
        # Set up mocks
        mock_get_token.return_value = "test_token"
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_data
        mock_get.return_value = mock_response

        # Call the function
        result = fetch_matches(from_date="2023-01-01", to_date="2023-12-31", tournament_id=1)

        # Verify the result
        self.assertEqual(result, self.sample_data)

        # Verify the mocks were called correctly
        mock_get_token.assert_called_once_with(force_refresh=False)
        mock_get.assert_called_once()

        # Verify the URL and headers
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['from-date'], "2023-01-01")
        self.assertEqual(kwargs['params']['to-date'], "2023-12-31")
        self.assertEqual(kwargs['params']['tournament-id'], 1)
        self.assertEqual(kwargs['params']['schedule-type'], "match")
        self.assertEqual(kwargs['headers']['authorization'], 'Bearer test_token')

    @patch('src.data.matches.fetch_matches')
    def test_fetch_upcoming_matches(self, mock_fetch_matches):
        """Test fetching upcoming matches."""
        # Set up mock
        mock_fetch_matches.return_value = self.sample_data

        # Call the function
        result = fetch_upcoming_matches(hours_ahead=24, days_ahead=0, tournament_id=1)

        # Verify the result
        self.assertEqual(result, self.sample_data)

        # Verify the mock was called correctly
        args, kwargs = mock_fetch_matches.call_args
        self.assertEqual(kwargs['schedule_type'], 'fixture')
        self.assertEqual(kwargs['tournament_id'], 1)
        self.assertEqual(kwargs['include_time'], True)
        self.assertEqual(kwargs['order_asc'], True)

        # Verify dates (approximate check since exact time will vary)
        now = datetime.now()
        from_datetime = now.strftime('%Y-%m-%d')
        to_datetime = (now + timedelta(hours=24)).strftime('%Y-%m-%d')
        self.assertTrue(kwargs['from_date'].startswith(from_datetime))
        self.assertTrue(kwargs['to_date'].startswith(to_datetime))

    @patch('src.data.matches.fetch_matches')
    def test_fetch_todays_matches(self, mock_fetch_matches):
        """Test fetching today's matches."""
        # Set up mock
        mock_fetch_matches.return_value = self.sample_data

        # Call the function
        result = fetch_todays_matches(tournament_id=1)

        # Verify the result
        self.assertEqual(result, self.sample_data)

        # Verify the mock was called correctly
        args, kwargs = mock_fetch_matches.call_args
        self.assertEqual(kwargs['schedule_type'], 'fixture')
        self.assertEqual(kwargs['tournament_id'], 1)
        self.assertEqual(kwargs['include_time'], True)
        self.assertEqual(kwargs['order_asc'], True)

        # Verify dates (approximate check since exact time will vary)
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        self.assertTrue(kwargs['from_date'].startswith(today))
        self.assertTrue(kwargs['to_date'].startswith(today))

    @patch('src.data.matches.fetch_upcoming_matches')
    def test_fetch_player_upcoming_matches(self, mock_fetch_upcoming):
        """Test fetching upcoming matches for a player."""
        # Set up mock
        mock_fetch_upcoming.return_value = self.sample_data

        # Call the function
        result = fetch_player_upcoming_matches(player_id=23, hours_ahead=24, tournament_id=1)

        # Verify the result
        # Player 23 appears in 3 matches in the sample data
        self.assertEqual(len(result), 3)

        # Verify all matches contain the player
        for match in result:
            self.assertTrue(
                match['homeParticipantId'] == 23 or match['awayParticipantId'] == 23,
                f"Match {match['matchId']} does not contain player 23"
            )

        # Verify the mock was called correctly
        mock_fetch_upcoming.assert_called_once_with(
            hours_ahead=24,
            days_ahead=0,
            tournament_id=1,
            force_refresh_token=False
        )

    @patch('src.data.matches.fetch_matches')
    def test_get_player_matches_for_date(self, mock_fetch_matches):
        """Test getting matches for a player on a specific date."""
        # Create a filtered sample data with only matches on 2023-08-10
        filtered_data = [
            match for match in self.sample_data
            if match.get('startDate', '').startswith('2023-08-10')
        ]

        # Set up mock to return only the filtered data
        mock_fetch_matches.return_value = filtered_data

        # Call the function with a specific date
        test_date = datetime(2023, 8, 10)  # A date that has matches in the sample data
        result = get_player_matches_for_date(player_id=23, date=test_date, tournament_id=1)

        # Verify the result
        # Player 23 appears in 1 match on 2023-08-10 in the filtered data
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['matchId'], 4)  # Match ID 4 is on 2023-08-10

        # Verify all matches contain the player
        for match in result:
            self.assertTrue(
                match['homeParticipantId'] == 23 or match['awayParticipantId'] == 23,
                f"Match {match['matchId']} does not contain player 23"
            )

        # Verify the mock was called correctly
        args, kwargs = mock_fetch_matches.call_args
        self.assertEqual(kwargs['schedule_type'], 'fixture')
        self.assertEqual(kwargs['tournament_id'], 1)
        self.assertEqual(kwargs['include_time'], True)
        self.assertEqual(kwargs['order_asc'], True)

        # Verify dates
        expected_date = test_date.strftime('%Y-%m-%d')
        self.assertTrue(kwargs['from_date'].startswith(expected_date))
        self.assertTrue(kwargs['to_date'].startswith(expected_date))

    @patch('src.data.matches.fetch_matches')
    def test_fetch_player_match_history(self, mock_fetch_matches):
        """Test fetching player match history."""
        # Set up mock
        mock_fetch_matches.return_value = self.sample_data

        # Call the function
        result = fetch_player_match_history(player_id=23, days_back=90, tournament_id=1)

        # Verify the result
        self.assertEqual(len(result), 3)  # Player 23 appears in 3 matches

        # Verify all matches contain the player
        for match in result:
            self.assertTrue(
                match['homeParticipantId'] == 23 or match['awayParticipantId'] == 23,
                f"Match {match['matchId']} does not contain player 23"
            )

    @patch('src.data.matches.fetch_matches')
    def test_get_head_to_head_matches(self, mock_fetch_matches):
        """Test getting head-to-head matches."""
        # Set up mock
        mock_fetch_matches.return_value = self.sample_data

        # Call the function
        result = get_head_to_head_matches(player1_id=23, player2_id=24, days_back=365, tournament_id=1)

        # Verify the result
        self.assertEqual(len(result), 2)  # Players 23 and 24 have 2 head-to-head matches

        # Verify all matches are between the two players
        for match in result:
            self.assertTrue(
                (match['homeParticipantId'] == 23 and match['awayParticipantId'] == 24) or
                (match['homeParticipantId'] == 24 and match['awayParticipantId'] == 23),
                f"Match {match['matchId']} is not between players 23 and 24"
            )

    def test_calculate_player_win_rate(self):
        """Test calculating player win rate."""
        # Call the function for player 23 (SPARKZ)
        win_rate = calculate_player_win_rate(self.sample_data, player_id=23)

        # Verify the result
        # Player 23 has 3 matches: 2 wins, 0 losses as home; 1 win, 0 losses as away
        self.assertEqual(win_rate, 100.0)

        # Call the function for player 24 (SAINT JR)
        win_rate = calculate_player_win_rate(self.sample_data, player_id=24)

        # Verify the result
        # Player 24 has 3 matches: 0 wins, 1 loss as home; 1 win, 1 loss as away
        self.assertAlmostEqual(win_rate, 33.33333, places=4)

    def test_calculate_player_average_score(self):
        """Test calculating player average score."""
        # Call the function for player 23 (SPARKZ)
        avg_score = calculate_player_average_score(self.sample_data, player_id=23)

        # Verify the result
        # Player 23 scores: 66, 70, 72
        self.assertEqual(avg_score, 69.33333333333333)

        # Call the function for player 24 (SAINT JR)
        avg_score = calculate_player_average_score(self.sample_data, player_id=24)

        # Verify the result
        # Player 24 scores: 63, 65, 68
        self.assertEqual(avg_score, 65.33333333333333)

    def test_get_player_form(self):
        """Test getting player form."""
        # Call the function for player 23 (SPARKZ)
        form = get_player_form(self.sample_data, player_id=23)

        # Verify the result
        # Player 23's most recent matches: win, win, win
        self.assertEqual(form, ['win', 'win', 'win'])

        # Call the function for player 24 (SAINT JR)
        form = get_player_form(self.sample_data, player_id=24)

        # Verify the result
        # Player 24's most recent matches: loss, loss, win
        self.assertEqual(form, ['loss', 'loss', 'win'])


if __name__ == '__main__':
    unittest.main()
