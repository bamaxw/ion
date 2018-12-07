'''Helper functions and classes for dealing with python functions'''
from typing import Callable, Optional

def describe_lambda(
        lambda_func: Callable,
        name: Optional[str] = None,
        doc: Optional[str] = None,
        force: bool = False
) -> Callable:
    '''Take a anonymous function and give it a name and a doc'''
    if name is not None:
        if not lambda_func.__name__ or force:
            lambda_func.__name__ = name
        if not lambda_func.__qualname__ or force:
            lambda_func.__qualname__ = name
    if doc is not None:
        if not lambda_func.__doc__ or force:
            lambda_func.__doc__ = doc
    return lambda_func
