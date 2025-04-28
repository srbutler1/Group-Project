"""
Example script to run the Macro Agent for economic analysis.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

from economic_summary.agents.macro import MacroAgent

def main():
    """Run the Macro Agent to analyze macroeconomic data."""
    try:
        print("Testing Macro Agent's ability to retrieve recent economic reports...")
        
        # Create a MacroAgent instance
        macro_agent = MacroAgent()
        
        # Get and print recent economic reports
        print("\nRecent Economic Reports:")
        sources = ['fed', 'bea', 'bls']  # Federal Reserve, Bureau of Economic Analysis, Bureau of Labor Statistics
        reports = macro_agent.get_recent_economic_reports(sources, limit_per_source=3)
        
        for source, releases in reports.items():
            print(f"\n  {source.upper()} Reports:")
            for release in releases:
                print(f"    - {release.get('name')}")
                if release.get('press_release'):
                    print(f"      Date: {release.get('press_release')}")
                if release.get('link'):
                    print(f"      Link: {release.get('link')}")
        
    except Exception as e:
        logger.error(f"Error retrieving economic reports: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
