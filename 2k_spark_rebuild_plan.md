# 2K Flash Rebuild Plan

## Overview

This document outlines a comprehensive plan for rebuilding the 2K Flash NBA 2K25 eSports Match Prediction System to create a more organized, maintainable, and professional application. The rebuild will preserve the core functionality while improving architecture, code quality, and user experience.

## Current System Analysis

### Strengths
- Comprehensive prediction pipeline for NBA 2K25 eSports matches
- Effective data collection from H2H GG League API
- Machine learning models for winner and score predictions
- Modern Next.js frontend with Shadcn UI components
- RESTful API for frontend-backend communication
- Automated model training and optimization

### Areas for Improvement
- Code organization and architecture
- Separation of concerns
- Error handling and logging
- Testing coverage
- Configuration management
- Documentation
- Deployment process
- User experience
- Code maintainability

## Rebuild Goals

1. Implement a clean, modular architecture
2. Improve code organization and maintainability
3. Enhance error handling and logging
4. Add comprehensive testing
5. Implement proper configuration management
6. Improve documentation
7. Streamline deployment process
8. Enhance user experience
9. Maintain all existing functionality

## Proposed Architecture

### Backend Architecture

We propose a modular, layered architecture for the backend:

```
backend/
├── app/                      # Application entry points
│   ├── api.py                # API server
│   └── cli.py                # Command-line interface
├── config/                   # Configuration management
│   ├── settings.py           # Application settings
│   └── logging_config.py     # Logging configuration
├── core/                     # Core business logic
│   ├── data/                 # Data access and processing
│   │   ├── fetchers/         # Data fetching modules
│   │   │   ├── token.py      # Authentication token retrieval
│   │   │   ├── match_history.py # Historical match data retrieval
│   │   │   └── upcoming_matches.py # Upcoming match data retrieval
│   │   ├── processors/       # Data processing modules
│   │   │   └── player_stats.py # Player statistics calculation
│   │   └── storage.py        # Data storage utilities
│   ├── models/               # Prediction models
│   │   ├── base.py           # Base model class
│   │   ├── winner_prediction.py # Winner prediction model
│   │   ├── score_prediction.py # Score prediction model
│   │   └── registry.py       # Model registry
│   └── optimization/         # Model optimization
│       ├── tuner.py          # Base tuner class
│       ├── auto_tuner.py     # Automated tuning
│       └── bayesian_optimizer.py # Bayesian optimization
├── api/                      # API endpoints
│   ├── routes/               # API route definitions
│   │   ├── predictions.py    # Prediction endpoints
│   │   ├── stats.py          # Statistics endpoints
│   │   └── refresh.py        # Data refresh endpoints
│   ├── middleware/           # API middleware
│   │   └── error_handler.py  # Error handling middleware
│   └── schemas/              # API request/response schemas
│       └── prediction.py     # Prediction schemas
├── services/                 # Service layer
│   ├── prediction_service.py # Prediction service
│   ├── data_service.py       # Data service
│   └── refresh_service.py    # Refresh service
├── utils/                    # Utility functions
│   ├── logging.py            # Logging utilities
│   ├── time.py               # Time utilities
│   └── validation.py         # Validation utilities
└── tests/                    # Tests
    ├── unit/                 # Unit tests
    ├── integration/          # Integration tests
    └── fixtures/             # Test fixtures
```

### Frontend Architecture

We propose a clean, component-based architecture for the Next.js frontend:

```
frontend/
├── app/                      # Next.js app directory
│   ├── page.tsx              # Home page
│   ├── layout.tsx            # Root layout
│   ├── predictions/          # Predictions page
│   ├── history/              # Prediction history page
│   ├── scores/               # Score predictions page
│   └── stats/                # Statistics page
├── components/               # React components
│   ├── ui/                   # UI components (from shadcn/ui)
│   ├── layout/               # Layout components
│   │   ├── header.tsx        # Header component
│   │   ├── sidebar.tsx       # Sidebar component
│   │   └── footer.tsx        # Footer component
│   ├── predictions/          # Prediction components
│   ├── history/              # History components
│   ├── scores/               # Score components
│   └── stats/                # Statistics components
├── lib/                      # Utility libraries
│   ├── api.ts                # API client
│   ├── utils.ts              # Utility functions
│   └── types.ts              # TypeScript types
├── hooks/                    # Custom React hooks
│   ├── use-predictions.ts    # Predictions hook
│   ├── use-history.ts        # History hook
│   └── use-api.ts            # API hook
└── public/                   # Static assets
```

