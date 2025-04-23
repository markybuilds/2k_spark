# NBA 2K eSports Prediction Model Scripts

This directory contains utility scripts for development, maintenance, and running the NBA 2K eSports prediction model pipeline.

## Contents

### Utility Scripts

- `test_api.py`: Script to test API endpoints
- `setup_git.bat`: Script to set up the Git repository

### Prediction Model Pipeline Scripts

- `run_data_pipeline.py`: Collects a comprehensive dataset of historical matches and player-team statistics
- `train_evaluate_models.py`: Trains and evaluates different prediction models
- `refine_prediction_algorithm.py`: Refines the prediction algorithm based on evaluation results
- `update_data.py`: Updates the dataset with new matches
- `generate_predictions.py`: Generates predictions for upcoming matches
- `schedule_tasks.py`: Schedules regular data updates and predictions

## Prediction Model Pipeline

These scripts implement the full workflow for the prediction model:

1. **Data Collection**: Collect historical match data and player statistics
2. **Data Processing**: Process raw data into features for the prediction model
3. **Model Training**: Train and evaluate different prediction models
4. **Algorithm Refinement**: Refine the prediction algorithm based on evaluation results
5. **Regular Updates**: Update the dataset with new matches
6. **Prediction Generation**: Generate predictions for upcoming matches
7. **Scheduled Tasks**: Schedule regular data updates and predictions

## Usage

### Utility Scripts

#### test_api.py

This script tests the API endpoint for player standings:

```
python scripts/test_api.py
```

#### setup_git.bat

This script sets up the Git repository:

```
.\scripts\setup_git.bat
```

### Prediction Model Pipeline Scripts

#### 1. Run Data Pipeline

Collects a comprehensive dataset of historical matches and player-team statistics.

```bash
python scripts/run_data_pipeline.py --start-date 2023-01-01 --end-date 2023-12-31
```

**Arguments:**
- `--start-date`: Start date in format YYYY-MM-DD (default: 90 days ago)
- `--end-date`: End date in format YYYY-MM-DD (default: today)
- `--tournament-id`: Tournament ID (default: 1)
- `--output-dir`: Output directory (default: data/processed)

#### 2. Train and Evaluate Models

Trains and evaluates different prediction models using the collected data.

```bash
python scripts/train_evaluate_models.py --test-size 0.2 --random-state 42
```

**Arguments:**
- `--processed-data-dir`: Directory containing processed data (default: data/processed)
- `--test-size`: Proportion of data to use for testing (default: 0.2)
- `--random-state`: Random state for reproducibility (default: 42)
- `--output-dir`: Output directory for model results (default: data/processed)

#### 3. Refine Prediction Algorithm

Refines the prediction algorithm based on model evaluation results.

```bash
python scripts/refine_prediction_algorithm.py --model-type RandomForest
```

**Arguments:**
- `--processed-data-dir`: Directory containing processed data (default: data/processed)
- `--model-type`: Type of model to refine (default: RandomForest)
- `--random-state`: Random state for reproducibility (default: 42)
- `--output-dir`: Output directory for refined model (default: data/processed)

#### 4. Update Data

Updates the dataset with new matches.

```bash
python scripts/update_data.py --days 7
```

**Arguments:**
- `--days`: Number of days to fetch data for (default: 7)
- `--tournament-id`: Tournament ID (default: 1)
- `--output-dir`: Output directory (default: data/processed)

#### 5. Generate Predictions

Generates predictions for upcoming matches.

```bash
python scripts/generate_predictions.py --hours 24 --min-confidence 0.6 --format json
```

**Arguments:**
- `--hours`: Number of hours ahead to predict matches for (default: 24)
- `--days`: Number of days ahead to predict matches for (default: 0)
- `--tournament-id`: Tournament ID (default: 1)
- `--min-confidence`: Minimum confidence threshold for high-confidence predictions (default: 0.6)
- `--output-dir`: Output directory (default: data/processed)
- `--format`: Output format (json, csv, or text) (default: text)

#### 6. Schedule Tasks

Schedules regular data updates and predictions.

```bash
python scripts/schedule_tasks.py --update-interval 12 --prediction-interval 6
```

**Arguments:**
- `--update-interval`: Interval in hours for data updates (default: 12)
- `--prediction-interval`: Interval in hours for predictions (default: 6)
- `--tournament-id`: Tournament ID (default: 1)
- `--output-dir`: Output directory (default: data/processed)

## Workflow Example

Here's an example workflow for using these scripts:

1. **Initial Data Collection**:
   ```bash
   python scripts/run_data_pipeline.py --start-date 2023-01-01
   ```

2. **Train and Evaluate Models**:
   ```bash
   python scripts/train_evaluate_models.py
   ```

3. **Refine the Prediction Algorithm**:
   ```bash
   python scripts/refine_prediction_algorithm.py
   ```

4. **Generate Predictions**:
   ```bash
   python scripts/generate_predictions.py --hours 24
   ```

5. **Schedule Regular Updates and Predictions**:
   ```bash
   python scripts/schedule_tasks.py
   ```

## Dependencies

These scripts require the following Python packages:

- pandas
- numpy
- scikit-learn
- schedule
- tabulate

You can install them using pip:

```bash
pip install pandas numpy scikit-learn schedule tabulate
```

## Notes

- The scripts use the configuration settings from `src/config.py`.
- Processed data is stored in the directory specified by `PROCESSED_DATA_DIR` in the config file.
- Raw data is stored in the directory specified by `RAW_DATA_DIR` in the config file.
- The refined prediction algorithm is saved to `src/prediction/refined_algorithm.py`.
