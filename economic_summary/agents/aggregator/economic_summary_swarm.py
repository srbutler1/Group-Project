"""
Economic Summary Swarm implementation using Mixture of Agents (MoA) architecture.
"""
import logging
import openai
import json
from swarms import MixtureOfAgents
from economic_summary.utils import get_openai_api_key
from economic_summary.agents.aggregator.aggregator_agent import AggregatorAgent

# Configure logging
logger = logging.getLogger(__name__)

class EconomicSummarySwarm:
    """
    Economic Summary Swarm using Mixture of Agents (MoA) architecture.
    
    This class orchestrates multiple domain-specific agents to generate
    a comprehensive economic summary.
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
    
    def add_domain_agent(self, domain, agent):
        """
        Add a domain agent to the swarm.
        
        Args:
            domain: Domain name
            agent: Agent instance
        """
        self.domain_agents[domain] = agent
        
        # Add to swarm_agents if it has an agent attribute
        if hasattr(agent, 'agent'):
            self.swarm_agents.append(agent.agent)
            
            # Reinitialize MixtureOfAgents with updated agents
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
    
    def collect_domain_insights(self, task):
        """
        Collect insights from each domain agent explicitly.
        
        Args:
            task: The task to perform
            
        Returns:
            dict: Dictionary mapping domain names to their insights
        """
        domain_insights = {}
        
        for domain, agent in self.domain_agents.items():
            logger.info(f"Collecting insights from {domain} agent...")
            try:
                # Run the agent with the task
                domain_task = f"Provide {domain} analysis for: {task}"
                insight = agent.run(domain_task)
                
                # Store the insight
                domain_insights[domain] = insight
                logger.info(f"Successfully collected insights from {domain} agent")
            except Exception as e:
                logger.error(f"Error collecting insights from {domain} agent: {str(e)}")
                domain_insights[domain] = f"Error: {str(e)}"
        
        return domain_insights
    
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
            # Explicitly collect insights from each domain agent
            domain_insights = self.collect_domain_insights(task)
            
            logger.info("Layer 2: Sequential processing to identify interdependencies...")
            # Format the collected insights for the aggregator
            formatted_insights = self.format_domain_insights(domain_insights)
            
            logger.info("Layer 3: Refined parallel analysis with context...")
            # Run domain agents again with awareness of other domains' insights
            refined_insights = self.refine_domain_insights(domain_insights, task)
            
            logger.info("Final Layer: Aggregator agent combining insights...")
            # Use the aggregator agent to synthesize the insights
            aggregator_task = f"""
            {task}
            
            Here are the domain-specific insights to synthesize:
            
            {refined_insights}
            
            Provide a comprehensive economic summary that integrates these insights.
            """
            
            result = self.aggregator_agent.run(aggregator_task)
            
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
    
    def format_domain_insights(self, domain_insights):
        """
        Format domain insights for the aggregator.
        
        Args:
            domain_insights: Dictionary mapping domain names to their insights
            
        Returns:
            str: Formatted insights
        """
        formatted = ""
        
        for domain, insight in domain_insights.items():
            formatted += f"\n\n=== {domain.upper()} INSIGHTS ===\n\n"
            formatted += insight
            formatted += "\n\n" + "-" * 40 + "\n"
        
        return formatted
    
    def refine_domain_insights(self, domain_insights, task):
        """
        Refine domain insights with awareness of other domains.
        
        Args:
            domain_insights: Dictionary mapping domain names to their insights
            task: The original task
            
        Returns:
            str: Formatted refined insights
        """
        refined_insights = {}
        
        # Format all insights for context
        all_insights = self.format_domain_insights(domain_insights)
        
        for domain, agent in self.domain_agents.items():
            logger.info(f"Refining insights from {domain} agent with cross-domain awareness...")
            try:
                # Create a refinement task with other domains' insights
                refinement_task = f"""
                {task}
                
                You previously provided this {domain} analysis:
                
                {domain_insights[domain]}
                
                Here are insights from other economic domains:
                
                {all_insights}
                
                Now, refine your {domain} analysis considering these other insights.
                Focus on how your domain interacts with or is affected by the others.
                """
                
                # Run the agent with the refinement task
                refined = agent.run(refinement_task)
                
                # Store the refined insight
                refined_insights[domain] = refined
                logger.info(f"Successfully refined insights from {domain} agent")
            except Exception as e:
                logger.error(f"Error refining insights from {domain} agent: {str(e)}")
                refined_insights[domain] = domain_insights[domain]  # Fall back to original insights
        
        # Format the refined insights
        return self.format_domain_insights(refined_insights)
    
    def run_sequential(self, task):
        """
        Run the Economic Summary Swarm sequentially.
        This is a simpler alternative to the MoA approach.
        
        Args:
            task: The task to perform
            
        Returns:
            str: Economic summary
        """
        try:
            # Collect insights from each domain agent
            domain_insights = {}
            
            for domain, agent in self.domain_agents.items():
                logger.info(f"Running {domain} agent...")
                domain_task = f"Provide {domain} analysis for: {task}"
                insight = agent.run(domain_task)
                domain_insights[domain] = insight
            
            # Format the insights for the aggregator
            formatted_insights = ""
            for domain, insight in domain_insights.items():
                formatted_insights += f"\n\n=== {domain.upper()} INSIGHTS ===\n\n"
                formatted_insights += insight
                formatted_insights += "\n\n" + "-" * 40 + "\n"
            
            # Run the aggregator agent
            logger.info("Running aggregator agent...")
            aggregator_task = f"""
            {task}
            
            Here are the domain-specific insights to synthesize:
            
            {formatted_insights}
            
            Provide a comprehensive economic summary that integrates these insights.
            """
            
            summary = self.aggregator_agent.run(aggregator_task)
            
            return summary
        except Exception as e:
            logger.error(f"Error running sequential Economic Summary Swarm: {str(e)}")
            return f"Error generating economic summary: {str(e)}"
    
    def run(self, task=None):
        """
        Run the Economic Summary Swarm.
        This is a convenience method that uses the MoA approach if available,
        otherwise falls back to sequential execution.
        
        Args:
            task: The task to perform (default: generate a general economic summary)
            
        Returns:
            str: Economic summary
        """
        if not task:
            task = "Generate a comprehensive economic summary covering all major domains."
            
        if self.moa:
            return self.run_with_moa(task)
        else:
            return self.run_sequential(task)
