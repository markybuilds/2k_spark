"""
Base model class for prediction models.
"""

import os
import json
import pickle
import time
from pathlib import Path
from abc import ABC, abstractmethod

from config.settings import MODELS_DIR, DEFAULT_RANDOM_STATE
from config.logging_config import get_model_tuning_logger
from utils.logging import log_execution_time, log_exceptions

logger = get_model_tuning_logger()


class BaseModel(ABC):
    """
    Base class for prediction models.
    """
    
    def __init__(self, model_id=None, random_state=DEFAULT_RANDOM_STATE):
        """
        Initialize the base model.
        
        Args:
            model_id (str): Model ID (default: timestamp-based ID)
            random_state (int): Random state for reproducibility
        """
        self.model_id = model_id or f"{int(time.time())}"
        self.random_state = random_state
        self.model = None
        self.model_info = {
            "model_id": self.model_id,
            "model_type": self.__class__.__name__,
            "training_time": None,
            "data_files": {},
            "parameters": {},
            "metrics": {}
        }
    
    @abstractmethod
    def train(self, *args, **kwargs):
        """
        Train the model.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            self: The trained model
        """
        pass
    
    @abstractmethod
    def predict(self, *args, **kwargs):
        """
        Make predictions with the model.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            Predictions
        """
        pass
    
    @abstractmethod
    def evaluate(self, *args, **kwargs):
        """
        Evaluate the model.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            dict: Evaluation metrics
        """
        pass
    
    @log_execution_time(logger)
    @log_exceptions(logger)
    def save(self, models_dir=MODELS_DIR):
        """
        Save the model and its metadata.
        
        Args:
            models_dir (str or Path): Directory to save the model
            
        Returns:
            tuple: (model_path, info_path)
        """
        models_dir = Path(models_dir)
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Set training time if not already set
        if not self.model_info["training_time"]:
            self.model_info["training_time"] = time.strftime("%Y%m%d_%H%M%S")
        
        # Generate file paths
        model_filename = f"{self.__class__.__name__.lower()}_{self.model_id}.pkl"
        info_filename = f"{self.__class__.__name__.lower()}_info_{self.model_id}.json"
        
        model_path = models_dir / model_filename
        info_path = models_dir / info_filename
        
        # Update model info with paths
        self.model_info["model_path"] = str(model_path)
        self.model_info["info_path"] = str(info_path)
        
        # Save model
        logger.info(f"Saving model to {model_path}")
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save model info
        logger.info(f"Saving model info to {info_path}")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_info, f, indent=2)
        
        logger.info(f"Successfully saved model {self.model_id}")
        return model_path, info_path
    
    @classmethod
    @log_exceptions(logger)
    def load(cls, model_path, info_path=None):
        """
        Load a model and its metadata.
        
        Args:
            model_path (str or Path): Path to the model file
            info_path (str or Path): Path to the model info file (optional)
            
        Returns:
            BaseModel: Loaded model
        """
        model_path = Path(model_path)
        
        # Infer info path if not provided
        if info_path is None:
            info_path = model_path.parent / model_path.name.replace('.pkl', '_info.json')
        else:
            info_path = Path(info_path)
        
        # Load model
        logger.info(f"Loading model from {model_path}")
        with open(model_path, 'rb') as f:
            model_obj = pickle.load(f)
        
        # Load model info if available
        model_info = {}
        if info_path.exists():
            logger.info(f"Loading model info from {info_path}")
            with open(info_path, 'r', encoding='utf-8') as f:
                model_info = json.load(f)
        
        # Create instance
        instance = cls()
        instance.model = model_obj
        instance.model_info = model_info
        instance.model_id = model_info.get("model_id", model_path.stem)
        
        logger.info(f"Successfully loaded model {instance.model_id}")
        return instance
    
    def get_info(self):
        """
        Get model information.
        
        Returns:
            dict: Model information
        """
        return self.model_info
    
    def update_info(self, key, value):
        """
        Update model information.
        
        Args:
            key (str): Information key
            value: Information value
        """
        self.model_info[key] = value
    
    def __str__(self):
        """
        String representation of the model.
        
        Returns:
            str: String representation
        """
        return f"{self.__class__.__name__}(model_id={self.model_id})"
