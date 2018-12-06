'''Module containing helper functions and classes associated with json module and format'''
from typing import Union, Any
from decimal import Decimal

import simplejson as json

JsonPayload = Union[str, bytes]


def load(payload: JsonPayload) -> Any:
    '''Converts json string or bytes to its python representation'''
    return json.loads(payload)

def aws_load(payload: JsonPayload) -> Any:
    '''Converts json string or bytes and converts floats to decimal.Decimal'''
    return json.loads(payload, parse_float=Decimal)

def dump(payload: Any) -> str:
    '''Converts python data structure into a json encoded string'''
    return json.dumps(payload, indent=4)
