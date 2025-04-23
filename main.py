"""
Main entry point for the NBA 2K prediction model application.
"""
import logging
import argparse

from src.auth import get_bearer_token, AuthenticationError
from src.data.players import fetch_players, PlayerDataError
from src.config import config

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="NBA 2K Prediction Model")
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh of authentication token"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    return parser.parse_args()


def main() -> None:
    """Main function to run the application."""
    args = parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    logger.info("Starting NBA 2K prediction model application")
    logger.info(f"Environment: {config['env']}")

    try:
        # Test authentication
        logger.info("Testing authentication...")
        get_bearer_token(force_refresh=args.force_refresh)  # Get token but don't store it
        logger.info("Authentication successful")

        # Fetch player data
        logger.info("Fetching player data...")
        players = fetch_players()
        logger.info(f"Retrieved {len(players)} players")

        # TODO: Implement prediction model
        logger.info("Prediction model not yet implemented")

    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        return
    except PlayerDataError as e:
        logger.error(f"Player data error: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return

    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()
