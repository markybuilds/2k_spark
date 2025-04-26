
import sys
import os
import traceback
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import refresh function and logging
from services.refresh_service import refresh_predictions
from config.logging_config import get_prediction_refresh_logger

# Initialize logger
logger = get_prediction_refresh_logger()

try:
    # Log start time
    start_time = time.time()
    logger.info(f"Refresh script started with PID: {os.getpid()}")

    # Run refresh
    success = refresh_predictions()

    # Log completion
    end_time = time.time()
    duration = end_time - start_time

    if success:
        logger.info(f"Refresh completed successfully in {duration:.2f} seconds")
    else:
        logger.error(f"Refresh failed after {duration:.2f} seconds")

    # Exit with appropriate code
    sys.exit(0 if success else 1)
except Exception as e:
    # Log any unhandled exceptions
    logger.error(f"Unhandled exception in refresh script: {str(e)}")
    logger.error(traceback.format_exc())
    sys.exit(1)
            