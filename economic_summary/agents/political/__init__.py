"""
Political Agent for the Economic Summary Swarm.

This module provides the PoliticalNewsAgent for analyzing political news
and their economic implications.
"""

from economic_summary.agents.political.political_agent import PoliticalNewsAgent

__all__ = ['PoliticalNewsAgent']

def run_political_agent(task=None):
    """
    Run the Political News Agent with a task.
    
    Args:
        task: The task to perform (optional)
        
    Returns:
        str: Political news analysis with economic implications
    """
    agent = PoliticalNewsAgent()
    return agent.run(task)
