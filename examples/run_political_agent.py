#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script to demonstrate the PoliticalNewsAgent functionality.

This script initializes the PoliticalNewsAgent and runs it to generate
a comprehensive analysis of political news and their economic implications.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from economic_summary.agents.political import run_political_agent

def main():
    """Run the PoliticalNewsAgent example."""
    # Load environment variables
    load_dotenv()
    
    print("\n" + "=" * 80)
    print("=" * 30 + " POLITICAL NEWS AGENT DEMONSTRATION " + "=" * 30)
    print("=" * 80)
    print("This example demonstrates the PoliticalNewsAgent's ability to analyze")
    print("political news and their economic implications.")
    
    print("\n" + "=" * 80)
    print("=" * 35 + " POLITICAL NEWS ANALYSIS " + "=" * 35)
    print("=" * 80)
    
    # Run the political agent
    analysis = run_political_agent(
        "Analyze recent political news and government policies, focusing on their "
        "potential impact on financial markets, economic growth, and specific sectors "
        "of the economy. Identify key political risks and opportunities for investors."
    )
    
    print(analysis)
    
    print("\n" + "=" * 80)
    print("=" * 35 + " DEMONSTRATION COMPLETE " + "=" * 35)
    print("=" * 80)
    print("The PoliticalNewsAgent has successfully analyzed political news and their economic implications.")

if __name__ == "__main__":
    main()
