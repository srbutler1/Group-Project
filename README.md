# Economic Summary Swarm Agent System

## Overview

The Economic Summary Swarm Agent System is an AI-powered platform that generates comprehensive economic analyses by leveraging multiple specialized domain agents. Each agent focuses on a specific economic sector, analyzes relevant data, and contributes domain-specific insights. These insights are then aggregated to produce a holistic economic summary.

## Project Architecture

### Domain Agents

The system employs specialized agents for different economic domains:

- **Equities Agent**: Analyzes stock market trends, major indices, and corporate performance
- **Fixed Income Agent**: Examines bond markets, yield curves, and interest rate trends
- **Macro Agent**: Evaluates broad economic indicators like GDP, inflation, and employment
- **Commodities Agent**: Tracks commodity prices, supply/demand dynamics, and market trends
- **Additional Domain Agents**: Can include FX, Real Estate, Crypto, etc.

Each domain agent:
1. Fetches data from relevant sources (APIs, news feeds, databases)
2. Analyzes trends and extracts insights within its domain
3. Generates a concise, structured summary of findings

### Aggregator Agent

The Aggregator Agent:
1. Collects summaries from all domain agents
2. Synthesizes information into a cohesive economic overview
3. Applies weighting and prioritization logic to highlight key insights
4. Produces the final economic summary report

### Orchestration Layer

The Swarm Controller orchestrates the entire process:
1. Initializes and executes domain agents in parallel
2. Manages error handling and retries
3. Collects domain summaries and passes them to the Aggregator Agent
4. Delivers the final report through designated channels (email, Slack, etc.)

## Setup and Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- SEC API key (for financial filings data)
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
   - Add any other required API keys for data sources

4. Set up the OpenAI configuration:
   - Create an `OAI_CONFIG_LIST.json` file in the root directory
   - Format according to the template in the documentation

## Usage

### Running the System

To generate a complete economic summary:

```python
python run_economic_summary.py
```

For individual domain analyses:

```python
python run_domain_agent.py --domain equities
python run_domain_agent.py --domain fixed_income
python run_domain_agent.py --domain macro
python run_domain_agent.py --domain commodities
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

### Week 1 (April 23-30, 2025)
- Set up project repository and environment
- Implement Equities Agent and Macro Agent
- Create basic data fetching mechanisms
- Establish prompt templates

### Week 2 (May 1-7, 2025)
- Implement Fixed Income and Commodities Agents
- Develop the Aggregator Agent
- Build the Swarm Controller for basic orchestration
- Implement initial error handling

### Week 3 (May 8-14, 2025)
- Enhance prompts and response quality
- Implement robust error handling and retries
- Add monitoring and logging
- Create deployment scripts
- Finalize documentation

### Week 4 (May 15-21, 2025)
- Testing and quality assurance
- Performance optimization
- User feedback integration
- Final deployment and handoff

## Team Roles and Responsibilities

| Team Member | Responsibility |
|-------------|----------------|
| Alice | Equities Agent: Stock market analysis using Yahoo Finance API |
| Bob | Fixed Income Agent: Bond market and yield curve analysis |
| Carol | Macro Agent: Economic indicators analysis (GDP, CPI, employment) |
| David | Commodities Agent: Commodity price trends and market drivers |
| Eve | Aggregator Agent: Synthesis of domain insights into cohesive summary |
| Frank | Swarm Controller: Orchestration, scheduling, and report delivery |

## Error Handling

The system implements robust error handling:
- Connection error management for API calls
- Graceful degradation when data sources are unavailable
- Fallback mechanisms for API key configuration
- Comprehensive logging for troubleshooting

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

## API Reference

### Domain Agent Interface

```python
def run_domain_agent(config: Dict) -> str:
    """
    Execute a domain-specific analysis and return a formatted summary.
    
    Args:
        config: Configuration dictionary with API keys and parameters
        
    Returns:
        Formatted string containing the domain analysis
    """
```

### Aggregator Interface

```python
def run_aggregator_agent(summaries: Dict[str, str], config: Dict) -> str:
    """
    Synthesize domain summaries into a comprehensive economic overview.
    
    Args:
        summaries: Dictionary mapping domain names to their summaries
        config: Configuration parameters for the aggregation
        
    Returns:
        Formatted comprehensive economic summary
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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Specify your license here]

## Acknowledgments

- OpenAI for providing the foundation models
- SEC-API.io for financial filing data access
- [Other acknowledgments as appropriate]