## Technical Improvements

### 1. Backend Improvements

#### Data Fetching and Processing
- **Authentication Token Management**:
  - Implement token caching and automatic refresh
  - Add retry mechanisms for token retrieval
  - Improve error handling for authentication failures

- **Data Fetching**:
  - Create a unified API client for all external requests
  - Implement proper rate limiting and backoff strategies
  - Add comprehensive error handling and logging
  - Support for proxy configuration

- **Data Processing**:
  - Implement data validation and sanitization
  - Improve player statistics calculation with more metrics
  - Add data versioning for tracking changes

#### Prediction Models
- **Model Architecture**:
  - Create a unified base model class
  - Implement model versioning and tracking
  - Add model evaluation metrics and reporting
  - Support for model export and import

- **Model Optimization**:
  - Enhance Bayesian optimization for better performance
  - Add early stopping and cross-validation
  - Implement feature importance analysis
  - Support for hyperparameter search space customization

#### API Server
- **API Design**:
  - Implement RESTful API best practices
  - Add proper request validation
  - Implement API versioning
  - Add comprehensive error responses
  - Support for pagination and filtering

- **Performance**:
  - Implement caching for frequently accessed data
  - Add request throttling and rate limiting
  - Optimize database queries and data processing

- **Security**:
  - Implement proper CORS configuration
  - Add request validation and sanitization
  - Implement API authentication (if needed)

### 2. Frontend Improvements

#### User Interface
- **Design System**:
  - Extend Shadcn UI with custom components
  - Implement consistent theming and styling
  - Add responsive design for all screen sizes
  - Improve accessibility compliance

- **User Experience**:
  - Add loading states and skeleton screens
  - Implement error handling and user feedback
  - Add animations and transitions
  - Improve navigation and information architecture

#### Data Management
- **State Management**:
  - Implement proper state management with React hooks
  - Add data caching and persistence
  - Implement optimistic updates for better UX

- **API Integration**:
  - Create a unified API client
  - Add request caching and deduplication
  - Implement retry mechanisms and error handling
  - Add request cancellation for improved performance

### 3. DevOps Improvements

#### Configuration Management
- Implement environment-based configuration
- Add support for configuration files and environment variables
- Create separate development, testing, and production configurations

#### Logging and Monitoring
- Implement structured logging
- Add log rotation and archiving
- Implement application monitoring
- Add performance metrics collection

#### Testing
- Implement unit tests for core functionality
- Add integration tests for API endpoints
- Create end-to-end tests for critical user flows
- Implement continuous integration

#### Deployment
- Create Docker containers for easy deployment
- Implement CI/CD pipelines
- Add deployment scripts and documentation
- Support for cloud deployment (AWS, Azure, GCP)

## Implementation Plan

### Phase 1: Foundation and Architecture

1. **Setup Project Structure**
   - Create new directory structure
   - Set up configuration management
   - Implement logging framework

2. **Core Data Components**
   - Implement token management
   - Create data fetching modules
   - Implement data processing and storage

3. **Base Model Framework**
   - Create base model classes
   - Implement model registry
   - Set up model evaluation framework

### Phase 2: Core Functionality

1. **Prediction Models**
   - Implement winner prediction model
   - Create score prediction model
   - Add model optimization components

2. **API Server**
   - Implement API routes
   - Add request validation
   - Create error handling middleware

3. **Frontend Foundation**
   - Set up Next.js project
   - Implement UI components
   - Create API client

### Phase 3: Integration and Enhancement

