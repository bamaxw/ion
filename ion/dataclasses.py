'''Helper functions and classes for extended use of python3.7's dataclasses'''
from dataclasses import dataclass, is_dataclass
from functools import wraps

def nested_dataclass(*args, **kwargs):
    '''
    Returns a dataclass that accepts another dataclasses as type annotations
    And is going to initialize these dataclasses by passing in the arguments
    to their constructors
    Usage:
        @dataclass
        class A:
            i: int = 0
        @dataclass
        class B:
            lst: field(default_factory=list)
        @nested_dataclass
        class C:
            a: A
            b: B
        c = C(a={'i': 10})
        >>> print(c)
        C(a=A(i=10), b=B(lst=[]))
    '''
    def wrapper(_cls):
        _cls = dataclass(_cls, **kwargs)
        original_init = _cls.__init__
        @wraps(_cls)
        def __init__(self, *a, **kw):
            for name, value in kw.items():
                field_type = _cls.__annotations__.get(name, None)
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kw[name] = new_obj
            original_init(self, *a, **kw)
        _cls.__init__ = __init__
        return _cls
    if args:
        return wrapper(args[0])
    return wrapper
