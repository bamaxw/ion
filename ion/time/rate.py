'''Root time module containing helper functions and classes for dealing with time and dates'''
from dataclasses import dataclass, field
from typing import Optional, Callable

from . import pts
from ..string import clean_multiline


@dataclass
class RateInfo:
    '''
    Helper class holding info about item processing rate
    To make RateInfo know about items being processed use RateInfo.log
    '''
    start: float = field(default_factory=pts)
    last: float = field(default_factory=pts)
    end: float = field(default_factory=pts)
    total: Optional[int] = None
    processed: int = 0
    recently_processed: int = 0

    @property
    def elapsed(self) -> float:
        '''Return time elapsed from the start of this RateInfo up until last log'''
        return self.end - self.start

    @property
    def recently_elapsed(self) -> float:
        '''Return time elapsed between the last and second last 'log\''''
        return self.end - self.last

    @property
    def remaining(self) -> int:
        '''If total was provided, return the number of items that were not processed yet'''
        if self.total:
            return self.total - self.processed
        return self.total

    @property
    def rate(self) -> float:
        '''Return an average rate of processed items per second since the start of the RateInfo'''
        return self.processed / self.elapsed

    @property
    def recent_rate(self) -> float:
        '''
        Return the most recent rate of processed items per seconds
        based on the time period between last and second last 'log'
        '''
        return self.recently_processed / self.recently_elapsed

    @property
    def remaining_time(self) -> Optional[float]:
        '''Return predicted remaining time based on current number of remaining items and average rate'''
        if self.remaining:
            return self.remaining / self.rate
        return None

    @property
    def recent_remaining_time(self) -> Optional[float]:
        '''Return predicted remaining time based on current number of remaining items and most recent rate'''
        if self.remaining:
            return self.remaining / self.recent_rate
        return None

    def log(self, amount: int = 1) -> None:
        '''Log processed items'''
        self.last, self.end = self.end, pts()
        self.processed += amount
        self.recently_processed = amount

TEMPLATE_NO_TOTAL = clean_multiline('''
Processed {processed} {item_name}s in {elapsed}s
    {recent_rate} {item_name}s per second [AVG: {rate} {item_name}s per second]
''')

TEMPLATE_TOTAL = clean_multiline('''
Processed {processed} {item_name}s in {elapsed}s [{remaining} {item_name}s remaining]
    {recent_rate} {item_name}s per second [AVG: {rate} {item_name}s per second]
    {recent_remaining_time} seconds left [AVG: {remaining_time} seconds left]
''')


class Stopper:
    '''
    Stopper measures a rate of throughput of items
    Arguments:
        == Optional ==
        total         -- set this if you know how many items in total are going to be processed
                         this enables Stopper to predict how much time is left
        logger        -- function used to log Stopper messages
                         set to None if you don't require logging
        log_frequency -- how often should log event be released
                         (if None the log is going to be printed on every 'log' call)
        item_name     -- set an item name for logging purposes
        template      -- set template used for logging
    '''
    def __init__(
            self,
            *,
            total: Optional[int] = None,
            logger: Callable = print,
            log_frequency: int = None,
            item_name: str = 'item',
            template: str = None
    ):
        self.rate = RateInfo(total=total)
        self._logger = logger
        self._log_freq = log_frequency
        self._last_logged = 0
        self.item_name = item_name
        self._template = template
        if template is None:
            self._template = TEMPLATE_TOTAL if total else TEMPLATE_NO_TOTAL
        self._logger(f'Started processing {self.item_name}s!!!')

    def get_message(self) -> str:
        '''Format template with data in RateInfo'''
        return self._template.format(
            **self.rate.__dict__,
            remaining=self.rate.remaining,
            elapsed=self.rate.elapsed,
            item_name=self.item_name,
            rate=self.rate.rate,
            recent_rate=self.rate.recent_rate,
            remaining_time=self.rate.remaining_time,
            recent_remaining_time=self.rate.recent_remaining_time
        )

    def _should_log(self) -> bool:
        if self._log_freq is None:
            return True
        if self._last_logged + self._log_freq <= pts():
            return True
        return False

    def print(self, force: bool = False):
        if force or self._should_log():
            self._logger(self.get_message())
            self._last_logged = pts()

    def log(self, amount: int = 1):
        self.rate.log(amount)
        self.print()