1. **Full Pipeline Integration**
   - Connect all components
   - Implement end-to-end workflow
   - Add automated processes

2. **User Interface Enhancements**
   - Implement all UI screens
   - Add data visualization
   - Improve user experience

3. **Testing and Optimization**
   - Write comprehensive tests
   - Optimize performance
   - Fix bugs and issues

### Phase 4: Finalization and Deployment

1. **Documentation**
   - Create user documentation
   - Write developer documentation
   - Add inline code documentation

2. **Deployment Setup**
   - Create Docker containers
   - Set up CI/CD pipeline
   - Prepare deployment scripts

3. **Final Testing and Launch**
   - Perform end-to-end testing
   - Fix any remaining issues
   - Launch the rebuilt application

## Technical Implementation Details

### 1. External API Integration

#### H2H GG League API Endpoints

The application interacts with the H2H GG League API to fetch match data. Here are the key endpoints and their usage:

1. **Authentication Token Retrieval**
   - Method: Browser automation with Selenium
   - URL: `https://www.h2hggl.com/en/ebasketball/players/`
   - Token Location: LocalStorage key `sis-hudstats-token`
   - Implementation:
     ```python
     def get_bearer_token():
         # Set up headless Chrome browser
         chrome_options = Options()
         chrome_options.add_argument('--headless')
         driver = webdriver.Chrome(options=chrome_options)

         try:
             # Visit the website
             driver.get('https://www.h2hggl.com/en/ebasketball/players/')

             # Wait for token to be set in local storage
             wait = WebDriverWait(driver, 10)
             token = driver.execute_script("return localStorage.getItem('sis-hudstats-token')")

             return token
         finally:
             driver.quit()
     ```

2. **Match History API**
   - Base URL: `https://api-sis-stats.hudstats.com/v1/schedule`
   - Method: GET
   - Headers:
     ```
     'accept': 'application/json, text/plain, */*'
     'accept-language': 'en-US,en;q=0.9'
     'authorization': 'Bearer {token}'
     'origin': 'https://www.h2hggl.com'
     'referer': 'https://www.h2hggl.com/'
     ```
   - Query Parameters:
     ```
     'schedule-type': 'match'
     'from': '{from_date}'  # Format: YYYY-MM-DD HH:MM
     'to': '{to_date}'      # Format: YYYY-MM-DD HH:MM
     'order': 'desc'
     'tournament-id': 1     # Default tournament ID
     ```
   - Response: JSON array of match data

3. **Upcoming Matches API**
   - Base URL: `https://api-sis-stats.hudstats.com/v1/schedule`
   - Method: GET
   - Headers: Same as Match History API
   - Query Parameters:
     ```
     'schedule-type': 'match'
     'from': '{current_date}'  # Format: YYYY-MM-DD HH:MM
     'to': '{future_date}'     # Format: YYYY-MM-DD HH:MM
     'order': 'asc'
     'tournament-id': 1        # Default tournament ID
     ```
   - Response: JSON array of upcoming match data

### 2. Internal API Endpoints

The application provides the following RESTful API endpoints for the frontend:

1. **Predictions API**
   - Endpoint: `/api/predictions`
   - Method: GET
   - Query Parameters:
     - `timestamp`: Cache-busting parameter
   - Response: JSON array of match predictions
   - Implementation:
     ```python
     @app.route('/api/predictions', methods=['GET'])
     def get_predictions():
         # Read predictions from file
         with open(PREDICTIONS_FILE, 'r', encoding='utf-8') as f:
             predictions = json.load(f)

         # Filter for future matches only
         eastern = pytz.timezone('US/Eastern')
         now = datetime.now(eastern)

         future_matches = [
             match for match in predictions
             if datetime.fromisoformat(match.get("match_time", "").replace("Z", "+00:00")) > now
         ]

         return jsonify(future_matches)
     ```

