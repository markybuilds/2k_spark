# Project Architecture

This document provides an overview of the NBA 2K Prediction Model project architecture.

## Project Structure

```
2k_spark/
├── cache/                  # Cache directory for tokens and other temporary data
├── docs/                   # Project documentation
├── examples/               # Example scripts demonstrating how to use the project
├── scripts/                # Utility scripts for development and maintenance
├── src/                    # Source code
│   ├── data/               # Data fetching and processing modules
│   │   ├── players.py      # Player data fetching module
│   │   └── standings.py    # Standings data fetching module
│   ├── models/             # Prediction models
│   ├── utils/              # Utility functions
│   ├── auth.py             # Authentication module
│   └── config.py           # Configuration settings
├── tests/                  # Unit tests
│   ├── sample_data/        # Sample data for testing
│   ├── test_auth.py        # Tests for authentication module
│   └── test_standings.py   # Tests for standings module
├── .gitignore              # Git ignore file
├── LICENSE                 # MIT License
├── main.py                 # Main application entry point
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

## Component Overview

### Authentication (src/auth.py)

The authentication module handles retrieving and managing tokens for the h2hggl.com website. It uses Selenium to retrieve a bearer token from the website's localStorage and caches it for subsequent requests.

### Data Modules (src/data/)

- **players.py**: Fetches player data from the h2hggl.com API
- **standings.py**: Fetches and processes player standings data

### Configuration (src/config.py)

The configuration module contains all configuration settings for the application, including logging, API endpoints, and authentication settings.

### Models (src/models/)

This directory will contain the prediction models for the NBA 2K eSports league.

### Tests (tests/)

The tests directory contains unit tests for all modules in the project.

### Examples (examples/)

The examples directory contains example scripts demonstrating how to use the project's modules.

## Data Flow

1. **Authentication**: The application first authenticates with the h2hggl.com website to retrieve a bearer token.
2. **Data Fetching**: Using the bearer token, the application fetches data from various API endpoints.
3. **Data Processing**: The fetched data is processed and prepared for the prediction model.
4. **Prediction**: The processed data is fed into the prediction model to generate predictions.

## Design Decisions

### Authentication

We use Selenium for authentication because the h2hggl.com website doesn't have an official API. This allows us to retrieve a bearer token from the website's localStorage, which we can then use for subsequent API requests.

### Caching

We cache the bearer token to minimize the need for browser automation, which is slow and resource-intensive.

### Modular Design

The project follows a modular design, with separate modules for authentication, data fetching, and prediction. This makes the code easier to maintain and extend.

### Testing

We use unittest for testing, with separate test files for each module. We also use sample data for testing to avoid making actual API requests during tests.
