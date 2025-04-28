"""
Economic Summary Swarm for orchestrating domain agents.
"""
import logging
from typing import Dict, Any, List, Optional
import openai
from swarms import Agent, MixtureOfAgents
from economic_summary.utils import get_openai_api_key, get_verbose, get_auto_save
from economic_summary.agents.aggregator.aggregator_agent import AggregatorAgent

# Configure logging
logger = logging.getLogger(__name__)

class EconomicSummarySwarm:
    """
    Swarm for orchestrating domain agents to generate a comprehensive economic summary.
    Implements the Mixture of Agents (MoA) architecture with a workflow that follows:
    - Layer 1: Parallel Agent Execution (all domain agents collect data)
    - Layer 2: Sequential Processing (identify interdependencies)
    - Layer 3: Parallel Agent Execution (refined analysis with context)
    - Final Aggregator Agent (combines all insights)
    """
    
    def __init__(self, domain_agents=None):
        """
        Initialize the Economic Summary Swarm with domain agents.
        
        Args:
            domain_agents: Dictionary mapping domain names to agent instances
        """
        self.domain_agents = domain_agents or {}
        self.aggregator_agent = AggregatorAgent()
        
        # Initialize OpenAI API key
        openai.api_key = get_openai_api_key()
        
        # Create Agent instances for the MixtureOfAgents
        self.swarm_agents = []
        for domain, agent_instance in self.domain_agents.items():
            if hasattr(agent_instance, 'agent'):
                self.swarm_agents.append(agent_instance.agent)
            else:
                logger.warning(f"Domain agent {domain} does not have an 'agent' attribute")
        
        # Create the MixtureOfAgents if we have domain agents
        if self.swarm_agents:
            # Initialize MixtureOfAgents with the correct parameters for Swarms 7.7.2
            self.moa = MixtureOfAgents(
                agents=self.swarm_agents,
                aggregator_agent=self.aggregator_agent.agent,
                aggregator_system_prompt=self.aggregator_agent._get_system_prompt(),
                name="EconomicSummaryMoA",
                description="Mixture of Agents for comprehensive economic analysis",
                return_str_on=True
            )
        else:
            self.moa = None
            logger.warning("No domain agents provided, MixtureOfAgents not initialized")
    
    def add_domain_agent(self, domain, agent_instance):
        """
        Add a domain agent to the swarm.
        
        Args:
            domain: Domain name
            agent_instance: Agent instance
        """
        self.domain_agents[domain] = agent_instance
        if hasattr(agent_instance, 'agent'):
            self.swarm_agents.append(agent_instance.agent)
            
            # Recreate the MixtureOfAgents with the correct parameters for Swarms 7.7.2
            self.moa = MixtureOfAgents(
                agents=self.swarm_agents,
                aggregator_agent=self.aggregator_agent.agent,
                aggregator_system_prompt=self.aggregator_agent._get_system_prompt(),
                name="EconomicSummaryMoA",
                description="Mixture of Agents for comprehensive economic analysis",
                return_str_on=True
            )
        else:
            logger.warning(f"Domain agent {domain} does not have an 'agent' attribute")
    
    def run_with_moa(self, task):
        """
        Run the Economic Summary Swarm using MixtureOfAgents.
        This implements the full MoA workflow:
        1. Layer 1: Parallel Agent Execution - Domain agents collect data
        2. Layer 2: Sequential Processing - Identify interdependencies
        3. Layer 3: Parallel Agent Execution - Refined analysis with context
        4. Final Aggregator Agent - Combines all insights
        
        Args:
            task: The task to perform
            
        Returns:
            str: Economic summary
        """
        if not self.moa:
            return "Error: MixtureOfAgents not initialized. Add domain agents first."
            
        try:
            logger.info("Layer 1: Starting parallel execution of domain agents...")
            # The MixtureOfAgents handles the parallel execution internally
            
            logger.info("Layer 2: Sequential processing to identify interdependencies...")
            # This happens automatically within the MoA architecture
            
            logger.info("Layer 3: Refined parallel analysis with context...")
            # This is also handled by the MoA architecture
            
            logger.info("Final Layer: Aggregator agent combining insights...")
            # Run the MixtureOfAgents which orchestrates all these layers
            result = self.moa.run(task=task)
            
            # Process the result to extract the actual economic summary
            if isinstance(result, dict):
                if "response" in result:
                    return result["response"]
                elif "output" in result:
                    return result["output"]
                elif "result" in result:
                    return result["result"]
                else:
                    # Try to find any string value in the dictionary
                    for key, value in result.items():
                        if isinstance(value, str) and len(value) > 100:
                            return value
            
            # If we couldn't extract a specific field, return the whole result
            return result
        except Exception as e:
            logger.error(f"Error running Economic Summary Swarm: {str(e)}")
            return f"Error generating economic summary: {str(e)}"
    
    def run_sequential(self, task=None):
        """
        Run the Economic Summary Swarm sequentially (without MixtureOfAgents).
        This is a simpler alternative to the full MoA architecture.
        
        Args:
            task: The task to perform (optional)
            
        Returns:
            str: Economic summary
        """
        try:
            # Run each domain agent
            domain_summaries = {}
            for domain, agent_instance in self.domain_agents.items():
                logger.info(f"Running {domain} agent...")
                try:
                    if hasattr(agent_instance, 'run'):
                        summary = agent_instance.run(task)
                        domain_summaries[domain] = summary
                    else:
                        logger.warning(f"Domain agent {domain} does not have a 'run' method")
                except Exception as e:
                    logger.error(f"Error running {domain} agent: {str(e)}")
                    domain_summaries[domain] = f"Error: {str(e)}"
            
            # Run the aggregator agent
            logger.info("Running aggregator agent...")
            return self.aggregator_agent.run(domain_summaries)
        except Exception as e:
            logger.error(f"Error running Economic Summary Swarm sequentially: {str(e)}")
            return f"Error generating economic summary: {str(e)}"
