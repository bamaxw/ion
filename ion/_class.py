'''Useful helper classes and class helpers'''
from pprint import pprint, pformat
from dataclasses import asdict
from functools import wraps
from typing import Type

import simplejson as json


class ToDict:
    '''
        ToDict implements to_dict method which
        returns a dictionary representation of
        an inheriting class instance
        Class level attributes:
            - fields: list of fields to be included in dict representation
    '''
    def __init__(self):
        self._dict = {}

    def __setattr__(self, attr, value):
        if attr != '_dict':
            self._dict[attr] = value
        super().__setattr__(attr, value)

    def __str__(self) -> str:
        return str(self.to_dict())

    def to_dict(self) -> dict:
        '''Returns dict representation of instance'''
        return self._dict


class StrictToDict(ToDict):
    '''Same as ToDict but allowing dict keys to be only from _fields'''
    _fields = []
    def __setattr__(self, attr, value):
        if attr in self._fields:
            self._dict[attr] = value
        object.__setattr__(self, attr, value)


class ToJson(ToDict):
    '''
        ToJson class implements to_json method which takes
        a dict representation of an inheriting class (self.to_dict())
        and converts it to json encoded string
    '''
    def to_json(self, **kw) -> str:
        '''Converts self.to_dict() to json string'''
        return json.dumps(self.to_dict(), **kw)


class PPrintable(ToDict):
    '''
        PPrintable implements pprint and pformat
        And changes behaviour of __str__ and __repr__ to use pformat
    '''
    def pprint(self, *a, **kw):
        '''look: pprint.pprint'''
        pprint(self.to_dict(), *a, **kw)

    def pformat(self, *a, **kw):
        '''look: pprint.pformat'''
        return pformat(self.to_dict(), *a, **kw)

    def __str__(self):
        return self.pformat()

    def __repr__(self):
        return str(self)


class DCDict:
    '''
    Data Class Dict
    Overwrite this with a dataclass to gain access to to_dict() method
    that basically acts as a asdict(self)
    '''
    def to_dict(self):
        '''Convert self dataclass to dict'''
        return asdict(self)

    def pprint(self, *a, **kw):
        '''look: pprint.pprint'''
        pprint(self.to_dict(), *a, **kw)

    def pformat(self, *a, **kw):
        return pformat(self.to_dict(), *a, **kw)


def singleton(cls: Type):
    '''
    Any class decorated with this decorator will have only one instance
    After first initialization, any subsequent attempts to initialize the
    same class will result in its original instance being returned
    '''
    instances = {}
    @wraps(cls)
    def _class(*a, **kw) -> Type:
        if cls not in instances:
            instances[cls] = cls(*a, **kw)
        return instances[cls]
    return _class

def make_property(
        cls: Type,
        prop_name: str,
        default=None,
        getter=True,
        setter=True
):
    '''
    Creates a getter and setter properties on a class object
    for a given property name
    '''
    prop_attr = f'_{prop_name}'
    _getter = _setter = None
    if getter:
        def _getter(self):
            return getattr(self, prop_attr)
        _getter.__name__ = f'{prop_name}_getter'
        _getter.__qualname__ = f'{cls.__name__}.{_getter.__name__}'
        _getter.__doc__ = f'{prop_name} getter'
    if setter:
        def _setter(self, value):
            setattr(self, prop_attr, value)
        _setter.__name__ = f'{prop_name}_setter'
        _setter.__qualname__ = f'{cls.__name__}.{_setter.__name__}'
        _setter.__doc__ = f'{prop_name} setter'
    setattr(cls, prop_attr, default)
    setattr(cls, prop_name, property(_getter, _setter))
