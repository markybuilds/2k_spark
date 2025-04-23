# Development Guide

This guide provides information for developers working on the NBA 2K Prediction Model project.

## Setting Up the Development Environment

1. Clone the repository:
   ```
   git clone https://github.com/markybuilds/2k_spark.git
   cd 2k_spark
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Project Structure

The project follows a modular structure:

- `src/`: Source code
  - `data/`: Data fetching and processing modules
  - `models/`: Prediction models
  - `utils/`: Utility functions
  - `auth.py`: Authentication module
  - `config.py`: Configuration settings
- `tests/`: Unit tests
- `examples/`: Example scripts
- `docs/`: Documentation
- `scripts/`: Utility scripts

## Development Workflow

1. **Create a Feature Branch**:
   ```
   git checkout -b feature/your-feature-name
   ```

2. **Write Tests**:
   - Add tests for your feature in the `tests/` directory
   - Follow the naming convention: `test_*.py`

3. **Implement Your Feature**:
   - Add your code to the appropriate module in the `src/` directory
   - Follow the project's coding standards

4. **Run Tests**:
   ```
   python -m unittest discover tests
   ```

5. **Create an Example**:
   - Add an example script in the `examples/` directory
   - Demonstrate how to use your feature

6. **Update Documentation**:
   - Update the relevant documentation in the `docs/` directory

7. **Commit Your Changes**:
   ```
   git add .
   git commit -m "Add your feature"
   ```

8. **Push Your Branch**:
   ```
   git push origin feature/your-feature-name
   ```

9. **Create a Pull Request**:
   - Go to the repository on GitHub
   - Create a pull request from your branch to the main branch

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for better code readability
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single task
- Use meaningful variable and function names

## Testing

- Write unit tests for all new code
- Use the `unittest` framework
- Place tests in the `tests/` directory
- Use sample data for testing to avoid making actual API requests

## Documentation

- Document all public functions, classes, and modules
- Update the API documentation when adding new endpoints
- Keep the project architecture document up to date

## Continuous Integration

- All tests must pass before merging a pull request
- Code should be formatted according to the project's coding standards
- Documentation should be up to date
