'''Helper functions, generators and classes for dealing with streams/generators'''
from typing import Generator, TypeVar, Callable, Optional, Union
import re

from .bash import colors

TypeA = TypeVar('A')
TypeB = TypeVar('B')


def filter(
        stream: Generator[TypeA, None, None],
        filter_func: Callable[[TypeA], bool]
)-> Generator[TypeA, None, None]:
    '''
    Filter stream with a filter function that returns True/False
    depending on whether an event should be accepted or rejected
    '''
    for event in stream:
        if filter_func(event):
            yield event

def re_filter(
        stream: Generator[str, None, None],
        regex: str,
        *,
        highlight: bool = False,
        key: Optional[str] = None
) -> Generator[str, None, None]:
    '''Filter out events in a stream if they don't match specified regex expression'''
    if key:
        def filter_func(event: dict) -> bool:
            return re.search(regex, event[key])
    else:
        def filter_func(event: str) -> bool:
            return re.search(regex, event)
    for event in filter(stream, filter_func):
        if key:
            event = event[key]
        if highlight:
            yield re.sub(f'({regex})', fr'{colors.yellow}\1{colors.reset}', event[key])
        else:
            yield event

def apply(
        stream: Generator[TypeA, None, None],
        apply_func: Callable[[TypeA], TypeB]
) -> Generator[TypeB, None, None]:
    '''Apply function to each event in stream'''
    for event in stream:
        yield apply_func(event)
