'''Root time module containing helper functions and classes for dealing with time and dates'''
second = 1000
minute = 60 * second
hour = 60 * minute
day = 24 * hour
week = 7 * day


def ts():
    '''Get current UNIX timestamp in seconds as an integer'''
    return int(time())

def pts():
    '''Get current UNIX timestamp in seconds as a fraction'''
    return time()

def msts():
    '''Get current UNIX timestamp in milliseconds as an integer'''
    return int(time() * 1000)

def dt_to_ts(date_time: 'datetime.datetime'):
    '''Convert datetime object to UNIX timetsamp'''
    return mktime(date_time.timetuple())

def to_midnight(date_time: 'datetime.datetime'):
    '''
    Round the provided datetime object to the last day
    Usage:
        >>> to_midnight(datetime.strptime('14 Aug 1993 10:21', '%d %b %Y %H:%M')).strftime('%d %b %Y %H:%M')
        "14 Aug 1993 00:00"
    '''
    return date_time.replace(hour=0, minute=0, second=0, microsecond=0)

def format_seconds(seconds: float, _format: str = '%mm:%ss.%msms'):
    '''
    Formats a number of seconds into a formatted string
    Usage:
        >>> format_seconds(10)
        '00m:10s.000ms'
        >>> format_seconds(110.24)
        '01m:50s.240ms'
        >>> format_seconds(3601.52, _format='%h:%m:%s.%ms')
        '01:00:01.520'
    '''
    string = _format
    # Days
    seconds_in_day = 60 * 60 * 24
    days = int(seconds / seconds_in_day)
    seconds = seconds % seconds_in_day
    # Hours
    seconds_in_hour = 60 * 60
    hours = int(seconds / seconds_in_hour)
    seconds = seconds % seconds_in_hour
    # Minutes
    seconds_in_minute = 60
    minutes = int(seconds / seconds_in_minute)
    seconds = seconds % seconds_in_minute
    # Seconds
    _seconds = int(seconds)
    seconds = seconds - _seconds
    # Milliseconds
    mseconds = int(seconds * 1000)
    # Formatting
    string = string.replace('%ms', '{:03d}'.format(mseconds))
    string = string.replace('%s', '{:02d}'.format(_seconds))
    string = string.replace('%m', '{:02d}'.format(minutes))
    string = string.replace('%h', '{:02d}'.format(hours))
    string = string.replace('%d', '{:02d}'.format(days))
    return string


from time import time, mktime
from .ticktock import tick, tock
