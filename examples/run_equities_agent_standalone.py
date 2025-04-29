"""
Example script to run the EquitiesAgent standalone.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
# This allows importing from the economic_summary package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file (especially API keys)
# Ensure you have a .env file in the project root with:
# OPENAI_API_KEY=your_openai_key
# SEC_API_KEY=your_sec_api_key (Optional, needed for SEC filings)
# NEWS_API_KEY=your_news_api_key (Optional, needed for news)
if load_dotenv():
    logger.info("Loaded environment variables from .env file.")
else:
    logger.warning("Could not find .env file. Ensure API keys are set via environment variables.")

# Import the agent
try:
    from economic_summary.agents.equities import EquitiesAgent
except ImportError as e:
    logger.error(f"Failed to import EquitiesAgent. Ensure the project root is in PYTHONPATH: {e}")
    sys.exit(1)

def run_standalone_equities(task=None):
    """Initialize and run the EquitiesAgent."""
    try:
        logger.info("Initializing EquitiesAgent...")
        equities_agent = EquitiesAgent()
        logger.info("EquitiesAgent initialized.")

        # Run the agent with an optional specific task
        logger.info(f"Running EquitiesAgent with task: {task if task else 'Default general analysis'}")
        analysis = equities_agent.run(task=task)

        print("\n" + "="*20 + " Equities Agent Analysis " + "="*20)
        print(analysis)
        print("="*61 + "\n")
        
        logger.info("EquitiesAgent run complete.")

    except Exception as e:
        logger.error(f"An error occurred while running the EquitiesAgent: {str(e)}", exc_info=True)
        print(f"\nError running Equities Agent: {str(e)}\n")

if __name__ == "__main__":
    # Example: Run with a specific task
    # specific_task = "Focus on the technology sector (XLK) performance and recent NVDA earnings."
    # run_standalone_equities(task=specific_task)

    # Example: Run with the default general analysis task
    run_standalone_equities() 