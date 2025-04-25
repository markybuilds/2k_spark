# 2K Flash - NBA 2K25 eSports Match Prediction System

2K Flash is a comprehensive prediction system for NBA 2K25 eSports matches in the H2H GG League. The system collects data from the H2H GG League API, processes player statistics, and uses machine learning models to predict match winners and scores.

## Features

- Data collection from H2H GG League API
- Comprehensive player statistics calculation
- Machine learning models for winner and score predictions
- RESTful API for frontend-backend communication
- Modern Next.js frontend with Shadcn UI components
- Automated model training and optimization

## Project Structure

```
2k_spark/
├── backend/                   # Backend code
│   ├── app/                   # Application entry points
│   ├── config/                # Configuration management
│   ├── core/                  # Core business logic
│   │   ├── data/              # Data access and processing
│   │   ├── models/            # Prediction models
│   │   └── optimization/      # Model optimization
│   ├── api/                   # API endpoints
│   ├── services/              # Service layer
│   ├── utils/                 # Utility functions
│   └── tests/                 # Tests
├── frontend/                  # Frontend code
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   ├── lib/                   # Utility libraries
│   ├── hooks/                 # Custom React hooks
│   └── public/                # Static assets
├── output/                    # Output data files
├── models/                    # Trained models
├── logs/                      # Log files
└── memory-bank/               # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Chrome browser (for Selenium)
- ChromeDriver (for Selenium)

### Backend Setup

1. Install Python dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```

2. Run the API server:
   ```
   python app/api.py
   ```

### CLI Usage

The CLI provides various commands for data fetching, model training, and more:

```
python app/cli.py fetch-token        # Fetch authentication token
python app/cli.py fetch-history      # Fetch match history
python app/cli.py fetch-upcoming     # Fetch upcoming matches
python app/cli.py calculate-stats    # Calculate player statistics
python app/cli.py train-winner-model # Train winner prediction model
python app/cli.py train-score-model  # Train score prediction model
python app/cli.py list-models        # List trained models
```

### Frontend Setup

1. Install Node.js dependencies:
   ```
   cd frontend
   npm install
   ```

2. Run the development server:
   ```
   npm run dev
   ```

## API Endpoints

- `GET /api/predictions`: Get predictions for upcoming matches
- `GET /api/score-predictions`: Get score predictions for upcoming matches
- `GET /api/prediction-history`: Get historical predictions with filtering
- `GET /api/stats`: Get prediction statistics and metrics
- `POST /api/refresh`: Trigger data refresh and prediction update

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- H2H GG League for providing the data API
- NBA 2K25 eSports community
