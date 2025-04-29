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

## Folder Structure

The project follows the recommended Swarms framework architecture with the following structure:

```
economic_summary/
├── __init__.py                  # Package initialization
├── agents/                      # Domain-specific agents
│   ├── __init__.py              # Agent module initialization
│   ├── aggregator/              # Aggregator agent (Sam)
│   ├── commodities/             # Commodities agent (Jake)
│   ├── equities/                # Equities agent (Himanshu)
│   ├── fixed_income/            # Fixed Income agent (Thomas)
│   ├── macro/                   # Macro agent (Sam)
│   └── political/               # Political news agent (Zach)
├── config/                      # Configuration files
│   └── __init__.py              # Config module initialization
├── data/                        # Data storage and processing
│   └── .gitkeep                 # Placeholder for empty directory
├── models/                      # Model definitions
│   └── .gitkeep                 # Placeholder for empty directory
├── tests/                       # Test files
│   └── .gitkeep                 # Placeholder for empty directory
└── utils/                       # Utility functions
    └── .gitkeep                 # Placeholder for empty directory
```

### Key Components

1. **Agents Directory**: Contains all domain-specific agents and the aggregator agent. Each agent is responsible for a specific economic domain and follows the Swarms Agent architecture.

2. **Config Directory**: Stores configuration files for API keys, model parameters, and other settings.

3. **Data Directory**: Used for data storage, processing, and caching. This includes financial data, news articles, and other information needed by the agents.

4. **Models Directory**: Contains model definitions and custom model implementations if needed.

5. **Utils Directory**: Houses utility functions for data processing, API interactions, and other common tasks.

6. **Tests Directory**: Contains test files for ensuring the reliability of the system.

## Features

### Macroeconomic Analysis
- Retrieves and analyzes key economic indicators from FRED
- Assesses recession risk based on yield curve and other factors
- Monitors recent economic reports from major sources
- **NEW: Analyzes important economic reports** - Automatically identifies and analyzes the most important recent economic reports that may impact the economy

### Aggregation and Synthesis
- Combines insights from all domain agents
- Identifies connections between different economic domains
- Prioritizes significant trends and provides a balanced outlook

## Architecture Implementation

The Economic Summary Swarm Agent System implements the Mixture of Agents (MoA) architecture from the Swarms framework. Here's how the components work together:

### 1. Agent Design

Each domain agent follows the Swarms agent architecture:

```
┌─────────────────────────────────────────┐
│                 Agent                   │
├─────────────────────────────────────────┤
│ 1. Task Initiation                      │
│    - Receives economic data query       │
│                                         │
│ 2. Initial LLM Processing               │
│    - Interprets task requirements       │
│    - Plans data collection strategy     │
│                                         │
│ 3. Tool Usage                           │
│    - Calls domain-specific APIs         │
│    - Retrieves relevant data            │
│                                         │
│ 4. Memory Interaction                   │
│    - Stores/retrieves historical data   │
│    - Uses RAG for context enhancement   │
│                                         │
│ 5. Final LLM Processing                 │
│    - Analyzes collected data            │
│    - Generates domain-specific summary  │
└─────────────────────────────────────────┘
```

### 2. MoA Workflow

The Mixture of Agents architecture follows a parallel → sequential → parallel → final output process:

