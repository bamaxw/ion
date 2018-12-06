'''Helper module defining functions and classes associated with injectors'''
from typing import Any, Type, Union, Optional, Dict
from functools import wraps
import logging

from ._class import singleton

# TYPES #
BindingKey = Union[Type, str]
Bindings = Dict[BindingKey, Any]
# # # # #
log = logging.getLogger(__name__)


@singleton
class Injector:
    '''Simple implementation of dependecy injector'''
    def __init__(self, bindings: Optional[Bindings] = None):
        if bindings is None:
            bindings = {}
        self.bindings: Bindings = bindings

    def bind(self, variable: Any, key: Optional[BindingKey] = None):
        '''
        Binds an object to this injector at particular key if it's defined or its type if it isn't
        Args:
            - variable: object to be bound
        Kwargs:
            - key: a key at which the object is to be bound
                DEFAULT: type(variable)
        '''
        if key is None:
            key = type(variable)
        if key in self.bindings:
            log.warning('Binding for %s already exists and is being overwritten!', key)
        self.bindings[key] = variable

    def get(self, key: BindingKey):
        '''Get an object bound to this Injector at key'''
        if key in self.bindings:
            return self.bindings[key]
        raise TypeError(f"{key} wasn't bound but was tried to be accessed!")


def inject(*dependencies):
    '''
    Decorator factory creating a decorator which injects specified dependencies
    Args:
        - *dependencies: list of keys at which dependencies are bound in Injector
                            keys can be either strings or types, depending how the
                            resource was bound to the injector
    Usage:
        >>> @inject(FooService, BarService, 'max', 'python')
        >>> def do_something(arg1, arg2, foo_service, bar_service, max, python, **kwargs)
        >>>     pass
    '''
    def wrapper(func):
        @wraps(func)
        def _func(*a, **kw):
            injector = Injector()
            deps = [injector.get(dep) for dep in dependencies]
            return func(*a, *deps, **kw)
        return _func
    wrapper.__name__ = 'inject'
    wrapper.__qualname__ = 'inject'
    wrapper.__doc__ = f'''Injects {dependencies} dependencies after all other args'''
    return wrapper
