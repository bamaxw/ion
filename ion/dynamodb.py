'''Helper functions facilitating boto3 usage'''
from decimal import Decimal
from typing import Dict
import math

from .dict import apply


def dedynamise(dct):
    '''Dedynamise typed dictionary returned from DDB'''
    if not isinstance(dct, dict):
        return dct
    if len(dct) == 1:
        k = next(iter(dct))
        if k in ('S', 'N', 'BOOL'):
            return dct[k]
        if 'L' in dct:
            return [dedynamise(elem) for elem in dct['L']]
        if 'M' in dct:
            return apply(dct['M'], key=dedynamise, value=dedynamise)
        if 'NULL' in dct:
            return None
    return {
        dedynamise(key): dedynamise(value)
        for key, value in dct.items()
    }


class DDBSize:
    '''Calculate DDB Size of different python objects'''
    @staticmethod
    def calc(payload: dict) -> int:
        '''Returns a full size a record would occupy in ddb'''
        return sum(
            DDBSize.key(key) + DDBSize.value(value)
            for key, value in payload.items()
        )

    @staticmethod
    def key(key: str):
        '''Validate and return the size of dynamodb key'''
        if isinstance(key, str):
            return len(key)
        raise TypeError(f'DynamoDB key should be `str` and not `{type(key).__name__}`')

    @staticmethod
    def value(value):
        '''
        Returns amount of memory in bytes a ddb value would occupy in dynamodb
        Usage:
            >>> DDBSize.value('x')
            1
            >>> DDBSize.value([1,2,3])
            6
            >>> DDBSize.value({'max': [1,2,3], 'python': 'whatever', 'nothing': None})
            37
        '''
        if isinstance(value, dict):
            return DDBSize.map(value)
        if isinstance(value, list):
            return DDBSize.list(value)
        if isinstance(value, str):
            return DDBSize.string(value)
        if isinstance(value, int):
            return DDBSize.integer(value)
        if isinstance(value, Decimal):
            return DDBSize.decimal(value)
        if value is None or isinstance(value, bool):
            return 1
        raise TypeError(f'Unrecognised type: {type(value).__name__} of {value}')

    @staticmethod
    def list(lst: list):
        '''Returns a size in bytes of a list as in stored in dynamodb'''
        return sum(
            DDBSize.value(elem)
            for elem in lst
        ) + 3

    @staticmethod
    def map(dct: dict) -> int:
        '''Returns amount of memory in bytes a mapping would occypy if it was stored in dynamodb'''
        return sum(
            DDBSize.key(k) + DDBSize.value(v)
            for k, v in dct.items()
        ) + 3

    @staticmethod
    def string(string: str) -> int:
        '''Returns amount of memory a given string would occupy in ddb'''
        return len(string.encode('utf-8'))

    @staticmethod
    def integer(integer: int) -> int:
        '''Returns amount of memory a given integer would occupy in ddb'''
        return math.ceil(len(str(integer)) / 2) + 1

    @staticmethod
    def decimal(decimal: Decimal) -> int:
        '''Returns amount of memory a given decimal would occupy in ddb'''
        return sum(
            math.ceil(len(chunk) / 2)
            for chunk in str(decimal).split('.')
        ) + 1

    @staticmethod
    def stats(payload: dict) -> Dict[str, int]:
        '''
        Returns a dictionary containing a total size a payload will occupy in ddb
        together with per-key break down
        Arguments:
            payload: payload to be passed to ddb
        '''
        sizes = {
            key: DDBSize.key(key) + DDBSize.value(value)
            for key, value in payload.items()
        }
        sizes['total'] = DDBSize.calc(payload)
        return sizes
