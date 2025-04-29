"""
Utilities for interacting with the FRED API.
"""
import logging
import pandas as pd
import requests
import json
from fredapi import Fred
from datetime import datetime, timedelta
from economic_summary.utils.config import get_fred_api_key

# Configure logging
logger = logging.getLogger(__name__)

class FREDDataManager:
    """
    Manager for retrieving and processing economic data from FRED.
    """
    
    def __init__(self):
        """Initialize the FRED Data Manager with API key."""
        self.api_key = get_fred_api_key()
        if not self.api_key:
            logger.error("FRED API key not found. FRED data retrieval will not work.")
            self.fred = None
        else:
            self.fred = Fred(api_key=self.api_key)
        
        # Common economic indicators
        self.indicators = {
            'GDP': 'GDP',                     # Gross Domestic Product
            'GDPC1': 'GDPC1',                 # Real GDP
            'UNRATE': 'UNRATE',               # Unemployment Rate
            'CPIAUCSL': 'CPIAUCSL',           # Consumer Price Index
            'FEDFUNDS': 'FEDFUNDS',           # Federal Funds Rate
            'T10Y2Y': 'T10Y2Y',               # 10-Year Treasury Constant Maturity Minus 2-Year
            'PAYEMS': 'PAYEMS',               # Total Nonfarm Payrolls
            'INDPRO': 'INDPRO',               # Industrial Production Index
            'HOUST': 'HOUST',                 # Housing Starts
            'RSAFS': 'RSAFS',                 # Retail Sales
            'PCE': 'PCE',                     # Personal Consumption Expenditures
            'DCOILWTICO': 'DCOILWTICO',       # Crude Oil Prices: WTI
            'USREC': 'USREC',                 # US Recession Indicator
            'UMCSENT': 'UMCSENT',             # Consumer Sentiment Index
            'BUSINV': 'BUSINV',               # Total Business Inventories
        }
        
        # Important economic data sources
        self.sources = {
            'fed': 1,                         # Board of Governors of the Federal Reserve System
            'bea': 18,                        # U.S. Department of Commerce: Bureau of Economic Analysis
            'census': 19,                     # U.S. Department of Commerce: Census Bureau
            'bls': 22,                        # U.S. Department of Labor: Bureau of Labor Statistics
            'eia': 53,                        # U.S. Department of Energy: Energy Information Administration
            'nber': 55,                       # National Bureau of Economic Research
            'imf': 60,                        # International Monetary Fund
            'eurostat': 61,                   # Eurostat
        }
    
    def get_series(self, series_id, start_date=None, end_date=None):
        """
        Get a time series from FRED.
        
        Args:
            series_id: FRED series ID
            start_date: Start date (default: 1 year ago)
            end_date: End date (default: today)
            
        Returns:
            pandas.Series: The requested time series
        """
        if not self.fred:
            logger.error("FRED client not initialized. Cannot retrieve data.")
            return None
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            # Add observation_start and observation_end parameters to ensure we get the most recent data
            data = self.fred.get_series(
                series_id, 
                observation_start=start_date, 
                observation_end=end_date,
                realtime_start=start_date,
                realtime_end=end_date
            )
            
            # Log the date range and most recent data point
            if not data.empty:
                most_recent_date = data.index.max().strftime('%Y-%m-%d')
                logger.info(f"Retrieved {series_id} data: most recent date is {most_recent_date}")
            else:
                logger.warning(f"No data found for {series_id} in the specified date range")
                
            return data
        except Exception as e:
            logger.error(f"Error retrieving FRED series {series_id}: {str(e)}")
            return None
    
    def get_indicator(self, indicator_name, start_date=None, end_date=None):
        """
        Get a specific economic indicator by name.
        
        Args:
            indicator_name: Name of the indicator (must be in self.indicators)
            start_date: Start date (default: 5 years ago)
            end_date: End date (default: today)
            
        Returns:
            pandas.Series: The requested indicator time series
        """
        if indicator_name not in self.indicators:
            logger.error(f"Unknown indicator: {indicator_name}")
            return None
        
        series_id = self.indicators[indicator_name]
        return self.get_series(series_id, start_date, end_date)
    
    def get_multiple_indicators(self, indicator_names, start_date=None, end_date=None):
        """
        Get multiple economic indicators and return as a DataFrame.
        
        Args:
            indicator_names: List of indicator names
            start_date: Start date (default: 5 years ago)
            end_date: End date (default: today)
            
        Returns:
            pandas.DataFrame: DataFrame containing all requested indicators
        """
        result = pd.DataFrame()
        
        for name in indicator_names:
            series = self.get_indicator(name, start_date, end_date)
            if series is not None:
                result[name] = series
                
        return result
    
    def get_indicator_metadata(self, indicator_name):
        """
        Get metadata for a specific indicator.
        
        Args:
            indicator_name: Name of the indicator
            
        Returns:
            dict: Metadata for the indicator
        """
        if not self.fred:
            logger.error("FRED client not initialized. Cannot retrieve metadata.")
            return None
            
        if indicator_name not in self.indicators:
            logger.error(f"Unknown indicator: {indicator_name}")
            return None
            
        series_id = self.indicators[indicator_name]
        
        try:
            info = self.fred.get_series_info(series_id)
            return info
        except Exception as e:
            logger.error(f"Error retrieving metadata for {indicator_name}: {str(e)}")
            return None
    
    def get_recession_periods(self, start_date=None, end_date=None):
        """
        Get recession periods from FRED.
        
        Args:
            start_date: Start date (default: 10 years ago)
            end_date: End date (default: today)
            
        Returns:
            list: List of (start_date, end_date) tuples for recession periods
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=10*365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            recession_data = self.get_series('USREC', start_date, end_date)
            if recession_data is None:
                return []
                
            # Find periods where recession indicator is 1
            recession_periods = []
            in_recession = False
            recession_start = None
            
            for date, value in recession_data.items():
                if value == 1 and not in_recession:
                    in_recession = True
                    recession_start = date
                elif value == 0 and in_recession:
                    in_recession = False
                    recession_periods.append((recession_start, date))
                    
            # Check if we're still in a recession at the end of the data
            if in_recession:
                recession_periods.append((recession_start, recession_data.index[-1]))
                
            return recession_periods
        except Exception as e:
            logger.error(f"Error retrieving recession periods: {str(e)}")
            return []
    
    def analyze_indicators(self, indicators=None, periods=1, start_date=None, end_date=None):
        """
        Analyze economic indicators and return a summary.
        
        Args:
            indicators: List of indicator names (default: all indicators)
            periods: Number of periods to analyze (default: 1)
            start_date: Start date
            end_date: End date
            
        Returns:
            dict: Analysis results
        """
        if not indicators:
            indicators = list(self.indicators.keys())
            
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        results = {}
        
        for indicator in indicators:
            try:
                # Get the indicator data
                series = self.get_indicator(indicator, start_date, end_date)
                
                if series is None or len(series) < 2:
                    logger.warning(f"Insufficient data for indicator {indicator}")
                    continue
                    
                # Get the most recent values
                current_value = series.iloc[-1]
                previous_value = series.iloc[-2] if len(series) > 1 else None
                
                # Calculate change
                change = None
                change_pct = None
                if previous_value is not None and previous_value != 0:
                    change = (current_value - previous_value) / previous_value
                    change_pct = change * 100
                
                # Determine trend direction
                trend_direction = "unknown"
                if len(series) >= 3:
                    recent_values = series.iloc[-3:]
                    if recent_values.is_monotonic_increasing:
                        trend_direction = "up"
                    elif recent_values.is_monotonic_decreasing:
                        trend_direction = "down"
                    else:
                        # Check if more ups than downs
                        diffs = recent_values.diff().dropna()
                        ups = sum(diffs > 0)
                        downs = sum(diffs < 0)
                        if ups > downs:
                            trend_direction = "up"
                        elif downs > ups:
                            trend_direction = "down"
                
                # Get the most recent date
                last_updated = series.index[-1].strftime('%Y-%m-%d')
                
                # Store the results
                results[indicator] = {
                    'current_value': current_value,
                    'previous_value': previous_value,
                    'change': change,
                    'change_pct': change_pct,
                    'trend_direction': trend_direction,
                    'data_points': len(series),
                    'last_updated': last_updated
                }
                
                logger.info(f"Analyzed indicator {indicator}: current value = {current_value}, last updated = {last_updated}")
                
            except Exception as e:
                logger.error(f"Error analyzing indicator {indicator}: {str(e)}")
                
        return results
    
    def get_sources(self):
        """
        Get a list of all sources available in FRED.
        
        Returns:
            dict: Dictionary of sources with their IDs
        """
        if not self.api_key:
            logger.error("FRED API key not found. Cannot retrieve sources.")
            return None
            
        try:
            url = f"https://api.stlouisfed.org/fred/sources?api_key={self.api_key}&file_type=json"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            sources = {}
            
            for source in data.get('sources', []):
                sources[source['id']] = {
                    'name': source['name'],
                    'link': source.get('link', None)
                }
                
            return sources
        except Exception as e:
            logger.error(f"Error retrieving FRED sources: {str(e)}")
            return None
    
    def get_source_releases(self, source_id=None, limit=25, realtime_start=None, realtime_end=None):
        """
        Get releases for a specific source from FRED.
        
        Args:
            source_id: ID of the source (default: None, which will use Board of Governors of the Federal Reserve System)
            limit: Maximum number of releases to return (default: 25)
            realtime_start: Start of the real-time period (default: today)
            realtime_end: End of the real-time period (default: today)
            
        Returns:
            list: List of releases for the source
        """
        if not self.api_key:
            logger.error("FRED API key not found. Cannot retrieve source releases.")
            return None
            
        # Default to Board of Governors of the Federal Reserve System if no source_id is provided
        if source_id is None:
            source_id = self.sources.get('fed', 1)
        elif isinstance(source_id, str) and source_id in self.sources:
            source_id = self.sources[source_id]
            
        # Set default dates if not provided
        if not realtime_start:
            realtime_start = datetime.now().strftime('%Y-%m-%d')
        if not realtime_end:
            realtime_end = datetime.now().strftime('%Y-%m-%d')
            
        try:
            url = (f"https://api.stlouisfed.org/fred/source/releases?"
                  f"source_id={source_id}&"
                  f"api_key={self.api_key}&"
                  f"file_type=json&"
                  f"realtime_start={realtime_start}&"
                  f"realtime_end={realtime_end}&"
                  f"limit={limit}&"
                  f"order_by=release_id&"
                  f"sort_order=desc")
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data.get('releases', [])
        except Exception as e:
            logger.error(f"Error retrieving releases for source {source_id}: {str(e)}")
            return None
    
    def get_recent_releases(self, sources=None, limit_per_source=5):
        """
        Get recent releases from multiple sources.
        
        Args:
            sources: List of source names or IDs (default: ['fed', 'bea', 'bls'])
            limit_per_source: Maximum number of releases per source (default: 5)
            
        Returns:
            dict: Dictionary mapping source names to their recent releases
        """
        if not sources:
            sources = ['fed', 'bea', 'bls']
            
        results = {}
        
        for source in sources:
            source_id = source
            source_name = source
            
            # Convert source name to ID if needed
            if isinstance(source, str) and source in self.sources:
                source_id = self.sources[source]
                source_name = source
                
            # Get releases for this source
            releases = self.get_source_releases(source_id, limit=limit_per_source)
            
            if releases:
                results[source_name] = releases
                
        return results
    
    def get_release_dates(self, release_id, limit=10):
        """
        Get dates for a specific release.
        
        Args:
            release_id: ID of the release
            limit: Maximum number of dates to return (default: 10)
            
        Returns:
            list: List of dates for the release
        """
        if not self.api_key:
            logger.error("FRED API key not found. Cannot retrieve release dates.")
            return None
            
        try:
            url = (f"https://api.stlouisfed.org/fred/release/dates?"
                  f"release_id={release_id}&"
                  f"api_key={self.api_key}&"
                  f"file_type=json&"
                  f"limit={limit}&"
                  f"sort_order=desc")
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data.get('release_dates', [])
        except Exception as e:
            logger.error(f"Error retrieving dates for release {release_id}: {str(e)}")
            return None
