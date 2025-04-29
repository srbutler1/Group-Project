"""
Fixed Income Agent for the Economic Summary Swarm.

This module provides the FixedIncomeAgent for analyzing bond markets,
yield curves, and interest rate trends.
"""

from economic_summary.agents.fixed_income.fixed_income_agent import FixedIncomeAgent

__all__ = ['FixedIncomeAgent']

def run_fixed_income_agent(task=None):
    """
    Run the Fixed Income Agent with a task.
    
    Args:
        task: The task to perform (optional)
        
    Returns:
        str: Fixed income analysis
    """
    agent = FixedIncomeAgent()
    return agent.run(task)
