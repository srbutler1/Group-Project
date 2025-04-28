"""
Macro Agent for analyzing macroeconomic indicators using FRED data.
"""
import logging
import openai
from swarms import Agent
from economic_summary.utils import get_openai_api_key, FREDDataManager, get_verbose, get_auto_save

# Configure logging
logger = logging.getLogger(__name__)

class MacroAgent:
    """
    Agent for analyzing macroeconomic indicators and trends.
    """
    
    def __init__(self):
        """Initialize the Macro Agent with FRED data manager and LLM."""
        self.fred_manager = FREDDataManager()
        # Initialize with OpenAI directly as per Swarms 7.7.2
        api_key = get_openai_api_key()
        self.agent = Agent(
            agent_name="MacroAgent",
            system_prompt=self._get_system_prompt(),
            model_name="gpt-4o",  # Use GPT-4o model
            api_key=api_key,     # Pass API key as a separate parameter
            max_loops=1,
            dashboard=False,
            streaming_on=False,  # Turn off streaming for cleaner output
            verbose=get_verbose(),
            stopping_token="<DONE>",
            state_save_file_type="json",
            saved_state_path="macro_agent.json",
            return_history=False  # Don't include history in response
        )
        
    def _get_system_prompt(self):
        """Get the system prompt for the Macro Agent."""
        return """
        You are a Macroeconomic Analysis Agent specializing in interpreting economic indicators and trends.
        Your task is to analyze macroeconomic data from FRED (Federal Reserve Economic Database) and provide 
        insightful analysis on the current state of the economy and potential future trends.
        
        Focus on these key areas:
        1. GDP growth and overall economic output
        2. Inflation and price stability
        3. Employment and labor market conditions
        4. Interest rates and monetary policy
        5. Consumer sentiment and spending
        6. Industrial production and business activity
        7. Housing market trends
        8. Recession indicators and economic cycle positioning
        
        For each analysis:
        - Identify significant trends and changes in key indicators
        - Explain what these changes mean for the overall economy
        - Note any warning signs or positive developments
        - Consider how different economic factors interact with each other
        - Provide a concise summary of the macroeconomic outlook
        
        Your analysis should be data-driven, balanced, and focused on the most relevant information.
        Avoid political bias and speculation not supported by the data.
        
        Format your response as a structured analysis with clear sections and bullet points where appropriate.
        End your analysis with "<DONE>" when complete.
        """
    
    def get_economic_indicators(self, indicators=None, periods=12, start_date=None, end_date=None):
        """
        Get and analyze economic indicators.
        
        Args:
            indicators: List of indicator names (default: key indicators)
            periods: Number of periods to analyze
            start_date: Start date
            end_date: End date
            
        Returns:
            dict: Analysis of economic indicators
        """
        if not indicators:
            indicators = [
                'GDP', 'GDPC1', 'UNRATE', 'CPIAUCSL', 'FEDFUNDS', 
                'T10Y2Y', 'PAYEMS', 'INDPRO', 'HOUST', 'UMCSENT'
            ]
            
        try:
            return self.fred_manager.analyze_indicators(indicators, periods, start_date, end_date)
        except Exception as e:
            logger.error(f"Error analyzing economic indicators: {str(e)}")
            return {"error": str(e)}
    
    def get_recession_risk(self):
        """
        Assess current recession risk based on key indicators.
        
        Returns:
            dict: Recession risk assessment
        """
        try:
            # Get yield curve (10Y-2Y spread)
            yield_curve = self.fred_manager.get_indicator('T10Y2Y')
            
            # Get unemployment rate
            unemployment = self.fred_manager.get_indicator('UNRATE')
            
            # Get industrial production
            industrial_production = self.fred_manager.get_indicator('INDPRO')
            
            # Simple recession risk model
            risk_factors = 0
            risk_details = []
            
            # Check yield curve inversion
            if yield_curve is not None and len(yield_curve) > 0:
                latest_spread = yield_curve.iloc[-1]
                if latest_spread < 0:
                    risk_factors += 1
                    risk_details.append(f"Yield curve is inverted: {latest_spread:.2f}%")
                    
            # Check unemployment trend
            if unemployment is not None and len(unemployment) > 6:
                recent_unemployment = unemployment.iloc[-6:]
                if recent_unemployment.iloc[-1] > recent_unemployment.iloc[0]:
                    risk_factors += 1
                    risk_details.append(f"Unemployment rate is rising: {recent_unemployment.iloc[0]:.1f}% to {recent_unemployment.iloc[-1]:.1f}%")
                    
            # Check industrial production trend
            if industrial_production is not None and len(industrial_production) > 3:
                recent_production = industrial_production.iloc[-3:]
                if recent_production.diff().mean() < 0:
                    risk_factors += 1
                    risk_details.append("Industrial production is declining")
                    
            # Determine risk level
            if risk_factors == 0:
                risk_level = "Low"
            elif risk_factors == 1:
                risk_level = "Moderate"
            elif risk_factors == 2:
                risk_level = "Elevated"
            else:
                risk_level = "High"
                
            return {
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "risk_details": risk_details
            }
        except Exception as e:
            logger.error(f"Error assessing recession risk: {str(e)}")
            return {"error": str(e)}
    
    def get_recent_economic_reports(self, sources=None, limit_per_source=5):
        """
        Get recent economic reports from FRED.
        
        Args:
            sources: List of source names or IDs (default: ['fed', 'bea', 'bls'])
            limit_per_source: Maximum number of reports per source
            
        Returns:
            dict: Dictionary of recent economic reports by source
        """
        try:
            return self.fred_manager.get_recent_releases(sources, limit_per_source)
        except Exception as e:
            logger.error(f"Error retrieving recent economic reports: {str(e)}")
            return {"error": str(e)}
    
    def run(self, task=None):
        """
        Run the Macro Agent to analyze economic data and generate insights.
        
        Args:
            task: Specific analysis task (optional)
            
        Returns:
            str: Economic analysis and insights
        """
        try:
            # Get economic indicators
            indicators_analysis = self.get_economic_indicators()
            
            # Get recession risk
            recession_risk = self.get_recession_risk()
            
            # Get recent economic reports
            recent_reports = self.get_recent_economic_reports()
            
            # Format the data for the LLM
            prompt = f"""
            Please analyze the following macroeconomic data and provide insights:
            
            Economic Indicators Analysis:
            {indicators_analysis}
            
            Recession Risk Assessment:
            {recession_risk}
            
            Recent Economic Reports:
            {recent_reports}
            
            Based on this data, provide a comprehensive analysis of the current macroeconomic situation, 
            key trends, and outlook. Include specific insights about GDP, inflation, employment, 
            interest rates, and recession risk.
            
            If there is a specific task to focus on, it is: {task if task else "Provide a general macroeconomic overview"}
            """
            
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
                return "The MacroAgent was unable to generate a proper analysis. Please check the logs for details."
                
            return analysis
        except Exception as e:
            logger.error(f"Error running Macro Agent: {str(e)}")
            return f"Error analyzing macroeconomic data: {str(e)}"
