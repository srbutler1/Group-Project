"""
Economic Summary Swarm implementation using Mixture of Agents (MoA) architecture.
"""
import logging
import openai
import json
from swarms import MixtureOfAgents
from economic_summary.utils import get_openai_api_key
from economic_summary.agents.aggregator.aggregator_agent import AggregatorAgent
import os
import datetime

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
        
        # Create agent workspace directory if it doesn't exist
        self.workspace_dir = os.path.join(os.getcwd(), "agent_workspace", "outputs")
        os.makedirs(self.workspace_dir, exist_ok=True)
    
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
                
                # Log the domain agent output to the workspace
                self._log_agent_output(domain, domain_task, insight)
                
                # Store the insight
                domain_insights[domain] = insight
                logger.info(f"Successfully collected insights from {domain} agent")
            except Exception as e:
                logger.error(f"Error collecting insights from {domain} agent: {str(e)}")
                domain_insights[domain] = f"Error: {str(e)}"
        
        return domain_insights
    
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
            
            # Limit the size of each insight to prevent context window issues
            if isinstance(insight, str) and len(insight) > 2000:
                # Extract the first and last parts of the insight
                first_part = insight[:1000]
                last_part = insight[-1000:]
                formatted += f"{first_part}\n\n[...content truncated...]\n\n{last_part}"
            else:
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
        
        # Create a condensed version of all insights for context
        condensed_insights = ""
        for domain, insight in domain_insights.items():
            condensed_insights += f"\n\n=== {domain.upper()} KEY POINTS ===\n\n"
            
            # Extract just a brief summary from each insight
            if isinstance(insight, str):
                if len(insight) > 500:
                    # Take just the first 500 characters as a summary
                    condensed_insights += insight[:500] + "..."
                else:
                    condensed_insights += insight
            
            condensed_insights += "\n\n"
        
        for domain, agent in self.domain_agents.items():
            logger.info(f"Refining insights from {domain} agent with cross-domain awareness...")
            try:
                # Create a refinement task with condensed insights from other domains
                refinement_task = f"""
                {task}
                
                You previously provided this {domain} analysis. Focus on refining it with awareness of other domains.
                
                Here are condensed insights from all economic domains:
                
                {condensed_insights}
                
                Provide a BRIEF refined {domain} analysis (maximum 500 words) that considers these other insights.
                Focus on how your domain interacts with or is affected by the others.
                """
                
                # Run the agent with the refinement task
                refined = agent.run(refinement_task)
                
                # Log the refined domain agent output to the workspace
                self._log_agent_output(f"{domain}_refined", refinement_task, refined)
                
                # Ensure the refined insight isn't too large
                if isinstance(refined, str) and len(refined) > 2000:
                    refined = refined[:2000] + "...[truncated]"
                
                # Store the refined insight
                refined_insights[domain] = refined
                logger.info(f"Successfully refined insights from {domain} agent")
            except Exception as e:
                logger.error(f"Error refining insights from {domain} agent: {str(e)}")
                # Use a condensed version of the original insights as fallback
                if isinstance(domain_insights[domain], str) and len(domain_insights[domain]) > 1000:
                    refined_insights[domain] = domain_insights[domain][:1000] + "...[truncated]"
                else:
                    refined_insights[domain] = domain_insights[domain]
        
        # Format the refined insights
        return self.format_domain_insights(refined_insights)
    
    def _log_agent_output(self, agent_name, task, output):
        """
        Log agent output to the agent workspace.
        
        Args:
            agent_name: Name of the agent
            task: The task that was performed
            output: The agent's output
        """
        try:
            # Create a timestamp for the log file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create a log file name
            log_file = os.path.join(self.workspace_dir, f"{agent_name}_{timestamp}.json")
            
            # Prepare the log data
            log_data = {
                "agent_name": agent_name,
                "timestamp": timestamp,
                "task": task,
                "output": output
            }
            
            # Write the log data to the file
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
            logger.info(f"Logged {agent_name} output to {log_file}")
        except Exception as e:
            logger.error(f"Error logging {agent_name} output: {str(e)}")
    
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
            # Create a concise version of the task and insights to avoid context window issues
            aggregator_task = f"""
            {task}
            
            Here are the key domain-specific insights to synthesize (condensed for brevity):
            
            {refined_insights}
            
            Provide a concise, comprehensive economic summary (maximum 1000 words) that integrates these insights.
            Focus on the most important connections between domains and key economic trends.
            """
            
            result = self.aggregator_agent.run(aggregator_task)
            
            # Log the aggregator output to the workspace
            self._log_agent_output("aggregator", aggregator_task, result)
            
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
                
                # Log the domain agent output to the workspace
                self._log_agent_output(domain, domain_task, insight)
                
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
            
            # Log the aggregator output to the workspace
            self._log_agent_output("aggregator", aggregator_task, summary)
            
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
