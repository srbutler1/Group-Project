"""
Configuration utilities for the Economic Summary Swarm Agent System.
"""
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_api_key(key_name, default=None):
    """
    Get an API key from environment variables with fallback to default.
    
    Args:
        key_name: Name of the environment variable containing the API key
        default: Default value to return if the key is not found
        
    Returns:
        The API key if found, otherwise the default value
    """
    api_key = os.getenv(key_name)
    if not api_key and default:
        logger.warning(f"{key_name} not found, using default/dummy value")
        return default
    elif not api_key:
        logger.error(f"{key_name} not found and no default provided")
        return None
    return api_key

def get_openai_api_key():
    """Get the OpenAI API key with fallback to a dummy key for testing."""
    return get_api_key(
        "OPENAI_API_KEY", 
        default="sk-dummy1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefgh"
    )

def get_fred_api_key():
    """Get the FRED API key."""
    return get_api_key("FRED_API_KEY")

def get_config(key, default=None):
    """
    Get a configuration value from environment variables.
    
    Args:
        key: Name of the environment variable
        default: Default value to return if the key is not found
        
    Returns:
        The configuration value if found, otherwise the default value
    """
    return os.getenv(key, default)

def get_verbose():
    """Get the verbose flag from environment variables."""
    return get_config("VERBOSE", "True").lower() == "true"

def get_auto_save():
    """Get the auto_save flag from environment variables."""
    return get_config("AUTO_SAVE", "True").lower() == "true"
