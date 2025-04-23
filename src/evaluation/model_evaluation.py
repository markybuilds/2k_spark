"""
Model evaluation module for NBA 2K eSports prediction model.

This module provides functions to evaluate the performance of prediction models.
"""
import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from src.config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)


class EvaluationError(Exception):
    """Exception raised for errors in the evaluation module."""
    pass


def load_predictions(file_path: str) -> List[Dict[str, Any]]:
    """
    Load predictions from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of prediction dictionaries
        
    Raises:
        EvaluationError: If there is an error loading the predictions
    """
    try:
        with open(file_path, 'r') as f:
            predictions = json.load(f)
        
        return predictions
    
    except Exception as e:
        logger.error(f"Error loading predictions from {file_path}: {e}")
        raise EvaluationError(f"Failed to load predictions: {e}") from e


def load_actual_results(file_path: str) -> List[Dict[str, Any]]:
    """
    Load actual match results from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of match result dictionaries
        
    Raises:
        EvaluationError: If there is an error loading the results
    """
    try:
        with open(file_path, 'r') as f:
            results = json.load(f)
        
        return results
    
    except Exception as e:
        logger.error(f"Error loading actual results from {file_path}: {e}")
        raise EvaluationError(f"Failed to load actual results: {e}") from e


def match_predictions_with_results(
    predictions: List[Dict[str, Any]],
    results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Match predictions with actual results.
    
    Args:
        predictions: List of prediction dictionaries
        results: List of match result dictionaries
        
    Returns:
        List of dictionaries with predictions and actual results
        
    Raises:
        EvaluationError: If there is an error matching predictions with results
    """
    try:
        # Create a dictionary to map match IDs to results
        result_map = {result.get('matchId'): result for result in results if result.get('matchId')}
        
        # Match predictions with results
        matched_data = []
        
        for pred in predictions:
            match_id = pred.get('match_id')
            
            if not match_id or match_id not in result_map:
                continue
            
            result = result_map[match_id]
            
            # Determine actual winner
            if result.get('result') == 'home_win':
                actual_winner_id = result.get('homeParticipantId')
                actual_winner_name = result.get('homeParticipantName')
            else:
                actual_winner_id = result.get('awayParticipantId')
                actual_winner_name = result.get('awayParticipantName')
            
            # Determine predicted winner
            prediction_data = pred.get('prediction', {})
            predicted_winner = prediction_data.get('predicted_winner')
            
            # Create matched data entry
            matched_entry = {
                'match_id': match_id,
                'home_player_id': result.get('homeParticipantId'),
                'home_player_name': result.get('homeParticipantName'),
                'away_player_id': result.get('awayParticipantId'),
                'away_player_name': result.get('awayParticipantName'),
                'home_team': result.get('homeTeamName'),
                'away_team': result.get('awayTeamName'),
                'actual_winner_id': actual_winner_id,
                'actual_winner_name': actual_winner_name,
                'predicted_winner': predicted_winner,
                'prediction_confidence': prediction_data.get('confidence', 0),
                'player1_win_probability': prediction_data.get('player1_win_probability', 0),
                'player2_win_probability': prediction_data.get('player2_win_probability', 0)
            }
            
            # Determine if prediction was correct
            if predicted_winner == actual_winner_name:
                matched_entry['prediction_correct'] = True
            else:
                matched_entry['prediction_correct'] = False
            
            matched_data.append(matched_entry)
        
        return matched_data
    
    except Exception as e:
        logger.error(f"Error matching predictions with results: {e}")
        raise EvaluationError(f"Failed to match predictions with results: {e}") from e


def calculate_evaluation_metrics(matched_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate evaluation metrics for matched predictions and results.
    
    Args:
        matched_data: List of dictionaries with predictions and actual results
        
    Returns:
        Dictionary with evaluation metrics
        
    Raises:
        EvaluationError: If there is an error calculating metrics
    """
    try:
        if not matched_data:
            return {
                'accuracy': 0,
                'precision': 0,
                'recall': 0,
                'f1_score': 0,
                'auc': 0,
                'total_matches': 0,
                'correct_predictions': 0,
                'incorrect_predictions': 0
            }
        
        # Extract prediction correctness
        y_true = [entry['prediction_correct'] for entry in matched_data]
        
        # Extract prediction confidence
        y_score = [entry['prediction_confidence'] for entry in matched_data]
        
        # Calculate basic metrics
        total_matches = len(matched_data)
        correct_predictions = sum(y_true)
        incorrect_predictions = total_matches - correct_predictions
        
        # Calculate accuracy
        accuracy = correct_predictions / total_matches if total_matches > 0 else 0
        
        # Calculate metrics by confidence threshold
        confidence_thresholds = [0.0, 0.25, 0.5, 0.75, 0.9]
        threshold_metrics = {}
        
        for threshold in confidence_thresholds:
            # Filter predictions by confidence
            filtered_data = [entry for entry in matched_data if entry['prediction_confidence'] >= threshold]
            
            if not filtered_data:
                threshold_metrics[str(threshold)] = {
                    'accuracy': 0,
                    'total_matches': 0,
                    'correct_predictions': 0,
                    'incorrect_predictions': 0
                }
                continue
            
            # Calculate metrics
            filtered_total = len(filtered_data)
            filtered_correct = sum(1 for entry in filtered_data if entry['prediction_correct'])
            filtered_incorrect = filtered_total - filtered_correct
            filtered_accuracy = filtered_correct / filtered_total if filtered_total > 0 else 0
            
            threshold_metrics[str(threshold)] = {
                'accuracy': filtered_accuracy,
                'total_matches': filtered_total,
                'correct_predictions': filtered_correct,
                'incorrect_predictions': filtered_incorrect
            }
        
        # Calculate metrics by team matchup
        team_metrics = {}
        
        for entry in matched_data:
            home_team = entry.get('home_team')
            away_team = entry.get('away_team')
            
            if not home_team or not away_team:
                continue
            
            team_matchup = f"{home_team} vs {away_team}"
            
            if team_matchup not in team_metrics:
                team_metrics[team_matchup] = {
                    'total_matches': 0,
                    'correct_predictions': 0,
                    'incorrect_predictions': 0
                }
            
            team_metrics[team_matchup]['total_matches'] += 1
            
            if entry['prediction_correct']:
                team_metrics[team_matchup]['correct_predictions'] += 1
            else:
                team_metrics[team_matchup]['incorrect_predictions'] += 1
        
        # Calculate accuracy for each team matchup
        for matchup, metrics in team_metrics.items():
            metrics['accuracy'] = metrics['correct_predictions'] / metrics['total_matches'] if metrics['total_matches'] > 0 else 0
        
        # Return all metrics
        return {
            'accuracy': accuracy,
            'total_matches': total_matches,
            'correct_predictions': correct_predictions,
            'incorrect_predictions': incorrect_predictions,
            'confidence_threshold_metrics': threshold_metrics,
            'team_matchup_metrics': team_metrics
        }
    
    except Exception as e:
        logger.error(f"Error calculating evaluation metrics: {e}")
        raise EvaluationError(f"Failed to calculate evaluation metrics: {e}") from e


def evaluate_model(
    prediction_file: str,
    result_file: str,
    save_to_file: bool = True
) -> Dict[str, Any]:
    """
    Evaluate a prediction model using predictions and actual results.
    
    Args:
        prediction_file: Path to the prediction JSON file
        result_file: Path to the actual results JSON file
        save_to_file: Whether to save the evaluation to a file (default: True)
        
    Returns:
        Dictionary with evaluation results
        
    Raises:
        EvaluationError: If there is an error evaluating the model
    """
    try:
        logger.info(f"Evaluating model using predictions from {prediction_file} and results from {result_file}")
        
        # Load predictions and results
        predictions = load_predictions(prediction_file)
        results = load_actual_results(result_file)
        
        # Match predictions with results
        matched_data = match_predictions_with_results(predictions, results)
        
        # Calculate evaluation metrics
        metrics = calculate_evaluation_metrics(matched_data)
        
        # Create evaluation results
        evaluation = {
            'prediction_file': prediction_file,
            'result_file': result_file,
            'evaluation_time': datetime.now().isoformat(),
            'metrics': metrics,
            'matched_data_count': len(matched_data)
        }
        
        # Save to file if requested
        if save_to_file:
            # Ensure directory exists
            os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
            
            # Create filename
            filename = f"model_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Save file
            with open(os.path.join(PROCESSED_DATA_DIR, filename), 'w') as f:
                json.dump(evaluation, f, indent=2)
            
            logger.info(f"Saved model evaluation to {filename}")
        
        return evaluation
    
    except Exception as e:
        logger.error(f"Error evaluating model: {e}")
        raise EvaluationError(f"Failed to evaluate model: {e}") from e


def compare_models(
    evaluations: List[Dict[str, Any]],
    save_to_file: bool = True
) -> Dict[str, Any]:
    """
    Compare multiple model evaluations.
    
    Args:
        evaluations: List of evaluation dictionaries
        save_to_file: Whether to save the comparison to a file (default: True)
        
    Returns:
        Dictionary with model comparison results
        
    Raises:
        EvaluationError: If there is an error comparing models
    """
    try:
        logger.info(f"Comparing {len(evaluations)} model evaluations")
        
        # Create comparison data
        comparison = {
            'models': [],
            'comparison_time': datetime.now().isoformat()
        }
        
        for i, eval_data in enumerate(evaluations):
            model_name = f"Model {i+1}"
            
            if 'model_name' in eval_data:
                model_name = eval_data['model_name']
            
            metrics = eval_data.get('metrics', {})
            
            model_data = {
                'model_name': model_name,
                'accuracy': metrics.get('accuracy', 0),
                'total_matches': metrics.get('total_matches', 0),
                'correct_predictions': metrics.get('correct_predictions', 0),
                'incorrect_predictions': metrics.get('incorrect_predictions', 0),
                'evaluation_time': eval_data.get('evaluation_time')
            }
            
            comparison['models'].append(model_data)
        
        # Sort models by accuracy (descending)
        comparison['models'].sort(key=lambda x: x['accuracy'], reverse=True)
        
        # Determine best model
        if comparison['models']:
            comparison['best_model'] = comparison['models'][0]['model_name']
            comparison['best_accuracy'] = comparison['models'][0]['accuracy']
        else:
            comparison['best_model'] = None
            comparison['best_accuracy'] = 0
        
        # Save to file if requested
        if save_to_file:
            # Ensure directory exists
            os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
            
            # Create filename
            filename = f"model_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Save file
            with open(os.path.join(PROCESSED_DATA_DIR, filename), 'w') as f:
                json.dump(comparison, f, indent=2)
            
            logger.info(f"Saved model comparison to {filename}")
        
        return comparison
    
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        raise EvaluationError(f"Failed to compare models: {e}") from e


def track_model_performance_over_time(
    model_name: str,
    evaluations: List[Dict[str, Any]],
    save_to_file: bool = True
) -> Dict[str, Any]:
    """
    Track a model's performance over time.
    
    Args:
        model_name: Name of the model
        evaluations: List of evaluation dictionaries for the model
        save_to_file: Whether to save the tracking to a file (default: True)
        
    Returns:
        Dictionary with model performance tracking results
        
    Raises:
        EvaluationError: If there is an error tracking model performance
    """
    try:
        logger.info(f"Tracking performance of model '{model_name}' over {len(evaluations)} evaluations")
        
        # Sort evaluations by time
        sorted_evals = sorted(evaluations, key=lambda x: x.get('evaluation_time', ''))
        
        # Extract metrics over time
        tracking = {
            'model_name': model_name,
            'tracking_time': datetime.now().isoformat(),
            'evaluations': []
        }
        
        for eval_data in sorted_evals:
            metrics = eval_data.get('metrics', {})
            
            eval_entry = {
                'evaluation_time': eval_data.get('evaluation_time'),
                'accuracy': metrics.get('accuracy', 0),
                'total_matches': metrics.get('total_matches', 0),
                'correct_predictions': metrics.get('correct_predictions', 0),
                'incorrect_predictions': metrics.get('incorrect_predictions', 0)
            }
            
            tracking['evaluations'].append(eval_entry)
        
        # Calculate trend
        if len(tracking['evaluations']) >= 2:
            first_accuracy = tracking['evaluations'][0]['accuracy']
            last_accuracy = tracking['evaluations'][-1]['accuracy']
            accuracy_change = last_accuracy - first_accuracy
            
            tracking['accuracy_change'] = accuracy_change
            
            if accuracy_change > 0.05:
                tracking['trend'] = 'improving'
            elif accuracy_change < -0.05:
                tracking['trend'] = 'declining'
            else:
                tracking['trend'] = 'stable'
        else:
            tracking['accuracy_change'] = 0
            tracking['trend'] = 'unknown'
        
        # Save to file if requested
        if save_to_file:
            # Ensure directory exists
            os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
            
            # Create filename
            filename = f"model_tracking_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Save file
            with open(os.path.join(PROCESSED_DATA_DIR, filename), 'w') as f:
                json.dump(tracking, f, indent=2)
            
            logger.info(f"Saved model tracking to {filename}")
        
        return tracking
    
    except Exception as e:
        logger.error(f"Error tracking model performance: {e}")
        raise EvaluationError(f"Failed to track model performance: {e}") from e
