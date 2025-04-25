"""
Logging utility functions for the 2K Flash application.
"""

import logging
import traceback
import functools
import time


def log_execution_time(logger):
    """
    Decorator to log the execution time of a function.
    
    Args:
        logger (logging.Logger): Logger to use
        
    Returns:
        function: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        return wrapper
    return decorator


def log_exceptions(logger, reraise=True):
    """
    Decorator to log exceptions raised by a function.
    
    Args:
        logger (logging.Logger): Logger to use
        reraise (bool): Whether to reraise the exception after logging
        
    Returns:
        function: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {str(e)}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
                if reraise:
                    raise
        return wrapper
    return decorator


def log_function_call(logger, level=logging.DEBUG):
    """
    Decorator to log function calls with arguments.
    
    Args:
        logger (logging.Logger): Logger to use
        level (int): Logging level
        
    Returns:
        function: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.log(level, f"Calling {func.__name__}({signature})")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_logger(name, level=logging.INFO):
    """
    Get a logger with the specified name and level.
    
    Args:
        name (str): Logger name
        level (int): Logging level
        
    Returns:
        logging.Logger: Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
