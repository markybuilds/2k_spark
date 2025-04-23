# NBA 2K eSports Prediction Model (2K Spark)

This project aims to build a prediction model for NBA 2K eSports league (specifically the H2H GG League) to predict the winners of upcoming matches. It fetches data from h2hggl.com and uses machine learning techniques to make predictions.

## Overview

2K Spark is a comprehensive tool for analyzing and predicting NBA 2K eSports matches. It provides:

- **Data Collection**: Automated fetching of player standings, match history, and upcoming matches
- **Data Analysis**: Tools for analyzing player performance, head-to-head matchups, and trends
- **Prediction Models**: Machine learning models to predict the outcomes of upcoming matches

The project is designed to be modular, extensible, and well-documented, making it easy to add new features and improve existing functionality.

## Project Structure

```
├── cache/              # Directory for caching data (tokens, etc.)
├── data/               # Data directory
│   ├── raw/            # Raw data from API
│   └── processed/      # Processed data for models
├── docs/               # Project documentation
│   ├── architecture.md # Project architecture document
│   ├── api.md          # API documentation
│   └── development.md  # Development guide
├── examples/           # Example scripts demonstrating how to use the project
│   ├── matches_example.py # Example of using the matches module
│   └── standings_example.py # Example of using the standings module
├── scripts/            # Utility scripts for development and maintenance
│   ├── test_api.py     # Script to test API endpoints
│   ├── test_schedule_api.py # Script to test schedule API endpoint
│   └── setup_git.bat   # Script to set up the Git repository
├── src/                # Source code directory
│   ├── data/           # Data fetching and processing modules
│   │   ├── matches.py  # Match data fetching module
│   │   ├── players.py  # Player data fetching module
│   │   └── standings.py # Standings data fetching module
│   ├── models/         # Prediction models
│   ├── utils/          # Utility functions
│   ├── auth.py         # Authentication module for retrieving tokens
│   └── config.py       # Configuration settings
├── tests/              # Unit tests
│   ├── sample_data/    # Sample data for testing
│   ├── test_auth.py    # Tests for authentication module
│   ├── test_matches.py # Tests for matches module
│   ├── test_standings.py # Tests for standings module
│   └── test_token_refresh.py # Tests for token refresh functionality
├── .gitignore          # Git ignore file
├── LICENSE             # MIT License
├── main.py             # Main application entry point
├── README.md           # Project documentation
└── requirements.txt    # Python dependencies
```

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

## Testing

Run all unit tests:
```
python -m unittest discover tests
```

Run a specific test file:
```
python -m unittest tests/test_auth.py
```

Run a specific test case:
```
python -m unittest tests.test_auth.TestTokenManager
```

## Features

### Authentication

The project uses Selenium to authenticate with h2hggl.com by retrieving a bearer token from localStorage. The token is cached for subsequent requests to minimize the need for browser automation.

### Data Collection

#### Player Standings

The project fetches player standings data from the h2hggl.com API, including:
- Win percentages
- Average points
- Field goal percentages
- Three-point percentages
- Other player statistics

#### Match Data

The project fetches match data from the h2hggl.com API, including:
- Past match results
- Upcoming matches
- Head-to-head statistics
- Player performance metrics

### Data Storage

All data is stored in the `data` directory:
- `data/raw`: Contains raw data fetched directly from the API
- `data/processed`: Contains processed data ready for use in prediction models

Data files are excluded from version control via `.gitignore`.

## Configuration

Configuration settings are defined in the `src/config.py` file. You can modify these settings directly in the file if needed.

## Usage Examples

### Fetching Player Standings

```python
from src.auth import get_bearer_token
from src.data.standings import fetch_standings

# Get authentication token
token = get_bearer_token()

# Fetch standings data
standings_data = fetch_standings(tournament_id=1)

# Process the data
for player in standings_data[:5]:  # First 5 players
    print(f"{player['participantName']}: {player['matchesWinPct']}%")
```

