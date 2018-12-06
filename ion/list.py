'''Helper functions for operations on sequences'''
from typing import Sequence, Iterable, Generator, TypeVar

from .typing import MaybeList

T = TypeVar('T')


def trim_list(lst: Iterable[T], trim: T = '') -> Iterable[T]:
    '''
    Look at the beginning and end of a list and trim elements that are equal to trim
    Args:
        - lst: list to be trimmed
        - trim: elements of lst at the beginning and the end equal to this argument will be removed
    Usage:
        >>> trim_list(['', 'max', ''])
        ['max']
        >>> trim_list(['max', 'max', '', '', 'max'], trim='max')
        ['', '']
    '''
    if not lst:
        return []
    for start, elem in enumerate(lst):
        if elem != trim:
            break
    else:
        return []
    for end, elem in reversed(list(enumerate(lst))):
        if elem != trim:
            break
    return lst[start:end + 1]

def as_list(arg: MaybeList[T], tuples: bool = True) -> Iterable[T]:
    '''
    Converts passed argument to list if it's not already a list
    Args:
        - arg: argument to be converted to list
    Kwargs:
        - tuples: whether to accept tuples as lists if set to False it will wrap tuple in list
    Usage:
        >>> as_list('max')
        ['max']
        >>> as_list(['max'])
        ['max']
        >>> as_list(('max',))
        ('max',)
        >>> as_list(('max',), tuples=False)
        [('max',)]
    '''
    list_types = (tuple, list) if tuples else list
    if isinstance(arg, list_types):
        return arg
    return [arg]

def allequal(lst: Iterable) -> bool:
    '''
    Check whether a sequence contains elements that are all equal to each other
    >>> allequal([1,2,3])
    False
    >>> allequal([])
    True
    >>> allequal([1])
    True
    >>> allequal([1,1,1])
    True
    '''
    if len(lst) <= 1:
        return True
    return all(elem == lst[0] for elem in lst[1:])

def chunk(lst: Iterable[T], size: int) -> Generator[Iterable[T], None, None]:
    '''Split an iterable into chunks of size `size`'''
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def chunk_into(lst: Iterable[T], chunks: int) -> Generator[Iterable[T], None, None]:
    '''Split an iterable into `chunks` chunks'''
    return chunk(lst, int(len(lst) / chunks))
