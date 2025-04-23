# NBA 2K eSports Prediction Model

This project aims to build a prediction model for NBA 2K eSports league to predict the winners of upcoming matches. It fetches data from h2hggl.com and uses machine learning techniques to make predictions.

## Project Structure

```
├── cache/              # Directory for caching data (tokens, etc.)
├── src/                # Source code directory
│   ├── data/           # Data fetching and processing modules
│   │   └── players.py  # Player data fetching module
│   ├── models/         # Prediction models
│   ├── utils/          # Utility functions
│   ├── auth.py         # Authentication module for retrieving tokens
│   └── config.py       # Configuration settings
├── tests/              # Unit tests
│   ├── test_auth.py    # Tests for authentication module
│   └── test_token_refresh.py # Tests for token refresh functionality
├── .gitignore          # Git ignore file
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

## Authentication

The project uses Selenium to authenticate with h2hggl.com by retrieving a bearer token from localStorage. The token is cached for subsequent requests to minimize the need for browser automation.

## Configuration

Configuration settings are defined in the `src/config.py` file. You can modify these settings directly in the file if needed.

## Requirements

- Python 3.8+
- Chrome browser (for Selenium WebDriver)

## Development

### Adding New Features

1. Create appropriate modules in the `src` directory
2. Write unit tests in the `tests` directory
3. Update documentation as needed

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.