2. **Score Predictions API**
   - Endpoint: `/api/score-predictions`
   - Method: GET
   - Query Parameters:
     - `timestamp`: Cache-busting parameter
   - Response: JSON object with predictions array and summary object
   - Implementation:
     ```python
     @app.route('/api/score-predictions', methods=['GET'])
     def get_score_predictions():
         # Read predictions from file
         with open(PREDICTIONS_FILE, 'r', encoding='utf-8') as f:
             predictions = json.load(f)

         # Filter for future matches only
         eastern = pytz.timezone('US/Eastern')
         now = datetime.now(eastern)

         future_matches = [
             match for match in predictions
             if datetime.fromisoformat(match.get("match_time", "").replace("Z", "+00:00")) > now
         ]

         # Get score model accuracy from registry
         score_model_accuracy = 10.0  # Default value
         try:
             registry = ScoreModelRegistry(MODELS_DIR)
             best_model = registry.get_best_model()
             if best_model:
                 score_model_accuracy = best_model.get("total_score_mae", 10.0)
         except Exception:
             pass

         return jsonify({
             "predictions": future_matches,
             "summary": {
                 "model_accuracy": score_model_accuracy
             }
         })
     ```

3. **Prediction History API**
   - Endpoint: `/api/prediction-history`
   - Method: GET
   - Query Parameters:
     - `player`: Filter by player name
     - `date`: Filter by date
     - `timestamp`: Cache-busting parameter
   - Response: JSON object with predictions array
   - Implementation:
     ```python
     @app.route('/api/prediction-history', methods=['GET'])
     def get_prediction_history():
         # Get filter parameters
         player_filter = request.args.get('player', '')
         date_filter = request.args.get('date', '')

         # Read prediction history from file
         with open(PREDICTION_HISTORY_FILE, 'r', encoding='utf-8') as f:
             predictions = json.load(f)

         # Apply filters
         filtered_predictions = predictions
         if player_filter:
             filtered_predictions = [
                 p for p in filtered_predictions
                 if player_filter.lower() in p.get('home_player', '').lower() or
                    player_filter.lower() in p.get('away_player', '').lower()
             ]

         if date_filter:
             filtered_predictions = [
                 p for p in filtered_predictions
                 if date_filter in p.get('match_time', '')
             ]

         return jsonify({
             "predictions": filtered_predictions
         })
     ```

4. **Stats API**
   - Endpoint: `/api/stats`
   - Method: GET
   - Query Parameters:
     - `timestamp`: Cache-busting parameter
   - Response: JSON object with prediction statistics
   - Implementation:
     ```python
     @app.route('/api/stats', methods=['GET'])
     def get_stats():
         # Read predictions from file
         with open(PREDICTIONS_FILE, 'r', encoding='utf-8') as f:
             predictions = json.load(f)

         # Calculate statistics
         total_matches = len(predictions)
         home_wins_predicted = sum(1 for match in predictions if match.get("predicted_winner") == "home")
         away_wins_predicted = total_matches - home_wins_predicted

         # Calculate average confidence
         confidences = [match.get("confidence", 0) for match in predictions]
         avg_confidence = sum(confidences) / len(confidences) if confidences else 0

         # Get model accuracy from registry
         model_accuracy = 0.5  # Default value
         try:
             registry = ModelRegistry(MODELS_DIR)
             best_model = registry.get_best_model()
             if best_model:
                 model_accuracy = best_model.get("accuracy", 0.5)
         except Exception:
             pass

         return jsonify({
             "total_matches": total_matches,
             "home_wins_predicted": home_wins_predicted,
             "away_wins_predicted": away_wins_predicted,
             "avg_confidence": avg_confidence,
             "model_accuracy": model_accuracy,
             "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
         })
     ```

5. **Refresh API**
   - Endpoint: `/api/refresh`
   - Method: POST
   - Response: JSON object with refresh status
   - Implementation:
     ```python
     @app.route('/api/refresh', methods=['POST'])
     def refresh_data():
         try:
             # Run the prediction refresh process
             success = refresh_predictions()

             if success:
                 return jsonify({"status": "success", "message": "Predictions refreshed successfully"})
             else:
                 return jsonify({"status": "error", "message": "Failed to refresh predictions"}), 500
         except Exception as e:
             return jsonify({"status": "error", "message": str(e)}), 500
     ```

