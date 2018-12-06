'''Separate interval module'''
from typing import Optional, Tuple

from .period import Period
from . import ts


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


class TickTock:
    '''
        An object recording two types of events and a distance between them
        Events:
            tick: starts a sequence, all following tock events will
                  calculate an elapsed time to tick as a start point
            tock: continues a sequence, calculates elapsed times since last tock and last tick
        Args:
            format:     print results in formatted/unformatted way          default=True
            print_func: which print handler to default to [eg. logger.info] default=print
            tick:       do the first 'tick' on initialization               default=True
    '''
    def __init__(self, format: bool=True, print_func: Callable=print, tick: bool=True) -> None:
        self.format_f = format
        self.print = print_func
        if tick:
            self.tick()
        else:
            self.start = None
            self.end = None

    def tick(self) -> None:
        '''Record a tick event'''
        self.start = self.last = helpers.ts(precision=True)

    def tock(self, format: Optional[bool]=None, print_func: Optional[Callable]=None) -> Tuple[float, float]:
        '''
            Record a tock event and print out how much time elapsed since last tock and tick
            Args:
                format:     print results in formatted/unformatted way
                print_func: which print handler to use [eg. logger.info]
            Returns:
                Tuple of floats => time since last tock, time since last tick
        '''
        if format is None:
            format = self.format_f
        if print_func is None:
            print_func = self.print
        new_last = helpers.ts(precision=True)
        old_last, self.last = self.last, new_last
        tock_elapsed = new_last - old_last
        tick_elapsed = new_last - self.start
        if format:
            tock_formatted = helpers.format_seconds(tock_elapsed)
            tick_formatted = helpers.format_seconds(tick_elapsed)
            msg = f'Elapsed {tock_formatted} / {tick_formatted} [last tock/last tick]'
        else:
            msg = f'{tock_elapsed}/{tick_elapsed}'
        print_func(msg)
        return tock_elapsed, tick_elapsed


_ticks_per_thread: Dict[int, TickTock] = {}
def tick(format: bool=True, print_func: Callable=print) -> None:
    '''
        Create a TickTock object for a current thread,
        or do a 'tick' for an existing one
        Args: look at helpers.time.TickTock.__init__
    '''
    global _ticks_per_thread
    ident: int = threading.get_ident()
    if ident in _ticks_per_thread:
        _ticks_per_thread[ident].tick()
    else:
        _ticks_per_thread[ident] = TickTock(format=format, print_func=print_func)

def tock(format: bool=True, print_func: Callable=print):
    '''
        Record a new 'tock' for a default TickTock object of a current thread
        [tock without a tick defaults to both tick and tock]
        Args: look at helpers.time.TickTock.tock
    '''
    global _ticks_per_thread
    ident = threading.get_ident()
    if ident not in _ticks_per_thread:
        _ticks_per_thread[ident] = TickTock(format=format, print_func=print_func)
    return _ticks_per_thread[ident].tock()

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

second = 1000
minute = 60 * second
hour = 60 * minute
day = 24 * hour
week = 7 * day

def pts():
    return time.time()
