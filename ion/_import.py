'''Functions and classes helping with import functionalities'''
import importlib
import logging
import inspect
from .files import is_interactive

log = logging.getLogger(__name__)


def load_object(path: str):
    '''
    Load an object from path
        e.g. 'helpers._import.load_object' will load this function object
    '''
    log.debug('Loading object from path: %s', path)
    *module_chunks, object_name = path.split('.')
    module_name = '.'.join(module_chunks)
    log.debug('Module: %s', module_name)
    log.debug('Object: %s', object_name)
    module = importlib.import_module(module_name)
    return getattr(module, object_name)

def get_caller_module(__reset_stack=0):
    '''Return module of this function's caller's caller'''
    caller_stack = inspect.stack()[2 + __reset_stack]
    caller_module = inspect.getmodule(caller_stack[0])
    if caller_module is None:
        if is_interactive():
            import __main__
            return __main__.__name__
    return caller_module.__name__
