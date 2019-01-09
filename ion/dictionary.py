'''Helper functions for operations on dictionaries'''
from typing import Iterable
from copy import deepcopy
import logging

log = logging.getLogger(__name__)


def path(path, dct, default=...):
    '''
    Get dictionary value at path
    Args:
        - path: path to where the value should be taken from e.g.: ['item'] or ['item', 'attr_name']
        - dct: dictionary to get the value from
    Kwargs:
        - default: a value to be returned if a given path doesn't exist
    Usage:
        >>> path(['item'], {'item': 100})
        100
        >>> path(['item', 'attr_name'], {'item': 100}, default=None)
        None
        >>> path(['item', 'attr_name'], {'item': {'attr_name': 'max'}})
        'max'
    '''
    if path is None:
        return default
    if not isinstance(path, (list, tuple)):
        raise TypeError('Path argument must be a sequence!')
    tmp = dct
    for field in path:
        try:
            tmp = tmp[field]
        except (KeyError, IndexError, TypeError):
            if default is ...:
                log.exception('The object doesnt have field %s [path: %s]', field, path)
            else:
                return default
    return tmp

def set_path(path, value, dct, inplace=True):
    '''
    Set path of a dictionary to a particular value
    Args:
        - path: path to where the value should be set e.g.: ['item'] or ['item', 'attr_name']
        - value: which value should be set at the path
        - dct: dictionary to be updated
    Kwargs:
        - inplace: if True this function mutates the original object
    Usage:
        >>> set_path(['item'], 100, {})
        {'item': 100}
        >>> set_path(['item', 'attr_name'], 100, {'item': {'attr_name': 0}})
        {'item': {'attr_name': 100}}
    '''
    if not isinstance(path, (list, tuple)):
        raise TypeError(f'Path argument must be a sequence!')
    if not inplace:
        tmp = deepcopy(dct)
    else:
        tmp = dct
    for field in path[:-1]:
        tmp = tmp[field]
    tmp[path[-1]] = value
    return tmp

def apply(dct: dict, key=lambda key: key, value=lambda val: val, item=None) -> dict:
    '''
    Return a new dictionary with keys and values changed according to provided functions
    Arguments:
        key: apply this function to each key in the dictionary
        value: apply this function to each value in the dictionary
        item: ignore key and value and apply both function to a tuple of (key, value)
    '''
    if item:
        return dict(
            item(_item)
            for _item in dct.items()
        )
    return {
        key(k): value(v) for k, v in dct.items()
    }

def just_keys(dct: dict, keys: Iterable) -> dict:
    '''Return a new dictionary containing just the specified keys'''
    return {k: v for k, v in dct.items() if k in keys}

def remove_keys(dct: dict, keys: Iterable) -> dict:
    '''Return a new dictionary without specified keys'''
    return {k: v for k, v in dct.items() if k not in keys}
