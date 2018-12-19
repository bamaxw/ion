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

def verbosity_to_level(verbosity: int) -> int:
    '''
    Get logging loglevel corresponding to scripts verbosity
    for instance -vv is verbosity 2 and -v is verbosity 1
    Usage:
        >>> verbosity_to_level(1)
        20
    '''
    return {
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG
    }[verbosity]