### 3. Data Processing Details

#### Player Statistics Calculation

The application calculates comprehensive player statistics from match history data:

```python
def calculate_player_stats(matches):
    # Initialize player stats dictionary
    player_stats = {}

    # Process each match
    for match in matches:
        # Extract match data
        home_player_id = match['homePlayer']['id']
        home_player_name = match['homePlayer']['name']
        away_player_id = match['awayPlayer']['id']
        away_player_name = match['awayPlayer']['name']

        home_team_id = match['homeTeam']['id']
        home_team_name = match['homeTeam']['name']
        away_team_id = match['awayTeam']['id']
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
                'teams_used': {},
                'opponents_faced': {}
            }

        # Update home player match data
        player_stats[home_player_id]['total_matches'] += 1
        player_stats[home_player_id]['total_score'] += home_score

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

        # Similar updates for away player...

    # Calculate derived stats
    for player_id, stats in player_stats.items():
        # Calculate win rate
        stats['win_rate'] = stats['wins'] / stats['total_matches'] if stats['total_matches'] > 0 else 0

        # Calculate average score
        stats['avg_score'] = stats['total_score'] / stats['total_matches'] if stats['total_matches'] > 0 else 0

        # Calculate team-specific stats
        for team_id, team_stats in stats['teams_used'].items():
            team_matches = team_stats['matches']
            team_stats['win_rate'] = team_stats['wins'] / team_matches if team_matches > 0 else 0
            team_stats['avg_score'] = team_stats['total_score'] / team_matches if team_matches > 0 else 0

    return player_stats
```

### 4. Prediction Model Details

#### Winner Prediction Model

The winner prediction model uses a RandomForest classifier with the following features:

```python
def _extract_features(self, player_stats, matches):
    features = []
    labels = []

    for match in matches:
        home_player_id = match['homePlayer']['id']
        away_player_id = match['awayPlayer']['id']

        # Skip if player stats not available
        if home_player_id not in player_stats or away_player_id not in player_stats:
            continue

        home_player = player_stats[home_player_id]
        away_player = player_stats[away_player_id]

        home_team_id = match['homeTeam']['id']
        away_team_id = match['awayTeam']['id']

        # Extract features
        match_features = [
            # Player overall stats
            home_player.get('win_rate', 0),
            away_player.get('win_rate', 0),
            home_player.get('avg_score', 0),
            away_player.get('avg_score', 0),
            home_player.get('total_matches', 0),
            away_player.get('total_matches', 0),

            # Team-specific stats
            self._get_team_win_rate(home_player, home_team_id),
            self._get_team_win_rate(away_player, away_team_id),
            self._get_team_avg_score(home_player, home_team_id),
            self._get_team_avg_score(away_player, away_team_id),
            self._get_team_matches(home_player, home_team_id),
            self._get_team_matches(away_player, away_team_id),

            # Head-to-head stats
            self._get_h2h_win_rate(home_player, away_player_id),
            self._get_h2h_win_rate(away_player, home_player_id),
        ]

        features.append(match_features)

        # Label: 1 if home win, 0 if away win
        home_score = match['homeScore']
        away_score = match['awayScore']
        label = 1 if home_score > away_score else 0
        labels.append(label)

    return np.array(features), np.array(labels)
```

#### Score Prediction Model

The score prediction model uses a stacking ensemble of multiple regression models:

