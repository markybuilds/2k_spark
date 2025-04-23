"""
Script to run the full data pipeline and collect a comprehensive dataset.

This script collects historical match data, processes it, and generates features
for the prediction model.
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.data_pipeline import run_full_pipeline
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the full data pipeline.')
    
    # Add arguments
    parser.add_argument('--start-date', type=str, 
                        help='Start date in format YYYY-MM-DD (default: 90 days ago)')
    parser.add_argument('--end-date', type=str, 
                        help='End date in format YYYY-MM-DD (default: today)')
    parser.add_argument('--tournament-id', type=int, default=1,
                        help='Tournament ID (default: 1)')
    parser.add_argument('--output-dir', type=str, 
                        help=f'Output directory (default: {PROCESSED_DATA_DIR})')
    
    return parser.parse_args()


def main():
    """Main function to run the data pipeline."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Set default dates if not provided
        if not args.start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        else:
            start_date = args.start_date
        
        if not args.end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = args.end_date
        
        # Set tournament ID
        tournament_id = args.tournament_id
        
        # Set output directory
        if args.output_dir:
            output_dir = args.output_dir
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = PROCESSED_DATA_DIR
            os.makedirs(output_dir, exist_ok=True)
        
        # Log parameters
        logger.info(f"Running data pipeline with the following parameters:")
        logger.info(f"Start Date: {start_date}")
        logger.info(f"End Date: {end_date}")
        logger.info(f"Tournament ID: {tournament_id}")
        logger.info(f"Output Directory: {output_dir}")
        
        # Run the full pipeline
        logger.info("Starting data pipeline...")
        pipeline_results = run_full_pipeline(start_date, end_date, tournament_id)
        
        # Save pipeline metadata
        metadata_file = os.path.join(output_dir, f"pipeline_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(metadata_file, 'w') as f:
            json.dump(pipeline_results['metadata'], f, indent=2)
        
        logger.info(f"Saved pipeline metadata to {metadata_file}")
        
        # Log pipeline results
        logger.info("Data pipeline completed successfully.")
        logger.info(f"Processed {pipeline_results['metadata']['match_count']} matches")
        logger.info(f"Generated {pipeline_results['metadata']['player_team_feature_count']} player-team features")
        logger.info(f"Generated {pipeline_results['metadata']['head_to_head_feature_count']} head-to-head features")
        
    except Exception as e:
        logger.error(f"Error running data pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
