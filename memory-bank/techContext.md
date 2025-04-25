# 2K Flash Technical Context

## Technology Stack

### Backend Technologies
- **Python 3.10+**: Core programming language
- **Flask**: Web framework for API development
- **NumPy & Pandas**: Data processing and manipulation
- **scikit-learn**: Machine learning framework
- **XGBoost**: Gradient boosting for prediction models
- **scikit-optimize**: Hyperparameter optimization
- **Selenium**: Web automation for token retrieval
- **Requests**: HTTP client for API interactions
- **Flask-CORS**: Cross-origin resource sharing support
- **python-dateutil & pytz**: Date and timezone handling

### Frontend Technologies
- **Next.js**: React framework for frontend development
- **React**: UI library
- **Shadcn UI**: Component library based on Tailwind CSS
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js & react-chartjs-2**: Data visualization
- **date-fns**: Date manipulation library
- **TypeScript**: Type-safe JavaScript

### Development Tools
- **Git**: Version control
- **Docker**: Containerization
- **pytest**: Testing framework
- **ESLint & Prettier**: Code linting and formatting
- **GitHub Actions**: CI/CD pipeline

## External Dependencies

### H2H GG League API
- **Authentication**: Token-based authentication via browser automation
- **Endpoints**:
  - Match History: `https://api-sis-stats.hudstats.com/v1/schedule`
  - Upcoming Matches: `https://api-sis-stats.hudstats.com/v1/schedule`
- **Rate Limits**: Unknown, implement conservative rate limiting
- **Data Format**: JSON

## Development Environment Setup

### Backend Setup
1. Python 3.10+ installation
2. Virtual environment creation
3. Dependencies installation via pip:
   ```
   pip install -r requirements.txt
   ```
4. Chrome browser installation (for Selenium)
5. ChromeDriver installation (for Selenium)

### Frontend Setup
1. Node.js 18+ installation
2. Dependencies installation via npm:
   ```
   npm install
   ```
3. Environment configuration:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

## Directory Structure

### Backend Structure
```
backend/
├── app/                      # Application entry points
│   ├── api.py                # API server
│   ├── cli.py                # Command-line interface
│   ├── optimize_score_model.py  # Score model optimization
│   ├── optimize_winner_model.py # Winner model optimization
│   └── clean_model_registry.py  # Model registry maintenance
├── config/                   # Configuration management
│   ├── settings.py           # Application settings
│   └── logging_config.py     # Logging configuration
├── core/                     # Core business logic
│   ├── data/                 # Data access and processing
│   │   ├── fetchers/         # Data fetching modules
│   │   ├── processors/       # Data processing modules
│   │   └── storage.py        # Data storage utilities
│   ├── models/               # Prediction models
│   │   ├── base.py           # Base model class
│   │   ├── winner_prediction.py # Winner prediction model
│   │   ├── score_prediction.py # Score prediction model
│   │   ├── registry.py       # Model registry
│   │   └── feature_engineering.py # Feature engineering
│   └── optimization/         # Model optimization
│       └── bayesian_optimizer.py # Bayesian optimization
├── services/                 # Service layer
├── utils/                    # Utility functions
└── tests/                    # Tests
```

### Frontend Structure
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
│   ├── predictions/          # Prediction components
│   ├── history/              # History components
│   ├── scores/               # Score components
│   └── stats/                # Statistics components
├── lib/                      # Utility libraries
├── hooks/                    # Custom React hooks
└── public/                   # Static assets
```

## Data Storage

### File-Based Storage
- **Match History**: `output/match_history.json`
- **Player Statistics**: `output/player_stats.json`
- **Upcoming Matches**: `output/upcoming_matches.json`
- **Match Predictions**: `output/upcoming_match_predictions.json`
- **Prediction History**: `output/prediction_history.json`
- **Model Registry**: `models/model_registry.json` and `models/score_model_registry.json`
- **Trained Models**: `models/prediction_model_*.pkl` and `models/score_prediction_model_*.pkl`
- **Model Metadata**: `models/model_info_*.json` and `models/score_model_info_*.json`

## API Endpoints

### Internal API
- **GET /api/predictions**: Get predictions for upcoming matches
- **GET /api/score-predictions**: Get score predictions for upcoming matches
- **GET /api/prediction-history**: Get historical predictions with filtering
- **GET /api/stats**: Get prediction statistics and metrics
- **POST /api/refresh**: Trigger data refresh and prediction update

## Technical Constraints

### Performance Constraints
- **API Response Time**: < 500ms for all endpoints
- **Prediction Generation**: < 5 minutes for full refresh
- **Model Training**: < 30 minutes for complete retraining

### Security Constraints
- **API Access**: No authentication required (internal use only)
- **CORS**: Configured for frontend origin only
- **Token Handling**: Secure storage of H2H GG League API tokens

### Deployment Constraints
- **Environment**: Windows or Linux server
- **Dependencies**: Chrome browser for token retrieval
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: Minimum 1GB free space required

## Technical Debt and Limitations

### Known Limitations
- **Token Retrieval**: Relies on browser automation which can be fragile
- **Data Refresh**: Manual trigger or scheduled task required
- **Error Handling**: Limited recovery from certain API failures
- **Scaling**: Not designed for high-volume concurrent usage

### Future Technical Improvements
- **Database Migration**: Move from file-based storage to proper database
- **API Authentication**: Add user authentication for secure access
- **Containerization**: Complete Docker setup for easier deployment
- **Monitoring**: Add comprehensive monitoring and alerting
- **Caching**: Implement proper caching layer for improved performance