```python
def _create_model(self, random_state=42):
    # Create base models
    xgb_model_home = XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=random_state
    )

    gb_model_home = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=random_state
    )

    ridge_model_home = Ridge(alpha=1.0, random_state=random_state)
    lasso_model_home = Lasso(alpha=0.1, random_state=random_state)

    # Create stacking ensemble for home score
    home_stacking_model = StackingRegressor(
        estimators=[
            ('xgb', xgb_model_home),
            ('gb', gb_model_home),
            ('ridge', ridge_model_home),
            ('lasso', lasso_model_home)
        ],
        final_estimator=Ridge(alpha=0.5, random_state=random_state),
        cv=5,
        n_jobs=-1
    )

    # Similar setup for away score model...

    # Create feature scaling and model pipeline
    home_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', home_stacking_model)
    ])

    away_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', away_stacking_model)
    ])

    return home_pipeline, away_pipeline
```

### 5. Frontend Integration

#### API Client

The frontend uses a custom API client with retry capability:

```typescript
// API base URL from environment or default
const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Fetch with retry function
async function fetchWithRetry(url: string, options = {}, maxRetries = 3) {
  let retries = 0;

  while (retries < maxRetries) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      retries++;
      console.error(`Attempt ${retries} failed: ${error.message}`);

      if (retries >= maxRetries) {
        throw error;
      }

      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retries)));
    }
  }
}

// Example usage in a React component
const fetchPredictions = async () => {
  try {
    setLoading(true);
    const timestamp = Date.now();
    const data = await fetchWithRetry(`${apiBaseUrl}/api/predictions?timestamp=${timestamp}`);
    setPredictions(data);
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

## Key Features to Preserve

1. **Data Collection**
   - Authentication token retrieval from H2H GG League
   - Historical match data fetching
   - Upcoming match data retrieval
   - Player statistics calculation

2. **Prediction Models**
   - Winner prediction model
   - Score prediction model
   - Model optimization and tuning
   - Model registry and versioning

3. **User Interface**
   - Match predictions display
   - Score predictions with point differentials
   - Prediction history tracking
   - Statistics and metrics visualization
   - Filtering and sorting capabilities

4. **Automation**
   - End-to-end prediction pipeline
   - Automated data refresh
   - Scheduled prediction updates

## Data Formats and File Structures

### Key Data Files

The application relies on several JSON files for data storage and exchange:

1. **Match History Data** (`output/match_history.json`)
   - Contains historical match data fetched from the H2H GG League API
   - Used for training prediction models and calculating player statistics
   - Example structure:
     ```json
     [
       {
         "id": "12345",
         "homePlayer": {
           "id": "91",
           "name": "DOUBLEFOUR"
         },
         "awayPlayer": {
           "id": "159",
           "name": "HOLLOW"
         },
         "homeTeam": {
           "id": "3",
           "name": "Boston Celtics"
         },
         "awayTeam": {
           "id": "20",
           "name": "New York Knicks"
         },
         "homeScore": 65,
         "awayScore": 58,
         "fixtureStart": "2025-04-20T18:30:00Z",
         "result": "home_win"
       }
     ]
     ```

2. **Player Statistics** (`output/player_stats.json`)
   - Contains calculated player statistics derived from match history
   - Used for feature extraction in prediction models
   - Example structure:
     ```json
     {
       "91": {
         "player_name": "DOUBLEFOUR",
         "total_matches": 322,
         "wins": 132,
         "losses": 190,
         "total_score": 17770,
         "win_rate": 0.4099,
         "avg_score": 55.1863,
         "teams_used": {
           "3": {
             "team_name": "Boston Celtics",
             "matches": 59,
             "wins": 25,
             "losses": 34,
             "total_score": 3147,
             "win_rate": 0.4237,
             "avg_score": 53.3390
           }
         },
         "opponents_faced": {
           "159": {
             "matches": 15,
             "wins": 7,
             "losses": 8,
             "win_rate": 0.4667
           }
         }
       }
     }
     ```

3. **Upcoming Matches** (`output/upcoming_matches.json`)
   - Contains data about upcoming matches fetched from the API
   - Used as input for generating predictions
   - Similar structure to match history but without scores and results

4. **Match Predictions** (`output/upcoming_match_predictions.json`)
   - Contains predictions for upcoming matches
   - Consumed by the frontend via the API
   - Example structure:
     ```json
     [
       {
         "fixtureId": "12345",
         "homePlayer": {
           "id": "91",
           "name": "DOUBLEFOUR"
         },
         "awayPlayer": {
           "id": "159",
           "name": "HOLLOW"
         },
         "homeTeam": {
           "id": "3",
           "name": "Boston Celtics"
         },
         "awayTeam": {
           "id": "20",
           "name": "New York Knicks"
         },
         "fixtureStart": "2025-04-25T18:30:00Z",
         "prediction": {
           "home_win_probability": 0.65,
           "away_win_probability": 0.35,
           "predicted_winner": "home",
           "confidence": 0.65
         },
         "score_prediction": {
           "home_score": 62,
           "away_score": 55,
           "total_score": 117
         }
       }
     ]
     ```

5. **Prediction History** (`output/prediction_history.json`)
   - Contains historical predictions for matches that have already started
   - Used for displaying prediction history in the frontend
   - Similar to match predictions but includes a `saved_at` timestamp

6. **Model Registry** (`models/model_registry.json` and `models/score_model_registry.json`)
   - Track trained models and their performance metrics
   - Used to select the best model for predictions
   - Example structure:
     ```json
     {
       "models": [
         {
           "model_id": "20250321_044530",
           "model_path": "models/prediction_model_20250321_044530.pkl",
           "info_path": "models/model_info_20250321_044530.json",
           "training_time": "20250321_044530",
           "accuracy": 0.6467,
           "num_samples": 8672,
           "data_files": {
             "player_stats": "output/player_stats.json",
             "match_history": "output/match_history.json"
           }
         }
       ],
       "best_model_id": "20250321_044530"
     }
     ```

### Model Files

1. **Winner Prediction Models** (`models/prediction_model_*.pkl`)
   - Serialized RandomForest classifier models for predicting match winners
   - Trained on historical match data and player statistics

2. **Score Prediction Models** (`models/score_prediction_model_*.pkl`)
   - Serialized stacking ensemble models for predicting match scores
   - Consists of two pipelines: one for home score and one for away score

3. **Model Metadata** (`models/model_info_*.json` and `models/score_model_info_*.json`)
   - Contains metadata about trained models including evaluation metrics
   - Used by the model registry to track model performance

## Error Handling and Logging

### Logging Configuration

The application uses Python's built-in logging module with a consistent configuration across components:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("{component_name}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("{ComponentName}")
```

