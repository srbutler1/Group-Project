import sys
import os

# Add the parent directory (your project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from economic_summary.agents.fixed_income.fixed_income_agent import FixedIncomeAgent

def main():
    agent = FixedIncomeAgent()
    summary = agent.run()
    print("\n--- Fixed Income Agent Summary ---")
    for key, value in summary.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
