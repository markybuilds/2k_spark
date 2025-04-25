"""
Time utility functions for the 2K Flash application.
"""

import datetime
import pytz
from dateutil.parser import parse

from config.settings import DEFAULT_TIMEZONE, DATE_FORMAT, API_DATE_FORMAT


def get_current_time(timezone=DEFAULT_TIMEZONE):
    """
    Get the current time in the specified timezone.
    
    Args:
        timezone (str): Timezone name (default: DEFAULT_TIMEZONE from settings)
        
    Returns:
        datetime.datetime: Current time in the specified timezone
    """
    tz = pytz.timezone(timezone)
    return datetime.datetime.now(tz)


def format_datetime(dt, format_str=DATE_FORMAT):
    """
    Format a datetime object as a string.
    
    Args:
        dt (datetime.datetime): Datetime object to format
        format_str (str): Format string (default: DATE_FORMAT from settings)
        
    Returns:
        str: Formatted datetime string
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=pytz.UTC)
    return dt.strftime(format_str)


def parse_datetime(dt_str, timezone=DEFAULT_TIMEZONE):
    """
    Parse a datetime string into a datetime object.
    
    Args:
        dt_str (str): Datetime string to parse
        timezone (str): Timezone name (default: DEFAULT_TIMEZONE from settings)
        
    Returns:
        datetime.datetime: Parsed datetime object
    """
    dt = parse(dt_str)
    if not dt.tzinfo:
        tz = pytz.timezone(timezone)
        dt = tz.localize(dt)
    return dt


def get_date_range(days_back, days_forward=0, timezone=DEFAULT_TIMEZONE):
    """
    Get a date range from days_back days ago to days_forward days in the future.
    
    Args:
        days_back (int): Number of days to go back
        days_forward (int): Number of days to go forward (default: 0)
        timezone (str): Timezone name (default: DEFAULT_TIMEZONE from settings)
        
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    now = get_current_time(timezone)
    start_date = now - datetime.timedelta(days=days_back)
    end_date = now + datetime.timedelta(days=days_forward)
    return start_date, end_date


def format_api_date_range(days_back, days_forward=0, timezone=DEFAULT_TIMEZONE):
    """
    Get a date range formatted for API requests.
    
    Args:
        days_back (int): Number of days to go back
        days_forward (int): Number of days to go forward (default: 0)
        timezone (str): Timezone name (default: DEFAULT_TIMEZONE from settings)
        
    Returns:
        tuple: (from_date, to_date) as strings formatted for API requests
    """
    start_date, end_date = get_date_range(days_back, days_forward, timezone)
    from_date = format_datetime(start_date, API_DATE_FORMAT)
    to_date = format_datetime(end_date, API_DATE_FORMAT)
    return from_date, to_date
