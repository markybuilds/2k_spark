"""
Script to schedule regular data updates and predictions.

This script sets up scheduled tasks to regularly update the dataset
and generate predictions for upcoming matches.
"""
import os
import sys
import logging
import argparse
import schedule
import time
import subprocess
from datetime import datetime, timedelta

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Schedule regular data updates and predictions.')
    
    # Add arguments
    parser.add_argument('--update-interval', type=int, default=12,
                        help='Interval in hours for data updates (default: 12)')
    parser.add_argument('--prediction-interval', type=int, default=6,
                        help='Interval in hours for predictions (default: 6)')
    parser.add_argument('--tournament-id', type=int, default=1,
                        help='Tournament ID (default: 1)')
    parser.add_argument('--output-dir', type=str, default=PROCESSED_DATA_DIR,
                        help=f'Output directory (default: {PROCESSED_DATA_DIR})')
    
    return parser.parse_args()


def run_update_data():
    """Run the update_data.py script."""
    try:
        logger.info("Running data update...")
        
        # Get the path to the update_data.py script
        script_path = os.path.join(os.path.dirname(__file__), 'update_data.py')
        
        # Run the script
        cmd = [sys.executable, script_path, 
               '--days', '7',
               '--tournament-id', str(args.tournament_id),
               '--output-dir', args.output_dir]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("Data update completed successfully.")
            logger.debug(stdout.decode())
        else:
            logger.error(f"Data update failed with return code {process.returncode}")
            logger.error(stderr.decode())
        
    except Exception as e:
        logger.error(f"Error running data update: {e}")


def run_generate_predictions():
    """Run the generate_predictions.py script."""
    try:
        logger.info("Generating predictions...")
        
        # Get the path to the generate_predictions.py script
        script_path = os.path.join(os.path.dirname(__file__), 'generate_predictions.py')
        
        # Run the script
        cmd = [sys.executable, script_path, 
               '--hours', '24',
               '--tournament-id', str(args.tournament_id),
               '--min-confidence', '0.6',
               '--output-dir', args.output_dir,
               '--format', 'json']
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("Prediction generation completed successfully.")
            logger.debug(stdout.decode())
        else:
            logger.error(f"Prediction generation failed with return code {process.returncode}")
            logger.error(stderr.decode())
        
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")


def main():
    """Main function to schedule regular data updates and predictions."""
    try:
        # Parse arguments
        global args
        args = parse_arguments()
        
        # Log parameters
        logger.info(f"Scheduling tasks with the following parameters:")
        logger.info(f"Update Interval: {args.update_interval} hours")
        logger.info(f"Prediction Interval: {args.prediction_interval} hours")
        logger.info(f"Tournament ID: {args.tournament_id}")
        logger.info(f"Output Directory: {args.output_dir}")
        
        # Run initial update and prediction
        logger.info("Running initial data update and prediction...")
        run_update_data()
        run_generate_predictions()
        
        # Schedule regular updates
        schedule.every(args.update_interval).hours.do(run_update_data)
        logger.info(f"Scheduled data updates every {args.update_interval} hours")
        
        # Schedule regular predictions
        schedule.every(args.prediction_interval).hours.do(run_generate_predictions)
        logger.info(f"Scheduled predictions every {args.prediction_interval} hours")
        
        # Run the scheduler
        logger.info("Scheduler started. Press Ctrl+C to exit.")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")
    
    except Exception as e:
        logger.error(f"Error in scheduler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
