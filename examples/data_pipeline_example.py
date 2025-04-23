"""
Example script demonstrating how to use the data pipeline module.
"""
import os
import sys
import json
import logging
import pandas as pd
from datetime import datetime, timedelta

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.standings import fetch_standings, get_player_by_name
from src.data.data_pipeline import (
    collect_historical_data,
    collect_player_team_data,
    process_match_data,
    create_player_team_features,
    create_head_to_head_features,
    run_full_pipeline
)
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def display_dataframe_info(df, name):
    """Display information about a DataFrame."""
    print(f"\n{name} DataFrame:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {', '.join(df.columns)}")
    print("\nSample data:")
    print(df.head(5))
    
    # Display basic statistics for numeric columns
    print("\nBasic statistics:")
    print(df.describe())


def main():
    """Main function to demonstrate the data pipeline module."""
    try:
        # Set date range for historical data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Collect historical data
        logger.info(f"Collecting historical data from {start_date} to {end_date}...")
        historical_data = collect_historical_data(start_date, end_date)
        
        # Process match data
        logger.info("Processing match data...")
        processed_matches = process_match_data(historical_data['matches'])
        
        # Display processed match data
        display_dataframe_info(processed_matches, "Processed Matches")
        
        # Collect player team data for top players
        logger.info("Collecting player team data for top players...")
        
        # Get top 10 players from standings
        standings = historical_data['standings']
        top_players = sorted(standings, key=lambda x: x.get('position', 999))[:10]
        top_player_ids = [player.get('participantId') for player in top_players if player.get('participantId')]
        
        player_data = collect_player_team_data(top_player_ids)
        
        # Create player-team features
        logger.info("Creating player-team features...")
        player_team_features = create_player_team_features(player_data)
        
        # Display player-team features
        display_dataframe_info(player_team_features, "Player-Team Features")
        
        # Create head-to-head features
        logger.info("Creating head-to-head features...")
        h2h_features = create_head_to_head_features(historical_data['matches'])
        
        # Display head-to-head features
        display_dataframe_info(h2h_features, "Head-to-Head Features")
        
        # Run a small pipeline for demonstration
        logger.info("Running a small pipeline for demonstration...")
        
        # Use a shorter date range for the demo
        demo_start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        demo_end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Run the pipeline
        pipeline_results = run_full_pipeline(demo_start_date, demo_end_date)
        
        # Display pipeline metadata
        print("\nPipeline Metadata:")
        for key, value in pipeline_results['metadata'].items():
            print(f"{key}: {value}")
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
