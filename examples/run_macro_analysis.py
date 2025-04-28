"""
Example script to run the Macro Agent and analyze macroeconomic data.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the MacroAgent
from economic_summary.agents.macro import MacroAgent

def main():
    """Run the Macro Agent to analyze macroeconomic data."""
    print("\n" + "="*80)
    print("Running Macro Agent Analysis".center(80))
    print("="*80 + "\n")
    
    # Initialize the Macro Agent
    print("Initializing Macro Agent...")
    macro_agent = MacroAgent()
    
    # Get economic indicators
    print("\n" + "-"*80)
    print("Economic Indicators:".center(80))
    print("-"*80)
    indicators = macro_agent.get_economic_indicators()
    print(indicators)
    
    # Get recession risk
    print("\n" + "-"*80)
    print("Recession Risk Assessment:".center(80))
    print("-"*80)
    recession_risk = macro_agent.get_recession_risk()
    print(recession_risk)
    
    # Get recent economic reports
    print("\n" + "-"*80)
    print("Recent Economic Reports:".center(80))
    print("-"*80)
    reports = macro_agent.get_recent_economic_reports()
    for source, source_reports in reports.items():
        print(f"\n{source.upper()} Reports:")
        for i, report in enumerate(source_reports[:3]):  # Show only top 3 per source
            print(f"{i+1}. {report.get('name', 'Unnamed Report')} - {report.get('date', 'No date')}")
            print(f"   Link: {report.get('link', 'No link')}")
    
    # NEW: Analyze important reports
    print("\n" + "-"*80)
    print("Analysis of Important Economic Reports:".center(80))
    print("-"*80)
    important_reports = macro_agent.analyze_important_reports(num_reports=2)
    
    if 'reports' in important_reports:
        for i, report in enumerate(important_reports['reports']):
            print(f"\nReport {i+1}: {report.get('name')} ({report.get('source').upper()})")
            print(f"Link: {report.get('link')}")
            print("\nAnalysis:")
            print(report.get('analysis', 'No analysis available'))
            print("-"*40)
    
    # Run the full analysis
    print("\n" + "="*80)
    print("Full Macroeconomic Analysis:".center(80))
    print("="*80 + "\n")
    analysis = macro_agent.run()
    print(analysis)
    
    print("\n" + "="*80)
    print("Macro Agent Analysis Complete".center(80))
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
