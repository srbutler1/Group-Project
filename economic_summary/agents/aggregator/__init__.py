"""
Aggregator Agent for synthesizing insights from all domain agents.
"""

from economic_summary.agents.aggregator.aggregator_agent import AggregatorAgent
from economic_summary.agents.aggregator.economic_summary_swarm import EconomicSummarySwarm

def run_aggregator_agent(domain_summaries):
    """
    Run the Aggregator Agent to synthesize domain insights.
    
    Args:
        domain_summaries: Dictionary mapping domain names to their summaries
        
    Returns:
        str: Comprehensive economic summary
    """
    agent = AggregatorAgent()
    return agent.run(domain_summaries)

def run_economic_summary_swarm(domain_agents=None, task=None, use_moa=True):
    """
    Run the Economic Summary Swarm.
    
    Args:
        domain_agents: Dictionary mapping domain names to agent instances
        task: The task to perform (optional)
        use_moa: Whether to use MixtureOfAgents (True) or sequential execution (False)
        
    Returns:
        str: Economic summary
    """
    swarm = EconomicSummarySwarm(domain_agents)
    if use_moa and swarm.moa:
        return swarm.run_with_moa(task or "Generate a comprehensive economic summary based on current data.")
    else:
        return swarm.run_sequential(task)

__all__ = [
    'AggregatorAgent',
    'EconomicSummarySwarm',
    'run_aggregator_agent',
    'run_economic_summary_swarm'
]
