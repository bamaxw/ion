'''Helper functions and classes for code banchmarking'''
from functools import wraps
from collections import defaultdict
import logging

from .time import pts

log = logging.getLogger(__name__)


class MeanTime:
    '''A decorator class for recording functions' elapsed times'''
    def __init__(self):
        self.per_func = defaultdict(self.default_value)

    @staticmethod
    def default_value():
        '''Default value for defaultdict'''
        return (0, 0)

    def __call__(self, func):
        '''Use this decorator to record elapsed times for a function func'''
        @wraps(func)
        def _wrapper(*a, **kw):
            start = pts()
            return_value = func(*a, **kw)
            end = pts()
            elapsed = end - start
            total, invoked_no = self.per_func[func]
            self.per_func[func] = (total + elapsed, invoked_no + 1)
            return return_value
        return _wrapper

    def get(self, func=None):
        '''Get the elapsed value for a particular function or all functions if no function is specified'''
        if func is None:
            return dict(self.per_func)
        return self.per_func.get(func)

    def get_message(self, func=None):
        '''
        Get a formatted message about an average runtime of a particular function
        or all functions if no function is specified
        '''
        if func is None:
            return self.get_message_all()
        return self.get_message_func(func)

    def get_message_all(self):
        '''Get formatted message for all recorded functions'''
        raise NotImplementedError

    def get_message_func(self, func):
        '''Get formatted message for a particular function func'''
        raise NotImplementedError

    def reset(self, func=None):
        '''
        Reset instances record of function's elapsed times or
        reset the entire record if no function is specified
        '''
        if func:
            del self.per_func[func]
        self.per_func = defaultdict(self.default_value)
meantime = MeanTime() # pylint: disable=invalid-name


class Measure:
    '''Context class which calculates elapsed time of its block'''
    def __init__(self):
        self.start = None
        self.end = None

    @property
    def elapsed(self):
        '''Calculates elapsed time'''
        return self.end - self.start

    def __enter__(self):
        self.start = pts()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = pts()


def timeit(func):
    '''This decorator logs elapsed time (DEBUG) after every run'''
    @wraps
    def timed(*args, **kwargs):
        ts_start = pts()
        result = func(*args, **kwargs)
        ts_end = pts()
        elapsed = ts_end - ts_start
        if log.isEnabledFor(logging.DEBUG):
            log.debug('%s (%s, %s) %02f sec', func.__qualname__, args, kwargs, elapsed)
        return result
    return timed

# TODO: Continue writing TimeIt abstraction of timeit function above
# class TimeIt:
#     '''This decorator stores duration time data for a particular function'''
#     def __init__(self, print=False):
#         self.print = print
#         self.total_elapsed = 0
#         self.invoked = 0
#
#     @property
#     def elapsed(self):
#         return self.total_elapsed
#
#     def __call__(self, )
