import os
from datetime import datetime, timedelta
from typing import Dict, List
import requests
from newsapi import NewsApiClient
from swarm_models import OpenAIChat
from tenacity import retry, stop_after_attempt, wait_fixed
from fredapi import Fred

class PoliticalNewsAgent:
    def __init__(self, api_keys: Dict[str, str]):
        """
        Simplified Political News Agent: fetches political/economic news from NewsAPI and Federal Register, then summarizes using OpenAI.
        Args:
            api_keys: Dict with 'newsapi' and 'openai' keys.
        """
        self.newsapi = NewsApiClient(api_key=api_keys.get("newsapi"))
        self.llm = OpenAIChat(api_key=api_keys.get("openai"))

    def fetch_newsapi(self, query: str = "politics OR government OR regulation", days_back: int = 3) -> List[Dict]:
        """Fetch recent political/economic news from NewsAPI."""
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        try:
            response = self.newsapi.get_everything(
                q=query + " -sports -entertainment",
                from_param=from_date,
                to=to_date,
                language="en",
                sort_by="relevancy",
                page_size=30,
                sources="reuters,bbc-news,financial-times,bloomberg,the-economist"
            )
            return response.get("articles", [])
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []

    def fetch_federal_register(self, query: str = "economic sanctions OR trade regulations OR fiscal policy", limit: int = 10) -> List[Dict]:
        """Fetch recent US government policy announcements from Federal Register."""
        try:
            url = f"https://www.federalregister.gov/api/v1/documents.json?conditions[term]={query.replace(' OR ', '+')}&per_page={limit}"
            response = requests.get(url)
            response.raise_for_status()
            documents = response.json().get("results", [])
            return [
                {"title": doc["title"], "description": doc.get("abstract", ""), "url": doc.get("html_url", "")}
                for doc in documents
            ]
        except Exception as e:
            print(f"Federal Register error: {e}")
            return []

    def summarize(self, articles: List[Dict], max_articles: int = 10) -> str:
        """Summarize a list of articles using OpenAI."""
        if not articles:
            return "No news articles found."
        # Prepare context for LLM
        context = "\n\n".join([
            f"Title: {a['title']}\nDescription: {a.get('description', '')}" for a in articles[:max_articles]
        ])
        prompt = (
            "Analyze the following political and economic news articles. "
            "Summarize the key events and their economic implications in 200-300 words.\n\n" + context
        )
        return self.llm(prompt)

    def run(self, query: str = "politics OR government OR regulation", days_back: int = 3) -> str:
        """Fetch and summarize political/economic news from NewsAPI and Federal Register."""
        newsapi_articles = self.fetch_newsapi(query=query, days_back=days_back)
        fedreg_articles = self.fetch_federal_register()
        all_articles = newsapi_articles + fedreg_articles
        return self.summarize(all_articles)

if __name__ == "__main__":
    # Example CLI usage
    api_keys = {
        "newsapi": os.getenv("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY_HERE"),
        "openai": os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY_HERE")
    }
    agent = PoliticalNewsAgent(api_keys)
    summary = agent.run()
    print("\n--- Political News Summary ---\n")
    print(summary)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_fred_data(self, series_id: str = "CPIAUCSL", observation_start: str = "2025-01-01") -> List[Dict]:
        """Fetch macroeconomic indicators from FRED."""
        cached = self.get_cached_articles(f"fred_{series_id}")
        if cached:
            return cached
        try:
            fred = Fred(api_key=self.api_keys.get("fred"))
            data = fred.get_series(series_id, observation_start=observation_start)
            articles = [{"date": str(index), "value": value, "indicator": series_id} for index, value in data.items()]
            self.cache_articles([{"title": f"{series_id} {d['date']}", "description": str(d["value"]), "url": ""} for d in articles], f"fred_{series_id}")
            return articles
        except Exception as e:
            print(f"FRED error for {series_id}: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_sec_filings(self, ticker: str, form_type: str = "10-K") -> List[Dict]:
        """Fetch SEC filings with political risk mentions."""
        cached = self.get_cached_articles(f"sec_{ticker}")
        if cached:
            return cached
        try:
            query_api = QueryApi(api_key=self.api_keys.get("sec"))
            query = {
                "query": f"ticker:{ticker} AND formType:{form_type} AND (political OR regulation OR policy)",
                "from": "2024-01-01",
                "size": 5
            }
            filings = query_api.get_filings(query)
            articles = [
                {"title": f"{filing['companyName']} {form_type}", "description": filing.get("description", ""), "url": filing.get("linkToFilingDetails", "")}
                for filing in filings["filings"]
            ]
            self.cache_articles(articles, f"sec_{ticker}")
            return articles
        except Exception as e:
            print(f"SEC API error for {ticker}: {e}")
            return []

    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title."""
        seen_titles = set()
        unique_articles = []
        for article in articles:
            title = article["title"].lower()
            if title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        return unique_articles

    def fetch_news(self, query: str = "economic policy OR trade policy OR fiscal policy OR sanctions OR regulation",
                   from_date: str = "2025-04-20", to_date: str = "2025-04-27") -> List[Dict]:
        """
        Fetch data from all sources.
        
        Args:
            query: Search query for NewsAPI and Federal Register.
            from_date: Start date for news.
            to_date: End date for news.
        
        Returns:
            List of articles and data points.
        """
        articles = []

        # NewsAPI for political news
        articles.extend(self.fetch_newsapi(query, from_date, to_date))

        # Federal Register for government policies and regulations
        articles.extend(self.fetch_federal_register(query))

        # FinancialDatasets for company-specific news (selective)
        tickers = ["XOM", "TSLA", "NVDA"]  # Focus on politically sensitive sectors
        for ticker in tickers:
            articles.extend(self.fetch_financial_news(ticker, limit=5))

        # Yahoo Finance for market news (selective)
        for ticker in tickers:
            articles.extend(self.fetch_yahoo_news(ticker))

        # SEC Filings for regulatory risks
        for ticker in tickers:
            articles.extend(self.fetch_sec_filings(ticker))

        # FRED for macro indicators (selective)
        fred_indicators = ["CPIAUCSL"]  # Focus on inflation
        for series_id in fred_indicators:
            articles.extend(self.fetch_fred_data(series_id))

        return self.deduplicate_articles(articles)

    def analyze_news(self, articles: List[Dict]) -> str:
        """
        Analyze fetched data and generate a summary.
        
        Args:
            articles: List of articles and data points.
        
        Returns:
            Summary of political news with economic implications.
        """
        if not articles:
            return "No relevant political news found for the specified period."

        context = "Recent political, financial, and macroeconomic data:\n"
        for article in articles[:15]:  # Limit to top 15 for brevity
            context += f"- {article['title']}: {article.get('description', '')}\n"

        task = (
            f"Analyze the following data and generate a concise summary (200-300 words) "
            f"focusing on the economic implications of political events and policies:\n{context}"
        )
        return self.agent.run(task)

    def run(self, task: str = "Analyze political news with economic implications for the current week") -> str:
        """
        Run the Political News Agent.
        
        Args:
            task: Task description.
        
        Returns:
            Summary of political news.
        """
        articles = self.fetch_news()
        return self.analyze_news(articles)
