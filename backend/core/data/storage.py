"""
Data storage utilities for the 2K Flash application.
"""

import json
import os
from pathlib import Path

from config.logging_config import get_data_fetcher_logger
from utils.logging import log_exceptions

logger = get_data_fetcher_logger()


class DataStorage:
    """
    Handles data storage and retrieval for the application.
    """
    
    @staticmethod
    @log_exceptions(logger)
    def save_json(data, file_path):
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            file_path (str or Path): File path
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = Path(file_path)
        logger.info(f"Saving data to {file_path}")
        
        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Successfully saved data to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {str(e)}")
            return False
    
    @staticmethod
    @log_exceptions(logger)
    def load_json(file_path, default=None):
        """
        Load data from a JSON file.
        
        Args:
            file_path (str or Path): File path
            default: Default value to return if file doesn't exist or is invalid
            
        Returns:
            Data from the file or default value
        """
        file_path = Path(file_path)
        logger.info(f"Loading data from {file_path}")
        
        if not file_path.exists():
            logger.warning(f"File {file_path} does not exist")
            return default if default is not None else {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Successfully loaded data from {file_path}")
            return data
            
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            return default if default is not None else {}
    
    @staticmethod
    @log_exceptions(logger)
    def append_json(data, file_path, key=None):
        """
        Append data to a JSON file.
        
        If the file contains a list, the data is appended to the list.
        If the file contains a dict and a key is provided, the data is added to the dict with the key.
        
        Args:
            data: Data to append
            file_path (str or Path): File path
            key: Key to use if the file contains a dict
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = Path(file_path)
        logger.info(f"Appending data to {file_path}")
        
        try:
            # Load existing data
            existing_data = DataStorage.load_json(file_path, default=[] if key is None else {})
            
            # Append data
            if isinstance(existing_data, list):
                existing_data.append(data)
            elif isinstance(existing_data, dict) and key is not None:
                existing_data[key] = data
            else:
                logger.error(f"Cannot append to {file_path}: incompatible data types")
                return False
            
            # Save updated data
            return DataStorage.save_json(existing_data, file_path)
            
        except Exception as e:
            logger.error(f"Error appending data to {file_path}: {str(e)}")
            return False
    
    @staticmethod
    @log_exceptions(logger)
    def file_exists(file_path):
        """
        Check if a file exists.
        
        Args:
            file_path (str or Path): File path
            
        Returns:
            bool: True if the file exists, False otherwise
        """
        file_path = Path(file_path)
        return file_path.exists()
    
    @staticmethod
    @log_exceptions(logger)
    def get_file_size(file_path):
        """
        Get the size of a file in bytes.
        
        Args:
            file_path (str or Path): File path
            
        Returns:
            int: File size in bytes, or -1 if the file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return -1
        
        return file_path.stat().st_size
    
    @staticmethod
    @log_exceptions(logger)
    def get_file_modification_time(file_path):
        """
        Get the last modification time of a file.
        
        Args:
            file_path (str or Path): File path
            
        Returns:
            float: Last modification time as a timestamp, or -1 if the file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return -1
        
        return file_path.stat().st_mtime
