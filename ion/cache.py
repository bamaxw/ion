'''Functions and classes helping with application-level caching and memoization'''
from typing import Callable, Any, Optional
from functools import wraps, partial
from collections import namedtuple
import time

TsValue = namedtuple('TsValue', ['value', 'timestamp'])


class MemoizeWithTimeout:
    '''
    Use this class to memoize a functions result for a certain period of time
    Class attributes:
        - _per_func_cache: stores a function result in a dictionary where
                              key is tuple(args, tuple(sorted(kwargs.items()))) tuple, and
                              value is TsValue with value being return value and ts being timestamp when it happened
        - _timeouts: stores timeout value for each of registered functions
    '''
    _per_func_cache = {}
    _timeouts = {}
    def __init__(self, timeout: int = 60):
        self.timeout = float(timeout)

    def collect(self) -> None:
        """Clear cache of results which have timed out"""
        for func, func_cache in self._per_func_cache.items():
            cache = {}
            for args_kwargs, cached in func_cache.items():
                if (time.time() - cached.timestamp) < self._timeouts[func]:
                    cache[args_kwargs] = cached
            self._per_func_cache[func] = cache

    def __call__(self, func):
        cache = self._per_func_cache[func] = {}
        self._timeouts[func] = self.timeout
        @wraps(func)
        def _wrapper(*args, **kwargs):
            args_kwargs = (args, tuple(sorted(kwargs.items())))
            try:
                cached = cache[args_kwargs]
                if (time.time() - cached.timestamp) > self.timeout:
                    raise KeyError
            except KeyError:
                return_value = func(*args, **kwargs)
                cached = cache[args_kwargs] = TsValue(
                    value=return_value,
                    timestamp=time.time()
                )
            return cached.value
        return _wrapper


def create_minute_memoize(no_minutes: float):
    '''Creates MemoizeWithTimeout with timeout equal no_minutes minutes'''
    return MemoizeWithTimeout(no_minutes * 60)

minute_memoize = MemoizeWithTimeout(60)

cache_for = create_minute_memoize

memoize_for = create_minute_memoize

_remember_cache = {}
def remember(func):
    @wraps(func)
    def _wrap(*a, **kw):
        if str(type(func)) in ("<class 'function'>", "<class 'builtin_function_or_method'>"):
            obj = None
        elif str(type(func)) == "<class 'method'>":
            obj = a[0]
        if obj not in _remember_cache:
            _remember_cache[obj] = {}
        if func not in _remember_cache[obj]:
            _remember_cache[obj][func] = func(*a, **kw)
        return _remember_cache[obj][func]
    return _wrap


def _from_cache_on_err(func: Callable, *, default: Any):
    '''
    Caches a function response, so that if the function is called
    in the future and results in an error, the cached response is returned
    If the first function call results in an error, the error is re-raised
    Assumed use-case is reading remote data, so that if the remote server goes down
    the previously read version of the data will be returned as a fallback
    '''
    _cached = default
    @wraps(func)
    def _wrap(*a, **kw):
        try:
            return func(*a, **kw)
        except: # pylint: disable=bare-except
            if _cached is default:
                raise
            return _cached

def from_cache_on_err(
        func: Optional[Callable] = None,
        default: Any = ...
):
    '''
    Wrapper around _from_cache_on_err allows for the from_cache_on_err to be called
    with additional argument *default* that initializes cache with data that is impossible
    to be returned from the function itself
    '''
    if func:
        return _from_cache_on_err(func, default=default)
    return partial(_from_cache_on_err, default=default)
