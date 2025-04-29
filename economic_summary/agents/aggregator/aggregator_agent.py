"""
Aggregator Agent for synthesizing insights from domain agents.
"""
import logging
import openai
from swarms import Agent
from economic_summary.utils import get_openai_api_key, get_verbose, get_auto_save

# Configure logging
logger = logging.getLogger(__name__)

class AggregatorAgent:
    """
    Agent for synthesizing insights from domain agents into a comprehensive economic summary.
    """
    
    def __init__(self):
        """Initialize the Aggregator Agent."""
        api_key = get_openai_api_key()
        self.agent = Agent(
            agent_name="AggregatorAgent",
            system_prompt=self._get_system_prompt(),
            model_name="gpt-4o",  # Use GPT-4o model
            api_key=api_key,     # Pass API key as a separate parameter
            max_loops=1,
            dashboard=False,
            streaming_on=False,  # Turn off streaming for cleaner output
            verbose=get_verbose(),
            stopping_token="<DONE>",
            state_save_file_type="json",
            saved_state_path="aggregator_agent.json",
            return_history=False  # Don't include history in response
        )
    
    def _get_system_prompt(self):
        """Get the system prompt for the Aggregator Agent."""
        return """
        You are an Economic Summary Aggregator Agent responsible for synthesizing insights from multiple 
        domain-specific economic analyses into a comprehensive, cohesive economic overview.
        
        Your task is to:
        1. Integrate insights from various economic domains (equities, fixed income, macroeconomics, 
           commodities, political news)
        2. Identify connections, correlations, and contradictions between different domains
        3. Prioritize the most significant economic trends and developments
        4. Synthesize a balanced, comprehensive economic summary
        5. Highlight key risks and opportunities in the current economic environment
        
        When synthesizing information:
        - IMPORTANT: Use ONLY the domain-specific insights provided to you - do not make up information
        - Maintain a balanced perspective that considers all domains
        - Identify how developments in one domain may impact others
        - Resolve apparent contradictions by providing context and nuance
        - Distinguish between leading and lagging indicators
        - Consider both short-term fluctuations and long-term trends
        - Avoid political bias or speculation not supported by the data
        
        Format your response as a structured economic summary with clear sections, 
        including an executive summary, domain-specific insights, cross-domain analysis, 
        and outlook. Use bullet points where appropriate for clarity.
        
        End your analysis with "<DONE>" when complete.
        """
    
    def run(self, task_or_insights):
        """
        Run the Aggregator Agent to synthesize economic insights.
        
        Args:
            task_or_insights: Either a task description or a dictionary/string of domain insights
            
        Returns:
            str: Synthesized economic summary
        """
        try:
            # Determine if we're given a task or insights
            if isinstance(task_or_insights, dict):
                # Format the dictionary of domain insights
                formatted_insights = ""
                for domain, insight in task_or_insights.items():
                    formatted_insights += f"\n\n=== {domain.upper()} INSIGHTS ===\n\n"
                    formatted_insights += insight
                    formatted_insights += "\n\n" + "-" * 40 + "\n"
                
                prompt = f"""
                Generate a comprehensive economic summary that synthesizes the following domain-specific insights:
                
                {formatted_insights}
                
                Focus on identifying connections between domains, highlighting key trends, and providing a balanced outlook.
                """
            elif isinstance(task_or_insights, str) and "===" in task_or_insights:
                # This is already formatted domain insights
                prompt = f"""
                Generate a comprehensive economic summary that synthesizes the following domain-specific insights:
                
                {task_or_insights}
                
                Focus on identifying connections between domains, highlighting key trends, and providing a balanced outlook.
                """
            else:
                # This is a task description
                prompt = task_or_insights
            
            # Run the agent
            response = self.agent.run(prompt)
            
            # Extract the analysis from the response
            analysis = ""
            if isinstance(response, dict):
                if "response" in response:
                    analysis = response["response"]
                elif "output" in response:
                    analysis = response["output"]
                elif "result" in response:
                    analysis = response["result"]
                else:
                    # Try to find any string value in the dictionary
                    for key, value in response.items():
                        if isinstance(value, str) and len(value) > 100:
                            analysis = value
                            break
            elif isinstance(response, str):
                analysis = response
                
            # Clean up the analysis
            # Remove the stopping token if present
            if analysis.endswith("<DONE>"):
                analysis = analysis[:-6].strip()
                
            # If analysis is still empty, return a default message
            if not analysis:
                return "The AggregatorAgent was unable to generate a proper analysis. Please check the logs for details."
                
            return analysis
        except Exception as e:
            logger.error(f"Error running Aggregator Agent: {str(e)}")
            return f"Error synthesizing economic insights: {str(e)}"
