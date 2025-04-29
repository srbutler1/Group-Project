"""
Domain agents for the Economic Summary Swarm Agent System.
"""

from swarms import Agent, MixtureOfAgents

from economic_summary.agents.macro import run_macro_agent, MacroAgent
from economic_summary.agents.aggregator import run_aggregator_agent, AggregatorAgent, EconomicSummarySwarm

def run_domain_agent(domain: str, **kwargs):
    """
    Run a specific domain agent.
    
    Args:
        domain: The domain to analyze (equities, fixed_income, macro, commodities, political)
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        The domain analysis summary
    """
    if domain == 'macro':
        return run_macro_agent(**kwargs)
    elif domain == 'aggregator':
        return run_aggregator_agent(**kwargs)
    else:
        raise ValueError(f"Domain agent '{domain}' not implemented yet")

__all__ = [
    'run_domain_agent',
    'run_macro_agent',
    'run_aggregator_agent',
    'MacroAgent',
    'AggregatorAgent',
    'EconomicSummarySwarm'
]
