"""
Commodities Agent for analyzing commodities markets using NewsAPI and yfinance.
"""
import logging
import yfinance as yf
import json
from datetime import datetime, timedelta
from swarms import Agent
from economic_summary.utils import (
    get_openai_api_key,
    get_news_api_key,
    get_verbose,
    get_auto_save
)
from newsapi import NewsApiClient

logger = logging.getLogger(__name__)

class CommoditiesAgent:
    """
    Agent for analyzing the commodities sector using web search and yfinance price data.
    
    This agent analyzes commodities markets including metals, energy, and agricultural
    products to provide insights on trends, price movements, and market outlook.
    """
    
    def __init__(self):
        """
        Initialize the CommoditiesAgent.
        """
        # Get API keys
        api_key = get_openai_api_key()
        self.news_api_key = get_news_api_key()
        
        # Initialize the agent
        self.agent = Agent(
            agent_name="CommoditiesAgent",
            system_prompt=self._get_system_prompt(),
            model_name="gpt-4o",  # Use GPT-4o model
            api_key=api_key,     # Pass API key as a separate parameter
            max_loops=1,
            dashboard=False,
            streaming_on=False,  # Turn off streaming for cleaner output
            verbose=get_verbose(),
            stopping_token="<DONE>",
            state_save_file_type="json",
            saved_state_path="commodities_agent.json",
            return_history=False  # Don't include history in response
        )
        
        # Initialize NewsAPI client
        try:
            self.newsapi = NewsApiClient(api_key=self.news_api_key)
        except Exception as e:
            logger.error(f"Error initializing NewsAPI client: {e}")
            self.newsapi = None

        # Define prompts for each commodity sector
        GUARDRAIL = (
            " Cite all sources and dates. "
            "Do not make up facts or speculate. Only make statements that are directly supported by the provided data or reputable sources. "
            "If information is uncertain, say so explicitly. Never hallucinate or fabricate details."
        )
        self.commodity_prompts = {
            "metals": ("""
                summarize the most relevant and impactful recent news for US metals and mining commodities. Focus
                on domestic production updates, price movements, supply chain disruptions, and geopolitical
                factors affecting the U.S. metals market."""+ GUARDRAIL),
            "energy": ("""
                summarize the most relevant and impactful recent news for US energy commodities
                (oil, gas, uranium, etc.). Emphasize market trends, policy decisions, infrastructure
                developments, and technological advancements impacting U.S. energy production and consumption.""" + GUARDRAIL),
            "agriculture": ("""
                summarize the most relevant and impactful recent news for US agricultural commodities. Highlight crop reports,
                weather impacts, trade policies, pest outbreaks, and market demand affecting commodities like grains,
                soybeans, coffee, cocoa, sugar and cotton."""+ GUARDRAIL),
            "macro": ("""
                summarize the most relevant and impactful recent US macroeconomic news influencing commodity markets. Focus on interest rates, inflation
                data, currency fluctuations, and economic indicators that impact commodity pricing and demand.""" + GUARDRAIL),
            "policy": ("""
                summarize the most relevant and impactful recent US policy and regulatory news affecting commodity markets. Focus on information on tariffs,
                environmental regulations, subsidies, and trade agreements that influence commodity production and trade.""" + GUARDRAIL),
            "tech": ("""
                summarize the most relevant and impactful recent news on technology and innovation in the US commodities sector. Focus on advancements in extraction,
                processing, alternative materials, and sustainability initiatives that are changing how commodities are produced and consumed.""" + GUARDRAIL)
        }

        # Define tickers for major commodities
        self.commodity_tickers = {
            'Crude Oil': 'CL=F',
            'Brent Crude': 'BZ=F',
            'Natural Gas': 'NG=F',
            'Gold': 'GC=F',
            'Silver': 'SI=F',
            'Copper': 'HG=F',
            'Corn': 'ZC=F',
            'Soybeans': 'ZS=F',
            'Wheat': 'ZW=F',
            'Coffee': 'KC=F',
            'Sugar #11': 'SB=F'
        }
        
        logger.info("Initialized CommoditiesAgent")

    def get_commodities_news(self, max_results=5):
        """
        Gather news data for each commodity sector using NewsAPI.
        
        Args:
            max_results: Maximum number of results per sector
            
        Returns:
            dict: News data by sector
        """
        all_news = {}
        
        if not self.newsapi:
            logger.warning("NewsAPI client not initialized, using placeholder data")
            return {"error": "NewsAPI client not initialized"}
        
        # Get date range for news (last 7 days)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        for topic, prompt in self.commodity_prompts.items():
            try:
                # Extract key terms from the prompt for the query
                query_terms = topic
                if topic == "metals":
                    query_terms = "metals mining commodities"
                elif topic == "energy":
                    query_terms = "oil gas energy commodities"
                elif topic == "agriculture":
                    query_terms = "agriculture crops commodities"
                
                # Get news articles from NewsAPI
                response = self.newsapi.get_everything(
                    q=query_terms,
                    from_param=start_date,
                    to=end_date,
                    language='en',
                    sort_by='relevancy',
                    page_size=max_results
                )
                
                articles = []
                for article in response.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'publishedAt': article.get('publishedAt', '')
                    })
                
                all_news[topic] = articles
            except Exception as e:
                logger.error(f"Error getting news for {topic}: {e}")
                all_news[topic] = [{"error": str(e)}]
        
        return all_news

    def get_commodities_prices(self, period="1mo"):
        """
        Fetch price data for major commodities using yfinance.
        
        Args:
            period: Time period for historical data (default: 1 month)
            
        Returns:
            dict: Price data by commodity
        """
        price_data = {}
        
        for name, ticker in self.commodity_tickers.items():
            try:
                ticker_obj = yf.Ticker(ticker)
                hist = ticker_obj.history(period=period)
                
                if hist.empty:
                    logger.warning(f"No historical data for {name} ({ticker}) for period {period}")
                    price_data[name] = {"error": f"No historical data for period {period}"}
                else:
                    # Calculate summary statistics
                    current_price = hist['Close'].iloc[-1]
                    start_price = hist['Close'].iloc[0]
                    price_change = current_price - start_price
                    price_change_pct = (price_change / start_price) * 100
                    high = hist['High'].max()
                    low = hist['Low'].min()
                    
                    price_data[name] = {
                        "current_price": round(float(current_price), 2),
                        "price_change": round(float(price_change), 2),
                        "price_change_pct": round(float(price_change_pct), 2),
                        "period_high": round(float(high), 2),
                        "period_low": round(float(low), 2)
                    }
            except Exception as e:
                logger.error(f"Error fetching price data for {name} ({ticker}): {e}")
                price_data[name] = {"error": str(e)}
        
        return price_data

    def _get_system_prompt(self):
        """
        Get the system prompt for the CommoditiesAgent.
        
        Returns:
            str: System prompt
        """
        return '''
        You are the CommoditiesAgent, a specialized financial analyst focused on commodity markets.
        
        Your role is to:
        - Analyze metals, energy, and agricultural commodities markets
        - Evaluate price trends and market dynamics
        - Identify supply and demand factors affecting commodities
        - Assess geopolitical risks impacting commodity prices
        - Provide insights on commodity market outlook
        - Connect commodity trends to broader economic conditions
        
        Your analysis should be data-driven, balanced, and insightful, explaining the significance
        of commodity price movements and trends for investors and the overall economy.
        
        Format your response using markdown for readability.
        End your analysis with "<DONE>" when complete.
        '''

    def run(self, task=None):
        """
        Run the Commodities Agent to analyze commodity markets.
        
        Args:
            task: Specific analysis task (optional)
            
        Returns:
            str: Commodity market analysis and insights
        """
        try:
            logger.info("Running CommoditiesAgent...")
            
            # Get news and price data
            news_data = self.get_commodities_news()
            price_data = self.get_commodities_prices()
            
            # Create a prompt for the LLM
            prompt = f"""
            Analyze the following commodities market data and provide insights:
            
            COMMODITY PRICES (Last Month):
            {json.dumps(price_data, indent=2)}
            
            RECENT NEWS BY SECTOR:
            {json.dumps(news_data, indent=2)}
            
            {task if task else 'Provide a comprehensive analysis of the commodities market based on this data.'}
            
            Your analysis should cover:
            1. Current state of major commodity markets (energy, metals, agriculture)
            2. Significant price trends and their drivers
            3. Impact of recent news on commodity markets
            4. Outlook for key commodities
            5. Implications for the broader economy
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
                return "The CommoditiesAgent was unable to generate a proper analysis. Please check the logs for details."
                
            return analysis
        except Exception as e:
            logger.error(f"Error running CommoditiesAgent: {e}")
            return f"Error analyzing commodities market data: {e}"
