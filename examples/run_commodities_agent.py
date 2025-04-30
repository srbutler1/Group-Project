#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script to demonstrate the CommoditiesAgent functionality.

This script initializes the CommoditiesAgent and runs it to generate
a comprehensive analysis of commodity markets including metals, energy,
and agricultural products.
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

from economic_summary.agents.commodities import run_commodities_agent

def main():
    """Run the CommoditiesAgent example."""
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting CommoditiesAgent example")
    
    # Run the commodities agent
    task = "Analyze the current state of commodity markets, focusing on energy, metals, and agricultural products. Identify key trends and their implications for the broader economy."
    result = run_commodities_agent(task)
    
    # Print the result
    print("\n" + "="*80)
    print("COMMODITIES MARKET ANALYSIS")
    print("="*80)
    print(result)
    print("="*80)
    
    logger.info("CommoditiesAgent example completed")

if __name__ == "__main__":
    main()
