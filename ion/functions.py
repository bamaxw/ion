'''Helper functions and classes for dealing with python functions'''
from typing import Callable, Optional
from functools import partial


def describe_function(
        lambda_func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        qualname: Optional[str] = None,
        doc: Optional[str] = None,
        force: bool = False
) -> Callable:
    '''Take a anonymous function and give it a name and a doc'''
    if lambda_func is None:
        return partial(describe_function, name=name, qualname=qualname, doc=doc, force=force)
    if name is not None:
        if not lambda_func.__name__ or force:
            lambda_func.__name__ = name
    if qualname is not None:
        if not lambda_func.__qualname__ or force:
            lambda_func.__qualname__ = name
    if doc is not None:
        if not lambda_func.__doc__ or force:
            lambda_func.__doc__ = doc
    return lambda_func
