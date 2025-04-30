"""
Commodities Agent for the Economic Summary Swarm.

This module provides the CommoditiesAgent for analyzing commodities markets,
including metals, energy, and agricultural products.
"""

from economic_summary.agents.commodities.commodities_agent import CommoditiesAgent

__all__ = ['CommoditiesAgent']

def run_commodities_agent(task=None):
    """
    Run the Commodities Agent with a task.
    
    Args:
        task: The task to perform (optional)
        
    Returns:
        str: Commodities market analysis
    """
    agent = CommoditiesAgent()
    return agent.run(task)
