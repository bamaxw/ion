'''Helper functions completing built-in math module'''
from typing import List, Optional

from .typing import Number


def mean(numbers: List[Number]) -> Optional[float]:
    '''Calculate mean of list of numbers'''
    if not numbers:
        return None
    return sum(numbers) / len(numbers)

def sign(number: Number) -> int:
    '''Return sign of a number'''
    if number > 0:
        return 1
    if number < 0:
        return -1
    return 0
