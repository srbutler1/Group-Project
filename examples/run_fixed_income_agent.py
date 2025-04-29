#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script to demonstrate the FixedIncomeAgent functionality.

This script initializes the FixedIncomeAgent and runs it to generate
a comprehensive fixed income market analysis.
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

from economic_summary.agents.fixed_income import run_fixed_income_agent

def main():
    """Run the FixedIncomeAgent example."""
    # Load environment variables
    load_dotenv()
    
    print("\n" + "=" * 80)
    print("=" * 30 + " FIXED INCOME AGENT DEMONSTRATION " + "=" * 30)
    print("=" * 80)
    print("This example demonstrates the FixedIncomeAgent's ability to analyze")
    print("Treasury yields, corporate bonds, high-yield bonds, and municipal bonds.")
    
    print("\n" + "=" * 80)
    print("=" * 35 + " FIXED INCOME ANALYSIS " + "=" * 35)
    print("=" * 80)
    
    # Run the fixed income agent
    analysis = run_fixed_income_agent(
        "Provide a comprehensive analysis of the current fixed income market, "
        "with particular attention to Treasury yields, corporate bonds, "
        "high-yield bonds, and municipal bonds. Explain the implications "
        "for investors and the broader economy."
    )
    
    print(analysis)
    
    print("\n" + "=" * 80)
    print("=" * 35 + " DEMONSTRATION COMPLETE " + "=" * 35)
    print("=" * 80)
    print("The FixedIncomeAgent has successfully analyzed the fixed income market.")

if __name__ == "__main__":
    main()