```
┌─────────────────────────────────────────────────────────────────┐
│                  MixtureOfAgents Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 1: Parallel Agent Execution                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│  │Equities │   │Fixed    │   │Macro    │   │Commod.  │   ...    │
│  │Agent    │   │Income   │   │Agent    │   │Agent    │          │
│  └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘          │
│       │             │             │             │               │
│       └─────────────┼─────────────┼─────────────┘               │
│                     │             │                             │
│  Layer 2: Sequential Processing   │                             │
│                     │             │                             │
│       ┌─────────────┼─────────────┼─────────────┐               │
│       │             │             │             │               │
│  Layer 3: Parallel Agent Execution                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│  │Equities │   │Fixed    │   │Macro    │   │Commod.  │   ...    │
│  │Agent    │   │Income   │   │Agent    │   │Agent    │          │
│  └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘          │
│       │             │             │             │               │
│       └─────────────┼─────────────┼─────────────┘               │
│                     │                                           │
│  Final Aggregator Agent                                         │
│  ┌─────────────────────────────────┐                            │
│  │Aggregator Agent                 │                            │
│  │- Synthesizes all domain insights│                            │
│  │- Produces final economic summary│                            │
│  └─────────────────────────────────┘                            │
│                     │                                           │
│  ┌─────────────────┴─────────────────┐                          │
│  │         Economic Summary          │                          │
│  └───────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Implementation Flow

1. **Initialization**: The system initializes all domain agents with their specific system prompts and configurations.

2. **Layer 1 - Initial Data Collection**: All domain agents run in parallel to collect and analyze data from their respective domains.

3. **Layer 2 - Intermediate Processing**: Sequential processing of initial results to identify interdependencies and cross-domain impacts.

4. **Layer 3 - Refined Analysis**: Domain agents run again in parallel with enhanced context from other domains to refine their analyses.

5. **Final Aggregation**: The Aggregator Agent combines all domain insights into a comprehensive economic summary.

### 4. Agent Communication

Agents communicate through the MixtureOfAgents orchestration:

1. **Conversation History**: Each agent's output is added to a shared conversation history.

2. **Context Preservation**: Important context is preserved between agent runs using the conversation history.

3. **Metadata Tracking**: The system tracks metadata about each agent's run, including timing, inputs, and outputs.

### 5. Data Flow

```
┌───────────┐     ┌───────────┐     ┌───────────┐
│           │     │           │     │           │
│  External │     │  Domain   │     │ Aggregator│
│   Data    │────▶│  Agents   │────▶│   Agent   │
│  Sources  │     │           │     │           │
│           │     │           │     │           │
└───────────┘     └───────────┘     └───────────┘
                                         │
                                         ▼
                                   ┌───────────┐
                                   │ Economic  │
                                   │  Summary  │
                                   │  Report   │
                                   └───────────┘
