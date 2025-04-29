"""
Example script to run the Economic Summary Swarm with MoA architecture.
"""
import os
import sys
import logging
import time
from dotenv import load_dotenv
import json

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

from economic_summary.agents.macro import MacroAgent
from economic_summary.agents.equities import EquitiesAgent
from economic_summary.agents.aggregator import EconomicSummarySwarm

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def main():
    """Run the Economic Summary Swarm with MoA architecture."""
    try:
        print_section("ECONOMIC SUMMARY SWARM DEMONSTRATION")
        print("This example demonstrates the Swarms Mixture of Agents (MoA) architecture")
        print("for generating comprehensive economic analyses.")
        
        # Step 1: Initialize domain agents
        print_section("STEP 1: INITIALIZING DOMAIN AGENTS")
        print("Creating MacroAgent for macroeconomic analysis...")
        macro_agent = MacroAgent()
        
        print("Creating EquitiesAgent for stock market analysis...")
        equities_agent = EquitiesAgent()
        
        # Get some sample data from the MacroAgent to show it's working
        print("\nRetrieving sample economic indicators from MacroAgent:")
        indicators = macro_agent.get_economic_indicators(['GDP', 'UNRATE', 'CPIAUCSL'])
        for name, value in indicators.items():
            print(f"  • {name}: {value}")
        
        # Get recession risk to show another MacroAgent capability
        print("\nRetrieving recession risk assessment from MacroAgent:")
        risk = macro_agent.get_recession_risk()
        print(f"  • Risk Level: {risk.get('risk_level', 'Unknown')}")
        
        # Run the MacroAgent to get macroeconomic insights
        print("\nGenerating macroeconomic insights...")
        macro_task = "Analyze current inflation trends and their impact on monetary policy"
        macro_insights = macro_agent.run(macro_task)
        
        print("\nMacroeconomic Insights Summary:")
        print("-" * 40)
        # Print the first 3 lines and last 3 lines of the insights to keep output manageable
        macro_lines = macro_insights.split('\n')
        if len(macro_lines) > 6:
            for line in macro_lines[:3]:
                print(line)
            print("...")
            for line in macro_lines[-3:]:
                print(line)
        else:
            print(macro_insights)
        
        # Create domain agents dictionary
        domain_agents = {
            'macro': macro_agent,
            'equities': equities_agent
            # In a full implementation, we would add other domain agents:
            # 'fixed_income': FixedIncomeAgent(),
            # 'commodities': CommoditiesAgent(),
            # 'political': PoliticalAgent()
        }
        
        # Step 2: Initialize the Economic Summary Swarm
        print_section("STEP 2: INITIALIZING ECONOMIC SUMMARY SWARM")
        print("Creating EconomicSummarySwarm with MoA architecture...")
        swarm = EconomicSummarySwarm(domain_agents)
        
        # Step 3: Run the swarm with MoA architecture
        print_section("STEP 3: RUNNING ECONOMIC SUMMARY SWARM")
        print("Executing the full MoA workflow:")
        print("  1. Layer 1: Parallel Agent Execution - Domain agents collect data")
        print("  2. Layer 2: Sequential Processing - Identify interdependencies")
        print("  3. Layer 3: Parallel Agent Execution - Refined analysis with context")
        print("  4. Final Layer: Aggregator Agent - Combines all insights")
        print("\nStarting MoA execution...\n")
        
        # Define the task
        task = "Generate a comprehensive economic summary focusing on inflation trends and monetary policy"
        print(f"Task: {task}\n")
        
        # Run the swarm with MoA architecture
        result = swarm.run_with_moa(task)
        
        # Step 4: Display results
        print_section("STEP 4: ECONOMIC SUMMARY RESULTS")
        
        # Extract the actual AI-generated content from the result
        # This is needed because the Swarms framework may return the full response including system prompts
        if isinstance(result, str):
            # Try to find the actual content after the prompt
            if "AggregatorAgent:" in result:
                result = result.split("AggregatorAgent:", 1)[1].strip()
            elif "H::" in result and "\n\n" in result.split("H::", 1)[1]:
                result = result.split("H::", 1)[1].split("\n\n", 1)[1].strip()
        
        print(result)
        
        print_section("DEMONSTRATION COMPLETE")
        print("The Economic Summary Swarm has successfully demonstrated the Swarms")
        print("Mixture of Agents (MoA) architecture for economic analysis.")
        
    except Exception as e:
        logger.error(f"Error running Economic Summary Swarm: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
