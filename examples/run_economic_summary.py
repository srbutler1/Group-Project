"""
Example script to run the Economic Summary Swarm with Macro and Aggregator agents.
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

from economic_summary.agents import MacroAgent, AggregatorAgent, EconomicSummarySwarm

def main():
    """Run the Economic Summary Swarm with available agents."""
    try:
        print("Initializing Economic Summary Swarm...")
        
        # Initialize domain agents
        print("Initializing Macro Agent...")
        macro_agent = MacroAgent()
        
        # Create a dictionary of domain agents
        domain_agents = {
            'macro': macro_agent
            # Add other domain agents as they are implemented
            # 'equities': equities_agent,
            # 'fixed_income': fixed_income_agent,
            # 'commodities': commodities_agent,
            # 'political': political_agent
        }
        
        # Create the Economic Summary Swarm
        swarm = EconomicSummarySwarm(domain_agents)
        
        # Run the swarm sequentially (since we only have one domain agent for now)
        print("\nRunning Economic Summary Swarm (Sequential)...")
        task = "Generate a comprehensive economic summary focusing on current macroeconomic trends and outlook."
        summary = swarm.run_sequential(task)
        
        print("\n=== Economic Summary ===")
        print(summary)
        
    except Exception as e:
        logger.error(f"Error running economic summary: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
