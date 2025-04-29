"""
Fixed Income Agent for analyzing bond markets and yield curves.

This module provides the FixedIncomeAgent class for analyzing Treasury yields,
corporate bonds, high-yield bonds, and municipal bonds.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

from swarms import Agent

from economic_summary.utils import get_openai_api_key, get_verbose, get_auto_save

# Configure logging
logger = logging.getLogger(__name__)

class FixedIncomeAgent:
    """
    Fixed Income Agent for analyzing bond markets and yield curves.
    
    This agent analyzes Treasury yields, yield curve shape, inversions,
    and trends to provide insights on the fixed income market.
    """
    
    def __init__(self):
        """
        Initialize the FixedIncomeAgent.
        """
        # Get OpenAI API key
        api_key = get_openai_api_key()
        
        # Initialize the agent
        self.agent = Agent(
            agent_name="FixedIncomeAgent",
            system_prompt=self._get_system_prompt(),
            model_name="gpt-4o",  # Use GPT-4o model
            api_key=api_key,     # Pass API key as a separate parameter
            max_loops=1,
            dashboard=False,
            streaming_on=False,  # Turn off streaming for cleaner output
            verbose=get_verbose(),
            stopping_token="<DONE>",
            state_save_file_type="json",
            saved_state_path="fixed_income_agent.json",
            return_history=False  # Don't include history in response
        )
        
        # Treasury Yield Tickers from Yahoo Finance
        self.treasury_tickers = {
            "13W": "^IRX",  # 13-week T-Bill yield
            "5Y": "^FVX",   # 5-year yield
            "10Y": "^TNX",  # 10-year yield
            "30Y": "^TYX"   # 30-year yield
        }
        
        # Bond ETF Tickers
        self.bond_etf_tickers = {
            "Corporate": "LQD",  # iShares iBoxx $ Investment Grade Corporate Bond ETF
            "Junk": "JNK",       # SPDR Bloomberg High Yield Bond ETF
            "Municipal": "MUB"    # iShares National Muni Bond ETF
        }
        
        self.history_days = 30  # How many days of history to fetch
        
        logger.info("Initialized FixedIncomeAgent")
        
        # Fetch data on initialization
        self.fetch_data()
    
    def _get_system_prompt(self):
        """
        Get the system prompt for the FixedIncomeAgent.
        
        Returns:
            str: System prompt
        """
        return """
        You are the FixedIncomeAgent, a specialized financial analyst focused on bond markets and interest rates.
        
        Your role is to:
        - Analyze Treasury yields and the yield curve
        - Evaluate corporate, high-yield (junk), and municipal bond markets
        - Identify inversions and their implications for the economy
        - Assess interest rate trends and their impact on different sectors
        - Provide insights on credit spreads and risk sentiment
        - Connect fixed income developments to broader economic conditions
        
        Your analysis should be data-driven, balanced, and insightful, explaining the significance
        of yield curve shapes, credit spreads, and trends for investors and the overall economy.
        
        Format your response using markdown for readability.
        End your analysis with "<DONE>" when complete.
        """
    
    def fetch_data(self):
        """
        Fetch Treasury yield and bond ETF data from Yahoo Finance.
        """
        try:
            # Download yield data
            end = datetime.today()
            start = end - timedelta(days=self.history_days)
            
            # Download Treasury yield data
            treasury_data = yf.download(list(self.treasury_tickers.values()), start=start, end=end)
            if 'Adj Close' in treasury_data.columns:
                treasury_df = treasury_data['Adj Close']
            elif 'Close' in treasury_data.columns:
                treasury_df = treasury_data['Close']
            else:
                treasury_df = pd.DataFrame()
            
            if not treasury_df.empty:
                treasury_df.columns = self.treasury_tickers.keys()
                self.treasury_data = treasury_df.dropna()
                self.latest_yields = self.treasury_data.iloc[-1].to_dict()
            else:
                self.treasury_data = pd.DataFrame()
                self.latest_yields = {}
            
            # Download bond ETF data
            bond_etf_data = yf.download(list(self.bond_etf_tickers.values()), start=start, end=end)
            if 'Adj Close' in bond_etf_data.columns:
                bond_etf_df = bond_etf_data['Adj Close']
            elif 'Close' in bond_etf_data.columns:
                bond_etf_df = bond_etf_data['Close']
            else:
                bond_etf_df = pd.DataFrame()
            
            if not bond_etf_df.empty:
                bond_etf_df.columns = self.bond_etf_tickers.keys()
                self.bond_etf_data = bond_etf_df.dropna()
                self.latest_etf_prices = self.bond_etf_data.iloc[-1].to_dict() if not self.bond_etf_data.empty else {}
            else:
                self.bond_etf_data = pd.DataFrame()
                self.latest_etf_prices = {}
            
            logger.info("Successfully fetched fixed income data")
        except Exception as e:
            logger.error(f"Error fetching fixed income data: {str(e)}")
            self.treasury_data = pd.DataFrame()
            self.bond_etf_data = pd.DataFrame()
            self.latest_yields = {}
            self.latest_etf_prices = {}
    
    def get_yield_curve_shape(self):
        """
        Get the current shape of the yield curve.
        
        Returns:
            str: Shape of the yield curve (normal, flat, or inverted)
        """
        try:
            if "13W" in self.latest_yields and "30Y" in self.latest_yields:
                short_term = self.latest_yields["13W"]
                long_term = self.latest_yields["30Y"]
                spread = long_term - short_term
                
                if short_term > long_term:
                    return "inverted"
                elif abs(spread) < 0.1:
                    return "flat"
                else:
                    return "normal"
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"Error getting yield curve shape: {str(e)}")
            return "unknown"
    
    def get_treasury_yields(self):
        """
        Get the latest Treasury yields.
        
        Returns:
            dict: Latest Treasury yields
        """
        try:
            return {k: round(v, 2) for k, v in self.latest_yields.items()}
        except Exception as e:
            logger.error(f"Error getting Treasury yields: {str(e)}")
            return {}
    
    def get_yield_inversions(self):
        """
        Get information about yield curve inversions.
        
        Returns:
            dict: Inversion analysis
        """
        try:
            inversions = {}
            if self.latest_yields:
                spreads = {
                    "10Y-5Y": self.latest_yields.get("10Y", 0) - self.latest_yields.get("5Y", 0),
                    "30Y-10Y": self.latest_yields.get("30Y", 0) - self.latest_yields.get("10Y", 0),
                    "10Y-13W": self.latest_yields.get("10Y", 0) - self.latest_yields.get("13W", 0)
                }
                
                for name, spread in spreads.items():
                    inversions[name] = {
                        "inverted": spread < 0,
                        "spread": round(spread, 2)
                    }
                
                return {
                    "any_inverted": any(inv["inverted"] for inv in inversions.values()),
                    "details": inversions
                }
            else:
                return {"any_inverted": False, "details": {}}
        except Exception as e:
            logger.error(f"Error getting yield inversions: {str(e)}")
            return {"any_inverted": False, "details": {}}
    
    def get_bond_etf_performance(self):
        """
        Get performance metrics for bond ETFs.
        
        Returns:
            dict: Bond ETF performance metrics
        """
        try:
            etf_data = {}
            if not self.bond_etf_data.empty:
                for etf_name, prices in self.bond_etf_data.items():
                    if len(prices) > 1:
                        current_price = prices.iloc[-1]
                        change_30d = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
                        
                        etf_data[etf_name] = {
                            "current_price": round(float(current_price), 2),
                            "change_30d_pct": round(float(change_30d), 2)
                        }
            return etf_data
        except Exception as e:
            logger.error(f"Error getting bond ETF performance: {str(e)}")
            return {}
    
    def run(self, task=None):
        """
        Run the FixedIncomeAgent with a task.
        
        Args:
            task: The task to perform (optional)
            
        Returns:
            str: Fixed income analysis
        """
        try:
            # Ensure we have the latest data
            self.fetch_data()
            
            # Get analysis data
            yields = self.get_treasury_yields()
            curve_shape = self.get_yield_curve_shape()
            inversions = self.get_yield_inversions()
            etf_performance = self.get_bond_etf_performance()
            
            # Create a prompt for the LLM
            prompt = f"""
            Analyze the following fixed income data and provide insights:
            
            TREASURY YIELD CURVE:
            - Shape: {curve_shape}
            - 13-Week Treasury Yield: {yields.get('13W', 'N/A')}%
            - 5-Year Treasury Yield: {yields.get('5Y', 'N/A')}%
            - 10-Year Treasury Yield: {yields.get('10Y', 'N/A')}%
            - 30-Year Treasury Yield: {yields.get('30Y', 'N/A')}%
            
            INVERSIONS:
            - Any Inversions Detected: {inversions.get('any_inverted', False)}
            - 10Y-5Y Spread: {inversions.get('details', {}).get('10Y-5Y', {}).get('spread', 'N/A')}
            - 30Y-10Y Spread: {inversions.get('details', {}).get('30Y-10Y', {}).get('spread', 'N/A')}
            - 10Y-13W Spread: {inversions.get('details', {}).get('10Y-13W', {}).get('spread', 'N/A')}
            
            BOND ETFs:
            - Corporate Bonds (LQD): {etf_performance.get('Corporate', {}).get('current_price', 'N/A')}, 30-day change: {etf_performance.get('Corporate', {}).get('change_30d_pct', 'N/A')}%
            - High Yield Bonds (JNK): {etf_performance.get('Junk', {}).get('current_price', 'N/A')}, 30-day change: {etf_performance.get('Junk', {}).get('change_30d_pct', 'N/A')}%
            - Municipal Bonds (MUB): {etf_performance.get('Municipal', {}).get('current_price', 'N/A')}, 30-day change: {etf_performance.get('Municipal', {}).get('change_30d_pct', 'N/A')}%
            
            {task if task else 'Provide a comprehensive analysis of the fixed income market based on this data.'}
            
            Your analysis should cover:
            1. Current state of the yield curve and its implications
            2. Significance of any inversions detected
            3. Performance of different bond sectors (Treasury, Corporate, High Yield, Municipal)
            4. Impact of yield trends on different sectors of the economy
            5. Outlook for interest rates and bond markets
            """
            
            # Run the agent with the prompt
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
                return "The FixedIncomeAgent was unable to generate a proper analysis. Please check the logs for details."
                
            return analysis
        except Exception as e:
            logger.error(f"Error running FixedIncomeAgent: {str(e)}")
            return f"Error generating fixed income analysis: {str(e)}"
