'''
generators.py
Module implementing various generator helpers
Author: Maximus Wasylow
'''
from typing import Generator, List
from functools import partialmethod

from .typing import Number

_sum = sum

EOS = object()

def coroutine(func):
    def _wrapper(*a, **kw):
        gen = func(*a, **kw)
        gen.send(None)
        return gen
    return _wrapper

@coroutine
def cotake(n: int, target: Generator) -> Generator:
    while n >= 0:
        target.send((yield))
        n -= 1
    target.send(EOS)

@coroutine
def cosum(target: Generator) -> Generator:
    '''Sum elements'''
    _sum = 0
    while True:
        n = yield
        if n == EOS:
            target.send(_sum)
            target.send(EOS)
        else:
            _sum += n

@coroutine
def cofilter(_filter, target):
    while True:
        item = yield
        if item == EOS:
            target.send(item)
        else:
            if _filter(item):
                target.send(item)

@coroutine
def cobroadcast(targets: List[Generator]) -> Generator:
    '''Broadcast to all targets'''
    while True:
        item = yield
        for target in targets:
            target.send(item)
@coroutine
def cogenerate() -> Generator:
    '''Generator'''
    while True:
        item = yield
        yield item

cgn = cogenerate()
source = range(1000)
ctk = cotake(
    100,
    cosum(
        cobroadcast(
            [
                cofilter(
                    lambda x: x % 2 == 0,
                    cgn
                ),
                cofilter(
                    lambda x: x % 3 == 0,
                    cgn
                )
            ]
        )
    )
)

for item in source:
    ctk.send(item)
for item in cgn:
    print(item)
import sys
sys.exit()


def take(n: int, source: Generator) -> Generator:
    '''Generator passing only first n elements of source'''
    if n <= 0:
        return
    yield next(source)
    yield from take(n-1, source)

def head(source: Generator) -> Generator:
    '''yields first element of the source and stops generating'''
    yield next(source)

def sum(source: Generator[Number, None, None]) -> Generator[Number, None, None]:
    yield _sum(source)

ALLOWED_CHAINABLE_GENERATORS = (
    take,
    head,
    map,
    sum
)


class ChainGenerator:
    def __init__(self, base_generator: Generator) -> None:
        self.gen = base_generator
        self.ops = []

    def _assign_global(self, *a, generator=lambda x: x, **kw) -> 'ChainGenerator':
        self.ops.append(
            (generator, a, kw)
        )
        return self

    def __iter__(self) -> Generator:
        last = iter(self.gen)
        for _op, a, kw in self.ops:
            last = _op(*a, last, **kw)
        yield from last
for generator in ALLOWED_CHAINABLE_GENERATORS:
    setattr(
        ChainGenerator,
        generator.__name__,
        partialmethod(
            ChainGenerator._assign_global,
            generator=generator
        )
    )
