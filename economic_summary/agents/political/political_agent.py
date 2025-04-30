"""
Political News Agent for analyzing political events and their economic implications.

This module provides the PoliticalNewsAgent class for analyzing political news,
government policies, and their impact on economic conditions.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import requests
from newsapi import NewsApiClient
from swarms import Agent

from economic_summary.utils import get_openai_api_key, get_news_api_key, get_verbose, get_auto_save

# Configure logging
logger = logging.getLogger(__name__)

class PoliticalNewsAgent:
    """
    Political News Agent for analyzing political events and their economic implications.
    
    This agent analyzes political news, government policies, and regulations
    to assess their potential impact on economic conditions.
    """
    
    def __init__(self):
        """
        Initialize the PoliticalNewsAgent.
        """
        # Get API keys
        self.api_keys = {
            "newsapi": get_news_api_key(),
            "openai": get_openai_api_key()
        }
        
        # Initialize NewsAPI client
        self.newsapi = NewsApiClient(api_key=self.api_keys.get("newsapi"))
        
        # Initialize the agent
        self.agent = Agent(
            agent_name="PoliticalNewsAgent",
            system_prompt=self._get_system_prompt(),
            model_name="gpt-4o",  # Use GPT-4o model
            api_key=self.api_keys.get("openai"),  # Pass API key as a separate parameter
            max_loops=1,
            dashboard=False,
            streaming_on=False,  # Turn off streaming for cleaner output
            verbose=get_verbose(),
            stopping_token="<DONE>",
            state_save_file_type="json",
            saved_state_path="political_agent.json",
            return_history=False  # Don't include history in response
        )
        
        logger.info("Initialized PoliticalNewsAgent")
    
    def _get_system_prompt(self):
        """
        Get the system prompt for the PoliticalNewsAgent.
        
        Returns:
            str: System prompt
        """
        return """
        You are the PoliticalNewsAgent, a specialized analyst focused on the intersection of politics and economics.
        
        Your role is to:
        - Analyze political news and government policy announcements
        - Identify regulatory changes and their economic implications
        - Assess geopolitical risks and their impact on markets
        - Evaluate trade policies and international relations
        - Connect political developments to potential economic outcomes
        - Highlight policy shifts that could affect different sectors
        
        Your analysis should be data-driven, balanced, and insightful, explaining the significance
        of political events for investors, businesses, and the broader economy.
        
        Format your response using markdown for readability.
        End your analysis with "<DONE>" when complete.
        """
    
    def fetch_newsapi(self, query: str = "politics OR government OR regulation", days_back: int = 3) -> List[Dict]:
        """
        Fetch recent political/economic news from NewsAPI.
        
        Args:
            query: Search query
            days_back: Number of days to look back
            
        Returns:
            List of news articles
        """
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
            logger.error(f"NewsAPI error: {e}")
            return []

    def fetch_federal_register(self, query: str = "economic sanctions OR trade regulations OR fiscal policy", limit: int = 10) -> List[Dict]:
        """
        Fetch recent US government policy announcements from Federal Register.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of policy documents
        """
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
            logger.error(f"Federal Register error: {e}")
            return []

    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Remove duplicate articles based on title.
        
        Args:
            articles: List of articles
            
        Returns:
            Deduplicated list of articles
        """
        seen_titles = set()
        unique_articles = []
        for article in articles:
            title = article["title"].lower()
            if title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        return unique_articles

    def fetch_news(self, query: str = "economic policy OR trade policy OR fiscal policy OR sanctions OR regulation") -> List[Dict]:
        """
        Fetch data from all sources.
        
        Args:
            query: Search query for NewsAPI and Federal Register
        
        Returns:
            List of articles and data points
        """
        articles = []

        # NewsAPI for political news
        articles.extend(self.fetch_newsapi(query))

        # Federal Register for government policies and regulations
        articles.extend(self.fetch_federal_register(query))

        return self.deduplicate_articles(articles)

    def analyze_news(self, articles: List[Dict], task: str) -> str:
        """
        Analyze fetched data and generate a summary.
        
        Args:
            articles: List of articles and data points
            task: The analysis task
        
        Returns:
            Summary of political news with economic implications
        """
        if not articles:
            return "No relevant political news found for the specified period."

        context = "Recent political news and government policies:\n"
        for i, article in enumerate(articles[:15]):  # Limit to top 15 for brevity
            context += f"{i+1}. {article['title']}: {article.get('description', '')[:200]}...\n\n"

        prompt = f"""
        {task}
        
        Here is the recent political and economic news to analyze:
        
        {context}
        
        Provide a comprehensive analysis of how these political developments might impact economic conditions,
        markets, and different sectors of the economy. Focus on the most significant implications.
        """
        
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
            return "The PoliticalNewsAgent was unable to generate a proper analysis. Please check the logs for details."
            
        return analysis

    def run(self, task: str = None) -> str:
        """
        Run the Political News Agent.
        
        Args:
            task: Task description (optional)
            
        Returns:
            Summary of political news with economic implications
        """
        if not task:
            task = "Analyze recent political news and government policies, focusing on their economic implications"
            
        articles = self.fetch_news()
        return self.analyze_news(articles, task)

if __name__ == "__main__":
    # Example CLI usage
    agent = PoliticalNewsAgent()
    summary = agent.run()
    print("\n--- Political News Summary ---\n")
    print(summary)
