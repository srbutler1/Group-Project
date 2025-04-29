"""
Macro Agent for analyzing macroeconomic indicators using FRED data.
"""

from economic_summary.agents.macro.macro_agent import MacroAgent

def run_macro_agent(task=None):
    """
    Run the Macro Agent to analyze macroeconomic data.
    
    Args:
        task: Specific analysis task (optional)
        
    Returns:
        str: Macroeconomic analysis
    """
    agent = MacroAgent()
    return agent.run(task)

__all__ = ['MacroAgent', 'run_macro_agent']