Each major component has its own logger and log file:
- `api.log` - API server logs
- `dashboard.log` - Dashboard launcher logs
- `model_tuning.log` - Model tuning logs
- `score_model_training.log` - Score model training logs
- `upcoming_matches.log` - Upcoming matches fetcher logs
- `prediction_refresh.log` - Prediction refresh logs

### Error Handling Patterns

1. **API Error Handling**
   - All API endpoints use try-except blocks to catch and handle exceptions
   - Errors are logged and returned as JSON responses with appropriate HTTP status codes
   - Example:
     ```python
     @app.route('/api/predictions', methods=['GET'])
     def get_predictions():
         try:
             # Implementation
             return jsonify(result)
         except Exception as e:
             logger.error(f"Error retrieving predictions: {e}")
             return jsonify({"error": str(e)}), 500
     ```

2. **Data Fetching Error Handling**
   - Network requests use try-except blocks with specific exception handling
   - Failed requests are logged and gracefully handled with fallback values
   - Retry mechanisms are implemented for transient failures

3. **Model Training Error Handling**
   - Model training errors are caught, logged, and reported
   - Failed model training falls back to using the best existing model

4. **Frontend Error Handling**
   - API requests use a custom `fetchWithRetry` function with exponential backoff
   - Error states are managed in React components with appropriate user feedback
   - Loading states are used to indicate ongoing operations

## Scheduled Tasks and Background Processes

The application includes several scheduled tasks and background processes:

