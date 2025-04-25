
import sys
import os
import subprocess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import refresh function
from services.refresh_service import refresh_predictions

# Run refresh
success = refresh_predictions()

# Exit with appropriate code
sys.exit(0 if success else 1)
            