```

This architecture follows the Swarms framework best practices for building complex multi-agent systems, with a focus on modularity, scalability, and effective agent collaboration.

## Current Status and Next Steps

### Current Implementation Status

- ✅ **Project Structure**: Established the folder structure following Swarms best practices
- ✅ **Macro Agent**: Implemented with FRED API integration for economic indicators and reports
- ✅ **Aggregator Agent**: Implemented with the ability to synthesize insights from domain agents
- ✅ **Economic Summary Swarm**: Implemented using the MixtureOfAgents architecture
- ✅ **Configuration Utilities**: Implemented for API keys and environment variables
- ✅ **Example Scripts**: Created to demonstrate the functionality of individual agents and the full swarm

### Next Steps: Implementing Additional Domain Agents

To complete the Economic Summary Swarm Agent System, the following domain agents need to be implemented:

#### 1. Equities Agent

1. **Create the basic structure**:
   ```bash
   mkdir -p economic_summary/agents/equities
   touch economic_summary/agents/equities/__init__.py
   touch economic_summary/agents/equities/equities_agent.py
   ```

2. **Implement the EquitiesAgent class**:
   - Use the MacroAgent as a template
   - Integrate with Yahoo Finance API (yfinance) for stock market data
   - Implement methods for analyzing major indices, sector performance, and earnings reports
   - Create a run method that generates insights about the equities market

#### 2. Fixed Income Agent

1. **Create the basic structure**:
   ```bash
   mkdir -p economic_summary/agents/fixed_income
   touch economic_summary/agents/fixed_income/__init__.py
   touch economic_summary/agents/fixed_income/fixed_income_agent.py
   ```

2. **Implement the FixedIncomeAgent class**:
   - Use the MacroAgent as a template
   - Integrate with FRED API for yield curve and interest rate data
   - Implement methods for analyzing bond markets, yield spreads, and credit conditions
   - Create a run method that generates insights about fixed income markets

#### 3. Commodities Agent

1. **Create the basic structure**:
   ```bash
   mkdir -p economic_summary/agents/commodities
   touch economic_summary/agents/commodities/__init__.py
   touch economic_summary/agents/commodities/commodities_agent.py
   ```

2. **Implement the CommoditiesAgent class**:
   - Use the MacroAgent as a template
   - Integrate with commodity price APIs (e.g., Yahoo Finance for commodity futures)
   - Implement methods for analyzing energy, metals, and agricultural commodities
   - Create a run method that generates insights about commodity markets

#### 4. Political News Agent

1. **Create the basic structure**:
   ```bash
   mkdir -p economic_summary/agents/political
   touch economic_summary/agents/political/__init__.py
   touch economic_summary/agents/political/political_agent.py
   ```

2. **Implement the PoliticalAgent class**:
   - Use the MacroAgent as a template
   - Integrate with news APIs (e.g., NewsAPI) for political and economic news
   - Implement methods for analyzing policy developments and geopolitical events
   - Create a run method that generates insights about political factors affecting the economy

### Integration Steps

Once all domain agents are implemented, follow these steps to integrate them into the Economic Summary Swarm:

1. **Update the main example script**:
   ```python
   from economic_summary.agents.macro import MacroAgent
   from economic_summary.agents.equities import EquitiesAgent
   from economic_summary.agents.fixed_income import FixedIncomeAgent
   from economic_summary.agents.commodities import CommoditiesAgent
   from economic_summary.agents.political import PoliticalAgent
   from economic_summary.agents.aggregator import EconomicSummarySwarm

   # Create all domain agents
   domain_agents = {
       'macro': MacroAgent(),
       'equities': EquitiesAgent(),
       'fixed_income': FixedIncomeAgent(),
       'commodities': CommoditiesAgent(),
       'political': PoliticalAgent()
   }

   # Create the Economic Summary Swarm
   swarm = EconomicSummarySwarm(domain_agents)

   # Run the swarm with MoA architecture
   task = "Generate a comprehensive economic summary with insights from all domains"
   result = swarm.run_with_moa(task)
   
   print(result)
   ```

2. **Test each agent individually** before integrating them into the swarm

3. **Refine the Aggregator Agent's system prompt** to better handle insights from all domains

4. **Add unit tests** for each agent and the full swarm

### Environment Setup

Before running the system, ensure you have:

1. **API Keys**: Add the following to your `.env` file in the project root directory (create the file if it doesn't exist):
   ```dotenv
   # Required for core LLM functionality
   OPENAI_API_KEY=your_openai_api_key
   
   # Required for MacroAgent (uses FRED Data)
   FRED_API_KEY=your_fred_api_key 
   
   # Required for EquitiesAgent (uses NewsAPI)
   NEWS_API_KEY=your_news_api_key

   # Required for EquitiesAgent (uses sec-api.io for filings)
   SEC_API_KEY=your_sec_api_key
   ```
   *(Note: The system uses `python-dotenv` to load these keys. Ensure your keys are obtained from the respective service providers.)*

2. **Dependencies**: Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Virtual Environment**: Use a virtual environment to isolate dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### Additional Enhancements

Once the basic system is working, consider these enhancements:

1. **Memory Integration**: Add long-term memory to agents for tracking historical trends
2. **Visualization**: Generate charts and graphs to accompany the economic summary
3. **Scheduled Runs**: Implement automated daily/weekly economic reports
4. **User Interface**: Create a simple web interface for viewing economic summaries
5. **Notification System**: Send alerts for significant economic developments

By following these steps, you'll complete the Economic Summary Swarm Agent System with all domain agents working together through the Swarms MoA architecture to generate comprehensive economic analyses.

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
