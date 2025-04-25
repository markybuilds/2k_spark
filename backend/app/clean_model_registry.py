"""
Script to clean the model registry by removing problematic models.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

from config.settings import MODELS_DIR, MODEL_REGISTRY_FILE
from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions
from core.models.registry import ModelRegistry

logger = get_model_tuning_logger()


@log_execution_time(logger)
@log_exceptions(logger)
def clean_model_registry(min_samples=100, remove_models=True):
    """
    Clean the model registry by removing problematic models.
    
    Args:
        min_samples (int): Minimum number of samples required for a model to be considered valid
        remove_models (bool): Whether to remove model files from disk
        
    Returns:
        tuple: (removed_models, remaining_models)
    """
    logger.info("Cleaning model registry")
    
    # Load registry
    registry = ModelRegistry()
    models = registry.list_models()
    
    logger.info(f"Found {len(models)} models in registry")
    
    # Identify problematic models
    problematic_models = []
    valid_models = []
    
    for model in models:
        model_id = model.get("model_id")
        num_samples = model.get("num_samples", 0)
        accuracy = model.get("accuracy", 0)
        
        # Check if model has suspiciously high accuracy or too few samples
        if num_samples < min_samples or accuracy == 1.0:
            logger.warning(f"Model {model_id} is problematic: samples={num_samples}, accuracy={accuracy}")
            problematic_models.append(model)
        else:
            valid_models.append(model)
    
    logger.info(f"Found {len(problematic_models)} problematic models and {len(valid_models)} valid models")
    
    # Remove problematic models from registry
    for model in problematic_models:
        model_id = model.get("model_id")
        logger.info(f"Removing model {model_id} from registry")
        
        # Remove from registry
        registry.remove_model(model_id)
        
        # Remove model files if requested
        if remove_models:
            model_path = model.get("model_path")
            info_path = model.get("info_path")
            
            if model_path and os.path.exists(model_path):
                logger.info(f"Removing model file: {model_path}")
                try:
                    os.remove(model_path)
                except Exception as e:
                    logger.error(f"Error removing model file: {str(e)}")
            
            if info_path and os.path.exists(info_path):
                logger.info(f"Removing model info file: {info_path}")
                try:
                    os.remove(info_path)
                except Exception as e:
                    logger.error(f"Error removing model info file: {str(e)}")
    
    # Print remaining models
    remaining_models = registry.list_models()
    logger.info(f"Registry now contains {len(remaining_models)} models")
    
    for model in remaining_models:
        model_id = model.get("model_id")
        num_samples = model.get("num_samples", 0)
        accuracy = model.get("accuracy", 0)
        logger.info(f"Model {model_id}: samples={num_samples}, accuracy={accuracy}")
    
    # Get best model
    best_model = registry.get_best_model_info()
    if best_model:
        logger.info(f"Best model is now {best_model.get('model_id')} with accuracy {best_model.get('accuracy', 0)}")
    else:
        logger.warning("No best model set in registry")
    
    return problematic_models, remaining_models


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Clean model registry")
    parser.add_argument("--min-samples", type=int, default=100, help="Minimum number of samples required for a model to be considered valid")
    parser.add_argument("--keep-files", action="store_true", help="Keep model files on disk")
    args = parser.parse_args()
    
    # Clean registry
    removed_models, remaining_models = clean_model_registry(
        min_samples=args.min_samples,
        remove_models=not args.keep_files
    )
    
    # Print results
    print(f"Removed {len(removed_models)} problematic models")
    print(f"Registry now contains {len(remaining_models)} models")
    
    # Print remaining models
    print("\nRemaining models:")
    for model in remaining_models:
        model_id = model.get("model_id")
        num_samples = model.get("num_samples", 0)
        accuracy = model.get("accuracy", 0)
        print(f"  - ID: {model_id}, Samples: {num_samples}, Accuracy: {accuracy:.4f}")
