"""
Utility functions for the application
"""
from datetime import datetime
import re

def str_to_datetime(date_str):
    """Convert string to datetime object with fallback"""
    if isinstance(date_str, str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            except ValueError:
                return datetime.now()
    return date_str

def sanitize_for_logging(input_str):
    """
    Sanitize input string for safe logging by removing dangerous characters
    that could be used for log injection attacks.
    
    Args:
        input_str (str): The input string to sanitize
        
    Returns:
        str: Sanitized string safe for logging
    """
    if not isinstance(input_str, str):
        input_str = str(input_str)
    
    # Remove newlines, carriage returns, and other control characters
    # that could be used for log injection
    sanitized = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', '', input_str)
    
    # Limit length to prevent log flooding
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "...[truncated]"
    
    return sanitized
