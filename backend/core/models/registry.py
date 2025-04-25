"""
Model registry for tracking and selecting models.
"""

import json
import os
from pathlib import Path

from config.settings import MODELS_DIR, MODEL_REGISTRY_FILE, SCORE_MODEL_REGISTRY_FILE
from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions

logger = get_model_tuning_logger()


class ModelRegistry:
    """
    Registry for tracking and selecting prediction models.
    """

    def __init__(self, models_dir=MODELS_DIR, registry_file=MODEL_REGISTRY_FILE):
        """
        Initialize the model registry.

        Args:
            models_dir (str or Path): Directory containing models
            registry_file (str or Path): Path to the registry file
        """
        self.models_dir = Path(models_dir)
        self.registry_file = Path(registry_file)
        self.registry = self._load_registry()

    @log_exceptions(logger)
    def _load_registry(self):
        """
        Load the model registry from file.

        Returns:
            dict: Model registry
        """
        if not self.registry_file.exists():
            logger.info(f"Registry file {self.registry_file} does not exist, creating new registry")
            return {"models": [], "best_model_id": None}

        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)

            logger.info(f"Loaded registry with {len(registry.get('models', []))} models")
            return registry

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error loading registry from {self.registry_file}: {str(e)}")
            return {"models": [], "best_model_id": None}

    @log_execution_time(logger)
    @log_exceptions(logger)
    def save_registry(self):
        """
        Save the model registry to file.

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Saving registry with {len(self.registry.get('models', []))} models to {self.registry_file}")

        try:
            # Create directory if it doesn't exist
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)

            # Save registry
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2)

            logger.info(f"Successfully saved registry to {self.registry_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving registry to {self.registry_file}: {str(e)}")
            return False

    @log_exceptions(logger)
    def register_model(self, model_info):
        """
        Register a model in the registry.

        Args:
            model_info (dict): Model information

        Returns:
            bool: True if successful, False otherwise
        """
        model_id = model_info.get("model_id")
        if not model_id:
            logger.error("Cannot register model without model_id")
            return False

        # Check if model already exists
        for i, existing_model in enumerate(self.registry["models"]):
            if existing_model.get("model_id") == model_id:
                # Update existing model
                logger.info(f"Updating existing model {model_id} in registry")
                self.registry["models"][i] = model_info
                return self.save_registry()

        # Add new model
        logger.info(f"Adding new model {model_id} to registry")
        self.registry["models"].append(model_info)

        # Update best model if needed
        self._update_best_model()

        return self.save_registry()

    @log_exceptions(logger)
    def _update_best_model(self):
        """
        Update the best model in the registry based on accuracy.
        """
        if not self.registry["models"]:
            logger.info("No models in registry, cannot update best model")
            self.registry["best_model_id"] = None
            return

        # Find model with highest accuracy
        best_model = max(self.registry["models"], key=lambda m: m.get("accuracy", 0))
        best_model_id = best_model.get("model_id")

        logger.info(f"Updated best model to {best_model_id} with accuracy {best_model.get('accuracy', 0)}")
        self.registry["best_model_id"] = best_model_id

    @log_exceptions(logger)
    def get_model_info(self, model_id):
        """
        Get information about a specific model.

        Args:
            model_id (str): Model ID

        Returns:
            dict: Model information or None if not found
        """
        for model in self.registry["models"]:
            if model.get("model_id") == model_id:
                return model

        logger.warning(f"Model {model_id} not found in registry")
        return None

    @log_exceptions(logger)
    def get_best_model_info(self):
        """
        Get information about the best model.

        Returns:
            dict: Best model information or None if no models
        """
        best_model_id = self.registry.get("best_model_id")
        if not best_model_id:
            logger.warning("No best model set in registry")
            return None

        return self.get_model_info(best_model_id)

    @log_exceptions(logger)
    def list_models(self):
        """
        List all models in the registry.

        Returns:
            list: List of model information dictionaries
        """
        return self.registry.get("models", [])

    @log_exceptions(logger)
    def remove_model(self, model_id):
        """
        Remove a model from the registry.

        Args:
            model_id (str): Model ID

        Returns:
            bool: True if successful, False otherwise
        """
        initial_count = len(self.registry.get("models", []))
        self.registry["models"] = [m for m in self.registry.get("models", []) if m.get("model_id") != model_id]

        if len(self.registry.get("models", [])) < initial_count:
            logger.info(f"Removed model {model_id} from registry")

            # Update best model if needed
            if self.registry.get("best_model_id") == model_id:
                self._update_best_model()

            return self.save_registry()
        else:
            logger.warning(f"Model {model_id} not found in registry")
            return False

    @log_exceptions(logger)
    def add_model(self, model_id, model_path, info_path, accuracy):
        """
        Add a model to the registry.

        Args:
            model_id (str): Model ID
            model_path (str or Path): Path to the model file
            info_path (str or Path): Path to the model info file
            accuracy (float): Model accuracy

        Returns:
            bool: True if successful, False otherwise
        """
        model_info = {
            "model_id": model_id,
            "model_path": str(model_path),
            "info_path": str(info_path),
            "accuracy": accuracy,
            "model_type": "WinnerPredictionModel"
        }

        return self.register_model(model_info)


class ScoreModelRegistry(ModelRegistry):
    """
    Registry for tracking and selecting score prediction models.
    """

    def __init__(self, models_dir=MODELS_DIR, registry_file=SCORE_MODEL_REGISTRY_FILE):
        """
        Initialize the score model registry.

        Args:
            models_dir (str or Path): Directory containing models
            registry_file (str or Path): Path to the registry file
        """
        super().__init__(models_dir, registry_file)

    @log_exceptions(logger)
    def _update_best_model(self):
        """
        Update the best model in the registry based on mean absolute error (lower is better).
        """
        if not self.registry["models"]:
            logger.info("No models in registry, cannot update best model")
            self.registry["best_model_id"] = None
            return

        # Find model with lowest MAE
        best_model = min(self.registry["models"], key=lambda m: m.get("total_score_mae", float('inf')))
        best_model_id = best_model.get("model_id")

        logger.info(f"Updated best model to {best_model_id} with MAE {best_model.get('total_score_mae', float('inf'))}")
        self.registry["best_model_id"] = best_model_id

    @log_exceptions(logger)
    def add_model(self, model_id, model_path, info_path, total_score_mae):
        """
        Add a model to the registry.

        Args:
            model_id (str): Model ID
            model_path (str or Path): Path to the model file
            info_path (str or Path): Path to the model info file
            total_score_mae (float): Total score mean absolute error

        Returns:
            bool: True if successful, False otherwise
        """
        model_info = {
            "model_id": model_id,
            "model_path": str(model_path),
            "info_path": str(info_path),
            "total_score_mae": total_score_mae,
            "model_type": "ScorePredictionModel"
        }

        return self.register_model(model_info)
