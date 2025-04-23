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

##### Past Matches

- **URL**: `https://api-sis-stats.hudstats.com/v1/schedule`
- **Method**: GET
- **Query Parameters**:
  - `schedule-type`: `match` (for past matches)
  - `from-date`: Start date in format 'YYYY-MM-DD'
  - `to-date`: End date in format 'YYYY-MM-DD'
  - `tournament-id`: The tournament ID (default: 1)
- **Headers**:
  - `authorization`: Bearer token
  - `origin`: https://h2hggl.com
  - `referer`: https://h2hggl.com/
- **Response**: Array of match data

Example response for past matches:
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

##### Upcoming Matches

- **URL**: `https://api-sis-stats.hudstats.com/v1/schedule`
- **Method**: GET
- **Query Parameters**:
  - `schedule-type`: `fixture` (for upcoming matches)
  - `from`: Start date and time in format 'YYYY-MM-DD HH:MM'
  - `to`: End date and time in format 'YYYY-MM-DD HH:MM'
  - `order`: `asc` (to sort by start time)
  - `tournament-id`: The tournament ID (default: 1)
- **Headers**:
  - `authorization`: Bearer token
  - `origin`: https://h2hggl.com
  - `referer`: https://h2hggl.com/
- **Response**: Array of upcoming match data

Example response for upcoming matches:
```json
[
  {
    "sport": "NBA",
    "avaStreamId": "sis-nba-3",
    "awayParticipantId": 957,
    "tournamentName": "Ebasketball H2H GG League",
    "homeParticipantExternalId": "1078",
    "fixtureStart": "2025-04-23T09:55:00Z",
    "homeTeamId": 20,
    "awayTeamName": "Minnesota Timberwolves",
    "homeParticipantId": 105,
    "homeTeamLogo": "teams/NYK.png",
    "homeTeamName": "New York Knicks",
    "awayParticipantLogo": "participants/EXO.png",
    "homeParticipantName": "KJMR",
    "awayTeamAbbreviation": "MIN",
    "tournamentId": 1,
    "fixtureId": 206252,
    "awayParticipantName": "EXO",
    "awayParticipantExternalId": "4286",
    "homeTeamAbbreviation": "NYK",
    "awayTeamId": 18,
    "awayTeamLogo": "teams/MT.png",
    "streamName": "Ebasketball 3",
    "homeParticipantLogo": "participants/KJMR.png"
  },
  ...
]
```

**Key Differences Between Past and Upcoming Matches:**

1. **API Parameters**:
   - Past matches use `from-date` and `to-date` with date only
   - Upcoming matches use `from` and `to` with date and time
   - Upcoming matches use `order=asc` to sort by start time

2. **Response Fields**:
   - Past matches have `startDate`, `homeScore`, `awayScore`, and `result`
   - Upcoming matches have `fixtureStart` instead of `startDate`
   - Upcoming matches don't have score or result fields

3. **Time Zone Handling**:
   - All date/time fields from the API are in UTC (indicated by the 'Z' suffix)
   - The project includes utility functions to convert UTC times to local time:
     - `parse_utc_datetime()`: Parses a UTC datetime string into a timezone-aware datetime object
     - `convert_to_local_time()`: Converts a UTC datetime to local time
     - `format_datetime()`: Formats a datetime object as a string

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

# Fetch upcoming matches for the next 24 hours
upcoming_matches = fetch_upcoming_matches(hours_ahead=24, tournament_id=1)

# Process upcoming matches with proper time zone handling
print(f"\nUpcoming matches: {len(upcoming_matches)}")
for match in upcoming_matches[:3]:  # First 3 upcoming matches
    # Parse UTC time and convert to local time
    utc_dt = parse_utc_datetime(match['fixtureStart'])
    local_dt = convert_to_local_time(utc_dt) if utc_dt else None
    time_str = format_datetime(local_dt) if local_dt else 'Unknown time'
    print(f"{time_str}: {match['homeParticipantName']} vs {match['awayParticipantName']}")

# Fetch today's matches
todays_matches = fetch_todays_matches(tournament_id=1)
print(f"\nToday's matches: {len(todays_matches)}")

# Fetch upcoming matches for a specific player
player = get_player_by_name(standings_data, "HOGGY")
if player:
    player_matches = fetch_player_upcoming_matches(player['participantId'], hours_ahead=48)
    print(f"\nUpcoming matches for {player['participantName']}: {len(player_matches)}")
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
