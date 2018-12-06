'''Helper functions and classes facilitating logging module usage'''
import logging
DEFAULT = 'WARNING'
DEFAULT_LEVEL = logging.WARNING


def get_level(level: str = DEFAULT) -> int:
    '''
    Get int representation of a log level from logging module
    Usage:
        >>> get_level('WARNING')
        30
        >>> get_level('INFO')
        20
    '''
    try:
        return getattr(logging, level)
    except AttributeError:
        return DEFAULT_LEVEL
