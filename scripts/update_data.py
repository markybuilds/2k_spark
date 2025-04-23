"""
Script to regularly update the dataset with new matches.

This script fetches new match data, processes it, and updates the dataset
for the prediction model.
"""
import os
import sys
import json
import logging
import argparse
import pandas as pd
from datetime import datetime, timedelta

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.data_pipeline import (
    collect_historical_data,
    process_match_data,
    create_player_team_features,
    create_head_to_head_features
)
from src.data.standings import fetch_standings
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Update the dataset with new matches.')
    
    # Add arguments
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to fetch data for (default: 7)')
    parser.add_argument('--tournament-id', type=int, default=1,
                        help='Tournament ID (default: 1)')
    parser.add_argument('--output-dir', type=str, default=PROCESSED_DATA_DIR,
                        help=f'Output directory (default: {PROCESSED_DATA_DIR})')
    
    return parser.parse_args()


def get_last_update_date():
    """Get the date of the last data update."""
    try:
        # Check if update log file exists
        log_file = os.path.join(PROCESSED_DATA_DIR, 'update_log.json')
        
        if os.path.exists(log_file):
            # Load update log
            with open(log_file, 'r') as f:
                update_log = json.load(f)
            
            # Get last update date
            last_update = update_log.get('last_update')
            
            if last_update:
                return datetime.fromisoformat(last_update)
        
        # Default to 7 days ago if no log exists
        return datetime.now() - timedelta(days=7)
    
    except Exception as e:
        logger.error(f"Error getting last update date: {e}")
        # Default to 7 days ago
        return datetime.now() - timedelta(days=7)


def update_log(update_info):
    """Update the data update log."""
    try:
        # Ensure output directory exists
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        
        # Create log file path
        log_file = os.path.join(PROCESSED_DATA_DIR, 'update_log.json')
        
        # Load existing log if it exists
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                update_log = json.load(f)
        else:
            update_log = {'updates': []}
        
        # Add current update to log
        update_log['last_update'] = datetime.now().isoformat()
        update_log['updates'].append(update_info)
        
        # Save updated log
        with open(log_file, 'w') as f:
            json.dump(update_log, f, indent=2)
        
        logger.info(f"Updated log file: {log_file}")
        
    except Exception as e:
        logger.error(f"Error updating log: {e}")


def merge_new_data(existing_data_file, new_data, key_column):
    """Merge new data with existing data."""
    try:
        # Load existing data if file exists
        if os.path.exists(existing_data_file):
            existing_data = pd.read_csv(existing_data_file)
            
            # Merge data
            merged_data = pd.concat([existing_data, new_data])
            
            # Remove duplicates based on key column
            merged_data = merged_data.drop_duplicates(subset=[key_column], keep='last')
            
            return merged_data
        else:
            # Return new data if no existing data
            return new_data
    
    except Exception as e:
        logger.error(f"Error merging data: {e}")
        raise


def main():
    """Main function to update the dataset."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Get last update date
        last_update = get_last_update_date()
        
        # Calculate date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (last_update - timedelta(days=1)).strftime('%Y-%m-%d')  # Overlap by 1 day to ensure no matches are missed
        
        logger.info(f"Updating data from {start_date} to {end_date}")
        
        # Collect new data
        new_data = collect_historical_data(start_date, end_date, args.tournament_id, save_to_file=True)
        
        # Process new match data
        new_processed_matches = process_match_data(new_data['matches'], save_to_file=False)
        
        # Merge with existing processed match data
        processed_matches_file = os.path.join(args.output_dir, 'processed_matches.csv')
        merged_matches = merge_new_data(processed_matches_file, new_processed_matches, 'match_id')
        
        # Save merged match data
        merged_matches.to_csv(processed_matches_file, index=False)
        logger.info(f"Saved merged match data to {processed_matches_file}")
        
        # Get player IDs from standings
        player_ids = [player.get('participantId') for player in new_data['standings'] if player.get('participantId')]
        
        # Update player-team features
        logger.info("Updating player-team features...")
        
        # Load existing player-team features if available
        player_team_file = os.path.join(args.output_dir, 'player_team_features.csv')
        
        if os.path.exists(player_team_file):
            # Load existing features
            existing_features = pd.read_csv(player_team_file)
            
            # Get existing player IDs
            existing_player_ids = existing_features['player_id'].unique().tolist()
            
            # Add new player IDs
            player_ids = list(set(player_ids + existing_player_ids))
        
        # Collect player-team data for all players
        from src.data.data_pipeline import collect_player_team_data
        player_data = collect_player_team_data(player_ids, args.tournament_id)
        
        # Create player-team features
        player_team_features = create_player_team_features(player_data, save_to_file=False)
        
        # Save player-team features
        player_team_features.to_csv(player_team_file, index=False)
        logger.info(f"Saved player-team features to {player_team_file}")
        
        # Update head-to-head features
        logger.info("Updating head-to-head features...")
        
        # Create head-to-head features from all processed matches
        h2h_features = create_head_to_head_features(merged_matches.to_dict('records'), save_to_file=False)
        
        # Save head-to-head features
        h2h_file = os.path.join(args.output_dir, 'head_to_head_features.csv')
        h2h_features.to_csv(h2h_file, index=False)
        logger.info(f"Saved head-to-head features to {h2h_file}")
        
        # Create update info
        update_info = {
            'update_time': datetime.now().isoformat(),
            'start_date': start_date,
            'end_date': end_date,
            'tournament_id': args.tournament_id,
            'new_matches': len(new_data['matches']),
            'total_matches': len(merged_matches),
            'player_count': len(player_ids),
            'player_team_feature_count': len(player_team_features),
            'head_to_head_feature_count': len(h2h_features)
        }
        
        # Update log
        update_log(update_info)
        
        logger.info("Data update completed successfully.")
        
    except Exception as e:
        logger.error(f"Error updating data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