### Fetching Match Data

```python
from src.auth import get_bearer_token
from src.data.matches import fetch_matches, fetch_upcoming_matches
from datetime import datetime, timedelta

# Get dates for the last 30 days
today = datetime.now()
from_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
to_date = today.strftime('%Y-%m-%d')

# Fetch match data
matches_data = fetch_matches(
    from_date=from_date,
    to_date=to_date,
    tournament_id=1,
    schedule_type='match'
)

# Process match data
print(f"Retrieved {len(matches_data)} matches")
for match in matches_data[:3]:  # First 3 matches
    print(f"{match['homeParticipantName']} {match['homeScore']} - {match['awayScore']} {match['awayParticipantName']}")

# Fetch upcoming matches
upcoming_matches = fetch_upcoming_matches(days_ahead=7, tournament_id=1)
print(f"Retrieved {len(upcoming_matches)} upcoming matches")
```

### Analyzing Head-to-Head Matchups

```python
from src.data.matches import get_head_to_head_matches, calculate_player_win_rate
from src.data.standings import get_player_by_name

# Get player IDs
player1 = get_player_by_name(standings_data, "SPARKZ")
player2 = get_player_by_name(standings_data, "SAINT JR")

# Get head-to-head matches
h2h_matches = get_head_to_head_matches(
    player1_id=player1['participantId'],
    player2_id=player2['participantId'],
    days_back=365
)

# Calculate win rates
player1_win_rate = calculate_player_win_rate(h2h_matches, player1['participantId'])
player2_win_rate = calculate_player_win_rate(h2h_matches, player2['participantId'])

print(f"{player1['participantName']} vs {player2['participantName']}")
print(f"Total matches: {len(h2h_matches)}")
print(f"{player1['participantName']} win rate: {player1_win_rate:.2f}%")
print(f"{player2['participantName']} win rate: {100 - player1_win_rate:.2f}%")
```

For more examples, see the scripts in the `examples/` directory.

## Requirements

- Python 3.8+
- Chrome browser (for Selenium WebDriver)

## Development

For detailed development guidelines, see the [Development Guide](docs/development.md).

### Project Organization

This project follows a modular organization to ensure maintainability and extensibility:

- **Modular Structure**: Each component has a specific responsibility
- **Separation of Concerns**: Data fetching, processing, and prediction are separated
- **Comprehensive Testing**: All modules have corresponding unit tests
- **Clear Documentation**: All code and APIs are documented

### Adding New Features

1. Create appropriate modules in the `src` directory
2. Write unit tests in the `tests` directory
3. Update documentation in the `docs` directory
4. Add example scripts in the `examples` directory

### Code Style

This project follows PEP 8 style guidelines and uses type hints for better code readability.

### Git Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Ensure your code follows the project's style guidelines
2. Add tests for new functionality
3. Update documentation as needed
4. Make sure all tests pass before submitting a pull request

## Future Plans

### Prediction Model

The next phase of development will focus on building the prediction model:

1. **Feature Engineering**: Create relevant features from the raw data
   - Player performance metrics
   - Head-to-head statistics
   - Recent form and trends
   - Team-based features

2. **Model Development**: Implement and evaluate various machine learning models
   - Logistic Regression
   - Random Forest
   - Gradient Boosting
   - Neural Networks

3. **Model Evaluation**: Assess model performance using appropriate metrics
   - Accuracy
   - Precision and Recall
   - ROC-AUC
   - Calibration

4. **Deployment**: Create a user-friendly interface for making predictions
   - Command-line interface
   - Web application (future enhancement)
   - Automated prediction reports

### Additional Features

- **Advanced Analytics**: Implement advanced statistical analysis of player and match data
- **Visualization**: Add data visualization tools for better insights
- **Real-time Updates**: Enable real-time updates of match results and predictions
- **Betting Odds Integration**: Compare predictions with betting odds from various sources

## License

This project is licensed under the MIT License - see the LICENSE file for details.
