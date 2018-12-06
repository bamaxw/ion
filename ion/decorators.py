'''Module containing various decorators'''
from functools import wraps
import sys


def aslist(func):
    '''Converts generator function into a function that returns list'''
    @wraps(func)
    def _wrapper(*a, **kw):
        return list(func(*a, **kw))
    return _wrapper

def asdict(func):
    '''
        Converts generator function into a function that returns dict
        Wrapped function must generate a key-value tuples
    '''
    @wraps(func)
    def _wrapper(*a, **kw) -> dict:
        return dict(func(*a, **kw))
    return _wrapper

def logreturn(func):
    '''Runs a wrapped function and logs its return value'''
    @wraps(func)
    def _wrapper(*a, **kw):
        return_val = func(*a, **kw)
        print(return_val)
        return return_val
    return _wrapper

def tail_call_optimized(func):
    """
        This function decorates a function with tail call
        optimization. It does this by throwing an exception
        if it is it's own grandparent, and catching such
        exceptions to fake the tail call optimization.

        This function fails if the decorated
        function recurses in a non-tail context.
    """
    @wraps(func)
    def _wrapped(*args, **kwargs):
        frame = sys._getframe() # pylint: disable=protected-access
        if frame.f_back and frame.f_back.f_back and frame.f_back.f_back.f_code == frame.f_code:
            raise TailRecurseException(args, kwargs)
        else:
            while True:
                try:
                    return func(*args, **kwargs)
                except TailRecurseException as ex:
                    args = ex.args
                    kwargs = ex.kwargs
    return func

class TailRecurseException(Exception):
    '''
    Exception thrown by tail_call_optimized to communicate a recursive call
    being its own grandparent
    '''
    def __init__(self, args, kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs
