"""
Example script to run the Economic Summary Swarm with all available agents.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

from economic_summary.agents.macro import MacroAgent
from economic_summary.agents.equities import EquitiesAgent
from economic_summary.agents.aggregator import AggregatorAgent, EconomicSummarySwarm

def main():
    """Run the Economic Summary Swarm with available agents."""
    try:
        print("Initializing Economic Summary Swarm...")
        
        # Initialize domain agents
        print("Initializing Macro Agent...")
        macro_agent = MacroAgent()
        
        print("Initializing Equities Agent...")
        equities_agent = EquitiesAgent()
        
        # Create a dictionary of domain agents
        domain_agents = {
            'macro': macro_agent,
            'equities': equities_agent
            # Add other domain agents as they are implemented
            # 'fixed_income': fixed_income_agent,
            # 'commodities': commodities_agent,
            # 'political': political_agent
        }
        
        # Create the Economic Summary Swarm
        print("Creating Economic Summary Swarm...")
        swarm = EconomicSummarySwarm(domain_agents)
        
        # Run the swarm
        print("\nRunning Economic Summary Swarm...")
        result = swarm.run()
        
        print("\n" + "="*80)
        print("Economic Summary".center(80))
        print("="*80)
        print(result)
        
    except Exception as e:
        logger.error(f"Error running Economic Summary Swarm: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
