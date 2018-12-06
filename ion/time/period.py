'''time.period defines useful word to datetime functions and classess'''
from typing import Union, Tuple, Optional
from datetime import timedelta, datetime
import time

from ..string import isdigit
from . import pts, ts


class PeriodChunk(object):
    def __init__(self, quant: float, order: str, force: bool = False) -> None:
        order_cfg = order_config[order]
        if not force:
            while quant >= order_cfg['max']:
                order = reverse_lookup[order_cfg['ordering'] + 1]
                quant = quant / order_cfg['max']
                order_cfg = order_config[order]
            while quant < 1 and order_cfg['ordering'] != 0:
                order = reverse_lookup[order_cfg['ordering'] - 1]
                order_cfg = order_config[order]
                quant = quant * order_cfg['max']
        self.value = quant * order_cfg['value']
        self.quant = quant
        self.order = order
        self.cfg = order_cfg

    def __str__(self) -> str:
        return f'<PeriodChunk {self.quant}{self.order} {self.value}s>'

    def __repr__(self) -> str:
        return str(self)

    def to_timedelta(self):
        get_kwargs = self.cfg['timedelta']
        return timedelta(**get_kwargs(self.quant))

    def to_order(self, order: str) -> 'PeriodChunk':
        if order not in order_config:
            raise ValueError(f"Can't convert to order {order}!")
        if order != self.order:
            ratio = self.cfg['value'] / order_config[order]['value']
            return self.__class__(self.quant * ratio, order, force=True)
        else:
            return self

    @classmethod
    def parse(cls, period: str):
        quant = ''
        order = ''
        for char in period:
            if isdigit(char) or char == '.':
                if order:
                    yield cls(float(quant), order)
                    quant = ''
                    order = ''
                quant += char
            elif char.isalpha():
                if not quant:
                    raise ValueError(f"Can't parse period string: {period}")
                order += char
            else:
                raise ValueError(f"Invalid character {char} in period string {period}")
        if quant:
            if not order:
                raise ValueError(f"Can't parse period string: {period}")
            yield cls(float(quant), order)

    def __add__(self, other: 'PeriodChunk') -> 'PeriodChunk':
        if self.order == other.order:
            return self.__class__(self.quant + other.quant, self.order)
        else:
            tmp = other.to_order(self.order)
            return self.__class__(self.quant + tmp.quant, self.order)


class Period(object):
    def __init__(self, period: str) -> None:
        self.representation = period
        if period == 'now':
            self.chunks = ['now']
            self.sorted = ['now']
            self.order = None
            self.seconds = 0
        else:
            self.chunks = list(PeriodChunk.parse(period))
            self.sorted = sorted(self.chunks, key=lambda chunk: chunk.value, reverse=True)
            self.order = self.sorted[0].order
            self.seconds = sum(chunk.value for chunk in self.chunks)

    @staticmethod
    def sort_key(period_chunk: Tuple[float, str, int]) -> int:
        return period_chunk[2]

    def to_timedelta(self) -> timedelta:
        return sum((chunk.to_timedelta() for chunk in self.chunks), timedelta())

    def to_timestamp(self, **kw) -> Union[int, float]:
        val: float = pts() - self.seconds
        if kw.get('precision'):
            return val
        elif kw.get('ms'):
            return int(val * 1000)
        else:
            return int(val)

    def fill(self, dt, asdate=False):
        cfg = self.sorted[0].cfg
        if isinstance(dt, (int, float)):
            ts = dt
        else:
            ts = dt_to_ts(dt)
        if self.order == 'w':
            newts = 345600 + ((int((ts - 345600) / cfg['value']) + 1) * cfg['value'])
        else:
            newts = (int(ts / cfg['value']) + 1) * cfg['value']
        if asdate:
            return datetime.fromtimestamp(newts)
        else:
            return newts

    def reset(self, dt, asdate=False):
        cfg = self.sorted[0].cfg
        if isinstance(dt, (int, float)):
            ts = dt
        else:
            ts = dt_to_ts(dt)
        if self.order == 'w':
            newts = 345600 + (int((ts - 345600) / cfg['value']) * cfg['value'])
        else:
            newts = int(ts / cfg['value']) * cfg['value']
        if asdate:
            return datetime.fromtimestamp(newts)
        else:
            return newts


class Interval:
    '''
    Interval object represents an amount of time
    for instance '1w1m3h' => 1 week or 1 month + 3 hours
    Args:
        after:  start of the interval as a UNIX timestamp
        before: end of the interval as a UNIX timestamp
        step:   optional argument to divide the interval into buckets eg. 1 hour intervals in 1 day
    '''
    def __init__(self, after: int, before: int, step: Optional[int] = None):
        self.after = after
        self.before = before - 1
        self.step = step

    @classmethod
    def from_str(
            cls,
            interval_str: str,
            before: Optional[str] = None,
            step: Optional[str] = None,
            natural: bool = True
    ) -> 'Interval':
        '''
        Creates interval from a string representation
        Args:
            interval_str:   string representation of the interval eg. 1H | 2w1.5d | 15M
            before:         optional argument specifying when does the interval end
            step:
            natural:        optional argument specifying whether interval should start and end
                                on naturally occuring time eg. midnight, or full hour
        Returns:
            Interval: Interval object corresponding to interval_str representation
        '''
        interval_period = Period(interval_str)
        now = ts()
        if before is not None:
            now = now - Period(before).seconds
        if not natural:
            return cls(now - interval_period.seconds, now, Period(step).seconds)
        if step is not None:
            now = Period(step).fill(now)
        else:
            now = interval_period.reset(now)
        return cls(now - interval_period.seconds, now, Period(step).seconds)

    def to_start_end(self) -> Tuple[int]:
        '''Get a tuple of bounding timestamps in milliseconds'''
        return self.after, self.before - 1

    def __contains__(self, obj) -> bool:
        '''Check whether a timestamp or another inteval is included in self'''
        if isinstance(obj, (int, float)):
            return self.after < obj < self.before
        if isinstance(obj, Interval):
            return obj.after >= self.after and obj.before < self.before
        return False

    def __iter__(self):
        if self.step is None:
            yield self
            return
        after, before = self.to_start_end()
        while after <= before:
            yield Interval(after, after + self.step)
            after += self.step


order_config = {
    'M': {
        'ordering': 0,
        'value': 60,
        'timedelta': lambda quant: {'minutes': quant},
        'max': 60
    },
    'H': {
        'ordering': 1,
        'value': 60 * 60,
        'timedelta': lambda quant: {'hours': quant},
        'max': 24
    },
    'd': {
        'ordering': 2,
        'value': 60 * 60 * 24,
        'timedelta': lambda quant: {'days': quant},
        'max': 7
    },
    'w': {
        'ordering': 3,
        'value': 60 * 60 * 24 * 7,
        'timedelta': lambda quant: {'weeks': quant},
        'max': 4
    },
    'm': {
        'ordering': 4,
        'value': 60 * 60 * 24 * 7 * 4,
        'timedelta': lambda quant: {'weeks': 4 * quant},
        'max': float('Infinity')
    }
}

reverse_lookup = {
    0: 'M',
    1: 'H',
    2: 'd',
    3: 'w',
    4: 'm'
}

def dt_to_ts(dt):
    return time.mktime(dt.timetuple())

def to_midnight(dt: datetime):
    '''
    Round the provided datetime object to the last day
    Usage:
        >>> to_midnight(datetime.strptime('14 Aug 1993 10:21', '%d %b %Y %H:%M')).strftime('%d %b %Y %H:%M')
        "14 Aug 1993 00:00"
    '''
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)