1. **Automatic Prediction Refresh**
   - Runs every hour to refresh predictions with the latest data
   - Implemented as a background thread in the API server
   - Uses a separate Python process to avoid threading issues
   - Implementation:
     ```python
     def refresh_predictions():
         import time
         while True:
             try:
                 # Wait for 1 hour
                 time.sleep(3600)

                 # Run the prediction refresh process
                 # Implementation details...

             except Exception as e:
                 logger.error(f"Error in refresh cycle: {e}")

     # Start the background thread
     refresh_thread = threading.Thread(target=refresh_predictions, daemon=True)
     refresh_thread.start()
     ```

2. **On-Demand Prediction Refresh**
   - Triggered via the `/api/refresh` endpoint
   - Creates and runs a temporary Python script to refresh predictions
   - Avoids circular imports and threading issues

## Environment Setup and Dependencies

### Python Dependencies

The application requires the following Python packages (from `requirements.txt`):

```
# Core libraries
requests
numpy
pandas
scikit-learn
scipy
xgboost

# Web scraping
selenium

# Model optimization
scikit-optimize

# Visualization (for debugging and analysis)
matplotlib
seaborn

# API Server
flask
flask-cors

# Utilities
python-dateutil
tqdm
pytz
```

### Frontend Dependencies

The Next.js frontend requires the following key dependencies (from `package.json`):

```json
{
  "dependencies": {
    "@radix-ui/react-*": "^1.1.*",
    "chart.js": "^4.4.8",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "date-fns": "^4.1.0",
    "lucide-react": "^0.483.0",
    "next": "15.2.3",
    "next-themes": "^0.4.6",
    "react": "^19.0.0",
    "react-chartjs-2": "^5.3.0",
    "react-dom": "^19.0.0",
    "tailwind-merge": "^3.0.2"
  }
}
```

### Browser Requirements

- Chrome browser is required for the Selenium-based token retrieval
- The application is designed to work with modern browsers (Chrome, Firefox, Safari, Edge)

## Configuration and Constants

The application uses hardcoded constants for configuration, which should be moved to a proper configuration system in the rebuild:

```python
# Constants - Use absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PREDICTIONS_FILE = os.path.join(OUTPUT_DIR, "upcoming_match_predictions.json")
PLAYER_STATS_FILE = os.path.join(OUTPUT_DIR, "player_stats.json")
MATCH_HISTORY_FILE = os.path.join(OUTPUT_DIR, "match_history.json")
PREDICTION_HISTORY_FILE = os.path.join(OUTPUT_DIR, "prediction_history.json")
MODELS_DIR = os.path.join(BASE_DIR, "models")
```

## Frontend-Backend Integration

The frontend and backend are integrated through the following mechanisms:

1. **API Base URL**
   - The frontend uses an environment variable `NEXT_PUBLIC_API_URL` to determine the API base URL
   - Falls back to `http://localhost:5000` if not specified
   - Example:
     ```typescript
     const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
     ```

2. **API Endpoints**
   - The frontend calls the backend API endpoints with a timestamp parameter to prevent caching
   - Example:
     ```typescript
     const timestamp = Date.now();
     const data = await fetchWithRetry(`${apiBaseUrl}/api/predictions?timestamp=${timestamp}`);
     ```

3. **Static File Serving**
   - The Flask API server serves the React frontend static files
   - The frontend is built and placed in the `frontend/2kflash-dashboard/build` directory
   - The API server serves the frontend at the root path (`/`)

## Conclusion

This rebuild plan aims to transform the 2K Flash application into a more organized, maintainable, and professional system while preserving all existing functionality. By implementing a clean architecture, improving code quality, and enhancing the user experience, the rebuilt application will be more robust, scalable, and easier to maintain.

The phased implementation approach allows for incremental improvements and ensures that the application remains functional throughout the rebuild process. Each phase builds upon the previous one, gradually transforming the application into its improved form.

The detailed technical information provided in this plan should give developers a comprehensive understanding of the current system's implementation details, data formats, error handling patterns, and integration points, enabling them to rebuild the application while preserving its core functionality.

Upon completion, the rebuilt 2K Flash application will provide a superior experience for both users and developers, with better performance, reliability, and maintainability.
