# Economic Summary Swarm Agent System

## Overview

The Economic Summary Swarm Agent System is an AI-powered platform that generates comprehensive economic analyses by leveraging the [Swarms](https://docs.swarms.world/en/latest/) framework with a [Mixture of Agents (MoA)](https://docs.swarms.world/en/latest/swarms/structs/moa/) architecture. Each specialized agent focuses on a specific economic domain, analyzes relevant data, and contributes domain-specific insights. These insights are then aggregated to produce a holistic economic summary.

## Project Architecture

The project implements the Mixture of Agents (MoA) architecture from the Swarms framework, which follows a parallel → sequential → parallel → final output agent process as described in [this research paper](https://arxiv.org/pdf/2406.04692).

### Domain Agents

The system employs specialized agents for different economic domains:

- **Equities Agent**: Analyzes stock market trends, major indices, and corporate performance
- **Fixed Income Agent**: Examines bond markets, yield curves, and interest rate trends
- **Macro Agent**: Evaluates broad economic indicators like GDP, inflation, and employment
- **Commodities Agent**: Tracks commodity prices, supply/demand dynamics, and market trends
- **Political News Agent**: Analyzes political news with economic implications
- **Additional Domain Agents**: Can include FX, Real Estate, Crypto, etc.

Each domain agent:
1. Fetches data from relevant sources (APIs, news feeds, databases)
2. Analyzes trends and extracts insights within its domain
3. Generates a concise, structured summary of findings

### Aggregator Agent

The Aggregator Agent serves as the final_agent in the MoA architecture:
1. Collects summaries from all domain agents
2. Synthesizes information into a cohesive economic overview
3. Applies weighting and prioritization logic to highlight key insights
4. Produces the final economic summary report

### Orchestration Layer

The Swarm Controller orchestrates the entire process using the MoA framework:
1. Initializes domain agents with appropriate system prompts and configurations
2. Executes agents in parallel for initial data gathering and analysis
3. Processes intermediate results sequentially where needed
4. Runs final parallel processing before aggregation
5. Delivers the final report through designated channels (email, Slack, etc.)

## Implementation Details

```python
from swarms import MixtureOfAgents, Agent
from swarm_models import OpenAIChat

# Define domain-specific agents
equities_agent = Agent(
    agent_name="EquitiesAgent",
    system_prompt="Analyze stock market trends, major indices, and corporate performance",
    llm=OpenAIChat(),
    verbose=True
)

fixed_income_agent = Agent(
    agent_name="FixedIncomeAgent",
    system_prompt="Examine bond markets, yield curves, and interest rate trends",
    llm=OpenAIChat(),
    verbose=True
)

macro_agent = Agent(
    agent_name="MacroAgent",
    system_prompt="Evaluate GDP, inflation, employment, and other economic indicators",
    llm=OpenAIChat(),
    verbose=True
)

commodities_agent = Agent(
    agent_name="CommoditiesAgent",
    system_prompt="Track commodity prices, supply/demand dynamics, and market trends",
    llm=OpenAIChat(),
    verbose=True
)

political_agent = Agent(
    agent_name="PoliticalAgent",
    system_prompt="Analyze political news with economic implications",
    llm=OpenAIChat(),
    verbose=True
)

# Define the aggregator agent
aggregator_agent = Agent(
    agent_name="AggregatorAgent",
    system_prompt="Synthesize domain-specific insights into a comprehensive economic summary",
    llm=OpenAIChat(),
    verbose=True
)

# Initialize the MixtureOfAgents
economic_swarm = MixtureOfAgents(
    agents=[equities_agent, fixed_income_agent, macro_agent, commodities_agent, political_agent],
    final_agent=aggregator_agent,
    verbose=True,
    auto_save=True
)

# Run the swarm
economic_summary = economic_swarm.run(task="Generate a comprehensive economic summary based on current data.")

## Setup and Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- SEC API key (for financial filings data)
- Fin Data API key (for financial data)
- FRED API key (for macroeconomic data)
- Access to relevant financial data APIs

### Environment Setup

1. Clone the repository:
   ```
   git clone [repository-url]
   cd economic-summary-swarm
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure API keys:
   - Create a `config_api_keys` file in the project root
   - Add your OpenAI API key (must start with 'sk-')
   - Add your SEC API key (obtain from sec-api.io)
   - Add your Fin Data API key
   - Add your FRED API key
   - Add any other required API keys for data sources

4. Set up the OpenAI configuration:
   - Create an `OAI_CONFIG_LIST.json` file in the root directory
   - Format according to the template in the documentation

## Usage

### Running the System

To generate a complete economic summary:

```python
from economic_summary.main import run_economic_summary

# Generate and save the economic summary
summary = run_economic_summary()
print(summary)
```

For individual domain analyses:

```python
from economic_summary.agents import run_domain_agent

# Run specific domain agent
equities_summary = run_domain_agent(domain="equities")
fixed_income_summary = run_domain_agent(domain="fixed_income")
macro_summary = run_domain_agent(domain="macro")
commodities_summary = run_domain_agent(domain="commodities")
political_summary = run_domain_agent(domain="political")
```

### Scheduling

Set up scheduled runs using:
- Cron jobs (Linux/Mac)
- Windows Task Scheduler
- Cloud-based schedulers (AWS Lambda, Google Cloud Functions)

Example cron setup for weekly reports (Sundays at 6 PM):
```
0 18 * * 0 cd /path/to/project && python run_economic_summary.py
```

## Implementation Timeline

### Step 1
- Set up project repository and environment
- Install Swarms framework and dependencies
- Implement Equities Agent and Macro Agent
- Create basic data fetching mechanisms
- Establish prompt templates

### Step 2
- Implement Fixed Income and Commodities Agents
- Develop the Political News Agent
- Build the Aggregator Agent
- Configure the MixtureOfAgents architecture
- Implement initial error handling

### Step 3
- Enhance prompts and response quality
- Implement robust error handling and retries
- Add monitoring and logging
- Create deployment scripts
- Finalize documentation

### Step 4
- Testing and quality assurance
- Performance optimization
- User feedback integration
- Final deployment and handoff

## Team Roles and Responsibilities

| Team Member | Responsibility |
|-------------|----------------|
| Sam | Aggregator Agent/Macro-FRED Agent |
| Jake | Commodities Agent |
| Thomas | Fixed Income (Treasuries, etc.) |
| Himanshu | Equities Agent |
| Zach | Political News Agent - Specific to economic topics |

## Error Handling

The system implements robust error handling within the Swarms framework:
- Connection error management for API calls
- Graceful degradation when data sources are unavailable
- Fallback mechanisms for API key configuration
- Comprehensive logging for troubleshooting
- Reliability checks using the MixtureOfAgents' reliability_check method

## Data Sources

### Equities
- Yahoo Finance API
- SEC 10-K filings (most recent 3 years)
- Financial news aggregators

### Fixed Income
- Federal Reserve Economic Data (FRED)
- Treasury yield data
- Bond market indices

### Macro
- Bureau of Economic Analysis
- Bureau of Labor Statistics
- Consumer Price Index reports
- GDP releases

### Commodities
- Commodity exchanges data
- Energy Information Administration
- Agricultural reports

### Political News
- News APIs with economic filters
- Government policy announcements
- Regulatory updates

## API Reference

### Domain Agent Interface

```python
from swarms import Agent

def create_domain_agent(domain_name: str, system_prompt: str) -> Agent:
    """
    Create a domain-specific agent with appropriate configuration.
    
    Args:
        domain_name: Name of the economic domain
        system_prompt: Specialized prompt for the domain
        
    Returns:
        Configured Agent instance for the domain
    """
```

### MixtureOfAgents Interface

```python
from swarms import MixtureOfAgents, Agent
from typing import List, Dict

def create_economic_swarm(domain_agents: List[Agent], aggregator_agent: Agent) -> MixtureOfAgents:
    """
    Create a MixtureOfAgents swarm for economic analysis.
    
    Args:
        domain_agents: List of domain-specific agents
        aggregator_agent: Agent for final aggregation
        
    Returns:
        Configured MixtureOfAgents instance
    """
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify API keys are correctly formatted
   - Check network connectivity
   - Ensure API usage limits haven't been exceeded

2. **SEC Data Retrieval Issues**
   - Confirm SEC API key is valid
   - Verify ticker symbols are correct
   - Check if filing dates are within available range

3. **OpenAI API Errors**
   - Ensure API key starts with 'sk-'
   - Check for rate limiting or quota issues
   - Verify prompt formatting is correct

4. **Swarms Framework Issues**
   - Ensure you're using the latest version of the Swarms library
   - Check agent initialization parameters
   - Verify the MixtureOfAgents configuration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Resources

- [Swarms Documentation](https://docs.swarms.world/en/latest/)
- [Mixture of Agents Architecture](https://docs.swarms.world/en/latest/swarms/structs/moa/)
- [Research Paper: Mixture of Agents](https://arxiv.org/pdf/2406.04692)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [SEC-API Documentation](https://sec-api.io/docs)

## License

[Specify your license here]

## Acknowledgments

- Swarms framework for providing the MixtureOfAgents architecture
- OpenAI for providing the foundation models
- SEC-API.io for financial filing data access
- [Other acknowledgments as appropriate]
