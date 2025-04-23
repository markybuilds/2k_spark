# API Documentation

This document provides documentation for the API endpoints used in the NBA 2K Prediction Model project.

## h2hggl.com API

The h2hggl.com website doesn't have an official API, but we've identified several endpoints that we can use to fetch data.

### Authentication

Authentication is done by retrieving a bearer token from the website's localStorage using Selenium. This token is then used for subsequent API requests.

### Endpoints

#### Player Standings

- **URL**: `https://api-sis-stats.hudstats.com/v1/standings/participant`
- **Method**: GET
- **Query Parameters**:
  - `tournament-id`: The tournament ID (default: 1)
- **Headers**:
  - `authorization`: Bearer token
  - `origin`: https://h2hggl.com
  - `referer`: https://h2hggl.com/
- **Response**: Array of player standings data

Example response:
```json
[
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
  ...
]
```

#### Match Schedule

- **URL**: `https://api-sis-stats.hudstats.com/v1/schedule`
- **Method**: GET
- **Query Parameters**:
  - `schedule-type`: Type of schedule to fetch (`match` for past matches, `fixture` for upcoming matches)
  - `from-date`: Start date in format 'YYYY-MM-DD'
  - `to-date`: End date in format 'YYYY-MM-DD'
  - `tournament-id`: The tournament ID (default: 1)
- **Headers**:
  - `authorization`: Bearer token
  - `origin`: https://h2hggl.com
  - `referer`: https://h2hggl.com/
- **Response**: Array of match data

Example response:
```json
[
  {
    "matchId": 1,
    "homeParticipantId": 23,
    "homeParticipantName": "SPARKZ",
    "awayParticipantId": 18,
    "awayParticipantName": "OREZ",
    "homeScore": 66,
    "awayScore": 60,
    "result": "home_win",
    "startDate": "2023-08-09T21:40:11Z",
    "homeTeamName": "Phoenix Suns",
    "awayTeamName": "Dallas Mavericks",
    "tournamentName": "Ebasketball H2H GG League"
  },
  ...
]
```

#### Other Endpoints

Additional API endpoints will be documented as they are discovered and implemented.

## Usage in Code

Here's an example of how to use the API in code:

```python
from src.auth import get_bearer_token
from src.data.standings import fetch_standings
from src.data.matches import fetch_matches, fetch_upcoming_matches
from datetime import datetime, timedelta

# Get authentication token
token = get_bearer_token()

# Fetch standings data
standings_data = fetch_standings(tournament_id=1)

# Process standings data
for player in standings_data[:5]:  # First 5 players
    print(f"{player['participantName']}: {player['matchesWinPct']}%")

# Fetch match data for the last 30 days
today = datetime.now()
from_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
to_date = today.strftime('%Y-%m-%d')

matches_data = fetch_matches(
    from_date=from_date,
    to_date=to_date,
    tournament_id=1,
    schedule_type='match'
)

# Process match data
print(f"\nRecent matches: {len(matches_data)}")
for match in matches_data[:3]:  # First 3 matches
    print(f"{match['homeParticipantName']} {match['homeScore']} - {match['awayScore']} {match['awayParticipantName']}")

# Fetch upcoming matches
upcoming_matches = fetch_upcoming_matches(days_ahead=7, tournament_id=1)

# Process upcoming matches
print(f"\nUpcoming matches: {len(upcoming_matches)}")
for match in upcoming_matches[:3]:  # First 3 upcoming matches
    print(f"{match['homeParticipantName']} vs {match['awayParticipantName']}")
```

## Error Handling

API requests may fail for various reasons, such as:
- Authentication errors
- Network errors
- Server errors

The code includes error handling to handle these cases gracefully. Each module has its own custom exception class that provides detailed error information:

- `AuthenticationError`: Raised when there's an issue with authentication
- `StandingsDataError`: Raised when there's an issue fetching standings data
- `MatchDataError`: Raised when there's an issue fetching match data

Example error handling:

```python
from src.data.matches import fetch_matches, MatchDataError

try:
    matches_data = fetch_matches(from_date='2023-01-01', to_date='2023-12-31')
    print(f"Retrieved {len(matches_data)} matches")
except MatchDataError as e:
    print(f"Error fetching match data: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
