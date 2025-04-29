"""
Equities Agent for analyzing stock market data, SEC filings, and financial news.
"""
import logging
import openai
import yfinance as yf  # Import yfinance
import pandas as pd
from swarms import Agent
from economic_summary.utils import (
    get_openai_api_key, 
    get_sec_api_key, # Import SEC key getter
    get_news_api_key, # Import News key getter
    get_verbose, 
    get_auto_save 
)
from sec_api import QueryApi # Import sec_api
from newsapi import NewsApiClient # Import NewsAPI client
from newsapi.newsapi_exception import NewsAPIException # Import specific exception (Corrected name)
# Placeholder for data manager imports
# from .data_managers import YahooFinanceManager, SECDataManager, NewsDataManager 

# Configure logging
logger = logging.getLogger(__name__)

class EquitiesAgent:
    """
    Agent for analyzing the equities market, including indices, sectors, 
    earnings reports, SEC filings, and financial news.

    Initializes API clients for data fetching (sec-api, NewsAPI) and the internal Swarms Agent (LLM).
    """
    
    def __init__(self):
        """Initialize the Equities Agent, setting up API clients and the internal LLM agent."""
        # Placeholder: Initialize data managers when created
        # self.yf_manager = YahooFinanceManager()
        # self.sec_manager = SECDataManager() # We can integrate sec_api here or keep it separate
        # self.news_manager = NewsDataManager()
        
        # Initialize SEC API client
        sec_key = get_sec_api_key()
        if sec_key:
             self.query_api = QueryApi(api_key=sec_key)
        else:
             logger.error("SEC_API_KEY not found. SEC filing features will be disabled.")
             self.query_api = None

        # Initialize NewsAPI client
        news_key = get_news_api_key()
        if news_key:
            self.news_api = NewsApiClient(api_key=news_key)
        else:
            logger.error("NEWS_API_KEY not found. Financial news features will be disabled.")
            self.news_api = None

        api_key = get_openai_api_key()
        self.agent = Agent(
            agent_name="EquitiesAgent",
            system_prompt=self._get_system_prompt(),
            model_name="gpt-4o",
            api_key=api_key,
            max_loops=1,
            dashboard=False,
            streaming_on=False,
            verbose=get_verbose(),
            stopping_token="<DONE>",
            state_save_file_type="json",
            saved_state_path="equities_agent.json",
            return_history=False
        )
        
    def _get_system_prompt(self):
        """Get the system prompt for the Equities Agent."""
        # Placeholder: Define a detailed prompt for equities analysis
        return """
        You are an Equities Market Analysis Agent. Your task is to analyze stock market data, 
        corporate filings (like SEC 10-Ks), and relevant financial news to provide insights 
        into the equities market.

        Focus on these key areas:
        1. Major Indices Performance (S&P 500, Nasdaq, Dow Jones): Trends, key levels, driving factors.
        2. Sector Performance: Identify leading and lagging sectors and reasons why.
        3. Earnings Reports Analysis: Summarize key findings from recent important earnings reports.
        4. SEC Filings Insights: Extract relevant information about company performance, risks, and outlook from 10-K filings.
        5. Financial News Impact: Analyze how current news events are affecting the market or specific stocks/sectors.
        6. Overall Market Sentiment and Outlook: Synthesize findings into a cohesive market view.

        For each analysis:
        - Use the provided data (market data, filing summaries, news headlines/summaries).
        - Identify significant trends, patterns, and anomalies.
        - Explain the potential impact on investors and the broader market.
        - Provide a concise, data-driven summary.
        - Avoid speculation not supported by the data.

        Format your response as a structured analysis with clear sections.
        End your analysis with "<DONE>" when complete.
        """

    # --- Placeholder Methods for Data Fetching ---
    def get_market_data(self, indices=None, sectors=None, period="1mo"):
        """
        Fetch market data for major indices and sector ETFs using yfinance.
        
        Args:
            indices (list): List of index tickers. Defaults to S&P 500, Nasdaq, Dow Jones.
            sectors (list): List of sector ETF tickers. Defaults to common SPDR ETFs.
            period (str): Data period to fetch (e.g., "1d", "5d", "1mo", ..., "max"). Defaults to "1mo".

        Returns:
            dict: Dictionary containing historical data and summary for each index/sector.
                  Returns an error message if fetching fails.
        """
        logger.info(f"Fetching market and sector data for period: {period}")
        if indices is None:
            indices = ['^GSPC', '^IXIC', '^DJI'] # S&P 500, Nasdaq, Dow Jones
        if sectors is None:
            sectors = ['XLK', 'XLF', 'XLV', 'XLY', 'XLP', 'XLE', 'XLI', 'XLU', 'XLB', 'XLRE', 'XLC']
        
        all_tickers = indices + sectors
        market_data = {}
        try:
            for ticker_symbol in all_tickers:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period=period)
                
                if hist.empty:
                    logger.warning(f"No historical data found for {ticker_symbol} for period {period}")
                    market_data[ticker_symbol] = {"error": f"No historical data found for period {period}"}
                    continue

                hist.index = hist.index.strftime('%Y-%m-%d')
                hist_dict = hist.to_dict(orient='index')
                info = ticker.info
                
                market_data[ticker_symbol] = {
                    "info": {
                        "symbol": ticker_symbol,
                        "shortName": info.get("shortName", ticker_symbol),
                        "currency": info.get("currency", "USD"),
                        "type": "Index" if ticker_symbol.startswith('^') else "Sector ETF"
                    },
                    "historical_data": hist_dict, # Consider summarizing this for the prompt later
                    "last_close": hist['Close'].iloc[-1] if not hist.empty else None,
                    "period_change_pct": ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100 if len(hist) > 1 else 0
                }
                logger.info(f"Successfully fetched data for {ticker_symbol}")

            # Add overall sector performance summary (e.g., sort by period_change_pct)
            sector_performance = sorted([
                (data['info']['shortName'], data['period_change_pct'])
                for symbol, data in market_data.items() if data.get('info', {}).get('type') == 'Sector ETF' and 'period_change_pct' in data
            ], key=lambda item: item[1], reverse=True)
            
            market_data['_summary'] = {
                 "sector_performance_ranking": sector_performance
            }

            return market_data

        except Exception as e:
            logger.error(f"Error fetching market data using yfinance: {str(e)}", exc_info=True)
            return {"error": f"Failed to fetch market data: {str(e)}"}

    def get_earnings_data(self, tickers=None, lookahead_days=7):
        """
        Fetch upcoming earnings dates for a list of stock tickers.

        Args:
            tickers (list): List of stock tickers (e.g., ['AAPL', 'MSFT']). Defaults to a sample list.
            lookahead_days (int): How many days ahead to look for earnings dates. Defaults to 7.

        Returns:
            dict: Dictionary containing earnings calendar info for each ticker.
                  Returns an error message if fetching fails.
        """
        logger.info(f"Fetching earnings calendar data for tickers: {tickers}")
        if tickers is None:
            # TODO: Decide on a default list or make required
            tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'] 

        earnings_data = {}
        try:
            today = pd.Timestamp.today().normalize()
            max_date = today + pd.Timedelta(days=lookahead_days)

            for ticker_symbol in tickers:
                ticker = yf.Ticker(ticker_symbol)
                # Handle cases where calendar is dict (error) or None
                try:
                    calendar = ticker.calendar
                    if not isinstance(calendar, pd.DataFrame):
                         logger.warning(f"Received non-DataFrame calendar data for {ticker_symbol}. Type: {type(calendar)}")
                         earnings_data[ticker_symbol] = {"status": f"Invalid calendar data received"}
                         continue
                except Exception as fetch_err:
                     logger.warning(f"Could not fetch calendar data for {ticker_symbol}: {fetch_err}")
                     earnings_data[ticker_symbol] = {"status": f"Failed to fetch calendar data: {fetch_err}"}
                     continue

                if calendar is None or 'Earnings Date' not in calendar.columns or calendar.empty:
                    logger.warning(f"No earnings calendar data found for {ticker_symbol}")
                    earnings_data[ticker_symbol] = {"status": "No upcoming earnings date found"}
                    continue

                # yfinance typically returns a range (e.g., '2024-07-25' to '2024-07-29')
                # We extract the start date for simplicity
                earnings_date_str = calendar['Earnings Date'][0]
                if isinstance(earnings_date_str, str) and 'to' in earnings_date_str:
                     earnings_date_str = earnings_date_str.split(' to ')[0]
                
                try:
                    earnings_date = pd.to_datetime(earnings_date_str).normalize()
                    if today <= earnings_date <= max_date:
                         earnings_data[ticker_symbol] = {
                             "earnings_date": earnings_date.strftime('%Y-%m-%d'),
                             "eps_estimate": calendar.get('Earnings Average', [None])[0],
                             "revenue_estimate": calendar.get('Revenue Average', [None])[0]
                         }
                         logger.info(f"Found upcoming earnings for {ticker_symbol} on {earnings_date.strftime('%Y-%m-%d')}")
                    else:
                         # Date is outside our lookahead window
                         earnings_data[ticker_symbol] = {"status": "No upcoming earnings date found within lookahead period"}
                except ValueError:
                    logger.warning(f"Could not parse earnings date '{earnings_date_str}' for {ticker_symbol}")
                    earnings_data[ticker_symbol] = {"status": f"Invalid date format found: {earnings_date_str}"}
                
            return earnings_data

        except Exception as e:
            logger.error(f"Error fetching earnings data using yfinance: {str(e)}", exc_info=True)
            return {"error": f"Failed to fetch earnings data: {str(e)}"}

    def get_sec_filings_data(self, tickers=None, filing_type="10-K", num_filings=1):
        """
        Fetch recent SEC filing metadata (e.g., 10-K) for specified tickers.

        Args:
            tickers (list): List of company stock tickers. Defaults to a sample list.
            filing_type (str): Type of SEC filing (e.g., "10-K", "10-Q", "8-K"). Defaults to "10-K".
            num_filings (int): Number of recent filings per ticker to fetch. Defaults to 1.

        Returns:
            dict: Dictionary containing filing metadata (URL, date) for each ticker.
                  Returns an error message if fetching fails or API key is missing.
        """
        logger.info(f"Fetching {filing_type} data for tickers: {tickers}")
        if self.query_api is None:
            return {"error": "SEC API key not configured. Cannot fetch filings."}
            
        if tickers is None:
            # TODO: Decide on a default list or make required
            tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'] 

        filings_data = {}
        try:
            for ticker_symbol in tickers:
                query = {
                    "query": { "query_string": { 
                        "query": f"ticker:{ticker_symbol} AND formType:\"{filing_type}\"" 
                    }}, 
                    "from": "0", 
                    "size": str(num_filings), 
                    "sort": [{ "filedAt": { "order": "desc" }}]
                }
                
                response = self.query_api.get_filings(query)
                
                if response and response.get('filings'):
                    ticker_filings = []
                    for filing in response['filings']:
                        ticker_filings.append({
                            "filedAt": filing.get('filedAt'),
                            "linkToFilingDetails": filing.get('linkToFilingDetails'),
                            # Add other relevant fields if needed, e.g., periodOfReport
                        })
                    filings_data[ticker_symbol] = ticker_filings
                    logger.info(f"Found {len(ticker_filings)} {filing_type} filings for {ticker_symbol}")
                else:
                    logger.warning(f"No recent {filing_type} filings found for {ticker_symbol}")
                    filings_data[ticker_symbol] = {"status": f"No recent {filing_type} filings found"}

            return filings_data

        except Exception as e:
            logger.error(f"Error fetching SEC filings data using sec-api: {str(e)}", exc_info=True)
            return {"error": f"Failed to fetch SEC filings data: {str(e)}"}

    def get_financial_news(self, keywords=None, num_articles=5, language='en', sort_by='relevancy'):
        """
        Fetch recent financial news articles relevant to the equities market.

        Args:
            keywords (str): Keywords or query to search for (e.g., "stock market", "AAPL earnings"). Defaults to general terms.
            num_articles (int): Number of articles to fetch. Defaults to 5.
            language (str): Language of articles. Defaults to 'en'.
            sort_by (str): How to sort articles ('relevancy', 'popularity', 'publishedAt'). Defaults to 'relevancy'.

        Returns:
            dict: Dictionary containing news articles (title, source, url, summary).
                  Returns an error message if fetching fails or API key is missing.
        """
        logger.info(f"Fetching financial news for keywords: {keywords}")
        if self.news_api is None:
            return {"error": "NewsAPI key not configured. Cannot fetch news."}

        if keywords is None:
            keywords = "stock market OR equities OR corporate earnings OR Wall Street" # Broad default query

        news_data = {}
        try:
            # Fetch top headlines or everything based on keywords
            # Using 'everything' endpoint for broader search based on keywords
            all_articles = self.news_api.get_everything(
                q=keywords,
                language=language,
                sort_by=sort_by,
                page_size=num_articles # Fetch requested number
            )

            if all_articles['status'] == 'ok' and all_articles['articles']:
                articles_summary = []
                for article in all_articles['articles']:
                    articles_summary.append({
                        "title": article.get('title'),
                        "source": article.get('source', {}).get('name'),
                        "url": article.get('url'),
                        "publishedAt": article.get('publishedAt'),
                        "summary": article.get('description') # Use description as a brief summary
                    })
                news_data['articles'] = articles_summary
                logger.info(f"Found {len(articles_summary)} relevant news articles.")
            else:
                logger.warning(f"No news articles found for keywords: {keywords}. Status: {all_articles.get('status')}")
                news_data = {"status": f"No articles found (Status: {all_articles.get('status')})"}

            return news_data

        except NewsAPIException as e: # Corrected exception name
             # Handle API specific errors (e.g., invalid key, rate limits)
             logger.error(f"NewsAPI specific error: {str(e)}", exc_info=True)
             # Return a slightly more informative error message if possible
             error_detail = str(e)
             if hasattr(e, 'get_message'): # Method in some versions
                  error_detail = e.get_message()
             return {"error": f"Failed to fetch financial news (NewsAPI Error): {error_detail}"}

        except Exception as e:
            # Handle potential NewsApiException explicitly if needed
            logger.error(f"Error fetching financial news using NewsAPI: {str(e)}", exc_info=True)
            return {"error": f"Failed to fetch financial news: {str(e)}"}

    # --- Placeholder Method for Analysis ---
    def analyze_equities(self, market_data, filings_data, news_data):
        """Placeholder: Analyze the collected equities data."""
        logger.info("Analyzing equities data...")
        # TODO: Format data and potentially use self.agent for preliminary analysis or synthesis
        return {"analysis": "Equities analysis not implemented"}

    # --- Main Run Method ---
    def run(self, task=None):
        """
        Run the Equities Agent to analyze the stock market and generate insights.
        
        Args:
            task: Specific analysis task (optional, e.g., "Focus on tech sector performance")
            
        Returns:
            str: Equities market analysis and insights
        """
        try:
            logger.info(f"Running EquitiesAgent with task: {task}")
            # 1. Fetch Data
            # TODO: Potentially pass specific indices/sectors/tickers based on task
            market_data = self.get_market_data()
            earnings_data = self.get_earnings_data() # Fetch earnings for default list for now
            filings_data = self.get_sec_filings_data() # Fetch 10-Ks for default list
            news_data = self.get_financial_news() # Fetch general financial news

            # --- Prepare data summaries for the prompt --- 
            # Create a concise summary of market data, excluding bulky historical data
            market_data_prompt_summary = {}
            for symbol, data in market_data.items():
                if symbol == '_summary': # Skip the internal summary key
                    continue 
                if isinstance(data, dict) and 'info' in data: # Check if it's valid ticker data
                     market_data_prompt_summary[symbol] = {
                         'info': data.get('info'),
                         'last_close': data.get('last_close'),
                         'period_change_pct': data.get('period_change_pct')
                     }
                else:
                     # Include errors or other non-standard entries
                     market_data_prompt_summary[symbol] = data 

            # Extract summaries for the prompt to avoid excessive length
            # market_summary = {k: v for k, v in market_data.items() if k == '_summary' or isinstance(v.get('historical_data'), dict) == False}
            sector_ranking = market_data.get('_summary',{}).get('sector_performance_ranking', 'Not available')
            earnings_summary = earnings_data # Keep as is for now
            filings_summary = filings_data # Keep as is for now
            news_summary = news_data.get('articles', 'Not available') # Extract just the articles list or status

            # 2. Format Data for LLM 
            # TODO: Improve formatting, possibly summarize historical data before sending
            prompt = f"""
            Please analyze the following equities market data and provide insights:
            
            Market Index & Sector ETF Overview (1mo Period):
            {market_data_prompt_summary}
            
            Sector Performance Ranking (1mo):
            {sector_ranking}

            Upcoming Earnings (next 7 days for sample tickers):
            {earnings_summary}
            
            Recent SEC Filings Insights (Latest 10-K):
            {filings_summary}
            
            Relevant Financial News Summaries:
            {news_summary}
            
            Based on this data, provide a comprehensive analysis of the current equities market situation. 
            Focus on:
            - Major index trends (S&P 500, Nasdaq, Dow Jones).
            - Key performing (leading/lagging) sectors and potential reasons.
            - Notable upcoming earnings and their potential significance.
            - Insights from recent SEC filings (if available).
            - Impact of recent financial news.
            - Overall market sentiment and outlook.
            - {task if task else "Provide a general equities market overview"}
            """
            
            # 3. Run the internal Swarms Agent
            response = self.agent.run(prompt)
            
            # 4. Process the response (similar to MacroAgent)
            analysis = ""
            if isinstance(response, dict):
                # Adapt based on actual Swarms Agent response structure
                analysis = response.get("response") or response.get("output") or response.get("result", "") 
                if not analysis:
                     for key, value in response.items():
                        if isinstance(value, str) and len(value) > 50: # Heuristic
                            analysis = value
                            break
            elif isinstance(response, str):
                analysis = response
                
            # Clean up
            if analysis.endswith("<DONE>"):
                analysis = analysis[:-6].strip()
                
            if not analysis:
                logger.warning("EquitiesAgent internal agent did not return a valid analysis.")
                return "The EquitiesAgent was unable to generate a proper analysis. Please check the logs."
                
            logger.info("EquitiesAgent analysis generated successfully.")
            return analysis
            
        except Exception as e:
            logger.error(f"Error running Equities Agent: {str(e)}", exc_info=True)
            return f"Error analyzing equities market data: {str(e)}"
