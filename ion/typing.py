'''Helper types'''
from typing import Union, List, Tuple, Any, Callable, TypeVar


Number = Union[int, float]
DictItems = List[Tuple[Any, Any]]

ByteLike = Union[str, bytes]
HashFunction = Callable[[ByteLike], int]
HexHashFunction = Callable[[ByteLike], str]

KeyValue = Tuple[Any, Any]

T = TypeVar('T')
MaybeList = Union[T, List[T]]

MultilineStr = MaybeList[str]
